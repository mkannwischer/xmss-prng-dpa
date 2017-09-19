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

#own libs
import helper
# other libs
import fixedint
import numpy as np
import hashlib
import array


'''
 * containing SHA256 specific helper functions
'''

"""
 * hashing a index to calculate the known message block
"""
def get_idx_hash(idx):
    bytesarray = [(idx >> i & 0xff) for i in (24, 16, 8, 0)]
    idx_hash =   hashlib.sha256(bytearray(bytesarray))
    idx_hash_array = np.array(array.array("B", idx_hash.digest()), dtype=np.uint8)
    return [idx_hash_array[:4],  idx_hash_array[4:8]]



'''
 * implementation of a cyclic shift
 * C equivalent: #define ROTR(x,n) ((x>>n)|(x<<(32-n)))
'''
def rotr(x, n):
    return ((x>>n)|(x<<(32-n)))


'''
 * implementation of the Sigma1 function of SHA256
 * input: int
 * C equivalent: #define Sigma_1(x) (ROTR(x,6)^ROTR(x,11)^ROTR(x,25))
'''
def __Sigma1(x):
    return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x,25)

'''
 * implementation of the Sigma1 function of SHA256
 * input: 4-element byte array
 * C equivalent: #define Sigma_1(x) (ROTR(x,6)^ROTR(x,11)^ROTR(x,25))
'''
def Sigma1(w):
    value = fixedint.UInt32(helper.byte_to_int_array(w))
    result = __Sigma1(value)
    return helper.int_to_byte(result)

'''
 * vectorized implementation of the Sigma1 function of SHA256
 * input: P x 4-dim byte matrix
'''
def Sigma1_vec(w):
    w = np.array(w)
    value = helper.byte_array_to_int_vec(w)
    result = __Sigma1(value)
    return helper.int_to_byte_vec(result)



'''
 * implementation of the Ch function of SHA256
 * Input: int
 * C equivalent: #define Ch(x,y,z) ((x&y)^((~x)&z))
'''
def __Ch(x,y,z):
    return ((x&y)^((~x)&z))

'''
 * implementation of the Ch function of SHA256
 * Input: 4-element byte array
 * C equivalent: #define Ch(x,y,z) ((x&y)^((~x)&z))
'''
def Ch(x,y,z):
    x = fixedint.UInt32(x)
    y = fixedint.UInt32(y)
    z = fixedint.UInt32(z)
    result = __Ch(x,y,z)
    return helper.int_to_byte(result);

'''
 * calculation of H (see algorithm 5.1 - line 6)
 * C equivalent: unsigned int T1 = h + Sigma_1(e)+ Ch(e,f,g)+ SHA256_K[t] + message_schedule[t];
'''
def calcH(T1, e, f, g, k, m):
    T1 = fixedint.UInt32(T1)
    e = fixedint.UInt32(e)
    f = fixedint.UInt32(f)
    g = fixedint.UInt32(g)
    k = fixedint.UInt32(k)
    m = fixedint.UInt32(m)
    return T1 - __Sigma1(e) - __Ch(e,f,g)-k - m;
