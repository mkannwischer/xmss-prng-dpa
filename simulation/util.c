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

#include "util.h"
#include <stdio.h>

/**
 * print unsigned int array to stdout as hex string
 */
void print_hex_uint(const unsigned int *data, int length){
  printf("0x");
  for(int i=0;i<length;i++){
      printf("%08x", data[i]);
  }
  printf("\n");
}

/**
 * prints byte array to stdout as hex string
 */
void print_hex(const unsigned char *data, int length){
  printf("0x");
  for(int i=0;i<length;i++){
    printf("%02x", data[i]);
  }
  printf("\n");
}


/**
 * converts a uint array to byte array
 * memory needs to be preallocated
 */
void uint_to_uchar(unsigned int *in, size_t size, unsigned char *out){
  for(unsigned int i=0;i<size;i++){
    out[i*4+0] = (in[i]>>24)&0xFF;
    out[i*4+1] = (in[i]>>16)&0xFF;
    out[i*4+2] = (in[i]>>8)&0xFF;
    out[i*4+3] = (in[i]>>0)&0xFF;
  }
}

/**
 * converts byte array (length divisible by 4) to uint array
 * memory needs to be preallocated
 */
void uchar_to_uint(unsigned char *in, size_t size, unsigned int *out){
  for(unsigned int i=0;i<size/4;i++){
    out[i]= (in[i*4+0] << 24)+
            (in[i*4+1] << 16)+
            (in[i*4+2] << 8)+
            (in[i*4+3] << 0);
  }
}

/**
 * parses a hex string (without 0x prefix, length divisible by 2) into a byte array
 * memory needs to be preallocated
 */
void hex_to_uchar(const char *hex, size_t size, unsigned char *out){
  for(unsigned int i=0;i<(size/2);i++){
      unsigned int tmp;
      sscanf(&hex[i*2], "%02x", &tmp);
      out[i] = (unsigned char) tmp;
  }
}
