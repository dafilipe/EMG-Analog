import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# Especificações
FS = 2000
FP = 500
FSTOP = 600
GPASS = 1
GSTOP = 30

# Determinar ordem mínima
N, WN = signal.buttord(
    FP, FSTOP,
    GPASS, GSTOP,
    fs=FS
)

# Criar filtro Butterworth
sos = signal.butter(
    N,
    WN,
    btype="lowpass",
    fs=FS,
    output="sos"
)

# Resposta em frequência
f, h = signal.sosfreqz(sos, worN=8192, fs=FS)
gain_db = 20 * np.log10(np.maximum(abs(h), 1e-12))

print("Ordem:", N)
print("Frequência natural:", WN, "Hz")

for freq in [100, 250, 400, 500, 600, 800]:
    _, response = signal.sosfreqz(sos, worN=[freq], fs=FS)
    gain = 20 * np.log10(abs(response[0]))
    print(f"{freq} Hz: {gain:.2f} dB")

plt.figure(figsize=(10, 5))
plt.plot(f, gain_db)
plt.axvline(500, linestyle="--", label="500 Hz")
plt.axvline(600, linestyle="--", label="600 Hz")
plt.axhline(-30, linestyle="--", label="-30 dB")
plt.xlabel("Frequência (Hz)")
plt.ylabel("Ganho (dB)")
plt.title("IIR Butterworth - Resposta em frequência")
plt.grid()
plt.legend()
plt.show()



# ============================================================
# SEGUNDO TESTE - SINAL COMPOSTO
# ============================================================

duration = 2.0
t = np.arange(0, duration, 1/FS)

# Sinal composto
x = (
    np.sin(2*np.pi*100*t)
    + 0.8*np.sin(2*np.pi*250*t)
    + 0.5*np.sin(2*np.pi*400*t)
    + 0.7*np.sin(2*np.pi*800*t)
)

# Aplicar filtro IIR
y = signal.sosfilt(sos, x)

# Ignorar transitório inicial
start = int(0.2 * FS)
x_test = x[start:]
y_test = y[start:]
t_test = t[start:]

# Medir amplitude de cada componente
frequencies = [100, 250, 400, 800]

print("\nGANHO MEDIDO POR COMPONENTE")
print("-" * 65)

for freq in frequencies:

    # Ajuste sinusoidal por mínimos quadrados
    A = np.column_stack([
        np.sin(2*np.pi*freq*t_test),
        np.cos(2*np.pi*freq*t_test)
    ])

    coef_in = np.linalg.lstsq(A, x_test, rcond=None)[0]
    coef_out = np.linalg.lstsq(A, y_test, rcond=None)[0]

    amp_in = np.linalg.norm(coef_in)
    amp_out = np.linalg.norm(coef_out)

    gain = 20*np.log10(amp_out/amp_in)

    print(
        f"{freq:8d} Hz | "
        f"Entrada: {amp_in:.6f} | "
        f"Saída: {amp_out:.6f} | "
        f"Ganho: {gain:.2f} dB"
    )

# Gráfico temporal
plt.figure(figsize=(12, 5))
plt.plot(t_test[:500], x_test[:500], label="Entrada")
plt.plot(t_test[:500], y_test[:500], label="Saída IIR")
plt.xlabel("Tempo (s)")
plt.ylabel("Amplitude")
plt.title("Teste do filtro IIR com sinal composto")
plt.grid()
plt.legend()
plt.show()