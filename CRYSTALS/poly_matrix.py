from CRYSTALS import ZqPolynomial
import hashlib
import secrets

class PolyMatrix():
    """ Matrix that has elements from the polynomial ring Z_q[x]/(x^n+1), which, in turn, are
        implemented in ZqPolynomial-class.
        Usage A = PolyMatrix(rows=2, columns=3, q=3329, n=256).
        You can access and set elements with brackets, A[i][j]=<polynomial>"""
    def __init__(self, rows, cols, q, n):
        self.rows = rows
        self.cols = cols
        self.q = q
        self.n = n
        self.matrix = [[ZqPolynomial(q, [0]*self.n) for _ in range(self.cols)]
                      for _ in range(self.rows)]

    def random_uniform(self):
        """ Fills the matrix with polynomials whose coefficients are from UNIFORM distribution.
             Only use to fill a matrix."""
        self.matrix = [[ZqPolynomial.random_uniform(self.n, self.q) for _ in range(self.cols)]
                      for _ in range(self.rows)]
        return self

    def random_binomial(self, eta):
        """ Fills the matrix with polynomials whose coefficients are from BINOMIAL distribution.
            Only use to fill a vector."""
        self.matrix = [[ZqPolynomial.random_binomial(self.n, self.q, eta) for _ in range(self.cols)]
                      for _ in range(self.rows)]
        return self

    def is_equal_to(self, other):
        """ Compares two instances of PolyMatrix. Checks dimensions, n, q and
            polynomial coefficients. If all match, return True, otherwise return False."""
        if not isinstance(other, PolyMatrix):
            return False

        if other.n != self.n:
            return False

        if other.q != self.q:
            return False

        if other.rows!= self.rows:
            return False

        if other.cols != self.cols:
            return False

        if self.rows == 1 and self.rows == 1:
            if self.matrix[0][0].is_equal_to(other.matrix[0][0]):
                return True
            else:
                return False

        else:
            for i in range(self.rows):
                for j in range(self.cols):
                    if not self.matrix[i][j].is_equal_to(other.matrix[i][j]):
                        return False

        return True

    def random_binomial_xof(self, eta, bytes_to_use):
        """ Fills the matrix with polynomials whose coefficients are from BINOMIAL distribution.
            Only use to fill a vector. bytes_to_use provide the random bits used in sampling."""
        start_index = 0
        end_index = 2*(((eta//8) + 1) * self.n)

        for i in range(self.rows):
            for j in range(self.cols):
                bytes_for_polynomial = bytes_to_use[start_index:end_index]
                self.matrix[i][j]= ZqPolynomial.random_binomial_xof(self.n, self.q, eta, bytes_for_polynomial )
                start_index = end_index
                end_index += 2*(((eta//8) + 1) * self.n)

        return self

    def fill_xof(self, seed_to_use):
        """ Fill the matrix with values extracted from SHAKE128
            with the given seed. The values are extracted by two
            bytes at a time, putting the limit of q to 2^16."""
        coefficients = []
        shake = hashlib.shake_128()
        # Initialize XOF with the seed. Now each party uses this same
        # method and since SHAKE128 is fully deterministic, they end
        # up with the same coefficients.
        shake.update(seed_to_use)
        bytes_per_number = 2  # This puts a limit on size of q
        random_bytes = shake.digest(self.rows*self.cols*self.n*bytes_per_number)
        for i in range(0, len(random_bytes), bytes_per_number):
            val = int.from_bytes(random_bytes[i:i + bytes_per_number], byteorder='big')
            coefficients.append(val % self.q)

        # Populate the matrix entries. Extract values for a polynomial
        # and use that to instantiate a new polynomial.
        for i in range(self.rows):
            for j in range(self.cols):
                new_coefficients = coefficients[0:self.n]
                coefficients = coefficients[self.n:]
                self[i, j] = ZqPolynomial(self.q, new_coefficients)
        return self

    def round(self):
        """ Round values to {0,1}. Used to extract the message."""
        for i in range(self.rows):
            for j in range(self.cols):
                self[i,j] = self[i,j].round()
        return self

    def compress(self, d):
        """ Compress the coefficients. Cascades the call to Zq.compress"""
        for i in range(self.rows):
            for j in range(self.cols):
                self[i,j] = self[i,j].compress(d)
        return self

    def decompress(self, d):
        """ Decompress the coefficients. Cascades the call to Zq.decompress"""
        for i in range(self.rows):
            for j in range(self.cols):
                self[i,j] = self[i,j].decompress(d)
        return self

    def extract_message(self):
        """" Extract the message from polynomial coefficients.
             Only extract it from the polynomial in self[0][0]"""
        return self[(0,0)].extract_coefficients_int()

    def extract_coefficients_int(self):
        """ Extract the coefficients of the polynomials in the matrix.
            Return them as a list of integers. This is meant to be used
            when concatenating A and t."""
        coefficients_int = []
        for i in range(self.rows):
            for j in range(self.cols):
                coefficients_int.extend(self[i,j].extract_coefficients_int())

        return coefficients_int

    def __getitem__(self, key):
        if not isinstance(key, tuple) or len(key) != 2:
            raise TypeError("Key must be a tuple of two elements")
        # key will be a tuple (i,j) when you call a[i,j]
        i, j = key
        return self.matrix[i][j]

    def __setitem__(self, key, value):
        if not isinstance(key, tuple) or len(key) != 2:
            raise TypeError("Key must be a tuple of two elements")

        if not isinstance(value, ZqPolynomial):
            raise TypeError("Matrix elements must be ZqPolynomial")

        if value.q != self.q or self.n != value.n:
            raise TypeError("Polynomial is from different ring")

        i, j = key
        self.matrix[i][j] = value

    @property
    def T(self):
        """Returns a new matrix that is the transpose of the current matrix.
           Call as M.T"""
        result = PolyMatrix(self.cols, self.rows, self.q, self.n)
        for i in range(self.rows):
            for j in range(self.cols):
                result[j, i] = self[i, j]
        return result

    def __matmul__(self, other):  # enables @ operator
        """ Matrix multiplication @ """
        if not isinstance(other, PolyMatrix):
            raise TypeError("Multiplication(@) expects a matrix")

        if self.cols != other.rows:
            raise ValueError("Inner dimensions must match")

        if self.q != other.q or self.n != other.n:
            raise ValueError("Matrice elements are not from same ring")

        result = PolyMatrix(self.rows, other.cols, self.q, self.n)

        for i in range(self.rows):
            for j in range(other.cols):
                # Sum of products for this position
                for k in range(self.cols):
                    result[i, j] += self[i, k] * other[k, j]

        return result


    def __add__(self, other):
        """Addition, element-wise"""
        if not isinstance(other, PolyMatrix):
            raise TypeError("Addition expects a matrix")

        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Matrices must have same dimensions")

        if self.q != other.q or self.n != other.n:
            raise ValueError("Matrice elements are not from same ring")

        result = PolyMatrix(self.rows, self.cols, self.q, self.n)

        for i in range(self.rows):
            for j in range(self.cols):
                result[i,j] = self[i,j] + other[i,j]
        return result

    def __sub__(self,other):
        """Subtraction, element-wise"""
        if not isinstance(other, PolyMatrix):
            raise TypeError("Subtraction expects a matrix")

        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Matrices must have same dimensions")

        if self.q != other.q or self.n != other.n:
            raise ValueError("Matrice elements are not from same ring")

        result = PolyMatrix(self.rows, self.cols, self.q, self.n)

        for i in range(self.rows):
            for j in range(self.cols):
                result[i,j] = self[i,j] - other[i,j]
        return result

    def __str__(self):
        """Returns a readable string representation of matrix."""
        rows_str = []
        for row in self.matrix:
            elements = [f"[{poly}]" for poly in row]
            rows_str.append("  ".join(elements))
        return "\n".join(rows_str)

    def __repr__(self):
        """Returns a detailed representation for debugging."""
        return f"PolyMatrix({self.rows}×{self.cols}, q={self.q})\n{self.__str__()}"


if __name__ == "__main__":
    A = PolyMatrix(2,1,5,3)
    A[0,0] = ZqPolynomial(5,[4,1,2])
    A[1,0] = ZqPolynomial(5,[0,1,3])

    B = PolyMatrix(2,1,5,3)
    B[0,0] = ZqPolynomial(5,[1,2,3])
    B[1,0] = ZqPolynomial(5,[0,4,0])
    print(f"({A[0,0]})({B[0,0]})={A[0,0]*B[0,0]}")
    print(f"A[1,0]*B[1,0]={A[1,0]*B[1,0]}")
    print(f"A.T@B={A.T@B}")

    print(f"A+B={A+B}")
    print(f"A-B={A-B}")
    print(f"A*B={A*B}")

    seed = secrets.token_bytes(32)
    C = PolyMatrix(3,3,3329,3)
    C = C.fill_xof(seed)
    print(C)