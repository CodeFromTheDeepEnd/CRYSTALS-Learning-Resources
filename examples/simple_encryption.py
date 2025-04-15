from CRYSTALS.kyber_params import KyberParams
from CRYSTALS.person import Person
import random

""" This file introduces the simple encryption and decryption scheme.
    We instantiate the Person-class which initializes A and t.
    We then define the message to be encrypted, encrypt, decrypt
    and finally check if we got the same message in return.
    This does not use the KEM-scheme."""
if __name__ == "__main__":

    KYBER512 = KyberParams(k=2, n=256, q=3329, eta1=3, eta2=2, du=10, dv=4)

    alice = Person("Alice", KYBER512)
    bob = Person("Bob", KYBER512)

    # The message to be transferred
    message = [random.randint(0,1) for _ in range(KYBER512.n)]
    u, v = bob.encrypt(message, alice.A, alice.t)
    decoded_message = alice.decrypt(u,v)

    difference = sum(a != b for a, b in zip(message, decoded_message))
    print(f"The total amount of bits that differ is {difference}")


