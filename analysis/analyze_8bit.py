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
import fixedint
import numpy as np
import time

start_time = time.time()

def usage():
    print "usage ./analyze_8bit.py traceFile secretDataFile [--silent]"
    exit()
# sanity check params
if len(sys.argv) < 3 or len(sys.argv) > 4:
    print "WRONG NUMBER OF ARGUMENTS"
    usage()

if len(sys.argv) == 4:
    if(sys.argv[3] != "--silent"):
        print "INVALID PARAMETER 2"
        usage()
    else:
        silent = 1
else:
    silent = 0


if(silent != 1): print "##### ANALYZING POWER TRACE #####"

np.seterr(divide='ignore', invalid='ignore')
# extract traces from file
[T, num_traces, size_per_traces] = helper.load_traces(sys.argv[1])

# calculate known data
message_0 = np.zeros([num_traces, 4], dtype=np.uint8)
message_1 = np.zeros([num_traces, 4], dtype=np.uint8)
for i in range (0, num_traces):
    message_0[i], message_1[i] = sha256_helper.get_idx_hash(i)

threshold = 0.99

'''
 * DPA 1
 * T1 = delta + W_0
'''
if(silent != 1): print 'DPA1: Recovering delta from T1 = delta + W_0...'
current_sample = 0
delta0, j = dpa.dpa_addition(T[:, current_sample:], 0, message_0, 3, -1, threshold)
#current_sample += j
delta1, j = dpa.dpa_addition(T[:, current_sample:], 0, message_0, 2, delta0, threshold)
current_sample += j
delta2, j = dpa.dpa_addition(T[:, current_sample:], 0, message_0, 1, delta1, threshold)
current_sample += j
delta3, j = dpa.dpa_addition(T[:, current_sample:], 0, message_0, 0, delta2, threshold)
current_sample += j
delta = helper.byte_to_int(delta3, delta2, delta1, delta0)
if(silent != 1): print "delta=", hex(delta)




'''
 * DPA 2
 * E_1 = D_0 + T1_1
'''
if(silent != 1): print 'DPA2: Recovering D_0 from E_1 = D_0 + T1_1...'
# calculate known T1's
T1 = helper.int_to_byte_vec(helper.byte_array_to_int_vec(message_0) + delta)
d_0_0, j = dpa.dpa_addition(T[:, current_sample:], 0, T1, 3, -1, threshold)
current_sample += j
d_0_1, j = dpa.dpa_addition(T[:, current_sample:], 0, T1, 2, d_0_0, threshold)
current_sample += j
d_0_2, j = dpa.dpa_addition(T[:, current_sample:], 0, T1, 1, d_0_1, threshold)
current_sample += j
d_0_3, j = dpa.dpa_addition(T[:, current_sample:], 0, T1, 0, d_0_2, threshold)
current_sample += j

D_0 = helper.byte_to_int(d_0_3, d_0_2, d_0_1, d_0_0)
if(silent != 1): print "D_0=", hex(D_0)


'''
 * DPA 3
 * A_1 = T1_1 + T2_1
'''
if(silent != 1): print 'DPA3: Recovering T2_1 from T1_1 + T2_1'
T2_0, j = dpa.dpa_addition(T[:, current_sample:], 0, T1, 3, -1, threshold)
current_sample += j
T2_1, j = dpa.dpa_addition(T[:, current_sample:], 0, T1, 2, T2_0, threshold)
current_sample += j
T2_2, j = dpa.dpa_addition(T[:, current_sample:], 0, T1, 1, T2_1, threshold)
current_sample += j
T2_3, j = dpa.dpa_addition(T[:, current_sample:], 0, T1, 0, T2_2, threshold)
current_sample += j
T2 = helper.byte_to_int(T2_3, T2_2, T2_1, T2_0)
if(silent != 1): print "T2=", hex(T2)


