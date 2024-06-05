import serial
import time

buffer_size = 64
meas_time = 2
number_of_measurements = 5

byte_cnt = 0
ser = serial.Serial('COM11', baudrate=9600, timeout=1)

average_data_rate = 0
measurement_list = []
for i in range(number_of_measurements):
    byte_cnt = 0

    t_start = time.time()
    elapsed_time = time.time() - t_start

    while elapsed_time < meas_time:
        data = ser.read_all()
        byte_cnt += len(data)
        elapsed_time = time.time() - t_start

    average_data_rate += (8 * byte_cnt) / (elapsed_time * 1000000)
    measurement_list.append((8 * byte_cnt) / (elapsed_time * 1000000))

ser.close()
average_data_rate /= number_of_measurements

# print("Read " + str(byte_cnt) + ' bytes in ' + str(elapsed_time) + 'sec')
# print("Average data rate: " + str((8 * byte_cnt) / (elapsed_time * 1000000)) + " Mbps")
print("Average data rate after " + str(number_of_measurements * meas_time) + "s: " + str(average_data_rate) + " Mbps")
print(measurement_list)
