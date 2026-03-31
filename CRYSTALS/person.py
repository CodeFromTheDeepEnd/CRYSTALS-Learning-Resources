from CRYSTALS import PolyMatrix, ZqPolynomial
import hashlib
import secrets
import random
import copy
import logging
import inspect

class Person():
    def __init__(self, name, kyber_params):
        """ Implements a person to better visualize the message exchange between
            participants. Will initialize A, t, s, e and z upon instantiation"""
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(message)s'
        )
        self.name = name
        self.A = None
        self.A_matrix = None
        self.s = None
        self.t = None
        self.e = None
        self.r = None
        self.e1 = None
        self.e2 = None
        self.du = None
        self.dv = None
        self.z = None
        self.kyber_params = kyber_params
        self.generate_keys()

    def debug(self, message):
        method_name = inspect.currentframe().f_back.f_code.co_name
        class_name = self.__class__.__name__
        logging.debug(f"{class_name}.{method_name}: {message}")

    def generate_keys(self):
        """ Generates A, t, s, e and z. A and t together are the public key """
        self.debug(f"{self.name} is generating keys")

        # Create 256 random bits from which the actual A parameters are constructed.
        self.A = secrets.token_bytes(32)
        self.A_matrix = PolyMatrix(self.kyber_params.k, self.kyber_params.k, self.kyber_params.q, self.kyber_params.n)
        self.A_matrix = self.A_matrix.fill_xof(self.A)

        # s and e coefficients are sampled from CBD (centered binomial distribution)
        self.s = PolyMatrix(self.kyber_params.k, 1, self.kyber_params.q, self.kyber_params.n)
        self.s = self.s.random_binomial(self.kyber_params.eta1)

        self.e = PolyMatrix(self.kyber_params.k, 1, self.kyber_params.q, self.kyber_params.n)
        self.e.random_binomial(self.kyber_params.eta2)

        # Compute t. (A,t) is the public key.
        self.t = self.A_matrix @ self.s + self.e

        self.z = [random.randint(0, 1) for _ in range(self.kyber_params.n)]

        return self

    @staticmethod
    def concatenate_matrices(first, second):
        """ Concatenates the coefficients of the matrices into a string."""
        if not isinstance(first, PolyMatrix) or not isinstance(second, PolyMatrix):
            raise TypeError("Person.concatenate_matrices: Expecting instances of PolyMatrix.")

        concatenated = []
        concatenated.extend(first.extract_coefficients_int())
        concatenated.extend(second.extract_coefficients_int())
        concatenated_string = ''.join(map(str, concatenated))

        return concatenated_string

    def encrypt_kem(self, others_a, others_t):
        """ Create the symmetric key and encrypt it with A and t.
            This method uses FO-transform and implements the full KEM-scheme.
            Use method encrypt if you want to encrypt a bit string of your own choice."""
        self.debug(f"{self.name} is encrypting a message")
        others_a_matrix = PolyMatrix(self.kyber_params.k, self.kyber_params.k, self.kyber_params.q, self.kyber_params.n)
        # Now others_a is the seed that we use to construct matrix A
        others_a_matrix = others_a_matrix.fill_xof(others_a)

        # Sample m
        m = [random.randint(0, 1) for _ in range(self.kyber_params.n)]

        # Let us construct a string that consists of all coefficients
        # Notice that two different coefficient lists may result to
        # same concatenated string.
        at_concatenated_string = self.concatenate_matrices(others_a_matrix, others_t)

        # This is H function
        sha3_256 = hashlib.sha3_256()

        # Encode the concatenated string to a byte string
        sha3_256.update(at_concatenated_string.encode('utf-8'))
        h = sha3_256.hexdigest()

        m_bytes = bytes(m)
        h_bytes = bytes.fromhex(h)
        mh_concatenated = m_bytes + h_bytes

        # This is G function
        sha3_512 = hashlib.sha3_512()
        sha3_512.update(mh_concatenated)
        random_value = sha3_512.hexdigest()

        # Now K is the actual symmetric key.
        K = random_value[0:64]
        R = random_value[64:]

        shake = hashlib.shake_128()
        shake.update(bytes.fromhex(R))

        # We need to extract the amount of bytes needed upfront and pass the
        # value to subsequent method calls. It seems shake_128 does not have
        # a way to extract bytes as we go.
        bytes_for_eta1 = 1 + (self.kyber_params.eta1//8)
        bytes_for_eta2 = 1 + (self.kyber_params.eta2//8)
        bytes_r = self.kyber_params.k * self.kyber_params.n * bytes_for_eta1
        bytes_e1 = self.kyber_params.k * self.kyber_params.n * bytes_for_eta2
        bytes_e2 = self.kyber_params.n * bytes_for_eta2
        bytes_sampled = shake.digest(2*(bytes_r + bytes_e1 + bytes_e2))

        self.r = PolyMatrix(self.kyber_params.k, 1, self.kyber_params.q, self.kyber_params.n)
        self.r.random_binomial_xof(self.kyber_params.eta1, bytes_sampled[0:(2*bytes_r)])

        self.e1 = PolyMatrix(self.kyber_params.k, 1, self.kyber_params.q, self.kyber_params.n)
        self.e1.random_binomial_xof(self.kyber_params.eta2, bytes_sampled[2*bytes_r:(2*bytes_r+2*bytes_e1)])

        self.e2 = PolyMatrix(1, 1, self.kyber_params.q, self.kyber_params.n)
        self.e2.random_binomial_xof(self.kyber_params.eta2, bytes_sampled[(2*bytes_r+2*bytes_e1):])

        m_new = [int((self.kyber_params.q / 2) * x + 0.5) for x in m]
        #m is polynomial, but we pack it to a matrix for smooth arithmetics
        m_matrix = PolyMatrix(1, 1, self.kyber_params.q, self.kyber_params.n)
        m_matrix[(0, 0)] = ZqPolynomial(self.kyber_params.q, m_new)


        v = others_t.T @ self.r + self.e2 + m_matrix
        u = others_a_matrix.T @ self.r + self.e1

        u = u.compress(self.kyber_params.du)
        v = v.compress(self.kyber_params.dv)

        return (u,v)

    def decrypt_kem(self, u, v):
        """ Decrypt the symmetric key. This method implements FO-transform
            and provides the KEM-schema. If you want to decrypt a message
            encrypted with the method encrypt, use the naive implementation
            decrypt() instead."""
        if not isinstance(u, PolyMatrix) or not isinstance(v, PolyMatrix):
            raise TypeError("Invalid cipher format")

        self.debug(f"{self.name} is decrypting a message")
        u_dec = copy.deepcopy(u)
        v_dec = copy.deepcopy(v)
        u_dec = u_dec.decompress(self.kyber_params.du)
        v_dec = v_dec.decompress(self.kyber_params.dv)

        decoded = v_dec - self.s.T @ u_dec
        decoded = decoded.round()
        decoded_message = decoded.extract_message()

        at_concatenated_string = self.concatenate_matrices(self.A_matrix, self.t)
        # This is H function
        sha3_256 = hashlib.sha3_256()

        # Encode the concatenated string to a byte string
        sha3_256.update(at_concatenated_string.encode('utf-8'))
        h = sha3_256.hexdigest()

        m_bytes = bytes(decoded_message)
        h_bytes = bytes.fromhex(h)
        mh_concatenated = m_bytes + h_bytes

        # This is G function
        sha3_512 = hashlib.sha3_512()
        sha3_512.update(mh_concatenated)
        random_value = sha3_512.hexdigest()

        # If the decrypt process succeeds, K is the symmetric key Alice will use.
        K = random_value[0:64]
        R = random_value[64:]

        shake = hashlib.shake_128()
        shake.update(bytes.fromhex(R))

        # We need to extract the amount of bytes needed upfront and pass the
        # value to subsequent method calls. It seems shake_128 does not have
        # a way to extract bytes as we go.
        bytes_for_eta1 = 1 + (self.kyber_params.eta1 // 8)
        bytes_for_eta2 = 1 + (self.kyber_params.eta2 // 8)

        bytes_r = self.kyber_params.k * self.kyber_params.n * bytes_for_eta1
        bytes_e1 = self.kyber_params.k * self.kyber_params.n * bytes_for_eta2
        bytes_e2 = self.kyber_params.n * bytes_for_eta2
        bytes_sampled = shake.digest(2 * (bytes_r + bytes_e1 + bytes_e2))

        # Sample the vectors
        self.r = PolyMatrix(self.kyber_params.k, 1, self.kyber_params.q, self.kyber_params.n)
        self.r.random_binomial_xof(self.kyber_params.eta1, bytes_sampled[0:(2 * bytes_r)])

        self.e1 = PolyMatrix(self.kyber_params.k, 1, self.kyber_params.q, self.kyber_params.n)
        self.e1.random_binomial_xof(self.kyber_params.eta2, bytes_sampled[2 * bytes_r:(2 * bytes_r + 2 * bytes_e1)])

        self.e2 = PolyMatrix(1, 1, self.kyber_params.q, self.kyber_params.n)
        self.e2.random_binomial_xof(self.kyber_params.eta2, bytes_sampled[(2 * bytes_r + 2 * bytes_e1):])

        m_new = [int((self.kyber_params.q / 2) * x + 0.5) for x in decoded_message]
        #m is polynomial, but we pack it to a matrix for smooth arithmetics
        m_matrix = PolyMatrix(1, 1, self.kyber_params.q, self.kyber_params.n)
        m_matrix[(0, 0)] = ZqPolynomial(self.kyber_params.q, m_new)

        u_prime = self.A_matrix.T @ self.r + self.e1
        v_prime = self.t.T @ self.r + self.e2 + m_matrix

        u_prime = u_prime.compress(self.kyber_params.du)
        v_prime = v_prime.compress(self.kyber_params.dv)

        # Lets check if the results equal.
        if u_prime.is_equal_to(u) and v_prime.is_equal_to(v):
            # All ok, continue to use K as the symmetric key.
            self.debug(f"Decrypt was successful")
        else:
            self.debug("Decryption failed")
            self.debug(f"u_prime={u_prime}")
            self.debug(f"u={u}")
            self.debug(f"v_prime={v_prime}")
            self.debug(f"v={v}")
            # Lets form the invalid output for the potential adversary
            j = hashlib.shake_256()
            concatenated = self.z + u + v
            for x in concatenated:
                j.update(x.to_bytes(4, 'big', signed=True))

            k_bar = j.digest(32)
            return k_bar

    def encrypt(self, message, others_a, others_t):
        """ Encrypt the message. Message is a list of zeroes and ones of length n.
            This method does not implement FO-transform, and the message must
            be provided separately. Use encrypt_symkey() for the KEM-implementation."""
        self.debug(f"{self.name} is encrypting a message")

        if not isinstance(others_t, PolyMatrix):
            raise TypeError("Expecting t to be PolyMatrix-type")

        if len(message) != self.kyber_params.n:
            raise ValueError(f"Unexpected message length {len(message)}.")

        A_matrix = PolyMatrix(self.kyber_params.k, self.kyber_params.k, self.kyber_params.q, self.kyber_params.n)
        # Now others_a is the seed that we use to construct matrix A.
        A_matrix = A_matrix.fill_xof(others_a)

        self.r = PolyMatrix(self.kyber_params.k, 1, self.kyber_params.q, self.kyber_params.n)
        self.r.random_binomial(self.kyber_params.eta1)

        self.e1 = PolyMatrix(self.kyber_params.k, 1, self.kyber_params.q, self.kyber_params.n)
        self.e1.random_binomial(self.kyber_params.eta2)

        self.e2 = PolyMatrix(1, 1, self.kyber_params.q, self.kyber_params.n)
        self.e2.random_binomial(self.kyber_params.eta2)

        # Pack the m into polynomial
        m_new = [int((self.kyber_params.q / 2) * x + 0.5) for x in message]

        #m is polynomial, but we pack it to a matrix for smooth arithmetics
        m_matrix = PolyMatrix(1, 1, self.kyber_params.q, self.kyber_params.n)
        m_matrix[(0, 0)] = ZqPolynomial(self.kyber_params.q, m_new)
        u = A_matrix.T @ self.r + self.e1
        v = others_t.T @ self.r + self.e2 + m_matrix
        u = u.compress(self.kyber_params.du)
        v = v.compress(self.kyber_params.dv)

        return u, v

    def decrypt(self, u,v):
        """ Decrypt the message. The message is a list of zeroes and ones.
            This method does not implement FO-transform and the message
            is defined by hand. Use decrypt_symkey() for a version with FO
            implemented."""
        if not isinstance(u, PolyMatrix) or not isinstance(v, PolyMatrix):
            raise TypeError("Invalid cipher format, expecting type PolyMatrix")

        self.debug(f"{self.name} is decrypting a message")
        u = u.decompress(self.kyber_params.du)
        v = v.decompress(self.kyber_params.dv)
        decoded = v - self.s.T @ u
        decoded = decoded.round()
        decoded_message = decoded.extract_message()
        return decoded_message

