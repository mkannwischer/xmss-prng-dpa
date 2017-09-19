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

#include "ownsha256.h"

#include <stdio.h>
#include "util.h"



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
      message_schedule[t] = sigma_1(message_schedule[t-2]) + message_schedule[t-7]+
                            sigma_0(message_schedule[t-15]) + message_schedule[t-16];
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
      unsigned int T1 = h + Sigma_1(e)+ Ch(e,f,g)+ SHA256_K[t] + message_schedule[t];
      unsigned int T2 = Sigma_0(a)+Maj(a,b,c);
      h=g; g=f; f=e;
      e= d + T1;
      d=c; c=b; b=a;
      a = T1+T2;
  }

  hash[0] = a + hash[0];
  hash[1] = b + hash[1];
  hash[2] = c + hash[2];
  hash[3] = d + hash[3];
  hash[4] = e + hash[4];
  hash[5] = f + hash[5];
  hash[6] = g + hash[6];
  hash[7] = h + hash[7];
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
