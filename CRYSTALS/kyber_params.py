
class KyberParams:
    def __init__(self, k, n, q, eta1, eta2, du, dv):
        self.k = k      # module rank
        self.n = n      # polynomial degree
        self.q = q      # modulus
        self.eta1 = eta1  # noise parameter for secret
        self.eta2 = eta2  # noise parameter for error
        self.du = du    # compression parameter for u
        self.dv = dv    # compression parameter for v