import struct
import timeit
import random

class Posit:
    def __init__(self, n=16, es=2):
        self.n = n
        self.es = es

    def posit_to_float(self, posit_value):
        if len(posit_value) != self.n:
            raise ValueError(f"Posit value length should be {self.n} bits")

        sign = int(posit_value[0])
        val = int(posit_value[1:], 2)

        if val == 0:
            if sign == 0:
                return 0.0
            else:
                return -0.0
        else:
            if sign != 0:
                val = ((1 << (self.n - 1)) - 1) & ~val + 1  # 2's complement

            regime, exp, frac = self.extract_fields(val)
            biased_exp = (regime << self.es) + exp + (2 ** (8 - 1) - 1)  # Bias calculation for IEEE float

            ieee_float = self.construct_ieee_float(sign, biased_exp, frac)
            return ieee_float

    def float_to_posit(self, float_value):
        sign = 0 if float_value >= 0 else 1
        float_value = abs(float_value)
        ieee_int = struct.unpack('!I', struct.pack('!f', float_value))[0]

        # Extract sign, exponent and fraction
        sign_bit = (ieee_int >> 31) & 1
        exponent = (ieee_int >> 23) & 0xFF
        fraction = ieee_int & 0x7FFFFF

        if exponent == 0:
            regime = 0
            exp = 0
        else:
            regime = (exponent - (2 ** (8 - 1) - 1)) >> self.es
            exp = (exponent - (2 ** (8 - 1) - 1)) & ((1 << self.es) - 1)

        val = (regime << (self.n - 2 - self.es)) | (exp << (self.n - 2 - self.es - self.es)) | (fraction >> (23 - (self.n - 2 - self.es)))
        posit_value = sign << (self.n - 1) | val

        return posit_value

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

    def compute_relative_error(self, original_value, ieee_float):
        if original_value == 0.0:
            return abs(original_value - ieee_float)
        else:
            return abs(original_value - ieee_float) / abs(original_value)

# Benchmarking
formats = [(16, 1), (16, 2), (16, 3), (16, 4)]
num_values = 50  # Liczba losowych wartości do wygenerowania dla każdego formatu

for n, es in formats:
    posit_system = Posit(n=n, es=es)
    random.seed(42)  # Ustawienie ziarna dla reprodukowalności
    values = [format(random.randint(0, (1 << n) - 1), f'0{n}b') for _ in range(num_values)]

    # Zapisywanie wyników do pliku CSV
    for value in values:
        start_time = timeit.default_timer()
        ieee_float = posit_system.posit_to_float(value)
        end_time = timeit.default_timer()
        elapsed_time_ms = (end_time - start_time) * 1000  # Czas wykonania w milisekundach

        print(f"Format: <{n},{es}>, Value: {value}, Execution Time: {elapsed_time_ms:.6f} ms, IEEE 754 Float: {ieee_float}")
