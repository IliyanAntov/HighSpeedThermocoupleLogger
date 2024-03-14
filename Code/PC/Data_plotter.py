from time import sleep

import numpy as np
import serial
import matplotlib.pyplot as plt

sampling_interval_us = 10

used_adc_count = 4
adc_buffer_size = 2000
usb_header_size = 20
usb_buffer_size = usb_header_size + (adc_buffer_size * used_adc_count)
buffers_to_receive = 5


time_list = list(x/1000 for x in range(0, int(adc_buffer_size/2) * buffers_to_receive * sampling_interval_us, sampling_interval_us))

ser = serial.Serial('COM11', baudrate=115200, timeout=None)

adc_values = []

for i in range(buffers_to_receive):
    data = ser.read(usb_buffer_size)

    header = data[:usb_header_size]
    adc_data = data[usb_header_size:]

    adc_data_split = []
    for j in range(used_adc_count):
        adc_data_split.append(adc_data[(adc_buffer_size*j):(adc_buffer_size*(j+1))])

    i = 0
    for adc_x_data in adc_data_split:
        adc_values.append([])
        for j in range(0, (len(adc_x_data) - 1), 2):
            adc_reading_num = (adc_x_data[j] << 8) + adc_x_data[j + 1]
            voltage_value = adc_reading_num / pow(2, 16) * 3.25
            adc_values[i].append(voltage_value)
        i += 1


print("Plotting graph...")
plt.plot(time_list, adc_values[0], color="red")
plt.plot(time_list, adc_values[1], color="blue")
plt.plot(time_list, adc_values[2], color="green")
plt.plot(time_list, adc_values[3], color="orange")
plt.xlabel("Time [ms]")
plt.ylabel("Voltage [V]")
plt.show()

# Y = np.fft.fft(adc_values[0])
# freq = np.fft.fftfreq(len(adc_values[0]), 0.00001)
#
# plt.figure()
# plt.plot(freq, np.abs(Y))

