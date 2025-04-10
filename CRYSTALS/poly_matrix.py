from .zq_polynomial import ZqPolynomial

class PolyMatrix:
    """ Matrix that has elements from the polynomial ring Z_q[x]/(x^n+1), which, in turn, are
        implemented in ZqPolynomial-class.
        Usage A = PolyMatrix(rows=2, columns=3, q=3329, n=17).
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

    def round(self):
        """ Round values to {0,1}. Used to extract the message."""
        for i in range(self.rows):
            for j in range(self.cols):
                self[i,j] = self[i,j].round()
        return self

    def extract_message(self):
        """" Extract the message from polynomial coefficients.
             Only extract it from the polynomial in self[0][0]"""
        result = []
        for i in range(self.n):
            result.append(self[(0,0)].at(i).value)
        return result

    def __getitem__(self, key):
        # key will be a tuple (i,j) when you call a[i,j]
        i, j = key
        return self.matrix[i][j]

    def __setitem__(self, key, value):
        i, j = key
        if not isinstance(value, ZqPolynomial):
            raise TypeError("Matrix elements must be ZqPolynomial")
        if value.q != self.q or self.n != value.n:
            raise TypeError("Polynomial is from different ring")
        self.matrix[i][j] = value

    @property
    def T(self):
        """Returns a new matrix that is the transpose of the current matrix. Call as M.T"""
        result = PolyMatrix(self.cols, self.rows, self.q, self.n)
        for i in range(self.rows):
            for j in range(self.cols):
                result[j, i] = self[i, j]
        return result

    def __matmul__(self, other):  # enables @ operator
        """ Matrix multiplication @ """
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

    def __mul__(self, other):
        """Element-wise multiplication (*)"""
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Matrices must have same dimensions")

        if self.q != other.q or self.n != other.n:
            raise ValueError("Matrice elements are not from same ring")

        result = PolyMatrix(self.rows, self.cols, self.q, self.n)

        for i in range(self.rows):
            for j in range(self.cols):
                result[i,j] = self[i,j] * other[i,j]
        return result

    def __add__(self, other):
        """Addition, element-wise"""
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
