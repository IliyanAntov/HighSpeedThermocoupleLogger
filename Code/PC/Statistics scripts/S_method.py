import math
import os
import statistics
import warnings

import numpy as np
import plotly.graph_objs as go
import plotly.express as px

from PC.MeasurementData.LogData import Record, Channel
import PC.MeasurementData.Parameters as Parameters
import jsonpickle as jsonpickle

show_all_traces = False
use_pred_data = True
# log_folders = ["../logs/test_logs"]
# log_folders = ["../logs/04_Second tests with impedance data/Proper"]
log_folders = [
    "../logs/04_Second tests with impedance data/Proper",
    "../logs/10_Large_sample_sizes/Bobi",
    "../logs/10_Large_sample_sizes/Bobi 2",
    "../logs/10_Large_sample_sizes/Iliyan"
]
tpred_log_folder = "./Tpred_logs"
logger_temp_time_offset = 0
dt_ms = 10

x_bounds = [0, 4000]
y_bounds = [0, 120]

w_values = []
s_values = []
tmax_values = []

if __name__ == '__main__':
    interp_plot_list = []
    for log_folder in log_folders:
        log_names = os.listdir(log_folder)
        tpred_log_names = os.listdir(tpred_log_folder)
        for log_name in log_names:
            if use_pred_data:
                selected_log_folder = tpred_log_folder
            else:
                selected_log_folder = log_folder

            with open(selected_log_folder + "/" + log_name) as log_file:
                file_raw = log_file.read()
                if not use_pred_data:
                    file_raw = file_raw.replace("MeasurementData.", "PC.MeasurementData.")
                record = jsonpickle.decode(file_raw)

            try:
                z_values = record.generator_raw_data["Z"]
            except AttributeError:
                z_values = record.impedance_raw_data
            except KeyError:
                continue

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
            for time_value_gen in time_values_gen:
                while time_values_temp[temp_index] < time_value_gen + logger_temp_time_offset:
                    temp_index += 1
                while time_values_temp[temp_index] < (time_value_gen + logger_temp_time_offset + 1):
                    current_average_list.append(temp_values[temp_index])
                    temp_index += 1

                temp_values_gen.append(statistics.fmean(current_average_list))
                current_average_list = []

            # NOTE: Temp = f(S)
            first_z_value = z_values[0]
            w_ms = None
            for i in range(len(z_values)):
                if z_values[i] > first_z_value:
                    w_ms = i
                    break
            if not w_ms:
                continue

            dz_ohm = z_values[w_ms + dt_ms] - z_values[w_ms]
            s_ohm_div_ms = dz_ohm / dt_ms

            tmax_at_w_degC = max(temp_values_gen[w_ms:(w_ms+dt_ms)])

            w_values.append(w_ms)
            s_values.append(s_ohm_div_ms)
            tmax_values.append(tmax_at_w_degC)

    # NOTE: Linear trendline
    # fig = px.scatter(x=s_values, y=tmax_values, trendline="ols")
    # NOTE: LOWESS trendline
    fig = px.scatter(x=s_values, y=tmax_values, trendline="lowess")

    fig_title = f"T{'pred' if use_pred_data else 'real'}(max)@W{'(+'+ str(logger_temp_time_offset) +'ms)' if logger_temp_time_offset > 0 else ''} = f(S)"
    fig.update_layout(xaxis_title="S[Ohm/ms]",
                      yaxis_title=f"T_{'pred' if use_pred_data else 'real'}[°C]",
                      title=fig_title
                      )

    fig.show()
