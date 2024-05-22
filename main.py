import struct
import timeit
import random
import csv

class Posit:
    def __init__(self, n, es):
        self.n = n
        self.es = es

    def posit_to_float(self, x):
        # Implementacja konwersji Pozytywu na IEEE 754
        sign = (x >> (self.n - 1)) & 1
        val = x & ((1 << (self.n - 1)) - 1)

        if val == 0:
            if sign == 0:
                return 0.0
            else:
                return float('nan')
        else:
            if sign == 0:
                abs_val = val
            else:
                abs_val = ((1 << (self.n - 1)) - 1) & ~val + 1

            regime, exp, frac = self.extract_fields(abs_val)
            bias = (2 ** (8 - 1)) - 1
            biased_exp = (regime << self.es) + exp + bias
            ieee_float = self.construct_ieee_float(sign, biased_exp, frac)
            return ieee_float

    def extract_fields(self, val):
        k = 0
        while val & (1 << (self.n - 2 - k)):
            k += 1
        regime = k - self.es
        exp = (val >> (self.n - 2 - k)) & ((1 << self.es) - 1)
        frac = (val & ((1 << (self.n - 2 - k)) - 1)) << (23 - (self.n - 2 - k))
        return regime, exp, frac

    def construct_ieee_float(self, sign, biased_exp, frac):
        ieee_int = (sign << 31) | (biased_exp << 23) | (frac & ((1 << 23) - 1))
        ieee_float = struct.unpack('!f', struct.pack('!I', ieee_int))[0]
        return ieee_float

# Example usage
formats = [(16, 1), (16, 2), (16, 3), (16, 4)]
num_values = 50  # Liczba losowych wartości do wygenerowania dla każdego formatu

# Otwieranie pliku CSV do zapisu wyników
filename = "posit_results_combined.csv"
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Format', 'Value', 'Execution Time (ms)', 'IEEE 754 Float'])

    # Inicjalizacja instancji klasy Pozytyw
    for n, es in formats:
        posit_system = Posit(n=n, es=es)
        random.seed(42)  # Ustawienie ziarna dla reprodukowalności
        values = [random.randint(0, (1 << n) - 1) for _ in range(num_values)]

        # Zapisywanie wyników do pliku CSV
        for value in values:
            start_time = timeit.default_timer()
            ieee_float = posit_system.posit_to_float(value)
            end_time = timeit.default_timer()
            elapsed_time_ms = (end_time - start_time) * 1000  # Czas wykonania w milisekundach

            writer.writerow([f"<{n}, {es}>", f"{value:0{n}b}", f"{elapsed_time_ms:.6f}", f"{ieee_float}"])

print(f"Zapisano wyniki do pliku CSV: {filename}")
