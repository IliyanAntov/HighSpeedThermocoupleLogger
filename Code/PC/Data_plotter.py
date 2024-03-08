import serial
import matplotlib.pyplot as plt

adc_buffer = 5000
usb_buffer = adc_buffer * 2
buffers_to_receive = 3


time_list = list(x/1000 for x in range(0, adc_buffer * buffers_to_receive * 10, 10))

ser = serial.Serial('COM11', baudrate=115200, timeout=None)
ser.flush()

ADC_values = []

for i in range(buffers_to_receive):
    data = ser.read(usb_buffer)
    for j in range(0, (len(data) - 1), 2):
        adc_reading_num = (data[j] << 8) + data[j+1]
        voltage_value = adc_reading_num / pow(2, 16) * 3.25
        ADC_values.append(voltage_value)

print("Plotting graph...")
plt.plot(time_list, ADC_values)
plt.xlabel("Time [ms]")
plt.ylabel("Voltage [V]")

plt.show()
