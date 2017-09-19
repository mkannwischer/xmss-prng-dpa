## Using the Code
- [dpa.py](dpa.py): Main DPA library which is independent of the actual attack and SHA256
- [helper.py](helper.py) helper function that are used multiple times, but independent of DPA and SHA256
- [sha256_helper.py](sha256_helper.py) supportive functions specific to SHA256
- [analyze_8bit.py](analyze_8bit.py) implementation of the full attack in the 8-bit HW leakage model. See [../README.MD](../README.MD) for usage
- [analyze_32bit_addition.py](analyze_32bit_addition.py) implementation of the DPA1 in the 32-bit HW leakage model. See [../README.MD](../README.MD) for usage
- [analyze_32bit_and.py](analyze_32bit_and.py) implementation DPA5 in the 32-bit HW leakage model. See [../README.MD](../README.MD) for usage
