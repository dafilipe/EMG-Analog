
#define IIR_SECTIONS 7

// Butterworth passa-baixo
// Ordem: 13
// Fs: 2000 Hz
// Frequencia natural: 516.535065 Hz
//
// Formato: b0, b1, b2, a0, a1, a2

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

// Estados internos das 7 secoes
double iir_z1[IIR_SECTIONS] = {0.0};
double iir_z2[IIR_SECTIONS] = {0.0};


// Inicializar filtro
void iir_init()
{
    for (int i = 0; i < IIR_SECTIONS; i++)
    {
        iir_z1[i] = 0.0;
        iir_z2[i] = 0.0;
    }
}


// Aplicar filtro a uma amostra
double iir_filter(double input)
{
    double output = input;

    for (int i = 0; i < IIR_SECTIONS; i++)
    {
        double b0 = iir_sos[i][0];
        double b1 = iir_sos[i][1];
        double b2 = iir_sos[i][2];

        double a1 = iir_sos[i][4];
        double a2 = iir_sos[i][5];

        // Direct Form II Transposed
        double y = b0 * output + iir_z1[i];

        iir_z1[i] = b1 * output - a1 * y + iir_z2[i];
        iir_z2[i] = b2 * output - a2 * y;

        output = y;
    }

    return output;
}
