import struct

class Posit:
    def __init__(self, n=16, es=2):
        self.n = n
        self.es = es

    def posit_to_float(self, x):
        # Krok 1: Pobranie znaku
        sign = (x >> (self.n - 1)) & 1

        # Krok 2: Pobranie wartości (bez znaku)
        val = x & ((1 << (self.n - 1)) - 1)

        # Krok 3: Sprawdzenie czy wartość jest równa 0
        if val == 0:
            # Krok 4: Jeśli znak jest 0, ustaw y na 0, w przeciwnym razie na NaN
            if sign == 0:
                return 0.0
            else:
                return float('nan')
        else:
            # Krok 9: Sprawdzenie znaku
            if sign == 0:
                abs_val = val
            else:
                # Krok 12: Obliczenie wartości bezwzględnej (2's complement)
                abs_val = ((1 << (self.n - 1)) - 1) & ~val + 1

            # Krok 13: Ekstrakcja pól regime, exp, frac
            regime, exp, frac = self.extract_fields(abs_val)

            # Krok 14: Bias dla wykładnika IEEE float
            bias = (2 ** (8 - 1)) - 1

            # Krok 15: Obliczenie biased_exp
            biased_exp = (regime << self.es) + exp + bias

            # Krok 16: Skonstruowanie liczby IEEE float
            ieee_float = self.construct_ieee_float(sign, biased_exp, frac)

            # Krok 17: Dodanie zer na końcu, jeśli to konieczne (już uwzględnione w konstrukcji liczby IEEE float)
            return ieee_float

    def extract_fields(self, val):
        k = 0
        while val & (1 << (self.n - 2 - k)):
            k += 1

        regime = k - 1
        exp = (val >> (self.n - 2 - k - self.es)) & ((1 << self.es) - 1)
        frac = (val & ((1 << (self.n - 2 - k - self.es)) - 1)) << (23 - (self.n - 2 - k - self.es))  # 23 is the number of bits in mantissa in IEEE 754

        return regime, exp, frac

    def construct_ieee_float(self, sign, biased_exp, frac):
        ieee_int = (sign << 31) | (biased_exp << 23) | (frac & ((1 << 23) - 1))
        ieee_float = struct.unpack('!f', struct.pack('!I', ieee_int))[0]
        return ieee_float


# Przykład użycia
posit_system = Posit(n=16, es=2)
posit_value = 0b0111010110101011  # Przykładowa wartość Posit
ieee_float = posit_system.posit_to_float(posit_value)

# Przykładowa wartość rzeczywista odpowiadająca Posit (to powinno być obliczone lub znane)

print(f"Posit: {posit_value:016b}, IEEE 754 Float: {ieee_float}")
