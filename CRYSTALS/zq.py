import random

class Zq():
    """ This class represents the elements of Z_q.
        It is used in ZqPolynomial in coefficients."""
    def __init__(self, q, value):
        if not isinstance(q, int):
            raise TypeError("Q can be only integer")

        if q < 2:
            raise ValueError("q must be > 1")

        if not isinstance(value, int) and not isinstance(value,Zq):
            raise TypeError("The value must be either int or Zq")

        if isinstance(value,int):
            # Python modulo operation is one of the few correctly implemented
            self.value = value % q
        else:
            self.value = value.get_value() % q
        self.q = q

    def get_value(self):
        """ Returns the value as int."""
        return self.value

    def compress(self, d):
        """ Compress the value."""
        self.value = round((2**d / self.q) * self.value) % 2**d
        return self

    def decompress(self, d):
        """ Decompress the value."""
        self.value = round((self.q / 2**d) * self.value) % self.q
        return self

    @classmethod
    def random_uniform(cls, q):
        """ Samples a value from random.randrange(q) and returns Zq-object.
            This is not the best way, but goes for our purpose."""
        # For public matrix A
        return cls(q, random.randrange(q))

    @classmethod
    def random_binomial(cls, q, eta):
        """ Samples a value from CBD and returns Zq-object.
        """
        if eta < 1:
            raise ValueError("eta smaller than 1")
        if q < 2:
            raise ValueError("q smaller than 2")

        # For secret/error terms
        bits1 = [random.randint(0, 1) for _ in range(eta)]
        bits2 = [random.randint(0, 1) for _ in range(eta)]
        value = sum(bits1) - sum(bits2)
        result = cls(q,value)
        result = result.to_symmetric()
        return result

    @classmethod
    def random_binomial_xof(cls, q, eta, bytes_to_use):
        """ Return Zq instance with value sampled from CBD. bytes_to_use is
            expected to have the random bits that is used in the sampling process.
        """
        # For secret/error terms
        bytes_needed = (eta // (8) ) + 1
        bits1 = []
        bits2 = []
        int_value = int.from_bytes(bytes_to_use[0:bytes_needed], byteorder='big')
        for i in range(eta):
            bits1.append( (int_value >> i) & 1)

        int_value = int.from_bytes(bytes_to_use[bytes_needed:], byteorder='big')
        for i in range(eta):
            bits2.append( (int_value >> i+1) & 1)

        value = sum(bits1) - sum(bits2)
        result = cls(q,value)
        result = result.to_symmetric()
        return result

    def to_symmetric(self):
        """Convert value to symmetric representation in [-(q-1)/2, q/2]"""
        if self.q % 2 == 0:  # even q
            if self.value >= self.q // 2:
                self.value = self.value - self.q
        else:  # odd q
            if self.value > self.q // 2:
                self.value = self.value - self.q
        return self

    def round(self):
        """ Round to 0 or 1. Presumably we are already symmetric."""
        # Center around q/2
        centered = abs(self.value - self.q / 2)
        # If closer to q/2 than to 0
        if centered < self.q / 4:
            self.value = 1
        else:
            self.value = 0
        return self

#    def compress(self,eta):


    def __add__(self, other):
        if not isinstance(other, Zq):
            return NotImplemented
        return Zq(self.q, self.get_value()+other.get_value())

    def __sub__(self, other):
        if not isinstance(other, Zq):
            return NotImplemented
        return Zq(self.q, self.get_value()-other.get_value())

    def __mul__(self, other):
        if not isinstance(other, Zq):
            return NotImplemented
        return Zq(self.q, self.get_value()*other.get_value())

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)



