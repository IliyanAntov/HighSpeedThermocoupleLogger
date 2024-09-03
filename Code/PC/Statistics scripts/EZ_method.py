import math
import os
import statistics
import warnings

import numpy as np
import plotly.graph_objs as go

from PC.MeasurementData.LogData import Record, Channel
import PC.MeasurementData.Parameters as Parameters
import jsonpickle as jsonpickle

show_all_traces = True
use_pred_data = False
# log_folders = ["../logs/test_logs"]
log_folders = ["../logs/04_Second tests with impedance data/Proper"]
tpred_log_folder = "./Tpred_logs"
logger_temp_time_offset = 8
end_values_to_skip = 5

x_bounds = [0, 4000]
y_bounds = [0, 120]

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

fig = go.Figure(layout_yaxis_range=y_bounds, layout_xaxis_range=x_bounds)


if __name__ == '__main__':
    temp_values_interp_all = []
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
            except (AttributeError, KeyError):
                continue
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
            for time_value_gen in time_values_gen:
                while time_values_temp[temp_index] < time_value_gen + logger_temp_time_offset:
                    temp_index += 1
                while time_values_temp[temp_index] < (time_value_gen + logger_temp_time_offset + 1):
                    current_average_list.append(temp_values[temp_index])
                    temp_index += 1

                temp_values_gen.append(statistics.fmean(current_average_list))
                current_average_list = []

            # NOTE: Temp = f(E*Z)
            if show_all_traces:
                fig.add_trace(go.Scatter(x=ez_values,
                                         y=temp_values_gen,
                                         name=log_name.replace(".json", ""),
                                         hoverinfo="skip"))

            values_for_interp = np.linspace(ez_interp_bounds["min"], ez_interp_bounds["max"], ez_interp_bounds["n"])
            if end_values_to_skip > 0:
                temp_values_interp = np.interp(values_for_interp,
                                               ez_values[:-end_values_to_skip],
                                               temp_values_gen[:-end_values_to_skip],
                                               left=np.nan,
                                               right=np.nan)
            else:
                temp_values_interp = np.interp(values_for_interp,
                                               ez_values,
                                               temp_values_gen,
                                               left=np.nan,
                                               right=np.nan)

            temp_values_interp_all.append(temp_values_interp)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        mean_plot = np.nanmean(temp_values_interp_all, axis=0)
        confidence_5percent = np.nanpercentile(temp_values_interp_all, 5, axis=0)
        confidence_95percent = np.nanpercentile(temp_values_interp_all, 95, axis=0)

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

    fig_title = f"T_{'pred' if use_pred_data else 'real'}{'(+'+ str(logger_temp_time_offset) +'ms)' if logger_temp_time_offset > 0 else ''} = f(E*Z)"
    fig.update_layout(xaxis_title="E*Z",
                      yaxis_title='Temp[°C]',
                      title=fig_title,
                      hovermode="x"
                      )

    fig.show()
