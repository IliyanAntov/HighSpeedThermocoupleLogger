import json

import numpy as np
# curve-fit() function imported from scipy
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt

f = open("./data/oscilloscope_data.json", "r")
osc_data = json.load(f)
f.close()

x_data_osc = osc_data["x_values"]
y_data_osc = osc_data["y_values"]
x_data_sliced = x_data_osc[21250:]
x_data = [x - x_data_sliced[0] for x in x_data_sliced]

y_data = y_data_osc[21250:]

tau_ms = 130
t_0 = y_data[0]
print(x_data[0])
print(y_data[0])
print(t_0)


def heating_function(x, t_env):
    return t_env + ((t_0 - t_env)*np.exp(-(1/(tau_ms/1000))*x))


param, param_cov = curve_fit(heating_function, x_data, y_data)

print("Tenv:")
print(param)
print("Covariance of coefficients:")
print(param_cov)
print("Standard error of coefficients:")
perr = np.sqrt(np.diag(param_cov))
print(perr)


prediction = []
for i in range(len(x_data)):
    prediction.append(param[0] + (t_0 - param[0])*np.exp(-(1/(tau_ms/1000))*x_data[i]))


plt.plot(x_data, y_data)
print("x_data[-1]: " + str(x_data[-1]))
plt.plot(x_data, prediction, color="red")
plt.show()

# # ans stores the new y-data according to
# # the coefficients given by curve-fit() function
# ans = (param[0] * (np.sin(param[1] * x)))
#
# '''Below 4 lines can be un-commented for plotting results
# using matplotlib as shown in the first example. '''
#
# plt.plot(x, y, 'o', color ='red', label ="data")
# plt.plot(x, ans, '--', color ='blue', label ="optimized data")
# plt.legend()
# plt.show()