import json

import numpy as np
from scipy import signal
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt


tau_ms = 133.6
t_0 = 0
temperature_queue_length = 5
sample_period_us = 20

filter_order = 3
osc_data_cutoff_freq_khz = 0.1
calculate_predictions = True
# calculate_predictions = False

# prediction_cutoff_freq_khz = 24.99999


def read_data():
    f = open("./data/oscilloscope_data.json", "r")
    osc_data = json.load(f)
    f.close()

    x_data = osc_data["x_values"]
    y_data = osc_data["y_values"]

    return x_data, y_data


# K type thermocouple
def calculate_thermocouple_temperature(tc_voltage):

    tc_voltage_uv = tc_voltage * 10**6
    coefficients = [0,
                    2.508355 * 10**(-2),
                    7.860106 * 10**(-8),
                    -2.503131 * 10**(-10),
                    8.315270 * 10**(-14),
                    -1.228034 * 10**(-17),
                    9.804036 * 10**(-22),
                    -4.413030 * 10**(-26),
                    1.057734 * 10**(-30),
                    -1.052755 * 10**(-35)
                    ]

    temperature = 0
    for i in range(len(coefficients)):
        temperature += coefficients[i] * (tc_voltage_uv**i)

    return temperature


def heating_function(x, t_env):
    return t_env + ((t_0 - t_env)*np.exp(-(1/(tau_ms/1000))*x))


def calculate_predicted_data(x_data, y_data):

    x_short = x_data[:temperature_queue_length]
    y_short = y_data[:temperature_queue_length]
    predictions = []

    for data_point in y_data[temperature_queue_length:]:
        global t_0
        t_0 = y_short[0]
        param, param_cov = curve_fit(heating_function, x_short, y_short)
        predictions.append(param[0])

        y_short.pop(0)
        y_short.append(data_point)

    predictions += [predictions[-1]]*temperature_queue_length

    data_json = {
        "x_values": x_data,
        "y_values": predictions
    }

    write_predicted_data(data_json)


def write_predicted_data(data_json):
    f = open("./data/predicted_data.json", "w")
    json.dump(data_json, f)
    f.close()


def read_predicted_data():
    f = open("./data/predicted_data.json", "r")
    predicted_data = json.load(f)
    f.close()

    return predicted_data["x_values"], predicted_data["y_values"]


def apply_filter(y_data, filter_corner_frequency_khz):

    cutoff_freq = (1/sample_period_us) * 1000
    nyquist_freq = cutoff_freq / 2
    b, a = signal.butter(N=filter_order, Wn=filter_corner_frequency_khz/nyquist_freq)

    y_data_filt = signal.filtfilt(b, a, y_data)

    return y_data_filt


def main():
    time_array, voltage_array = read_data()

    # TC voltage = Measured voltage / Amplifier gain = y/199
    # Voltage at 23°C = 0.879 mV
    # TC measurement voltage = TC voltage + TC room temp = y/199 + 0.000879
    x_data = time_array
    # x_data = x_data[22500:]
    # x_data = [x - x_data[0] for x in x_data]
    # voltage_array = voltage_array[22500:]

    y_data = [calculate_thermocouple_temperature(voltage / 199 + 0.000879) for voltage in voltage_array]
    y_data = list(apply_filter(y_data, filter_corner_frequency_khz=osc_data_cutoff_freq_khz))

    if calculate_predictions:
        calculate_predicted_data(x_data, y_data)

    x_data, predictions = read_predicted_data()

    # predictions_filt = apply_filter(predictions, filter_corner_frequency_khz=prediction_cutoff_freq_khz)

    plt.plot(x_data, predictions, color="blue")
    plt.plot(x_data, y_data, color="red")
    max_value = max(y_data)
    max_value_line = [max_value] * len(y_data)
    plt.plot(x_data, max_value_line, color="green")
    plt.show()


if __name__ == "__main__":
    main()