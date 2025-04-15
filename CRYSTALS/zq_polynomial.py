from CRYSTALS.zq import Zq

class ZqPolynomial:
    """ Polynomial in the polynomial ring Z_q[x]/(x^n+1)
        coefficients is a list of length n. The lowest degree elements come first.
        For example polynomial 2x+4x^2 in Z_5[x]/(x^5+1) would be instantiated
        as ZqPolynomial(5,[0,2,4,0,0]). If your coefficients are larger than or
        equal to q, the corresponding modulo value is used. q must be > 1."""
    def __init__(self, q, coefficients):
        self.q = q
        if not isinstance(q, int):
            raise TypeError("q can only be an integer")

        if not isinstance(coefficients, list):
            raise TypeError("Coefficients must be a list of integers")

        for i in coefficients:
            if not isinstance(i,int) and not isinstance(i,Zq):
                raise TypeError("All coefficients must be integers or Zqs.")

        self.coefficients = coefficients
        for i in range(len(coefficients)):
            self.coefficients[i] = Zq(self.q, self.coefficients[i])
        # n from (x^n+1)
        self.n = len(coefficients)

    def extract_coefficients_int(self):
        """" Extracts the coefficients of the polynomial and returns
            them as a list of integers."""
        coefficients_int = []
        for i in range(self.n):
            coefficients_int.append(self.coefficients[i].value)
        return coefficients_int

    @classmethod
    def random_uniform(cls, n, q):
        """Creates and returns a new polynomial whose coefficients are drawn from uniform distribution"""
        # Creates and returns NEW polynomial
        coeffs = [Zq.random_uniform(q) for _ in range(n)]
        return cls(q, coeffs)

    def is_equal_to(self, other):
        """ Compares two polynomials for equality. Will check n, q and coefficients."""
        if not isinstance(other, ZqPolynomial):
            print(f"ZqPolynomial.is_equal_to: Other is not ZqPolynomial")
            return False

        if self.n != other.n:
            print(f"ZqPolynomial.is_equal_to: Different n values")
            return False

        if self.q != other.q:
            print(f"ZqPolynomial.is_equal_to: Different q values")
            return False

        for i in range(self.n):
            if self.coefficients[i].value != other.coefficients[i].value:
                print(f"ZqPolynomial.is_equal_to: Different coefficients at ({i})")
                return False

        return True

    @classmethod
    def random_binomial_xof(cls, n, q, eta, bytes_to_use):
        """Creates and returns a new polynomial whose coefficients are drawn from
            CBD-distribution. This method uses the XOF-instance to sample the bits."""
        coeffs = []
        start_index = 0
        end_index = 2*((eta//8) + 1)

        for i in range(n):
            coeffs.append(Zq.random_binomial_xof(q, eta, bytes_to_use[start_index:end_index]))
            start_index=end_index
            end_index += 2*((eta//8) + 1)

        result = cls(q,coeffs)
        result = result.to_symmetric()
        return result

    @classmethod
    def random_binomial(cls, n, q, eta):
        """Creates and returns a new polynomial whose coefficients are drawn from
            CBD-distribution"""
        coeffs = [Zq.random_binomial(q, eta) for _ in range(n)]
        result = cls(q,coeffs)
        result = result.to_symmetric()
        return result

    def to_symmetric(self):
        """ Change coefficients to symmetric form """
        for i in range(len(self.coefficients)):
            self.coefficients[i] = self.coefficients[i].to_symmetric()
        return self

    def round(self):
        """ Round polynomial coefficients to {0,1} to extract the message"""
        for i in range(len(self.coefficients)):
            self.coefficients[i] = self.coefficients[i].round()
        return self

    def compress(self, d):
        """ Compress the coefficients"""
        for i in range(len(self.coefficients)):
            self.coefficients[i] = self.coefficients[i].compress(d)
        return self

    def decompress(self, d):
        """ Decompress the coefficients"""
        for i in range(len(self.coefficients)):
            self.coefficients[i] = self.coefficients[i].decompress(d)
        return self



    def __repr__(self):
        result = ""
        if self.coefficients[0].get_value() != 0:
            result = str(self.coefficients[0].get_value())

        if len(self.coefficients) == 1:
            return result

        for i in range(len(self.coefficients)):
            if self.coefficients[i].get_value() == 0:
                continue
            if i == 0:
                continue
            if i == 1:
                if self.coefficients[i].get_value() != 1:
                    str_value = "+" + str(self.coefficients[i].get_value()) + "x"
                else:
                    str_value = "+" + "x"
            else:
                if self.coefficients[i].get_value() != 1:
                    str_value = "+" + str(self.coefficients[i].get_value()) + "x^" + str(i)
                else:
                    str_value = "+" + "x^" + str(i)
            result += str_value

        # Clumsy but works.
        if len(result) > 0 and result[0] == "+":
            result = result[1:]

        return result

    def get_coefficients(self):
        return self.coefficients

    def __str__(self):
        return self.__repr__()

    def __add__(self, other):
        if not isinstance(other, ZqPolynomial):
            return NotImplemented

        if len(self.coefficients) != len(other.get_coefficients()):
            raise ValueError("Polynomials are of different size")

        new_coefficients = []

        for i in range(len(self.coefficients)):
            new_coefficients.append(Zq(self.q,self.coefficients[i].get_value()+other.get_coefficients()[i].get_value()))
        return ZqPolynomial(self.q, new_coefficients)

    def __sub__(self, other):
        if not isinstance(other, ZqPolynomial):
            return NotImplemented

        if len(self.coefficients) != len(other.get_coefficients()):
            raise ValueError("Polynomials are of different size")

        new_coefficients = []

        for i in range(len(self.coefficients)):
            new_coefficients.append(Zq(self.q,self.coefficients[i].get_value()-other.get_coefficients()[i].get_value()))
        return ZqPolynomial(self.q, new_coefficients)


    # The naive implementation. NTT-version will follow later.
    def __mul__(self, other):
        if not isinstance(other, ZqPolynomial):
            raise TypeError("Can only multiply with another polynomial")

        if len(self.coefficients) != len(other.get_coefficients()):
            raise ValueError("Polynomials are of different size")

        if self.q != other.q:
            raise TypeError("Polynomials must be from the same ring")

        n = len(self.coefficients)
        # Initialize result coefficients with zeros
        result = [Zq(self.q, 0) for _ in range(n)]

        # Perform polynomial multiplication
        for i in range(n):
            for j in range(n):
                # Position in the product
                pos = i + j

                # If position exceeds n-1, we need to reduce modulo x^n + 1
                if pos >= n:
                    # When reducing mod x^n + 1, x^n = -1
                    # So x^(n+k) = -x^k
                    pos = pos - n
                    result[pos] -= self.coefficients[i] * other.coefficients[j]
                else:
                    result[pos] += self.coefficients[i] * other.coefficients[j]
        return ZqPolynomial(self.q, result)


if __name__ == "__main__":
    f = ZqPolynomial(5, [3, 2, 4, 3, 0,0,0,0])
    h = ZqPolynomial(5, [2, 1, 4, 4, 1,0,0,0])
    print(f"f(x)+h(x)={f+h}")
    print(f"f(x)-h(x)={f-h}")
    print(f"f(x)h(x)={f*h}")



