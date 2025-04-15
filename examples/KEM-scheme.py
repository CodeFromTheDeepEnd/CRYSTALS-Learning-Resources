from CRYSTALS.kyber_params import KyberParams
from CRYSTALS.person import Person

""" This file introduces the full KEM-scheme implementation.
    The message is created and encrypted byb Bob. Alice
    decrypts the message and checks, if it has been changed.
    If Alice notices that the message has probably been changed, she
    returns nonsense to Bob."""
if __name__ == "__main__":

    KYBER512 = KyberParams(k=2, n=256, q=3329, eta1=3, eta2=2, du=10, dv=4)

    alice = Person("Alice", KYBER512)
    bob = Person("Bob", KYBER512)

    # The message to be transferred
    u, v = bob.encrypt_kem(alice.A, alice.t)
    k_bar = alice.decrypt_kem(u,v)



