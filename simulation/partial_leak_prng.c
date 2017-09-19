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

/**
 * Entry point for partial power trace simulation, i.e., the HW of the relevant
 * operation results during PRNG is leaked to a file,
 * This was mainly used for developing and debugging the DPA
 * In contrast: full traces (see full_leak_prng.c) contain all operations
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "ownsha256.h"
#include "util.h"
#include "leak.h"

void create_all_traces(unsigned char seed[32], unsigned int num_traces, int silent);
void create_trace(const unsigned int iv[8], unsigned int trace_idx);

int main(int argc, char** argv)
{
  if(argc < 2){
      printf("WRONG NUMBER OF ARGUMENTS!");
      exit(-1);
  }

  unsigned int num_traces;
  sscanf(argv[1], "%u", &num_traces);

  int silent=0;
  if(argc == 3){
    silent = 1;
  }

  // we use a 256 bit seed
  unsigned char seed[32];

  srand (time(NULL));

  for(int j=0;j<32;j++){
    seed[j] = rand();
  }


  if(!silent){
    printf("\n\n##### SIMULATING POWER TRACE #####\n");
    printf("seed="); print_hex(seed, 32);
    printf("Creating %u traces\n", num_traces);
  }
  create_all_traces(seed, num_traces, silent);
}


void create_all_traces(unsigned char seed[32], unsigned int num_traces, int silent){
  // create the first block
  unsigned char block[64];
  memset(block, 0, 64);
  memcpy(block, seed, 32);

  // now we obtain the iv after the first compression function all

  // set the iv
  unsigned int iv[8];
  memcpy(iv, SHA256_IV, 32);

  // call compression function
  ownsha256_compression_function(iv, block);


  unsigned int a,b,c;
  unsigned int e,f,g,h;
  a = iv[0]; b = iv[1]; c = iv[2];
  e = iv[4]; f = iv[5]; g = iv[6]; h = iv[7];


  unsigned int delta = h + Sigma_1(e)+ Ch(e,f,g)+ 0x428a2f98UL;
  unsigned int T2 = Sigma_0(a)+Maj(a,b,c);

  if(!silent){
    printf("iv[0]="); print_hex_uint(iv, 8);
    printf("iv[1]="); print_hex_uint(iv, 8);
    printf("a_0=0x%08x\n", iv[0]);
    printf("b_0=0x%08x\n", iv[1]);
    printf("c_0=0x%08x\n", iv[2]);
    printf("d_0=0x%08x\n", iv[3]);
    printf("e_0=0x%08x\n", iv[4]);
    printf("f_0=0x%08x\n", iv[5]);
    printf("g_0=0x%08x\n", iv[6]);
    printf("h_0=0x%08x\n", iv[7]);
    printf("delta=0x%08x\n", delta);
    printf("T2=0x%08x\n", T2);
  }

  char file_name[250];
  unsigned int seed_uint[8];
  uchar_to_uint(seed, 32, seed_uint);
  sprintf(file_name, "leakage_0x%08x%08x%08x%08x%08x%08x%08x%08x_%u.bin",
    iv[0], iv[1], iv[2], iv[3], iv[4], iv[5], iv[6], iv[7],
    num_traces);
  if(!silent) printf("%s\n", file_name);

  leak_start(HW, file_name);
  for(unsigned int i=0;i<num_traces; i++){
    if(!silent && i%100 == 0) printf("progress: %d/%d (%.2f %%)\n", i, num_traces, (i/(float) num_traces)*100.0);
    create_trace(iv, i);
  }
  leak_end();


}

void create_trace(const unsigned int iv[8], unsigned int trace_idx){
  // first we hash the idx
  // conversion to byte array
  // we do not care for endian-ness right now
  unsigned char idx_char[4];
  uint_to_uchar(&trace_idx, 1, idx_char);
  unsigned char idx_hash[32];

  //printf("idx_char[%d]=", trace_idx); print_hex(idx_char, 4);
  ownsha256(idx_char, 4, idx_hash);

  unsigned int idx_hash_int_0;
  uchar_to_uint(idx_hash, 4, &idx_hash_int_0);

  unsigned int idx_hash_int_1;
  uchar_to_uint(&idx_hash[4], 4, &idx_hash_int_1);

  //printf("idx_hash[%d]=", trace_idx); print_hex(idx_hash, 32);

  // see the compression function for reference.
  // we do only simulate the required calculations for performance reasons

  unsigned int a,b,c,d,e,f,g,h;
  a = iv[0]; b = iv[1]; c = iv[2]; d = iv[3];
  e = iv[4]; f = iv[5]; g = iv[6]; h = iv[7];

  //unsigned int T1 = h + Sigma_1(e)+ Ch(e,f,g)+ SHA256_K[0] + idx_hash_int;
  unsigned int T1 = leak_uint_plus(h + Sigma_1(e)+ Ch(e,f,g)+ SHA256_K[0], idx_hash_int_0);

  unsigned int T2 = Sigma_0(a)+Maj(a,b,c);




  // ITERATION 1
  //printf("W0=0x%08x\n", idx_hash_int_0);
  //printf("W1=0x%08x\n", idx_hash_int_1);
  //printf("delta=0x%08x\n", h + Sigma_1(e)+ Ch(e,f,g)+ SHA256_K[0]);
  //printf("T1=w+delta=0x%08x\n", T1);
  //printf("T2=0x%08x\n", T2);


  //int T2 = Sigma_0(a)+Maj(a,b,c);

  h=g; g=f; f=e;
  // e = d + T1;
  e = leak_uint_plus(d, T1);
  //printf("e_1=d_0+T1=0x%08x\n", e);


  d=c; c=b; b=a;
  //a = T1+T2;
  a = leak_uint_plus(T1, T2);
  //printf("a_1=T1+T2=0x%08x\n", a);


  // ITERATION 2
  leak_uint_and(~e,g);
  leak_uint_and(e,f);
  leak_uint_and(a,b);
  leak_uint_and(a,c);

  //printf("sigma1(e1)=0x%08x\n",  Sigma_1(e));
  //printf("Ch(e_1,f_1,g_1)=0x%08x\n", Ch(e,f,g));


  //printf("known_sum=0x%08x\n",  );

  //printf("T1(1)=0x%08x\n", h + Sigma_1(e)+ Ch(e,f,g)+ SHA256_K[1]+idx_hash_int_1);


  // leaking t1
  T1 = leak_uint_plus(h, Sigma_1(e));
  T1 = T1 +Ch(e,f,g)+ SHA256_K[1]+idx_hash_int_1;

  leak_uint_plus(d, T1);






}
