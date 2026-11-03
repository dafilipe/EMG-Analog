
%% EMS LAB 2 - Dimensionamento do Segundo Amplificador

clear; clc; close all;

% 1. ESPECIFICACOES

G_INA       = 100;       % Ganho da instrumentacao
Vin_pp      = 2e-3;       % EMG maximo na entrada da INA [Vpp]

Vref        = 1.65;       % Referencia DC [V]
Vcc         = 3.3;        % Alimentacao [V]

Vout_min_lim = 0.3;       % Limite inferior de projeto [V]
Vout_max_lim = 3.0;       % Limite superior de projeto [V]

fc_in       = 2;          % Corte inferior de entrada [Hz]

GBW         = 1e6;        % MCP6004: GBW tipico [Hz]
f_max       = 500;        % Frequencia maxima EMG [Hz]

% 2. GANHO NECESSARIO

% Excursao maxima simetrica em torno de Vref
Vout_pp_target = 2 * min(Vref - Vout_min_lim,Vout_max_lim - Vref);

% Ganho total da cadeia
Gtotal = Vout_pp_target / Vin_pp;

% Ganho necessario do segundo amplificador
Av_req = Gtotal / G_INA;

fprintf('--- GANHO ---\n');
fprintf('Ganho INA = %.2f\n', G_INA);
fprintf('Ganho total necessario = %.2f\n', Gtotal);
fprintf('Ganho necessario no segundo estagio = %.2f\n', Av_req);

% 3. DIMENSIONAMENTO DAS RESISTENCIAS

Rg = 10e3;

% Calcular Rf a partir do ganho pretendido
Rf_ideal = (Av_req - 1) * Rg;

% Selecionar valor comercial E12
Rf = e12(Rf_ideal);

Rb = 100e3;
Av = 1 + Rf/Rg;

fprintf('\n--- RESISTENCIAS ---\n');
fprintf('Rg = %.2f kOhm\n', Rg/1e3);
fprintf('Rf ideal = %.2f kOhm\n', Rf_ideal/1e3);
fprintf('Rf comercial = %.2f kOhm\n', Rf/1e3);
fprintf('Rb = %.2f kOhm\n', Rb/1e3);
fprintf('Ganho real = %.3f\n', Av);

%% 4. DIMENSIONAMENTO DE Cin

% Assume impedancia de saida da INA desprezavel
Cin_ideal = 1/(2*pi*Rb*fc_in);

% Valor comercial E12
Cin = e12(Cin_ideal);

% Frequencia de corte real
fc_in_real = 1/(2*pi*Rb*Cin);

fprintf('\n--- CONDENSADOR ---\n');
fprintf('Cin ideal = %.3f uF\n', Cin_ideal*1e6);
fprintf('Cin comercial = %.3f uF\n', Cin*1e6);
fprintf('fc entrada real = %.3f Hz\n', fc_in_real);



%% 10. FUNCAO AUXILIAR E12

function y = e12(x)

    E = [1.0 1.2 1.5 1.8 2.2 2.7 ...
         3.3 3.9 4.7 5.6 6.8 8.2];

    d = floor(log10(x));
    m = x/10^d;

    [~,i] = min(abs(log10(E)-log10(m)));

    y = E(i)*10^d;

end