'''
 * DPA 8
 * G_0 equals H_1
 * T1_2 = H_1 + Sigma(E_1) + ...
'''
if(silent != 1): print 'DPA8: Recovering G_0=H_1 from T1_2 = H_1 + Sigma(E_1)...'
E1 = helper.int_to_byte_vec(helper.byte_array_to_int_vec(T1) + D_0)
Sigma1_E1 = [sha256_helper.Sigma1(w) for w in E1]
G_0_0, j = dpa.dpa_addition(T[:, current_sample:], 1, Sigma1_E1, 3, -1, threshold)
current_sample += j
G_0_1, j = dpa.dpa_addition(T[:, current_sample:], 0, Sigma1_E1, 2, G_0_0, threshold)
current_sample += j
G_0_2, j = dpa.dpa_addition(T[:, current_sample:], 0, Sigma1_E1, 1, G_0_1, threshold)
current_sample += j
G_0_3, j = dpa.dpa_addition(T[:, current_sample:], 0, Sigma1_E1, 0, G_0_2, threshold)
current_sample += j
G_0 = helper.byte_to_int(G_0_3, G_0_2, G_0_1, G_0_0)
if(silent != 1): print "G_0=", hex(G_0)


'''
 * DPA 5
 * F_0 equals G_1
 * ~E_1 & G_1 in Ch
'''
if(silent != 1): print 'DPA5: Recovering F_0=G_1 from ~E_1 & G_1 in Ch...'
# Ch(e_1, f_1, g_1)
# remember: #define Ch(x,y,z) ((x&y)^((~x)&z))
# first we calculate our known e_1s
nE1 = helper.int_to_byte_vec(~helper.byte_array_to_int_vec(E1))
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




'''
 * DPA 4
 * E_0 equals F_1
 * E_1 & F_1 in Ch
'''
if(silent != 1): print 'DPA4: Recovering E_0=F_1 from E_1 & F_1 in Ch...'
# Ch(e_1,f_1,g_1)
# remember: #define Ch(x,y,z) ((x&y)^((~x)&z))
E_0_0, j = dpa.dpa_and(T[:, current_sample:], 0, E1, 3, threshold)
current_sample += j
E_0_1, j = dpa.dpa_and(T[:, current_sample:], 0, E1, 2, threshold)
current_sample += j
E_0_2, j = dpa.dpa_and(T[:, current_sample:], 0, E1, 1, threshold)
current_sample += j
E_0_3, j = dpa.dpa_and(T[:, current_sample:], 0, E1, 0, threshold)
current_sample += j
E_0 = helper.byte_to_int(E_0_3, E_0_2, E_0_1, E_0_0)
if(silent != 1): print "E_0=", hex(E_0)

'''
 * DPA 7
 * B_0 equals C_1
 * A_1 & C_1 in Maj
'''
if(silent != 1): print 'DPA7: Recovering B_0=C_1 from A_1 & C_1 in Maj...'
# it is recovered from Maj(a_1,b_1,c_1)
A1 = helper.int_to_byte_vec(helper.byte_array_to_int_vec(T1) + T2)
B_0_0, j = dpa.dpa_and(T[:, current_sample:], 0, A1, 3, threshold)
current_sample += j
B_0_1, j = dpa.dpa_and(T[:, current_sample:], 0, A1, 2, threshold)
current_sample += j
B_0_2, j = dpa.dpa_and(T[:, current_sample:], 0, A1, 1, threshold)
current_sample += j
B_0_3, j = dpa.dpa_and(T[:, current_sample:], 0, A1, 0, threshold)
current_sample += j
B_0 = helper.byte_to_int(B_0_3, B_0_2, B_0_1, B_0_0)
if(silent != 1): print "B_0=", hex(B_0)

'''
 * DPA 6
 * A_0 equals B_1
 * A_1 & B_1 in Maj
'''
if(silent != 1): print 'DPA6: Recovering A_0=B_1 from A_1 & B_1 in Maj...'
# it is recovered from Maj(a_1,b_1,c_1)
# remember: #define Maj(x,y,z) ((x&y)^(x&z)^(y&z))
A_0_0, j = dpa.dpa_and(T[:, current_sample:], 0, A1, 3, threshold)
current_sample += j
A_0_1, j = dpa.dpa_and(T[:, current_sample:], 0, A1, 2, threshold)
current_sample += j
A_0_2, j = dpa.dpa_and(T[:, current_sample:], 0, A1, 1, threshold)
current_sample += j
A_0_3, j = dpa.dpa_and(T[:, current_sample:], 0, A1, 0, threshold)
current_sample += j
A_0 = helper.byte_to_int(A_0_3, A_0_2, A_0_1, A_0_0)
if(silent != 1): print "A_0=", hex(A_0)



