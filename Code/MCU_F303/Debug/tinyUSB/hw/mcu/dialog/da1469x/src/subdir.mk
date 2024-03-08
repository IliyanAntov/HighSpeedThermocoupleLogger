################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (11.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../tinyUSB/hw/mcu/dialog/da1469x/src/da1469x_clock.c \
../tinyUSB/hw/mcu/dialog/da1469x/src/hal_gpio.c \
../tinyUSB/hw/mcu/dialog/da1469x/src/hal_system.c \
../tinyUSB/hw/mcu/dialog/da1469x/src/hal_system_start.c \
../tinyUSB/hw/mcu/dialog/da1469x/src/system_da1469x.c 

OBJS += \
./tinyUSB/hw/mcu/dialog/da1469x/src/da1469x_clock.o \
./tinyUSB/hw/mcu/dialog/da1469x/src/hal_gpio.o \
./tinyUSB/hw/mcu/dialog/da1469x/src/hal_system.o \
./tinyUSB/hw/mcu/dialog/da1469x/src/hal_system_start.o \
./tinyUSB/hw/mcu/dialog/da1469x/src/system_da1469x.o 

C_DEPS += \
./tinyUSB/hw/mcu/dialog/da1469x/src/da1469x_clock.d \
./tinyUSB/hw/mcu/dialog/da1469x/src/hal_gpio.d \
./tinyUSB/hw/mcu/dialog/da1469x/src/hal_system.d \
./tinyUSB/hw/mcu/dialog/da1469x/src/hal_system_start.d \
./tinyUSB/hw/mcu/dialog/da1469x/src/system_da1469x.d 


# Each subdirectory must supply rules for building sources it contributes
tinyUSB/hw/mcu/dialog/da1469x/src/%.o tinyUSB/hw/mcu/dialog/da1469x/src/%.su tinyUSB/hw/mcu/dialog/da1469x/src/%.cyclo: ../tinyUSB/hw/mcu/dialog/da1469x/src/%.c tinyUSB/hw/mcu/dialog/da1469x/src/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F303xE -c -I../Core/Inc -I../Drivers/STM32F3xx_HAL_Driver/Inc -I../Drivers/STM32F3xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32F3xx/Include -I../Drivers/CMSIS/Include -I"C:/Users/AntovI/Desktop/Uni/DR/Code/MCU/tinyUSB/src" -I"C:/Users/AntovI/Desktop/Uni/DR/Code/MCU/tinyUSB/hw/bsp" -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-tinyUSB-2f-hw-2f-mcu-2f-dialog-2f-da1469x-2f-src

clean-tinyUSB-2f-hw-2f-mcu-2f-dialog-2f-da1469x-2f-src:
	-$(RM) ./tinyUSB/hw/mcu/dialog/da1469x/src/da1469x_clock.cyclo ./tinyUSB/hw/mcu/dialog/da1469x/src/da1469x_clock.d ./tinyUSB/hw/mcu/dialog/da1469x/src/da1469x_clock.o ./tinyUSB/hw/mcu/dialog/da1469x/src/da1469x_clock.su ./tinyUSB/hw/mcu/dialog/da1469x/src/hal_gpio.cyclo ./tinyUSB/hw/mcu/dialog/da1469x/src/hal_gpio.d ./tinyUSB/hw/mcu/dialog/da1469x/src/hal_gpio.o ./tinyUSB/hw/mcu/dialog/da1469x/src/hal_gpio.su ./tinyUSB/hw/mcu/dialog/da1469x/src/hal_system.cyclo ./tinyUSB/hw/mcu/dialog/da1469x/src/hal_system.d ./tinyUSB/hw/mcu/dialog/da1469x/src/hal_system.o ./tinyUSB/hw/mcu/dialog/da1469x/src/hal_system.su ./tinyUSB/hw/mcu/dialog/da1469x/src/hal_system_start.cyclo ./tinyUSB/hw/mcu/dialog/da1469x/src/hal_system_start.d ./tinyUSB/hw/mcu/dialog/da1469x/src/hal_system_start.o ./tinyUSB/hw/mcu/dialog/da1469x/src/hal_system_start.su ./tinyUSB/hw/mcu/dialog/da1469x/src/system_da1469x.cyclo ./tinyUSB/hw/mcu/dialog/da1469x/src/system_da1469x.d ./tinyUSB/hw/mcu/dialog/da1469x/src/system_da1469x.o ./tinyUSB/hw/mcu/dialog/da1469x/src/system_da1469x.su

.PHONY: clean-tinyUSB-2f-hw-2f-mcu-2f-dialog-2f-da1469x-2f-src

