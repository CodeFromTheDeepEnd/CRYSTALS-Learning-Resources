# CRYSTALS-Learning-Resources
## Introduction
This project provides a Python implementation of the CRYSTALS Kyber algorithm, with plans to include the Dilithium algorithm in the future. The current focus is on implementing the core of Kyber, with other components to follow.

The goal is to offer a clear, educational implementation in Python. For theoretical background and further elaborations, refer to my [blog](https://jani.isohanni.fi/crystals-the-gently-introduction/). This repository and the blog are designed to be used together.

If you are looking for code for production purposes, you want to consult other resources.

## Current Features
- Core implementation of the Kyber algorithm.
- Compression of A, u and v.
- Fujisaki-Okamoto transform (KEM-scheme)
- Example usage provided in `KEM-scheme.py`, demonstrating message encoding and decoding.
## Example Usage
```python
    KYBER512 = KyberParams(k=2, n=256, q=3329, eta1=3, eta2=2, du=10, dv=4)

    alice = Person("Alice", KYBER512)
    bob = Person("Bob", KYBER512)

    # The message to be transferred
    u, v = bob.encrypt_kem(alice.A, alice.t)
    k_bar = alice.decrypt_kem(u,v)
```
## Future work

* Adding Number Theoretic Transform (NTT).
* Implementation of the Dilithium algorithm.

