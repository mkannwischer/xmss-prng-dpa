/*
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
*/

#ifndef OWNSHA256_H
#define OWNSHA256_H

#include <stdlib.h>
#include <string.h>

#define ROTR(x,n) ((x>>n)|(x<<(32-n)))
#define SHR(x,n) (x>>n)
#define sigma_0(x) (ROTR(x,7)^ROTR(x,18)^SHR(x,3))
#define sigma_1(x) (ROTR(x,17)^ROTR(x,19)^SHR(x,10))
#define Sigma_0(x) (ROTR(x,2)^ROTR(x,13)^ROTR(x,22))
#define Sigma_1(x) (ROTR(x,6)^ROTR(x,11)^ROTR(x,25))
#define Ch(x,y,z) ((x&y)^((~x)&z))
#define Maj(x,y,z) ((x&y)^(x&z)^(y&z))





static unsigned int SHA256_IV[8] =  {0x6a09e667UL, 0xbb67ae85UL, 0x3c6ef372UL, 0xa54ff53aUL,
                                     0x510e527fUL, 0x9b05688cUL, 0x1f83d9abUL, 0x5be0cd19UL};

static unsigned int SHA256_K[64] = {
  0x428a2f98UL, 0x71374491UL, 0xb5c0fbcfUL, 0xe9b5dba5UL,
  0x3956c25bUL, 0x59f111f1UL, 0x923f82a4UL, 0xab1c5ed5UL,
  0xd807aa98UL, 0x12835b01UL, 0x243185beUL, 0x550c7dc3UL,
  0x72be5d74UL, 0x80deb1feUL, 0x9bdc06a7UL, 0xc19bf174UL,
  0xe49b69c1UL, 0xefbe4786UL, 0x0fc19dc6UL, 0x240ca1ccUL,
  0x2de92c6fUL, 0x4a7484aaUL, 0x5cb0a9dcUL, 0x76f988daUL,
  0x983e5152UL, 0xa831c66dUL, 0xb00327c8UL, 0xbf597fc7UL,
  0xc6e00bf3UL, 0xd5a79147UL, 0x06ca6351UL, 0x14292967UL,
  0x27b70a85UL, 0x2e1b2138UL, 0x4d2c6dfcUL, 0x53380d13UL,
  0x650a7354UL, 0x766a0abbUL, 0x81c2c92eUL, 0x92722c85UL,
  0xa2bfe8a1UL, 0xa81a664bUL, 0xc24b8b70UL, 0xc76c51a3UL,
  0xd192e819UL, 0xd6990624UL, 0xf40e3585UL, 0x106aa070UL,
  0x19a4c116UL, 0x1e376c08UL, 0x2748774cUL, 0x34b0bcb5UL,
  0x391c0cb3UL, 0x4ed8aa4aUL, 0x5b9cca4fUL, 0x682e6ff3UL,
  0x748f82eeUL, 0x78a5636fUL, 0x84c87814UL, 0x8cc70208UL,
  0x90befffaUL, 0xa4506cebUL, 0xbef9a3f7UL, 0xc67178f2UL
};




void ownsha256_compression_function(unsigned int hash[8], unsigned char message_block[64]);
void ownsha256(const unsigned char *message, size_t message_length,
  unsigned char *message_digest);

#endif
