import math
import os
import statistics

import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import InterpolatedUnivariateSpline

from PC.MeasurementData.LogData import Record, Channel
import PC.MeasurementData.Parameters as Parameters
import jsonpickle as jsonpickle

log_folders = ["../logs/test_logs"]
logger_temp_time_offset = 7

interp_plot_list = []
for log_folder in log_folders:
    log_names = os.listdir(log_folder)
    for log_name in log_names:
        with open(log_folder + "/" + log_name) as log_file:
            file_raw = log_file.read()
            file_raw = file_raw.replace("MeasurementData.", "PC.MeasurementData.")
            record = jsonpickle.decode(file_raw)

            z_values = record.generator_raw_data["Z"]
            p_values = record.generator_raw_data["P"]
            e_values = []
            ez_values = []
            for i in range(len(p_values)):
                if len(e_values) == 0:
                    e_value = p_values[i]/1000
                else:
                    e_value = e_values[i-1] + p_values[i]/1000  # /1000 because time is in ms

                e_values.append(e_value)

                ez_value = e_value * z_values[i]
                ez_values.append(ez_value)

            time_values_gen = list(range(Parameters.generator_log_start_time_ms,
                                         Parameters.generator_log_start_time_ms + len(z_values),
                                         Parameters.generator_log_interval_ms))

            temp_values = record.channels[0].raw_data
            time_values_temp = np.linspace(0, record.length_ms,
                                           int(record.length_ms / (record.interval_us / 1000)))
            time_values_temp = np.round(time_values_temp, math.ceil(math.log10(1000 / record.interval_us)))

            temp_values_gen = []
            current_average_list = []
            temp_index = 0
            for gen_time_value in time_values_gen:
                while time_values_temp[temp_index] < gen_time_value + logger_temp_time_offset:
                    temp_index += 1
                while time_values_temp[temp_index] < (gen_time_value + logger_temp_time_offset + 1):
                    current_average_list.append(temp_values[temp_index])
                    temp_index += 1

                temp_values_gen.append(statistics.fmean(current_average_list))
                current_average_list = []
            # print(temp_values_gen)
            # temp_values = np.interp()

            # print(ez_values)
            plt.plot(ez_values, temp_values_gen)

            ez_values_for_interp = np.linspace(0, 5000, 1000)
            temp_interp = np.interp(ez_values_for_interp, ez_values, temp_values_gen)
            interp_plot_list.append(temp_interp)

combined_plot = np.mean(interp_plot_list, axis=0)
plt.plot(ez_values_for_interp, combined_plot, linestyle="--", linewidth=3, color="red")
# plt.figure()

# plt.figure()
# plt.plot(temp_values_for_interp, interp_plt)
# print(interp_plt)
plt.show()
