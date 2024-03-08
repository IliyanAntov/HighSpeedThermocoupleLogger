import json

import numpy as np
# curve-fit() function imported from scipy
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt

f = open("./data/oscilloscope_data.json", "r")
osc_data = json.load(f)
f.close()

print(osc_data)
x_data = osc_data["x_values"]
y_data = osc_data["y_values"]

plt.plot(x_data, y_data)
plt.show()


# y is another array which stores 3.45 times
# the sine of (values in x) * 1.334.
# The random.normal() draws random sample
# from normal (Gaussian) distribution to make
# them scatter across the base line
y = 3.45 * np.sin(1.334 * x) + np.random.normal(size=40)


# Test function with coefficients as parameters
def test(x, a, b):
    return a * np.sin(b * x)

def heating_function(x, a):
    return a + ()


# curve_fit() function takes the test-function
# x-data and y-data as argument and returns
# the coefficients a and b in param and
# the estimated covariance of param in param_cov
param, param_cov = curve_fit(test, x, y)

print("Sine function coefficients:")
print(param)
print("Covariance of coefficients:")
print(param_cov)
print("Standard error of coefficients:")
perr = np.sqrt(np.diag(param_cov))
print(perr)



# ans stores the new y-data according to
# the coefficients given by curve-fit() function
ans = (param[0] * (np.sin(param[1] * x)))

'''Below 4 lines can be un-commented for plotting results
using matplotlib as shown in the first example. '''

plt.plot(x, y, 'o', color ='red', label ="data")
plt.plot(x, ans, '--', color ='blue', label ="optimized data")
plt.legend()
plt.show()