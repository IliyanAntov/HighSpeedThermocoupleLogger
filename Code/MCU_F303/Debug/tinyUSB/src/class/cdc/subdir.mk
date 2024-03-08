################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (11.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../tinyUSB/src/class/cdc/cdc_device.c \
../tinyUSB/src/class/cdc/cdc_host.c \
../tinyUSB/src/class/cdc/cdc_rndis_host.c 

OBJS += \
./tinyUSB/src/class/cdc/cdc_device.o \
./tinyUSB/src/class/cdc/cdc_host.o \
./tinyUSB/src/class/cdc/cdc_rndis_host.o 

C_DEPS += \
./tinyUSB/src/class/cdc/cdc_device.d \
./tinyUSB/src/class/cdc/cdc_host.d \
./tinyUSB/src/class/cdc/cdc_rndis_host.d 


# Each subdirectory must supply rules for building sources it contributes
tinyUSB/src/class/cdc/%.o tinyUSB/src/class/cdc/%.su tinyUSB/src/class/cdc/%.cyclo: ../tinyUSB/src/class/cdc/%.c tinyUSB/src/class/cdc/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F303xE -c -I../Core/Inc -I../Drivers/STM32F3xx_HAL_Driver/Inc -I../Drivers/STM32F3xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32F3xx/Include -I../Drivers/CMSIS/Include -I"C:/Users/AntovI/Desktop/Uni/DR/Code/MCU/tinyUSB/src" -I"C:/Users/AntovI/Desktop/Uni/DR/Code/MCU/tinyUSB/hw" -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-tinyUSB-2f-src-2f-class-2f-cdc

clean-tinyUSB-2f-src-2f-class-2f-cdc:
	-$(RM) ./tinyUSB/src/class/cdc/cdc_device.cyclo ./tinyUSB/src/class/cdc/cdc_device.d ./tinyUSB/src/class/cdc/cdc_device.o ./tinyUSB/src/class/cdc/cdc_device.su ./tinyUSB/src/class/cdc/cdc_host.cyclo ./tinyUSB/src/class/cdc/cdc_host.d ./tinyUSB/src/class/cdc/cdc_host.o ./tinyUSB/src/class/cdc/cdc_host.su ./tinyUSB/src/class/cdc/cdc_rndis_host.cyclo ./tinyUSB/src/class/cdc/cdc_rndis_host.d ./tinyUSB/src/class/cdc/cdc_rndis_host.o ./tinyUSB/src/class/cdc/cdc_rndis_host.su

.PHONY: clean-tinyUSB-2f-src-2f-class-2f-cdc

