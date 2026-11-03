"""
Teste do filtro FIR EMG gerado pelo T-Filter.

Especificacoes declaradas no ficheiro SampleFilter.h:
- Frequencia de amostragem: 2000 Hz
- Banda passante: 0 a 500 Hz
- Banda de rejeicao: 600 a 1000 Hz
- Ripple desejado: 5 dB (obtido: ~0.7592 dB)
- Atenuacao desejada: 40 dB (obtida: ~54.6484 dB)

O script:
1. Verifica os coeficientes e a simetria.
2. Desenha a resposta em frequencia.
3. Mede o ganho em 100, 400 e 800 Hz.
4. Compara sinais de entrada e saida.
5. Mostra a resposta ao impulso e estima o atraso.

Instalacao:
    python -m pip install numpy scipy matplotlib

Execucao:
    python test_fir_emg.py
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# ============================================================
# 1. ESPECIFICACOES E COEFICIENTES REAIS DO T-FILTER
# ============================================================

FS = 2000.0  # Hz
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

# Frequencias a testar (Hz)
TEST_FREQUENCIES = [100.0, 400.0, 800.0]

# ============================================================
# 2. FUNCOES AUXILIARES
# ============================================================

def measure_sine_amplitude(x, frequency, fs, start_time=0.1):
    """
    Estima a amplitude de uma sinusoidal por ajuste least-squares:
    x(t) = A*sin(2*pi*f*t) + B*cos(2*pi*f*t) + C.

    Ignora o transitório inicial do filtro.
    """
    x = np.asarray(x, dtype=float)
    time = np.arange(len(x)) / fs
    mask = time >= start_time

    if np.count_nonzero(mask) < 3:
        raise ValueError("Sinal demasiado curto para medir a amplitude.")

    t_valid = time[mask]
    x_valid = x[mask]

    matrix = np.column_stack((
        np.sin(2 * np.pi * frequency * t_valid),
        np.cos(2 * np.pi * frequency * t_valid),
        np.ones_like(t_valid)
    ))

    coeffs, *_ = np.linalg.lstsq(matrix, x_valid, rcond=None)
    return float(np.hypot(coeffs[0], coeffs[1]))


def db(value):
    """Converte uma amplitude positiva para dB."""
    return 20 * np.log10(max(float(value), 1e-15))


# ============================================================
# 3. VALIDACAO DOS COEFICIENTES
# ============================================================

number_of_taps = len(TAPS)
group_delay_samples = (number_of_taps - 1) / 2
group_delay_seconds = group_delay_samples / FS

print("=" * 60)
print("VALIDACAO DOS COEFICIENTES")
print("=" * 60)
print(f"Numero de taps: {number_of_taps}")
print(f"Soma dos coeficientes (ganho DC): {np.sum(TAPS):.8f}")
print(f"Erro maximo de simetria: {np.max(np.abs(TAPS - TAPS[::-1])):.3e}")
print(f"Atraso de grupo: {group_delay_samples:.1f} amostras")
print(f"Atraso de grupo: {group_delay_seconds * 1000:.3f} ms")

if number_of_taps != 41:
    print("AVISO: eram esperados 41 coeficientes segundo SampleFilter.h.")

# ============================================================
# 4. RESPOSTA EM FREQUENCIA
# ============================================================

frequencies, response = signal.freqz(TAPS, worN=16384, fs=FS)
magnitude_db = 20 * np.log10(np.maximum(np.abs(response), 1e-12))

passband = frequencies <= 500
stopband = frequencies >= 600

passband_db = magnitude_db[passband]
stopband_db = magnitude_db[stopband]

# Ripple peak-to-peak na banda passante
passband_ripple_pp = np.max(passband_db) - np.min(passband_db)
# Atenuacao minima na banda de rejeicao, referida a 0 dB
stopband_max_db = np.max(stopband_db)
stopband_attenuation = -stopband_max_db

print("\n" + "=" * 60)
print("RESPOSTA EM FREQUENCIA")
print("=" * 60)
print(f"Ripple pico-a-pico medido (0-500 Hz): {passband_ripple_pp:.4f} dB")
print(f"Maior nivel na banda de rejeicao (600-1000 Hz): {stopband_max_db:.4f} dB")
print(f"Atenuacao minima medida na banda de rejeicao: {stopband_attenuation:.4f} dB")

plt.figure(figsize=(10, 5))
plt.plot(frequencies, magnitude_db, label="Resposta do FIR")
plt.axvline(500, linestyle="--", label="Fim da banda passante: 500 Hz")
plt.axvline(600, linestyle="--", label="Inicio da banda de rejeicao: 600 Hz")
plt.axhline(-40, linestyle=":", label="Atenuacao pretendida: -40 dB")
plt.xlim(0, FS / 2)
plt.ylim(-100, 5)
plt.xlabel("Frequencia (Hz)")
plt.ylabel("Magnitude (dB)")
plt.title("Resposta em frequencia do filtro FIR EMG")
plt.grid(True)
plt.legend()
plt.tight_layout()

# ============================================================
# 5. RESPOSTA AO IMPULSO
# ============================================================

impulse = np.zeros(150)
impulse[0] = 1.0
impulse_output = signal.lfilter(TAPS, [1.0], impulse)

plt.figure(figsize=(10, 4))
plt.stem(np.arange(number_of_taps), TAPS)
plt.xlabel("Indice da amostra n")
plt.ylabel("h[n]")
plt.title("Resposta ao impulso / coeficientes FIR")
plt.grid(True)
plt.tight_layout()

# ============================================================
# 6. TESTES COM SINUSOIDAIS DE 100, 400 E 800 HZ
# ============================================================

duration = 1.0  # segundos
time = np.arange(int(FS * duration)) / FS
input_amplitude = 1.0

print("\n" + "=" * 60)
print("TESTES COM SINUSOIDAIS")
print("=" * 60)

results = []

for test_frequency in TEST_FREQUENCIES:
    x = input_amplitude * np.sin(2 * np.pi * test_frequency * time)

    # Equivalente matematico ao FIR: y[n] = sum(h[k] * x[n-k])
    y = signal.lfilter(TAPS, [1.0], x)

    amplitude_in = measure_sine_amplitude(x, test_frequency, FS)
    amplitude_out = measure_sine_amplitude(y, test_frequency, FS)
    gain_db = db(amplitude_out / amplitude_in)

    results.append((test_frequency, amplitude_in, amplitude_out, gain_db))

    print(f"\nFrequencia: {test_frequency:.0f} Hz")
    print(f"Amplitude de entrada: {amplitude_in:.6f}")
    print(f"Amplitude de saida:   {amplitude_out:.6f}")
    print(f"Ganho medido:         {gain_db:.2f} dB")

    # Grafico temporal: mostra 40 ms apos o transitório inicial
    plot_start = 0.10
    plot_end = 0.14
    plot_mask = (time >= plot_start) & (time <= plot_end)

    plt.figure(figsize=(10, 4))
    plt.plot(time[plot_mask], x[plot_mask], label="Entrada")
    plt.plot(time[plot_mask], y[plot_mask], label="Saida filtrada")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Amplitude")
    plt.title(f"Entrada e saida do FIR - {test_frequency:.0f} Hz")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

# ============================================================
# 7. RESUMO DOS RESULTADOS
# ============================================================

print("\n" + "=" * 60)
print("RESUMO")
print("=" * 60)
print(f"{'Frequencia':>12} | {'Ganho (dB)':>12} | Interpretacao")
print("-" * 48)

for frequency, _, _, gain in results:
    if frequency <= 500:
        interpretation = "Banda passante"
    elif frequency >= 600:
        interpretation = "Banda de rejeicao"
    else:
        interpretation = "Banda de transicao"

    print(f"{frequency:>9.0f} Hz | {gain:>10.2f} dB | {interpretation}")

plt.show()


