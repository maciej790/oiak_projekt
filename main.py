#libki
import struct
import timeit
import random
import csv

class Posit:
    def __init__(self, n=32, es=2):
        self.n = n
        self.es = es

    #konwersja na z posit na float
    def posit_na_float(self, posit_liczba):

        znak = int(posit_liczba[0]) #sam znak
        bez_znaku = int(posit_liczba[1:], 2) #liczba obcieta o znak

        if bez_znaku == 0:
            return -0.0 if znak else 0.0 #jesli same zera po znaku => 0, jesli znak = 1 => liczba ujemna, w przeciwnym wypadku => dodatnia
        else:
            if znak != 0: #ujemna
                # dopelnienie do 2
                bez_znaku = ((1 << (self.n - 1)) - 1) & ~bez_znaku + 1  #przesuwanie bitow liczby i negacja NOT

            regime, wykladnik, mantysa = self.pobierz_pola_posit(bez_znaku) #wyluskanie pol posit
            bias_mantysa = (regime << self.es) + wykladnik + (2**(8 - 1) - 1)  # mozna by odrazu 127 ale dla czytelnosci arytmetyki ieee :)

            # na podstawie wyluskanych danych tworzymy reprezentacje floata
            ieee_float = self.stworz_ieee_float(znak, bias_mantysa, mantysa)
            return ieee_float

    def float_na_posit(self, float_bez_znaku):
        # jesli liczba jest ujemna ustaw znak na 1 w przeciwnym na 0
        znak = 0 if float_bez_znaku >= 0 else 1
        float_bez_znaku = abs(float_bez_znaku)
        #konwertowanie floata na binarke (4 bajty) - funkaja wbudowana w pythona
        ieee_int = struct.unpack('!I', struct.pack('!f', float_bez_znaku))[0]

        # wyodrebnianie pol ieee
        znak_bit = (ieee_int >> 31) & 1 # bit znaku - przesuwamy o 31 w prawo i maska 1
        wykladnik_float = (ieee_int >> 23) & 0xFF #wykladnik - przesuwamy o 23 w prawo i maska 0xff
        mantysa_float = ieee_int & 0x7FFFFF #mantysa - to co zostalo i maska 

        #liczba zdenormalizowana wtedy regime i exp na 0
        if wykladnik_float == 0:
            regime = 0
            wykladnik = 0
        #znormalizowana
        else:
            regime = (wykladnik_float - (2**(8 - 1) - 1)) >> self.es #odejmij przesuniecie bias i przesun w prawo o es
            wykladnik = (wykladnik_float - (2**(8 - 1) - 1)) & ((1 << self.es) - 1) # przesun o tyle samo i maska

        # jesli przesuniecie jest < 0 to mantysa jest wieksza od 23bit
        przesuniecie_bitowe = (23 - (self.n - 2 - self.es)) #roznica bitow mantysy ieee a posit
        if przesuniecie_bitowe < 0:
            przesuniecie_bitowe = 0

        #laczenie pol wykladnika i mantysy z przesunieciem
        bez_znaku = (regime << (self.n - 2 - self.es)) | (wykladnik << (self.n - 2 - self.es - self.es)) | (mantysa_float >> przesuniecie_bitowe)
        # laczymy z bitem znaku i mamy liczbe
        posit_liczba = znak << (self.n - 1) | bez_znaku

        return posit_liczba
    
    # pobieranie pol z posit
    def pobierz_pola_posit(self, bez_znaku):
        k = 0
        # dopoki napotkany bit jest 1
        while bez_znaku & (1 << (self.n - 2 - k)) and k < self.n - 2: #czy bit na (self.n - 2 - k) jest 1 lub 0
            k += 1

        regime = k - 1
        #przesuwaj bity bez_znaku w prawo o liczbe bitow równa (self.n - 2 - k - self.es) 
        # aby uzyskac bity wykladnika na najmniej znaczących pozycjach
        wykladnik = (bez_znaku >> (self.n - 2 - k - self.es)) & ((1 << self.es) - 1)

        #liczba bitow potrzebnych na przesunieta mantyse ieee (23bity)
        przesuniecie_bitowe = (23 - (self.n - 2 - k - self.es))
        # jesli przesuniecie < 0 to 0 zeby nie przesuwac w lewo
        if przesuniecie_bitowe < 0:
            przesuniecie_bitowe = 0

        #wyodrebnij mantyse
        mantysa = (bez_znaku & ((1 << (self.n - 2 - k - self.es)) - 1)) << przesuniecie_bitowe  # 23 liczba bitow mantysy ieee

        return regime, wykladnik, mantysa

    #tworzenie reprezenracji floata z posita
    def stworz_ieee_float(self, znak, bias_mantysa, mantysa):
        #przesun znak na najbrarziej znaczece miejsce (31) potem wykladnik od 23 pozycji a reszta mantysa
        ieee_int = (znak << 31) | (bias_mantysa << 23) | (mantysa & ((1 << 23) - 1))
        #skonweruj na binarke big endian float
        ieee_float = struct.unpack('!f', struct.pack('!I', ieee_int))[0]
        return ieee_float

    def oblicz_blad_wzgledny(self, oryginalna_bez_znaku, skonwertowana_bez_znaku):
        if oryginalna_bez_znaku == 0:
            return abs(oryginalna_bez_znaku - skonwertowana_bez_znaku)
        else:
            return abs(oryginalna_bez_znaku - skonwertowana_bez_znaku) / abs(oryginalna_bez_znaku)


# Tutaj beda benchmarki dla kodu
# zapis do plikow excelowskich
formaty = [(32, 1), (32, 2), (32, 3), (32, 4)]
ilosc_powtorzen = 50 

for n, es in formaty:
    plik = f"wyniki{n}_{es}.csv"
    with open(plik, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Format', 'Liczba', 'Czas (ms)', 'IEEE 754 Float', 'Blad wzgledny'])

        posit_system = Posit(n=n, es=es)
        losowe_liczby = [format(random.randint(0, (1 << n) - 1), f'0{n}b') for _ in range(ilosc_powtorzen)]

        for liczba in losowe_liczby:
            pomiar_start = timeit.default_timer()
            ieee_float = posit_system.posit_na_float(liczba)
            pomiar_stop = timeit.default_timer()
            czas_calkowity = (pomiar_stop - pomiar_start) * 1000  # ms

            skonwertowany_posit = posit_system.float_na_posit(ieee_float)

            blad_wzgledny = posit_system.oblicz_blad_wzgledny(int(liczba, 2), skonwertowany_posit)

            writer.writerow([f"<{n},{es}>", liczba, f"{czas_calkowity:.6f}".replace('.', ','), ieee_float, f"{blad_wzgledny:.2f}".replace('.', ',')])

    print(f"Zapisano wyniki do pliku CSV: {plik}")

