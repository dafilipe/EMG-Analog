"""
Segundo teste do filtro FIR EMG:
- Sinal composto por 100, 250, 400 e 800 Hz
- Compara entrada e saída no tempo
- Compara espectros de amplitude
- Mede o ganho de cada componente
- Considera o atraso linear do FIR (20 amostras = 10 ms)

Instalar:
    python -m pip install numpy scipy matplotlib

Executar:
    python second_test_fir_emg.py
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# ============================================================
# 1. CONFIGURACAO DO FILTRO
# ============================================================

FS = 2000.0  # Frequencia de amostragem (Hz)

# 41 coeficientes reais exportados pelo T-Filter
TAPS = np.array([
    0.00015601092510117117,
    -0.00788066566055242,
    -0.015212584807290128,
    -0.0051757886625766435,
    0.010287142538108768,
    0.0021359202821149463,
    -0.01331299988252857,
    0.000897418909446179,
    0.017512250021890986,
    -0.0058136692224486815,
    -0.022216328379151724,
    0.01386646078192495,
    0.027008437007516397,
    -0.026877800188187126,
    -0.03137670260833094,
    0.04927276219201276,
    0.03490049003725312,
    -0.09699196858890283,
    -0.03719050858495419,
    0.31518557868167985,
    0.5379778171271277,
    0.31518557868167985,
    -0.03719050858495419,
    -0.09699196858890283,
    0.03490049003725312,
    0.04927276219201276,
    -0.03137670260833094,
    -0.026877800188187126,
    0.027008437007516397,
    0.01386646078192495,
    -0.022216328379151724,
    -0.0058136692224486815,
    0.017512250021890986,
    0.000897418909446179,
    -0.01331299988252857,
    0.0021359202821149463,
    0.010287142538108768,
    -0.0051757886625766435,
    -0.015212584807290128,
    -0.00788066566055242,
    0.00015601092510117117
], dtype=float)

# Componentes do sinal de teste: (frequencia_Hz, amplitude)
COMPONENTS = [
    (100.0, 1.0),
    (250.0, 0.8),
    (400.0, 0.5),
    (800.0, 0.7),
]

DURATION = 2.0
GROUP_DELAY_SAMPLES = (len(TAPS) - 1) // 2
GROUP_DELAY_SECONDS = GROUP_DELAY_SAMPLES / FS

# ============================================================
# 2. CRIAR E FILTRAR O SINAL COMPOSTO
# ============================================================

time = np.arange(int(FS * DURATION)) / FS

x = np.zeros_like(time)
for frequency, amplitude in COMPONENTS:
    x += amplitude * np.sin(2 * np.pi * frequency * time)

# FIR causal, equivalente ao processamento amostra a amostra
y = signal.lfilter(TAPS, [1.0], x)

print("=" * 65)
print("SEGUNDO TESTE - SINAL COMPOSTO")
print("=" * 65)
print(f"Frequencia de amostragem: {FS:.0f} Hz")
print(f"Numero de taps: {len(TAPS)}")
print(f"Atraso de grupo: {GROUP_DELAY_SAMPLES} amostras "
      f"({GROUP_DELAY_SECONDS * 1000:.2f} ms)")
print("Componentes: " + ", ".join(
    f"{f:.0f} Hz (A={a:g})" for f, a in COMPONENTS
))

# ============================================================
# 3. MEDIR A AMPLITUDE DE CADA COMPONENTE
# ============================================================

def estimate_amplitude(signal_data, frequency, sample_times):
    """
    Ajusta A*sin(2*pi*f*t) + B*cos(2*pi*f*t) + C.
    A amplitude estimada e sqrt(A**2 + B**2).
    """
    matrix = np.column_stack((
        np.sin(2 * np.pi * frequency * sample_times),
        np.cos(2 * np.pi * frequency * sample_times),
        np.ones_like(sample_times)
    ))
    coefficients, *_ = np.linalg.lstsq(matrix, signal_data, rcond=None)
    return np.hypot(coefficients[0], coefficients[1])


# Ignorar o arranque do filtro. Depois deste intervalo, o sinal
# está em regime estacionário para esta experiência.
analysis_start = 0.20
valid = time >= analysis_start
t_valid = time[valid]

print("\nGANHO MEDIDO POR COMPONENTE")
print("-" * 65)
print(f"{'Frequencia':>12} | {'A entrada':>12} | {'A saida':>12} | {'Ganho':>10}")
print("-" * 65)

for frequency, input_amplitude in COMPONENTS:
    amplitude_in = estimate_amplitude(x[valid], frequency, t_valid)
    amplitude_out = estimate_amplitude(y[valid], frequency, t_valid)
    gain_db = 20 * np.log10(max(amplitude_out / amplitude_in, 1e-15))

    # Valor teórico obtido diretamente da resposta em frequência
    _, h_at_frequency = signal.freqz(
        TAPS, worN=np.array([frequency]), fs=FS
    )
    theoretical_gain_db = 20 * np.log10(max(abs(h_at_frequency[0]), 1e-15))

    print(f"{frequency:9.0f} Hz | {amplitude_in:12.6f} | "
          f"{amplitude_out:12.6f} | {gain_db:8.2f} dB")
    print(f"{'Ganho teorico:':>12} {'':>12} {'':>12} | "
          f"{theoretical_gain_db:8.2f} dB")

# ============================================================
# 4. GRAFICO TEMPORAL
# ============================================================

# Mostrar uma janela curta para ser possivel observar as ondas.
# A saida esta atrasada 10 ms relativamente a entrada.
plot_start = 0.20
plot_end = 0.24
plot_mask = (time >= plot_start) & (time <= plot_end)

plt.figure(figsize=(11, 5))
plt.plot(time[plot_mask], x[plot_mask], label="Entrada", alpha=0.75)
plt.plot(time[plot_mask], y[plot_mask], label="Saida filtrada", linewidth=1.5)
plt.xlabel("Tempo (s)")
plt.ylabel("Amplitude")
plt.title("Sinal composto: entrada vs. saida do FIR")
plt.grid(True)
plt.legend()
plt.tight_layout()

# ============================================================
# 5. ESPECTRO DE AMPLITUDE
# ============================================================

# Usar apenas a parte estacionaria para reduzir o efeito do arranque.
x_steady = x[valid]
y_steady = y[valid]
n = len(x_steady)

# Como a duracao e as frequencias sao escolhidas para alinhar
# com bins da FFT, podemos comparar diretamente as amplitudes.
window = np.hanning(n)
window_sum = np.sum(window)

X = np.fft.rfft(x_steady * window)
Y = np.fft.rfft(y_steady * window)
freq_axis = np.fft.rfftfreq(n, d=1 / FS)

# Espectro de amplitude unilateral, corrigido pelo ganho da janela.
spectrum_in = 2 * np.abs(X) / window_sum
spectrum_out = 2 * np.abs(Y) / window_sum

plt.figure(figsize=(11, 5))
plt.plot(freq_axis, spectrum_in, label="Entrada")
plt.plot(freq_axis, spectrum_out, label="Saida filtrada")
plt.xlim(0, FS / 2)
plt.xlabel("Frequencia (Hz)")
plt.ylabel("Amplitude")
plt.title("Espectro de amplitude: antes e depois do FIR")
plt.grid(True)
plt.legend()
plt.tight_layout()

# Vista ampliada das quatro componentes.
plt.figure(figsize=(11, 5))
plt.plot(freq_axis, spectrum_in, label="Entrada")
plt.plot(freq_axis, spectrum_out, label="Saida filtrada")
plt.xlim(0, 1000)
plt.ylim(bottom=0)
plt.xticks(np.arange(0, 1001, 100))
plt.xlabel("Frequencia (Hz)")
plt.ylabel("Amplitude")
plt.title("Espectro de amplitude (0-1000 Hz)")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.show()
