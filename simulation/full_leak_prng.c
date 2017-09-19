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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "leaky_sha256.h"
#include "util.h"
#include "leak.h"

/**
 * Entry point for full power trace simulation, i.e., the HW of all
 * operation results during PRNG is leaked to a file,
 * In contrst: partial traces (see partial_leak_prng.c) only leak the relevant
 * operations
 */




void create_all_traces(unsigned char seed[32], unsigned int num_traces, enum leakage_type l_type);

void usage(){
  printf("Usage: simulate n t [k]\n");
  printf("\tn : number of traces, indices: 0 <= i < n \n");
  printf("\tt : leakage type (HW, HW_BYTE)\n");
  printf("\tk : fixed 256-bit seed as hex string without 0x, optional\n");
  printf("If no seed is given, a random one will be generated.\n");
  exit(-1);
}
int main(int argc, char** argv){
  if(argc < 3 || argc > 4){
      printf("WRONG NUMBER OF ARGUMENTS!");
      usage();
  }

  unsigned int num_traces;
  sscanf(argv[1], "%u", &num_traces);

  enum leakage_type l_type;
  if(strcmp(argv[2], "HW") == 0){
    l_type = HW;
  } else if (strcmp(argv[2], "HW_BYTE") == 0){
    l_type = HW_BYTE;
  } else {
    printf("INVALID LEAKAGE TYPE!");
    usage();
  }

  // we use a 256 bit seed
  unsigned char seed[32];


  if(argc == 4){
    // seed given
    if(strlen(argv[3]) != (256/4)){
      printf("INVALID SEED LENGTH - 256 BIT REQUIRED!");
      usage();
    } else {
      hex_to_uchar(argv[3], 64, seed);
    }
  } else {
    // pick a random seed
    srand (time(NULL));
    for(int j=0;j<32;j++){
      seed[j] = rand();
    }
  }

  printf("\n\n##### SIMULATING POWER TRACE #####\n");
  printf("seed="); print_hex(seed, 32);
  printf("leakage_type=%d\n", l_type);
  printf("Creating %u traces\n", num_traces);
  create_all_traces(seed, num_traces, l_type);
}


void create_all_traces(unsigned char seed[32], unsigned int num_traces, enum leakage_type l_type){

  unsigned char msg[64+32];
  memset(msg, 0, 64+32);
  memcpy(&msg[32], seed, 32);
  msg[31]= 3;



  //  this part is just for validating our result later

  // set the iv
  unsigned int iv[8];
  memcpy(iv, SHA256_IV, 32);
  printf("iv[0]="); print_hex_uint(iv, 8);
  // call compression function
  ownsha256_compression_function(iv, msg);
  printf("iv[1]="); print_hex_uint(iv, 8);
  printf("a_0=0x%08x\n", iv[0]);
  printf("b_0=0x%08x\n", iv[1]);
  printf("c_0=0x%08x\n", iv[2]);
  printf("d_0=0x%08x\n", iv[3]);
  printf("e_0=0x%08x\n", iv[4]);
  printf("f_0=0x%08x\n", iv[5]);
  printf("g_0=0x%08x\n", iv[6]);
  printf("h_0=0x%08x\n", iv[7]);

  unsigned int a,b,c;
  unsigned int e,f,g,h;
  a = iv[0]; b = iv[1]; c = iv[2];
  e = iv[4]; f = iv[5]; g = iv[6]; h = iv[7];


  unsigned int delta = h + Sigma_1(e)+ Ch(e,f,g)+ 0x428a2f98UL;
  printf("delta=0x%08x\n", delta);
  unsigned int T2 = Sigma_0(a)+Maj(a,b,c);
  printf("T2=0x%08x\n", T2);

  char file_name[250];
  unsigned int seed_uint[8];
  uchar_to_uint(seed, 32, seed_uint);

  FILE *secret_data_file = fopen("secret_data.txt", "w");
  fprintf(secret_data_file, "seed=0x%08x%08x%08x%08x%08x%08x%08x%08x\n", seed_uint[0],seed_uint[1],seed_uint[2],seed_uint[3],seed_uint[4],seed_uint[5],seed_uint[6],seed_uint[7]);
  fprintf(secret_data_file, "iv_1=0x%08x%08x%08x%08x%08x%08x%08x%08x\n", iv[0], iv[1], iv[2], iv[3], iv[4], iv[5], iv[6], iv[7]);
  fprintf(secret_data_file, "delta=0x%08x\nT2=0x%08x\n", delta, T2);
  fclose(secret_data_file);

  sprintf(file_name, "leakage_%u.bin", num_traces);
  printf("%s\n", file_name);

  leak_start(l_type, file_name);
  // here begins the actual experiment
  for(unsigned int trace_idx=0;trace_idx<num_traces;trace_idx++){
    // hash the idx
    unsigned char idx_char[4];
    uint_to_uchar(&trace_idx, 1, idx_char);
    leak_pause();
    ownsha256(idx_char, 4, &msg[64]);
    leak_resume();
    // get the key
    unsigned char pseudo_random_number[32];
    ownsha256(msg, sizeof(msg), pseudo_random_number);
  }
  leak_end();
}
