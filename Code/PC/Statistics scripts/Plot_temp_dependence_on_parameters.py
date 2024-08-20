import math
import os
import statistics

import numpy as np
import pandas as pd

from PC.MeasurementData.LogData import Record, Channel
import PC.MeasurementData.Parameters as Parameters
import jsonpickle as jsonpickle
import plotly.express as px

# log_folders = ["../logs/test_logs"]
log_folders = [r"..\logs\04_Second tests with impedance data\Proper"]
logger_temp_time_offset = 0

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

df_full = None

for log_folder in log_folders:
    log_names = os.listdir(log_folder)
    for log_name in log_names:
        with open(log_folder + "/" + log_name) as log_file:
            file_raw = log_file.read()
            file_raw = file_raw.replace("MeasurementData.", "PC.MeasurementData.")
            record = jsonpickle.decode(file_raw)

            try:
                z_values = record.generator_raw_data["Z"]
            except AttributeError as e:
                z_values = record.impedance_raw_data

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

            try:
                df_current = pd.DataFrame.from_dict(record.generator_raw_data)
            except AttributeError:
                df_current = pd.DataFrame.from_dict({"Z": record.impedance_raw_data})
            name_map = Parameters.excel_column_names
            df_current.rename(columns=name_map, inplace=True)
            df_current.insert(0, "Time[ms]", pd.Series(time_values_gen))
            df_current.insert(1, "Temp[°C]", pd.Series(temp_values_gen))
            df_current.insert(0, "Name", log_name.replace(".json", ""))
            if df_full is None:
                df_full = df_current
            else:
                df_full = pd.concat([df_full, df_current], ignore_index=True)

for column_name, column_values in df_full.items():
    if "Name" in column_name or "Temp" in column_name:
        continue

    fig = px.line(df_full, x=column_name, y="Temp[°C]", color="Name")
    fig.show()

