################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (11.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../tinyUSB/hw/mcu/sony/cxd56/mkspk/clefia.c \
../tinyUSB/hw/mcu/sony/cxd56/mkspk/mkspk.c 

OBJS += \
./tinyUSB/hw/mcu/sony/cxd56/mkspk/clefia.o \
./tinyUSB/hw/mcu/sony/cxd56/mkspk/mkspk.o 

C_DEPS += \
./tinyUSB/hw/mcu/sony/cxd56/mkspk/clefia.d \
./tinyUSB/hw/mcu/sony/cxd56/mkspk/mkspk.d 


# Each subdirectory must supply rules for building sources it contributes
tinyUSB/hw/mcu/sony/cxd56/mkspk/%.o tinyUSB/hw/mcu/sony/cxd56/mkspk/%.su tinyUSB/hw/mcu/sony/cxd56/mkspk/%.cyclo: ../tinyUSB/hw/mcu/sony/cxd56/mkspk/%.c tinyUSB/hw/mcu/sony/cxd56/mkspk/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F303xE -c -I../Core/Inc -I../Drivers/STM32F3xx_HAL_Driver/Inc -I../Drivers/STM32F3xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32F3xx/Include -I../Drivers/CMSIS/Include -I"C:/Users/AntovI/Desktop/Uni/DR/Code/MCU/tinyUSB/src" -I"C:/Users/AntovI/Desktop/Uni/DR/Code/MCU/tinyUSB/hw/bsp" -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-tinyUSB-2f-hw-2f-mcu-2f-sony-2f-cxd56-2f-mkspk

clean-tinyUSB-2f-hw-2f-mcu-2f-sony-2f-cxd56-2f-mkspk:
	-$(RM) ./tinyUSB/hw/mcu/sony/cxd56/mkspk/clefia.cyclo ./tinyUSB/hw/mcu/sony/cxd56/mkspk/clefia.d ./tinyUSB/hw/mcu/sony/cxd56/mkspk/clefia.o ./tinyUSB/hw/mcu/sony/cxd56/mkspk/clefia.su ./tinyUSB/hw/mcu/sony/cxd56/mkspk/mkspk.cyclo ./tinyUSB/hw/mcu/sony/cxd56/mkspk/mkspk.d ./tinyUSB/hw/mcu/sony/cxd56/mkspk/mkspk.o ./tinyUSB/hw/mcu/sony/cxd56/mkspk/mkspk.su

.PHONY: clean-tinyUSB-2f-hw-2f-mcu-2f-sony-2f-cxd56-2f-mkspk

