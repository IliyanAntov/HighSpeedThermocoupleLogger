import json

# ../../Measurements/Oscilloscope_data.xlsx
import pandas as pd

xls = pd.ExcelFile('../../../Measurements/Oscilloscope_data.xlsx')
dataframe = pd.read_excel(xls, 'tek0001CH1')

x_dataframe = dataframe["Time"].dropna().astype(float)
y_dataframe = dataframe["Voltage"].dropna().astype(float)

x_data = x_dataframe.values.tolist()
y_data = y_dataframe.values.tolist()

data_json = {
    "x_values": x_data,
    "y_values": y_data
}

f = open("../data/oscilloscope_data.json", "w")
json.dump(data_json, f)
f.close()
print("Done")
