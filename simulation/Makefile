CC := gcc
LD := gcc
CFLAGS_COMMON := -std=c99 -Wall -g -gdwarf-2 -O3
MAIN := simulate_partial
MAIN2 := simulate

CFLAGS := $(CFLAGS_COMMON)
LDFLAGS :=

OBJ_PARTIAL :=  util.o ownsha256.o leak.o partial_leak_prng.o
OBJ_FULL    := util.o leaky_sha256.o leak.o full_leak_prng.o

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

all: clean $(MAIN) $(MAIN2)

partial: clean $(MAIN)
full: clean $(MAIN2)


$(MAIN): $(OBJ_PARTIAL)
	$(LD) $(OBJ_PARTIAL) -o $(MAIN) $(LDFLAGS)

$(MAIN2): $(OBJ_FULL)
	$(LD) $(OBJ_FULL) -o $(MAIN2) $(LDFLAGS)


.PHONY: clean
clean:
	rm -rf $(OBJ_PARTIAL) $(MAIN)
	rm -rf $(OBJ_FULL) $(MAIN2)
