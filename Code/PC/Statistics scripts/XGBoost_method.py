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

from scipy.stats import linregress
from sklearn.model_selection import train_test_split, LeaveOneGroupOut, GroupKFold, GridSearchCV
from sklearn.metrics import mean_squared_error, root_mean_squared_error
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from tsfresh import extract_relevant_features
from xgboost import plot_importance, callback

from PC.MeasurementData.LogData import Record, Channel
import PC.MeasurementData.Parameters as Parameters

use_previous_df = True
save_df_to_file = False
# use_previous_df = False
# save_df_to_file = True

df_csv_path = "./training_data/df.csv"
model_path = "./training_data/model.json"

use_previous_model = True
# use_previous_model = False

logger_temp_time_offset = 0
# use_pred_data = True
use_pred_data = False
tpred_log_folder = "./Tpred_logs"

log_folders = [
    # "../logs/04_Second tests with impedance data/Proper",
    "../logs/10_Large_sample_sizes/Bobi",
    "../logs/10_Large_sample_sizes/Bobi 2",
    "../logs/10_Large_sample_sizes/Iliyan"
]


target_parameter = "Temp"

training_columns_to_drop = [
                            target_parameter,
                            "dTemp",
                            "measurement_name",
                            "t",
                            ]


validation_records = [
    "2024-09-04_15-48-31",
    "2024-09-04_15-50-57",
    "2024-09-04_16-03-55",
    "2024-09-04_15-58-46",
    "2024-09-04_16-00-17",
    # "2024-09-04_15-50-41",
    "2024-09-04_16-03-29"
]

# validation_records = [
#     "2024-09-04_16-00-11",  # Iliyan
#     "2024-09-04_16-03-33",
#     "2024-09-04_15-59-18",
#
#     "2024-09-04_15-48-28",  # Bobi
#     "2024-09-04_15-49-18",
#     "2024-09-04_15-49-55",
#
#     "2024-09-10_11-43-46",  # Bobi 2
#     "2024-09-10_11-46-48",
#     "2024-09-10_11-47-44",
# ]

# lagged_feature_lags = [1, 5, 10, 20]
# mean_feature_lens = [1, 5, 10, 20]
# slope_feature_lens = [1, 5, 10, 20]
lagged_feature_lags = [1, 3, 8, 15]
mean_feature_lens = [1, 3, 8, 15]
slope_feature_lens = [1, 3, 8, 15]


# Define custom loss function
def custom_loss_function(alpha=10.0, beta=1.0, p=6):
    """
    Custom asymmetric loss function that penalizes negative errors more than positive errors.
    Alpha: penalty for negative errors (y_true > y_pred).
    Beta: penalty for positive errors (y_true < y_pred).
    p: power to penalize large errors (default is cubic loss).
    """

    def _custom_loss(y_pred, dtrain):
        y_true = dtrain.get_label()  # Extract true labels from DMatrix
        residual = y_true - y_pred
        residual = np.where(y_true < 110, residual * 20, residual)
        # print(residual)

        # Gradient: the first derivative of the loss function
        grad = np.where(residual > 0, -alpha * np.power(residual, p - 1), -beta * np.power(residual, p - 1))

        # Hessian: the second derivative of the loss function
        hess = np.where(residual > 0, alpha * (p - 1) * np.power(residual, p - 2),
                        beta * (p - 1) * np.power(residual, p - 2))

        return grad, hess

    return _custom_loss


def train_model(df):
    global validation_records
    if not use_previous_model:
        # df_training = df
        df_training = df[~df["measurement_name"].isin(validation_records)]
        X_training = df_training.drop(columns=training_columns_to_drop)
        y_training = df_training[target_parameter]

        df_validation = df[df["measurement_name"].isin(validation_records)]
        X_validation = df_validation.drop(columns=training_columns_to_drop)
        y_validation = df_validation[target_parameter]

        dtrain_reg = xgb.DMatrix(X_training, y_training)
        dvalid_reg = xgb.DMatrix(X_validation, y_validation)

        num_features = df_training.shape[1]
        weights = np.ones(num_features)
        dtrain_reg.set_info(feature_weights=weights)

        parameters = {
                      # "objective": "reg:squarederror",
                      # "objective": "reg:quantileerror",
                      # "quantile_alpha": 0.7,
                      "eval_metric": "rmse",
                      "device": "cuda",
                      'learning_rate': 0.01,
                      'max_depth': 4,
                      "gamma": 10,
                      'min_child_weight': 15,
                      'colsample_bytree': 0.25,
                      'seed': 80085,
                      }

        evals = [(dtrain_reg, "train"), (dvalid_reg, "validation")]

        model = xgb.train(
            params=parameters,
            dtrain=dtrain_reg,
            early_stopping_rounds=500,
            num_boost_round=10000,
            verbose_eval=100,
            evals=evals,
            obj=custom_loss_function()
        )

        model.save_model(model_path)

    else:
        model = xgb.Booster()
        model.load_model(model_path)

    plot_validation_results(df, model, validation_records)

    plot_importance(model)
    plt.show()


