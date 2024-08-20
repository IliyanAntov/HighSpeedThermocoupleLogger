import math
import os
import statistics
import warnings

import numpy as np
from matplotlib import pyplot as plt
import plotly.graph_objs as go
from scipy.interpolate import InterpolatedUnivariateSpline

from PC.MeasurementData.LogData import Record, Channel
import PC.MeasurementData.Parameters as Parameters
import jsonpickle as jsonpickle

show_all_traces = False
log_folders = ["../logs/test_logs"]
logger_temp_time_offset = 7
end_values_to_skip = 5

ez_interp_bounds = {
    "min": 0,
    "max": 5000,
    "n": 1000
}

temp_interp_bounds = {
    "min": 20,
    "max": 120,
    "n": 1000
}

fig = go.Figure()

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

            # NOTE: E*Z = f(Temp)
            # plt.plot(temp_values_gen, ez_values)
            # values_for_interp = np.linspace(temp_interp_bounds["min"], temp_interp_bounds["max"], temp_interp_bounds["n"])
            # if end_values_to_skip > 0:
            #     values_interp = np.interp(values_for_interp, temp_values_gen[:-end_values_to_skip],
            #                             ez_values[:-end_values_to_skip], left=np.NaN, right=np.NaN)
            # else:
            #     values_interp = np.interp(values_for_interp, temp_values_gen,
            #                               ez_values, left=np.NaN, right=np.NaN)
            #
            # interp_plot_list.append(values_interp)

            # NOTE: Temp = f(E*Z)
            if show_all_traces:
                # plt.plot(ez_values, temp_values_gen)
                fig.add_trace(go.Scatter(x=ez_values,
                                         y=temp_values_gen,
                                         name=log_name.replace(".json", ""),
                                         hoverinfo="skip"))

            values_for_interp = np.linspace(ez_interp_bounds["min"], ez_interp_bounds["max"], ez_interp_bounds["n"])
            if end_values_to_skip > 0:
                values_interp = np.interp(values_for_interp,
                                          ez_values[:-end_values_to_skip],
                                          temp_values_gen[:-end_values_to_skip],
                                          left=np.NaN,
                                          right=np.NaN)
            else:
                values_interp = np.interp(values_for_interp,
                                          ez_values,
                                          temp_values_gen,
                                          left=np.NaN,
                                          right=np.NaN)

            interp_plot_list.append(values_interp)

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=RuntimeWarning)
    mean_plot = np.nanmean(interp_plot_list, axis=0)
    confidence_5percent = np.nanpercentile(interp_plot_list, 5, axis=0)
    confidence_95percent = np.nanpercentile(interp_plot_list, 95, axis=0)

# NOTE: matplotlib version
# plt.plot(values_for_interp, mean_plot, linestyle="--", linewidth=3, color="red", label="Mean")
# plt.fill_between(values_for_interp, confidence_5percent, confidence_95percent, alpha=0.5, label='5% and 95% confidence interval')
#
# ez_value = 2500
# temp_low = np.interp(ez_value, values_for_interp, confidence_5percent)
# temp_high = np.interp(ez_value, values_for_interp, confidence_95percent)
# temp_mean = np.interp(ez_value, values_for_interp, mean_plot)
# print(f"Low: {temp_low:.2f}°C")
# print(f"Mean: {temp_mean:.2f}°C")
# print(f"High: {temp_high:.2f}°C")
# print(f"\nInterval size: {temp_high-temp_low:.2f}°C")
#
# plt.minorticks_on()
# plt.grid(visible=True, which="both")
# plt.legend()
# plt.show()

# NOTE: pyplot version
fig.add_trace(go.Scatter(name='Mean',
                         x=values_for_interp,
                         y=mean_plot,
                         mode='lines',
                         line=dict(color='red', width=5, dash="dash")
                         )
              )

fig.add_trace(go.Scatter(name='High',
                         x=values_for_interp,
                         y=confidence_95percent,
                         mode='lines',
                         marker=dict(color="#444"),
                         line=dict(width=0),
                         showlegend=False
                         )
              )

fig.add_trace(go.Scatter(name='Low',
                         x=values_for_interp,
                         y=confidence_5percent,
                         marker=dict(color="#444"),
                         line=dict(width=0),
                         mode='lines',
                         fillcolor='rgba(68, 68, 68, 0.3)',
                         fill='tonexty',
                         showlegend=False
                         )
              )

fig.update_layout(xaxis_title="E*Z",
                  yaxis_title='Temp[°C]',
                  title='Temp = f(E*Z)',
                  hovermode="x"
                  )

fig.show()
