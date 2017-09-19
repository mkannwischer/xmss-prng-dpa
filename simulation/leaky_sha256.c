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


#include "leaky_sha256.h"

#include <stdio.h>
#include "util.h"

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


/**
 * implementing the SHA256 padding of a message, s.t. the length is divisible by 512 bits
 */
size_t padding(const unsigned char *message, size_t message_length, unsigned char **padded_msg_ptr){
  // padding
  int padding_length_byte = (56 - message_length - 1)%64;
  int padded_message_length = message_length+1+padding_length_byte+8;
  // message + 1 +  padding + length
  unsigned char *padded_msg = (unsigned char *) malloc(padded_message_length * sizeof(unsigned char));

  memcpy(padded_msg, message, message_length);
  padded_msg[message_length] = 0x80;
  memset(&padded_msg[message_length+1], 0, padding_length_byte);

  for(int i=0;i<8;i++){
    padded_msg[message_length+1+padding_length_byte+i]= (unsigned char)  (0xFF & (8*message_length >> (56-i*8)));
  }

  *padded_msg_ptr = padded_msg;
  return padded_message_length;
}

/**
 * creating the message schedule for the compression function from a 512-bit message block
 * i.e. expanding 512 bit to 64x32 bit, which are later consumed in the 64 compression function iterations
 */
void create_message_schedule(unsigned char* message_block, unsigned int **message_schedule_ptr){

    unsigned int *message_schedule = (unsigned int *) malloc(64*sizeof(unsigned int));
    uchar_to_uint(message_block, 64, message_schedule);

    for(int t=16;t<64;t++){
      message_schedule[t] = leak_uint_plus(leak_uint_plus(leak_uint_plus(sigma_1(message_schedule[t-2]), message_schedule[t-7]),
                            sigma_0(message_schedule[t-15])), message_schedule[t-16]);
    }

    *message_schedule_ptr = message_schedule;
}

/**
 * implementation of the SHA256 compression function
 * 256 bit (iv) x 512 bit (message_block) -> 256 bit (hash/iv)
 * input of iv and output in hash
 */
void ownsha256_compression_function(unsigned int hash[8], unsigned char message_block[64]){
  unsigned int *message_schedule;
  create_message_schedule(message_block, &message_schedule);
  unsigned int a,b,c,d,e,f,g,h;
  a = hash[0]; b = hash[1]; c = hash[2]; d = hash[3];
  e = hash[4]; f = hash[5]; g = hash[6]; h = hash[7];

  for(int t=0;t<64;t++){
      unsigned int T1 = leak_uint_plus(h, Sigma_1(e));
      T1 = leak_uint_plus(T1, Ch(e,f,g));
      T1 = leak_uint_plus(T1, SHA256_K[t]);
      T1 = leak_uint_plus(T1, message_schedule[t]);
      unsigned int T2 = leak_uint_plus(Sigma_0(a),Maj(a,b,c));
      h=g; g=f; f=e;
      e= leak_uint_plus(d,T1);
      d=c; c=b; b=a;
      a = leak_uint_plus(T1,T2);
  }

  hash[0] = leak_uint_plus(a, hash[0]);
  hash[1] = leak_uint_plus(b, hash[1]);
  hash[2] = leak_uint_plus(c, hash[2]);
  hash[3] = leak_uint_plus(d, hash[3]);
  hash[4] = leak_uint_plus(e, hash[4]);
  hash[5] = leak_uint_plus(f, hash[5]);
  hash[6] = leak_uint_plus(g, hash[6]);
  hash[7] = leak_uint_plus(h, hash[7]);
  free(message_schedule);
}

/**
 * implementing the SHA256 hash computation
 */
void ownsha256(const unsigned char *message, size_t message_length,
  unsigned char *message_digest){
    //printf("message=");
    //print_hex(message, message_length);

    // padding
    unsigned char *padded_msg;
    size_t padded_message_length = padding(message, message_length, &padded_msg);
    //printf("padded_message=");
    //print_hex(padded_msg, padded_message_length);

    // state
    unsigned int hash[8];
    memcpy(hash, SHA256_IV, 32);


    int number_of_blocks = padded_message_length/64;
    for(int i=0;i<number_of_blocks;i++){
      ownsha256_compression_function(hash, &padded_msg[i*64]);
    }
    free(padded_msg);
    uint_to_uchar(hash, 8, message_digest);
    //printf("message_digest=");
    //print_hex(message_digest, 32);
}
