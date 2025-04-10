import random

class Zq:
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
        return self.value

    @classmethod
    def random_uniform(cls, q):
        # For public matrix A
        return cls(q, random.randrange(q))

    @classmethod
    def random_binomial(cls, q, eta):
        # For secret/error terms
        bits1 = [random.randint(0, 1) for _ in range(eta)]
        bits2 = [random.randint(0, 1) for _ in range(eta)]
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



