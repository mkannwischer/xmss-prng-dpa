## Using the Code
 - [full_leak_prng.c](full_leak_prng.c) Entry point for full power trace simulation, i.e., the HW of all operation results during PRNG is leaked to a file
 - [partial_leak_prng.c](partial_leak_prng.c) Entry point for partial power trace simulation, i.e., the HW of the relevant  operation results during PRNG is leaked to a file. This was mainly used for developing and debugging the DPA, not in the experiments.
- [leak.c](leak.c) Leakage lib as described in the thesis
- [ownsha256.c](ownsha256.c) our own implementation of SHA256. Cross-checked against open-ssl
- [leaky_sha256.c](leaky_sha256.c) instrumented version of [ownsha256.c](ownsha256.c), i.e., added calls to [leak.c](leak.c)
- [util.c](util.c) helper functions that implement logging and byte/int conversion