if(silent != 1): print 'Calculating H_0...'
# rest is pure calculation
H_0 = sha256_helper.calcH(helper.byte_to_int_array(T1[0]), E_0, F_0, G_0, 0x428a2f98L, helper.byte_to_int_array(message_0[0]))
if(silent != 1): print "H_0=", hex(H_0)
H_1 = fixedint.UInt32(G_0)
F_1 = fixedint.UInt32(E_0)
G_1 = fixedint.UInt32(F_0)

T1_1 = np.zeros([len(T1), 4], dtype=np.uint8)
for i in range(0, len(T1)):
    E_tmp = fixedint.UInt32(helper.byte_to_int_array(E1[i]))
    S0E1 = fixedint.UInt32(helper.byte_to_int_array(Sigma1_E1[i]))
    const = fixedint.UInt32(0x71374491L)
    mes = fixedint.UInt32(helper.byte_to_int_array(message_1[i]))
    value = H_1 + S0E1 + sha256_helper.__Ch(E_tmp, F_1, G_1) + const + mes
    T1_1[i] = helper.int_to_byte(value)

'''
 * DPA 9
 * C_0 equals D_1
 * E_2 = D_1 +T1_2
'''
if(silent != 1): print 'DPA9: Recovering C_0=D_1 from E_2 = D_1 +T1_2...'
C_0_0, j = dpa.dpa_addition(T[:, current_sample:], 0, T1_1, 3, -1, threshold)
current_sample += j
C_0_1, j = dpa.dpa_addition(T[:, current_sample:], 0, T1_1, 2, C_0_0, threshold)
current_sample += j
C_0_2, j = dpa.dpa_addition(T[:, current_sample:], 0, T1_1, 1, C_0_1, threshold)
current_sample += j
C_0_3, j = dpa.dpa_addition(T[:, current_sample:], 0, T1_1, 0, C_0_2, threshold)
current_sample += j
C_0 = helper.byte_to_int(C_0_3, C_0_2, C_0_1, C_0_0)
if(silent != 1): print "C_0=", hex(C_0)
end_time = time.time()

[secretSeed, secretIv , secretDelta, secretT1] = helper.load_secret_data(sys.argv[2])


attack_success = helper.compareBytes(secretIv, [A_0, B_0, C_0, D_0, E_0, F_0, G_0, H_0])
if(silent != 1):
    print "#####################"
    print "A_0=", hex(A_0)
    print "B_0=", hex(B_0)
    print "C_0=", hex(C_0)
    print "D_0=", hex(D_0)
    print "E_0=", hex(E_0)
    print "F_0=", hex(F_0)
    print "G_0=", hex(G_0)
    print "H_0=", hex(H_0)

    print "iv=", secretIv


    GREEN = '\033[92m'
    RED = '\033[91m'
    if attack_success:
        print GREEN, "FOUND CORRECT KEY"
    else:
        print RED, "KEY NOT CORRECT"

        ENDC = '\033[0m'
        print ENDC
if silent == 1:
    #success;num_traces;samples_per_trace;secretSeed;secretIv;secretT1;secretDelta;
    #recoveredA;recoveredB;recoveredC;recoveredD;recoveredE,recoveredF;recoveredG; recoveredH
    #recoveredT2;recoveredDelta;start_time; end_time
    print "%d;%d;%d;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%d;%d" % (attack_success, num_traces, size_per_traces, secretSeed, secretIv, secretT1, secretDelta, hex(A_0), hex(B_0), hex(C_0), hex(D_0), hex(E_0), hex(F_0), hex(G_0), hex(H_0), hex(T2), hex(delta), start_time, end_time)
