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

j = 0
'''
 * DPA 1
 * T1 = delta + W_0
'''
delta0, _j = dpa.dpa_addition(T[:, j:], 0, message_0, 3, -1, threshold);
j += _j
delta1, _j = dpa.partial_dpa_addition(T[:, j:j+1], 0, message_0, 2, [delta0], threshold);
delta2, _j = dpa.partial_dpa_addition(T[:, j:j+1], 0, message_0, 1, [delta0, delta1], threshold);
delta3, _j = dpa.partial_dpa_addition(T[:, j:j+1], 0, message_0, 0, [delta0, delta1, delta2], threshold);

delta = helper.byte_to_int(delta3, delta2, delta1, delta0)
# we now recovered delta
if(silent != 1): print "delta=", hex(delta)
end_time = time.time()
[secretSeed, secretIv , secretDelta, secretT1] = helper.load_secret_data(sys.argv[2])

attack_success = helper.compareBytes(secretDelta, [delta]);
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
    print "%d;%d;%d;%s;%s;%s;%s;%f;%d;%d" % (attack_success, num_traces,size_per_traces, secretSeed, secretIv, secretDelta, hex(delta), threshold, start_time, end_time)
