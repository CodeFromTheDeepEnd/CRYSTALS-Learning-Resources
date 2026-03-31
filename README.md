# CRYSTALS-Learning-Resources

**Educational** Python implementation of post-quantum cryptographic algorithms from the CRYSTALS suite.

## About

This repository implements the CRYSTALS-Kyber key encapsulation mechanism (KEM) in Python for learning purposes. The code prioritizes clarity over performance.

**For detailed mathematical background**, see the accompanying blog post-series: [CRYSTALS: The Gentle Introduction](https://jani.isohanni.fi/crystals-the-gently-introduction/)

The blog covers:
- Modular algebra and lattice problems
- Polynomial ring theory
- Step-by-step algorithm explanation

**Not for production use**

## Features

- Core Kyber algorithm (near-FIPS 203 compliant)
- Compression of A, u, and v
- Fujisaki-Okamoto transform (KEM scheme)
- Working examples with key exchange

## Quick Start

```python
KYBER512 = KyberParams(k=2, n=256, q=3329, eta1=3, eta2=2, du=10, dv=4)

alice = Person("Alice", KYBER512)
bob = Person("Bob", KYBER512)

# Key encapsulation
u, v = bob.encrypt_kem(alice.A, alice.t)
k_bar = alice.decrypt_kem(u, v)
```

Run examples
```bash
python -m examples.simple_encryption
python -m examples.KEM-scheme
```

