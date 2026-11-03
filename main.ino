
#include <Arduino.h>

// ==================================================
// EMS LAB #2 - EMG DIGITAL FILTERING
// Raspberry Pi Pico 2 W
// ==================================================

// 1. CONFIGURACAO

#define ADC_PIN 26              // GP26 - ADC0
#define DAC_PIN 15              // GP15 - PWM (saida analogica)

#define FIR_TAP_NUM 41
#define IIR_SECTIONS 7

#define ADC_MAX_VALUE 4095.0
#define ADC_REFERENCE 3.3

#define SAMPLE_PERIOD_US 500    // Fs = 2000 Hz

uint32_t lastSampleMicros = 0;


// 2. VETORES DE ENTRADA E SAIDA

double x[FIR_TAP_NUM] = {0.0};

double y[2] = {0.0, 0.0};

// y[0] = FIR
// y[1] = IIR


// ==================================================
// 3. FILTRO FIR - 41 TAPS
// ==================================================

const double fir_coefficients[FIR_TAP_NUM] = {
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
};


// ==================================================
// 4. FILTRO IIR - BUTTERWORTH ORDEM 13
// Fs = 2000 Hz
// 7 SECOES SOS
// ==================================================

const double iir_sos[IIR_SECTIONS][6] = {

    {
        0.0007042301941195593,
        0.001408460388239119,
        0.0007042301941195593,
        1.0,
        0.02597906164895776,
        0.0
    },

    {
        1.0, 2.0, 1.0,
        1.0,
        0.05272363277124318,
        0.01541805623759816
    },

    {
        1.0, 2.0, 1.0,
        1.0,
        0.05511238904813538,
        0.06142373012641150
    },

    {
        1.0, 2.0, 1.0,
        1.0,
        0.05942551982097117,
        0.1444914292861744
    },

    {
        1.0, 2.0, 1.0,
        1.0,
        0.06625806197477792,
        0.2760811227179961
    },

    {
        1.0, 2.0, 1.0,
        1.0,
        0.07668866632741676,
        0.4769668250195441
    },

    {
        1.0, 1.0, 0.0,
        1.0,
        0.09268882674051430,
        0.7851180454911892
    }
};


// Estados internos do IIR

double iir_z1[IIR_SECTIONS] = {0.0};
double iir_z2[IIR_SECTIONS] = {0.0};


// ==================================================
// 5. INICIALIZACAO DO IIR
// ==================================================

void iir_init()
{
    for (int i = 0; i < IIR_SECTIONS; i++)
    {
        iir_z1[i] = 0.0;
        iir_z2[i] = 0.0;
    }
}


// ==================================================
// 6. FUNCAO DO FILTRO IIR
// DIRECT FORM II TRANSPOSED
// ==================================================

double iir_filter(double input)
{
    double output = input;

    for (int i = 0; i < IIR_SECTIONS; i++)
    {
        double b0 = iir_sos[i][0];
        double b1 = iir_sos[i][1];
        double b2 = iir_sos[i][2];

        double a0 = iir_sos[i][3];
        double a1 = iir_sos[i][4];
        double a2 = iir_sos[i][5];

        double temp = (b0 / a0) * output + iir_z1[i];

        iir_z1[i] = (b1 / a0) * output
                    - (a1 / a0) * temp
                    + iir_z2[i];

        iir_z2[i] = (b2 / a0) * output
                    - (a2 / a0) * temp;

        output = temp;
    }

    return output;
}


// ==================================================
// 7. SETUP
// ==================================================

void setup()
{
    Serial.begin(921600);

    // Configurar ADC para 12 bits
    analogReadResolution(12);

    // Configurar PWM como saida analogica
    analogWriteResolution(12);
    analogWriteFreq(20000);
    pinMode(DAC_PIN, OUTPUT);

    // Inicializar IIR
    iir_init();

    // Inicializar temporizacao
    lastSampleMicros = micros();
}


// ==================================================
// 8. LOOP PRINCIPAL
// ==================================================

void loop()
{
    uint32_t now = micros();

    // Controlar periodo de amostragem
    if ((uint32_t)(now - lastSampleMicros) >= SAMPLE_PERIOD_US)
    {
        lastSampleMicros = now;


        // ------------------------------------------
        // A. AQUISICAO ADC
        // ------------------------------------------

        int adcValue = analogRead(ADC_PIN);

        x[0] = (double)adcValue * ADC_REFERENCE
               / ADC_MAX_VALUE;


        // ------------------------------------------
        // B. FILTRO FIR
        // ------------------------------------------

        y[0] = 0.0;

        for (int i = 0; i < FIR_TAP_NUM; i++)
        {
            y[0] += fir_coefficients[i] * x[i];
        }


        // ------------------------------------------
        // C. FILTRO IIR
        // ------------------------------------------

        y[1] = iir_filter(x[0]);


        // ------------------------------------------
        // D. SAIDA PWM (DAC SIMULADO)
        // ------------------------------------------

        // Selecionar a saida FIR
        double dacVoltage = y[0];

        // Para utilizar o IIR, substituir por:
        // double dacVoltage = y[1];

        // Limitar tensao a 0-3.3 V
        if (dacVoltage < 0.0)
            dacVoltage = 0.0;

        if (dacVoltage > 3.3)
            dacVoltage = 3.3;

        int dacValue = (int)(
            dacVoltage * 4095.0 / 3.3
        );

        analogWrite(DAC_PIN, dacValue);


        // ------------------------------------------
        // E. SERIAL PLOTTER
        // ------------------------------------------

        Serial.print(x[0], 5);
        Serial.print('\t');

        Serial.print(y[0], 5);
        Serial.print('\t');

        Serial.println(y[1], 5);


        // ------------------------------------------
        // F. ATUALIZACAO DO HISTORICO FIR
        // ------------------------------------------

        for (int i = FIR_TAP_NUM - 2; i >= 0; i--)
        {
            x[i + 1] = x[i];
        }
    }
}
