import math
import os
import statistics
import warnings

import jsonpickle as jsonpickle
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.graph_objs as go

import matplotlib.pyplot as plt
import plotly.express as px
import warnings
from sklearn.model_selection import train_test_split, LeaveOneGroupOut
from sklearn.metrics import mean_squared_error, root_mean_squared_error
import xgboost as xgb

from PC.MeasurementData.LogData import Record, Channel
import PC.MeasurementData.Parameters as Parameters


use_pred_data = False
# log_folders = ["../logs/test_logs"]
log_folders = ["../logs/04_Second tests with impedance data/Proper"]
tpred_log_folder = "./Tpred_logs"
logger_temp_time_offset = 0


if __name__ == '__main__':
    df_full = pd.DataFrame()

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

            df_current = pd.DataFrame.from_dict(record.generator_raw_data)
            df_current["t"] = time_values_gen
            df_current["Temp"] = temp_values_gen
            df_current["measurement_id"] = log_name.replace(".json", "")

            df_full = pd.concat([df_full, df_current], ignore_index=True)

    # NOTE: ML algorithm
    df_validation = df_full[df_full["measurement_id"] == "Bobi_nov 3"]
    X_validation = df_validation.drop(columns=["measurement_id", "Temp"])
    y_validation = df_validation["Temp"]

    df_training = df_full[df_full["measurement_id"] != "Bobi_nov 3"]
    X = df_training.drop(columns=["measurement_id", "Temp"])
    y = df_training["Temp"]
    groups = df_training["measurement_id"]
    logo = LeaveOneGroupOut()

    rmse_min = -1
    chosen_model = None
    for i, (train_indices, test_indices) in enumerate(logo.split(X=X, y=None, groups=groups)):
        X_train = X.iloc[train_indices]
        X_test = X.iloc[test_indices]
        y_train = y.iloc[train_indices]
        y_test = y.iloc[test_indices]

        # Create regression matrices
        dtrain_reg = xgb.DMatrix(X_train, y_train)
        dtest_reg = xgb.DMatrix(X_test, y_test)

        # Define hyperparameters
        params = {"objective": "reg:squarederror", "tree_method": "hist", "device": "cuda"}

        evals = [(dtrain_reg, "train"), (dtest_reg, "validation")]

        n = 10000
        model = xgb.train(
           params=params,
           dtrain=dtrain_reg,
           num_boost_round=n,
           evals=evals,
           verbose_eval=5,  # Every ten rounds
           early_stopping_rounds=50
        )

        y_pred = model.predict(dtest_reg)
        rmse = root_mean_squared_error(y_test, y_pred)
        if rmse_min == -1 or rmse < rmse_min:
            rmse_min = rmse
            chosen_model = model

    # Validation
    y_pred_validation = chosen_model.predict(xgb.DMatrix(X_validation, y_validation))
    rmse_validation = root_mean_squared_error(y_validation, y_pred_validation)
    print(f"Validation RMSE: {rmse_validation}")

    df_ytest = pd.DataFrame()
    df_ytest["t"] = df_validation["t"]
    df_ytest["Temp"] = df_validation["Temp"]
    df_ytest["Designator"] = "Actual data"
    df_ypred = pd.DataFrame()
    df_ypred["t"] = df_validation["t"]
    df_ypred["Temp"] = y_pred_validation
    df_ypred["Designator"] = "Predicted data"
    df_plot = pd.concat([df_ytest, df_ypred], ignore_index=True)
    # print(df_plot)
    fig = px.line(df_plot, x="t", y="Temp", color="Designator")
    fig.show()
