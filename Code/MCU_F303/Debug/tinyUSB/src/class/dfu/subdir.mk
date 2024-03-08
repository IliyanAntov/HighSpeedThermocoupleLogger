################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (11.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../tinyUSB/src/class/dfu/dfu_device.c \
../tinyUSB/src/class/dfu/dfu_rt_device.c 

OBJS += \
./tinyUSB/src/class/dfu/dfu_device.o \
./tinyUSB/src/class/dfu/dfu_rt_device.o 

C_DEPS += \
./tinyUSB/src/class/dfu/dfu_device.d \
./tinyUSB/src/class/dfu/dfu_rt_device.d 


# Each subdirectory must supply rules for building sources it contributes
tinyUSB/src/class/dfu/%.o tinyUSB/src/class/dfu/%.su tinyUSB/src/class/dfu/%.cyclo: ../tinyUSB/src/class/dfu/%.c tinyUSB/src/class/dfu/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F303xE -c -I../Core/Inc -I../Drivers/STM32F3xx_HAL_Driver/Inc -I../Drivers/STM32F3xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32F3xx/Include -I../Drivers/CMSIS/Include -I"C:/Users/AntovI/Desktop/Uni/DR/Code/MCU/tinyUSB/src" -I"C:/Users/AntovI/Desktop/Uni/DR/Code/MCU/tinyUSB/hw" -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-tinyUSB-2f-src-2f-class-2f-dfu

clean-tinyUSB-2f-src-2f-class-2f-dfu:
	-$(RM) ./tinyUSB/src/class/dfu/dfu_device.cyclo ./tinyUSB/src/class/dfu/dfu_device.d ./tinyUSB/src/class/dfu/dfu_device.o ./tinyUSB/src/class/dfu/dfu_device.su ./tinyUSB/src/class/dfu/dfu_rt_device.cyclo ./tinyUSB/src/class/dfu/dfu_rt_device.d ./tinyUSB/src/class/dfu/dfu_rt_device.o ./tinyUSB/src/class/dfu/dfu_rt_device.su

.PHONY: clean-tinyUSB-2f-src-2f-class-2f-dfu

