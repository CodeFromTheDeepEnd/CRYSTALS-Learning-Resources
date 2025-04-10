# CRYSTALS-Learning-Resources
## Introduction
This project provides a Python implementation of the CRYSTALS Kyber algorithm, with plans to include the Dilithium algorithm in the future. The current focus is on implementing the core of Kyber, with other components to follow.

The goal is to offer a clear, educational implementation. For theoretical background and further elaborations, refer to my blog at [ADDRESS]. This repository and the blog are designed to be used together.

If you are looking for code for production purposes, you might want to consult other resources.

## Current Features
- Core implementation of the Kyber algorithm.
- Example usage provided in `person.py`, demonstrating message encoding and decoding.

## Example Usage
```python
KYBER512 = KyberParams(k=2, n=256, q=3329, eta1=3, eta2=2, du=10, dv=4)

alice = Person("Alice", KYBER512)
bob = Person("Bob", KYBER512)
```
The message to be transferred
```python
message = [random.randint(0,1) for _ in range(KYBER512.n)]
u, v = bob.encrypt(message, alice.A, alice.t)

decoded_message = alice.decrypt(u,v)

difference = sum(a != b for a, b in zip(message, decoded_message))
print(f"The total amount of bits that differ is {difference}")
```
## Future work

* Implementing compression techniques.
* Adding Number Theoretic Transform (NTT).
* Integrating Fujisaki-Okamoto transform.
* Completing the implementation of the Dilithium algorithm.