def plot_validation_results(df, model, records_list):
    for validation_record in records_list:
        df_validation = df[df["measurement_name"] == validation_record]
        X_validation = df_validation.drop(columns=training_columns_to_drop)
        y_validation = df_validation["Temp"]

        dvalid_reg = xgb.DMatrix(X_validation, y_validation)
        y_pred_validation = model.predict(dvalid_reg, iteration_range=(0, model.best_iteration + 1))

        if target_parameter == "dTemp":
            y_pred_temp = y_pred_validation.cumsum()
            y_pred_temp += 30.0
        else:
            y_pred_temp = y_pred_validation

        rmse_validation = root_mean_squared_error(y_validation, y_pred_temp)
        print(f"Validation RMSE: {rmse_validation}")
        plt.scatter(df_validation["t"], df_validation["Temp"], color="tab:blue", s=10)
        plt.scatter(df_validation["t"], y_pred_temp, color="tab:orange", s=10)
        plt.ylim(20, 130)
        plt.show()


def add_cumulative_maximum_slope_features(df, feature, slope_duration):
    df[f"cumulative_max_{feature}_slope"] = df[f"slope_{feature}_{slope_duration}ms"].cummax()


def add_initial_features(df, feature):
    df[f"initial_{feature}"] = df[f"{feature}"][0]
    return df


def add_lagged_features(df, feature, lags):
    for lag in lags:
        df[f"lagged_{feature}_{lag}ms"] = df[f"{feature}"].shift(lag)
    return df


def add_rolling_mean(df, feature, window_sizes):
    for window_size in window_sizes:
        df[f"mean_{feature}_{window_size}ms"] = df[feature].rolling(window_size).mean()
    return df


def add_slope(df, feature, slope_durations):
    for slope_duration in slope_durations:
        df[f"slope_{feature}_{slope_duration}ms"] = df[feature].diff(slope_duration)


if __name__ == '__main__':

    if use_previous_df:
        df_full = pd.read_csv(df_csv_path)
    else:
        df_full = pd.DataFrame()

        current_measurement_id = 0
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

                # NOTE: Calculate generator temperatures
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
                df_current.insert(0, "Temp", temp_values_gen)
                df_current.insert(1, "dTemp", df_current["Temp"].diff())
                df_current["dTemp"] = df_current["dTemp"].fillna(0)
                df_current["measurement_name"] = log_name.replace(".json", "")
                df_current.insert(0, "measurement_id", current_measurement_id)
                current_measurement_id += 1

                # NOTE: Calculate Energy values
                p_values = record.generator_raw_data["P"]
                e_values = []
                for i in range(len(p_values)):
                    if len(e_values) == 0:
                        e_value = p_values[i] / 1000
                    else:
                        e_value = e_values[i - 1] + p_values[i] / 1000  # /1000 because time is in ms
                    e_values.append(e_value)
                df_current["E"] = e_values
                add_lagged_features(df_current, "E", lagged_feature_lags)
                add_rolling_mean(df_current, "E", mean_feature_lens)
                add_slope(df_current, "E", slope_feature_lens)

                # NOTE: Lagged features
                for feature_name in record.generator_raw_data.keys():
                    add_lagged_features(df_current, feature_name, lagged_feature_lags)
                    add_rolling_mean(df_current, feature_name, mean_feature_lens)
                    add_slope(df_current, feature_name, slope_feature_lens)
                    add_initial_features(df_current, feature_name)

                add_cumulative_maximum_slope_features(df_current, "Z", 3)

                df_full = pd.concat([df_full, df_current], ignore_index=True)

        if save_df_to_file:
            df_full.to_csv(df_csv_path, index=False)

    # NOTE: Column shuffle
    # df_full = df_full[np.random.default_rng().permutation(df_full.columns.values)]
    print(df_full.head().to_string())

    # NOTE: ML algorithm
    train_model(df_full)
