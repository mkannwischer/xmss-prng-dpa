#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
 * Copyright (c) 2017, Matthias Julius Kannwischer
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
'''
# own libs
import dpa
import helper
import sha256_helper

# other libs
import sys
import numpy as np
import time
start_time = time.time()

def usage():
    print "usage ./analyze_8bit.py traceFile secretDataFile threshold [--silent]"
    exit()
# sanity check params
if len(sys.argv) < 4 or len(sys.argv) > 5:
    print "WRONG NUMBER OF ARGUMENTS"
    usage()

if len(sys.argv) == 5:
    if(sys.argv[4] != "--silent"):
        print "INVALID PARAMETER 2"
        usage()
    else:
        silent = 1
else:
    silent = 0



if(silent != 1):print "##### ANALYZING POWER TRACE #####"

[secretSeed, secretIv , secretDelta, secretT1] = helper.load_secret_data(sys.argv[2])
threshold = float(sys.argv[3])


np.seterr(divide='ignore', invalid='ignore')
# extract traces from file
[T, num_traces, size_per_traces] = helper.load_traces(sys.argv[1])
#print T
# calculate known data
message_0 = np.zeros([num_traces, 4], dtype=np.uint8);
message_1 = np.zeros([num_traces, 4], dtype=np.uint8);
for i in range (0, num_traces):
    message_0[i], message_1[i] = sha256_helper.get_idx_hash(i)

current_sample = 0


# cheating a bit here
# these are given in a file, since we only want to perform DPA5
delta = int(secretDelta[2:], 16)
D_0 = int(secretIv[2+24:2+32], 16)
T1 = helper.int_to_byte_vec(helper.byte_array_to_int_vec(message_0) + delta)
E1 = helper.int_to_byte_vec(helper.byte_array_to_int_vec(T1) + D_0)
nE1 = helper.int_to_byte_vec(~helper.byte_array_to_int_vec(E1))

'''
 * DPA 5
 * F_0 equals G_1
 * ~E_1 & G_1 in Ch
'''
F_0_0, j = dpa.dpa_and(T[:, current_sample:], 1, nE1, 3, threshold)
current_sample += j
F_0_1, j = dpa.dpa_and(T[:, current_sample:], 0, nE1, 2, threshold)
current_sample += j
F_0_2, j = dpa.dpa_and(T[:, current_sample:], 0, nE1, 1, threshold)
current_sample += j
F_0_3, j = dpa.dpa_and(T[:, current_sample:], 0, nE1, 0, threshold)
current_sample += j
F_0 = helper.byte_to_int(F_0_3, F_0_2, F_0_1, F_0_0)
if(silent != 1): print "F_0=", hex(F_0)

end_time = time.time()




attack_success = helper.compareBytes("0x"+secretIv[2+5*8:2+6*8], [F_0])
if silent != 1:
    GREEN = '\033[92m'
    RED = '\033[91m'
    if attack_success:
        print GREEN, "FOUND CORRECT KEY"
    else:
        print RED, "KEY NOT CORRECT"
    ENDC = '\033[0m'
    print ENDC

if silent == 1:
    #success; num_traces; samples_per_trace; secretSeed; secretIv; secretDelta; delta; threshold; start_time; end_time
    print "%d;%d;%d;%s;%s;%s;%s;%f;%d;%d" % (attack_success, num_traces,size_per_traces, secretSeed, secretIv, secretDelta, hex(F_0), threshold, start_time, end_time)
