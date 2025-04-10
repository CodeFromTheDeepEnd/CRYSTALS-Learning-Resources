from CRYSTALS import PolyMatrix, KyberParams, ZqPolynomial
import random

class Person:
    def __init__(self, name, kyber_params):
        """ Implements a person to better visualize the message exchange between participants.
            Will initialize A and t upon instantiation"""
        self.name = name
        self.A = None
        self.s = None
        self.t = None
        self.e = None
        self.r = None
        self.e1 = None
        self.e2 = None
        self.kyber_params = kyber_params
        self.generate_keys()

    def generate_keys(self):
        """ Generates A, s, e and t. A and t together are the public key """
        print(f"{self.name} is generating keys")
        self.A = PolyMatrix(self.kyber_params.k, self.kyber_params.k, self.kyber_params.q, self.kyber_params.n)
        self.A.random_uniform()

        self.s = PolyMatrix(self.kyber_params.k, 1, self.kyber_params.q, self.kyber_params.n)
        self.s = self.s.random_binomial(self.kyber_params.eta1)

        self.e = PolyMatrix(self.kyber_params.k, 1, self.kyber_params.q, self.kyber_params.n)
        self.e.random_binomial(self.kyber_params.eta2)

        self.t = self.A @ self.s + self.e

        return self

    def encrypt(self, message, others_a, others_t):
        """ Encrypt the message. Message is a list of zeroes and ones of length n."""
        print(f"{self.name} is encrypting a message")
        self.r = PolyMatrix(self.kyber_params.k, 1, self.kyber_params.q, self.kyber_params.n)
        self.r.random_binomial(self.kyber_params.eta1)

        self.e1 = PolyMatrix(self.kyber_params.k, 1, self.kyber_params.q, self.kyber_params.n)
        self.e1.random_binomial(self.kyber_params.eta2)

        self.e2 = PolyMatrix(1, 1, self.kyber_params.q, self.kyber_params.n)
        self.e2.random_binomial(self.kyber_params.eta2)

        m_new = [int((self.kyber_params.q / 2) * x + 0.5) for x in message]
        m_matrix = PolyMatrix(1, 1, self.kyber_params.q, self.kyber_params.n)
        m_matrix[(0, 0)] = ZqPolynomial(self.kyber_params.q, m_new)
        u = others_a.T @ self.r + self.e1
        v = others_t.T @ self.r + self.e2 + m_matrix
        return (u,v)

    def decrypt(self, u,v):
        """ Decrypt the message. The message is a list of zeroes and ones."""
        if not isinstance(u, PolyMatrix) or not isinstance(v, PolyMatrix):
            raise TypeError("Invalid cipher format")

        print(f"{self.name} is decrypting a message")
        decoded = v - self.s.T @ u
        decoded = decoded.round()
        decodedmessage = decoded.extract_message()
        return decodedmessage

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

