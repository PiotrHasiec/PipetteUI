import numpy as np
import matplotlib.pyplot as plt

# Zakres napięcia
V = np.linspace(-0.1, 1.05, 2000)

# Parametry diody
I0 = 1e-12      # prąd nasycenia [A]
n = 1.8         # współczynnik idealności
Vt = 0.0259     # napięcie termiczne [V]
Iph = 2e-3      # fotoprąd [A]

# Charakterystyka ciemna
I_dark = I0 * (np.exp(V / (n * Vt)) - 1)

# Charakterystyka pod oświetleniem
I_light = I_dark - Iph

# Zamiana na mA
I_dark_mA = I_dark 
I_light_mA = I_light

# Wykres
plt.figure(figsize=(10, 6))

plt.plot(V, I_dark_mA, linewidth=2,
         label='Charakterystyka ciemna')

plt.plot(V, I_light_mA, linewidth=2,
         label='Charakterystyka pod oświetleniem')

# Osie OX i OY
plt.axhline(0, color='black', linewidth=1.2)
plt.axvline(0, color='black', linewidth=1.2)

# Opisy osi
plt.xlabel('Napięcie [V]', fontsize=12)
plt.ylabel('Prąd [mA]', fontsize=12)

# Tytuł
plt.title('Charakterystyka prądowo-napięciowa ogniwa fotowoltaicznego')



# Siatka
plt.grid(True)

# Legenda
plt.legend()

plt.show()