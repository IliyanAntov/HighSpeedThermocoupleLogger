import copy
import math
import multiprocessing
import os
import time
from functools import partial
from multiprocessing import Pool

import numpy as np
from scipy import signal
from scipy.optimize import curve_fit

import jsonpickle as jsonpickle

# log_folders = ["../logs/test_logs"]
log_folders = [
    # "../logs/04_Second tests with impedance data/Proper",
    "../logs/10_Large_sample_sizes/Bobi",
    "../logs/10_Large_sample_sizes/Iliyan"
]
tpred_log_folder = "./Tpred_logs"


# Converting records to predicted temperature
def heating_function(x, t_env, tau_ms, t_0):
    return t_env + ((t_0 - t_env) * np.exp(-(1 / (tau_ms / 1000)) * x))


def calculate_predicted_data(x_data, y_data, channel_parameters):
    x_short_ms = x_data[:channel_parameters.prediction_queue_length]
    x_short = list((x * 10 ** (-3)) for x in x_short_ms)
    y_short = y_data[:channel_parameters.prediction_queue_length]

    y_sets = []
    for data_point in y_data[channel_parameters.prediction_queue_length:]:
        y_sets.append(copy.copy(y_short))

        y_short.pop(0)
        y_short.append(data_point)

    pool = Pool(processes=multiprocessing.cpu_count())
    predictions = pool.map(partial(calculate_predicted_data_point, x_short, channel_parameters),
                           y_sets)

    return predictions


def calculate_predicted_data_point(x_data, channel_parameters, y_data):
    t_0 = y_data[0]
    heating_function_fixed_params = partial(heating_function,
                                            tau_ms=channel_parameters.prediction_time_constant_ms,
                                            t_0=t_0)
    param, param_cov = curve_fit(heating_function_fixed_params, x_data, y_data)
    return param[0]


def apply_low_pass_filter(data, order, corner_frequency_khz, cutoff_freq_khz):
    nyquist_freq_khz = cutoff_freq_khz / 2
    b, a = signal.butter(N=order, Wn=corner_frequency_khz / nyquist_freq_khz)
    data_filtered = signal.filtfilt(b, a, data)
    return data_filtered.tolist()


if __name__ == '__main__':
    interp_plot_list = []
    for log_folder in log_folders:
        log_names = os.listdir(log_folder)
        for log_name in log_names:
            print(f"Converting log {log_name}...")
            with open(log_folder + "/" + log_name) as log_file:
                file_raw = log_file.read()
                file_raw = file_raw.replace("MeasurementData.", "PC.MeasurementData.")
                record = jsonpickle.decode(file_raw)

                for i in range(len(record.channels)):
                    if not record.channels[i].available:
                        continue

                    actual_temperature = record.channels[i].raw_data
                    cutoff_freq_khz = (1 / record.interval_us) * 1000
                    actual_temperature_filtered = apply_low_pass_filter(actual_temperature,
                                                                        record.channels[i].data_filter_order,
                                                                        record.channels[i].data_filter_freq_khz,
                                                                        cutoff_freq_khz)

                    x_values = np.linspace(0, record.length_ms, int(record.length_ms / (record.interval_us / 1000)))
                    x_values = np.round(x_values, math.ceil(math.log10(1000 / record.interval_us)))

                    prediction_values = calculate_predicted_data(x_values, actual_temperature_filtered, record.channels[i])
                    record.channels[i].raw_data = prediction_values

                    jsonpickle.set_encoder_options('json', indent=4)
                    output_json = jsonpickle.encode(record)
                    print(f"Saving log {log_name}...")
                    with open(str(tpred_log_folder + "/" + log_name), "w") as output_file:
                        output_file.writelines(output_json)

    print("Done")