#libki
import struct
import timeit
import random
import csv

class KonwersjaPosit:
    def __init__(self, n, es):
        self.n = n
        self.es = es

    def KonwersjaNaFloat(self, x):
        #Konwersja wartosci posit na liczbe zmiennoprzecinkowa IEEE 754.
        # x: Wartość w formacie posit.
        
        # Wyodrębnienie bitu znaku i wartości
        znak = (x >> (self.n - 1)) & 1
        wartosc = x & ((1 << (self.n - 1)) - 1)

        if wartosc == 0:
            if znak == 0:
                return 0.0
            else:
                return float('nan')
        else:
            # wtedy oblicz wartosc bezwzgledna
            if znak == 0:
                wartosc_bezwzgledna = wartosc
            else:
                wartosc_bezwzgledna = ((1 << (self.n - 1)) - 1) & ~wartosc + 1

            # wyodrebnienie pol dla posit
            regime, wykladnik, mantysa = self.PobierzPolaPosit(wartosc_bezwzgledna)
            #bias dla wykladnika - nadmiar
            bias = (2 ** (8 - 1)) - 1 # mozna by po prostu 127 ale tak widac jak dziala arytmetyka ieee :)
            bias_wykladnik = (regime << self.es) + wykladnik + bias
            #stworz na podstawie pol liczbe float dla ieee
            ieee_float = self.Stworz_IEEE_Float(znak, bias_wykladnik, mantysa)
            return ieee_float

    #funkcja dla pobierania pol z posit
    def PobierzPolaPosit(self, wartosc):
        k = 0
        while wartosc & (1 << (self.n - 2 - k)):
            k += 1
        regime = k - self.es
        wykladnik = (wartosc >> (self.n - 2 - k)) & ((1 << self.es) - 1)
        mantysa = (wartosc & ((1 << (self.n - 2 - k)) - 1)) << (23 - (self.n - 2 - k))
        return regime, wykladnik, mantysa

    def Stworz_IEEE_Float(self, znak, bias_wykladnik, mantysa):
        #tworzenie liczby float z bitu znaku, znormalizowanego wykładnika i mantysy.

        ieee_int = (znak << 31) | (bias_wykladnik << 23) | (mantysa & ((1 << 23) - 1))
        ieee_float = struct.unpack('!f', struct.pack('!I', ieee_int))[0]
        return ieee_float


# Tutaj używamy gotowego kodu klasy
# Również tutaj odbywa się benchmark
# Oraz zapis wyniku benchmarku do pliku

formaty = [(16, 1), (16, 2), (16, 3), (16, 4)]
#UWAGA#
#dla wiekszych formatow jest zbyt duzo bledow
#wynikaja one ze zbyt duzego wykladnika w stostunku do dlugosci liczby
#osiagany jest warunek graniczny (jeszczr )
#stad przetestowano najpoularniejsze wedlug literatury rozmiary es
#UWAGA#
ilosc_powtorzen = 50  # Liczba losowych wartości do wygenerowania dla każdego formatu

# Otwieranie pliku CSV do zapisu wyników
plik = "wyniki.csv"
with open(plik, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Format', 'liczba', 'Czas (ms)', 'IEEE 754 Float'])

    #rozpoczynamy konwersje dla kazdego formatu 
    for n, es in formaty:
        konwersja = KonwersjaPosit(n=n, es=es)
        losowe_liczby = [random.randint(0, (1 << n) - 1) for _ in range(ilosc_powtorzen)]

        # Zapisywanie wyników do pliku CSV
        for liczba in losowe_liczby:
            pomiar_start = timeit.default_timer()
            ieee_float = konwersja.KonwersjaNaFloat(liczba)
            pomiar_stop = timeit.default_timer()
            czas = (pomiar_stop - pomiar_start) * 1000  # Czas wykonania w milisekundach

            writer.writerow([f"<{n}, {es}>", f"{liczba:0{n}b}", f"{czas:.6f}", f"{ieee_float}"])

print(f"Zapisano wyniki do pliku CSV: {plik}")

