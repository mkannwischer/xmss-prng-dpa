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

# other libs
import numpy as np

hw_lut = [0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4,
          1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
          1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
          2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
          1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
          2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
          2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
          3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
          1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5,
          2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
          2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
          3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
          2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
          3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
          3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7,
          4, 5, 5, 6, 5, 6, 6, 7, 5, 6, 6, 7, 6, 7, 7, 8]

hw_lut_vec = np.array(hw_lut)


"""
 * optimized and vectorized implementation of the Hamming weight computation
 * called extremly often
"""
def hw_vec(x):
    x = np.array(x, dtype=np.uint8)
    return hw_lut_vec[x]

"""
 * vectorized implementation of the Pearson correlation coefficient
"""
def correlate(A,B):
    A_mA = A - A.mean(1)[:,None]
    B_mB = B - B.mean(1)[:,None]
    ssA = (A_mA**2).sum(1)
    ssB = (B_mB**2).sum(1)
    return np.dot(A_mA,B_mB.T)/np.sqrt(np.dot(ssA[:,None],ssB[None]))

"""
 * Given traces T and hypothetical power consumption values H the key candidates
 * with the highest correlations are obtained.
 * Returns all key hypotheses with correlations higher than threshold*max
 *
 * threshold obtained experimentally
 * it depends on the leakage model (HW or HW_BYTE)
 * and the attacked operation (AND or ADD)
"""
def getMaxCorrelation(T, H, threshold):
    R = correlate(T.T,H.T)

    # for plots/corr_over_time.py uncomment this
    #np.save("data/correlation_values", R)
    #exit();

    # for experiment7 uncomment this
    #np.save("data/exp_7/%d"%len(T), R)
    #exit()

    R[np.isnan(R)] = -1
    for i in range (0, R.shape[0]):
        R[i, R[i] != R[i].max()] = 0

    max_idxs = np.asarray(np.where(np.matrix(R) >= threshold *np.matrix(R).max())).T
    return max_idxs

"""
 * implements a 8-bit dpa for addition
 * T: DxT power traces
 * T_idx: sometimes several operations in the traces have high correlations and we
 *        know that we are attacking the i-th one. T_idx can be used to select the
 *        i-th sample with high correlations
 * d: Dx4 containing known data (per byte)
 * d_idx: the index of the byte that is currently attacked (0...3)
 * prev: less significant recovered value, required for carry calculation, -1 if d_idx=3
 * threshold: see getMaxCorrelation
"""
def dpa_addition(T, T_idx, d, d_idx, prev, threshold):
    d = np.array(d, dtype=np.uint16)
    H = np.zeros([len(T), 256])

    if prev == -1:
        carry = np.zeros([len(T)])
    else:
        carry = (d[:, d_idx+1]+prev)//256

    d = np.array(d, dtype=np.uint8)
    for hyp in range(0,256):
        H[:, hyp] = hw_vec(np.add(d[:, d_idx], carry)+hyp)

    corr = getMaxCorrelation(T, H, threshold)
    if(len(corr) <= T_idx):
        #print 'warning: ', T_idx, 'out of bounds'
        return corr[-1][::-1]
    else:
        return corr[T_idx][::-1]

'''
 *  similar as dpa_addition
 *  but all previously recovered values are required in prev_arr
'''
def partial_dpa_addition(T, T_idx, d, d_idx, prev_arr, threshold):
    d = np.array(d)
    H = np.zeros([len(T), 256])

    lower_significant_hw = np.zeros([len(T)])
    carry = np.zeros([len(T)])
    for idx, prev in enumerate(prev_arr):
        tmp = np.add(d[:, 3-idx], carry)+prev
        lower_significant_hw = np.add(lower_significant_hw,  hw_vec(tmp%256))
        carry = tmp // 256

    for hyp in range(0,256):
        H[:, hyp] = np.add(lower_significant_hw, hw_vec(np.add(d[:, d_idx], carry)+hyp))
    corr = getMaxCorrelation(T, H, threshold)
    if(len(corr) <= T_idx):
        #print 'warning: ', T_idx, 'out of bounds'
        return corr[-1][::-1]
    else:
        return corr[T_idx][::-1]

'''
 *   similar as dpa_addition
 *   but no prev is required, because we don't have a carry bit
'''
def dpa_and(T, T_idx, d, d_idx, threshold):
    d = np.array(d)
    H = np.zeros([len(T), 256])

    for hyp in range(0,256):
        H[:, hyp] = hw_vec(d[:, d_idx]&hyp)
    corr = getMaxCorrelation(T, H, threshold)
    if(len(corr) <= T_idx):
        #print 'warning: ', T_idx, 'out of bounds'
        return corr[-1][::-1]
    else:
        return corr[T_idx][::-1]

'''
 *   similar as dpa_and
 *   but all prev values are required for properly predicting the HW
'''
def partial_dpa_and(T, T_idx, d, d_idx, prev_arr, threshold):
    d = np.array(d)
    H = np.zeros([len(T), 256])
    lower_significant_hw = np.zeros([len(T)])
    for idx, prev in enumerate(prev_arr):
        lower_significant_hw = np.add(lower_significant_hw,  hw_vec(d[:, 3-idx]&prev))
    for hyp in range(0,256):
        H[:, hyp] = np.add(lower_significant_hw, hw_vec(d[:, d_idx]&hyp))
    corr = getMaxCorrelation(T, H, threshold)
    print corr
    if(len(corr) <= T_idx):
        print 'warning: ', T_idx, 'out of bounds'
        return corr[-1][::-1]
    else:
        return corr[T_idx][::-1]
