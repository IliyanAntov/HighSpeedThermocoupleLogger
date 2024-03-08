################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (11.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../tinyUSB/src/portable/espressif/esp32sx/dcd_esp32sx.c 

OBJS += \
./tinyUSB/src/portable/espressif/esp32sx/dcd_esp32sx.o 

C_DEPS += \
./tinyUSB/src/portable/espressif/esp32sx/dcd_esp32sx.d 


# Each subdirectory must supply rules for building sources it contributes
tinyUSB/src/portable/espressif/esp32sx/%.o tinyUSB/src/portable/espressif/esp32sx/%.su tinyUSB/src/portable/espressif/esp32sx/%.cyclo: ../tinyUSB/src/portable/espressif/esp32sx/%.c tinyUSB/src/portable/espressif/esp32sx/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F303xE -c -I../Core/Inc -I../Drivers/STM32F3xx_HAL_Driver/Inc -I../Drivers/STM32F3xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32F3xx/Include -I../Drivers/CMSIS/Include -I"C:/Users/AntovI/Desktop/Uni/DR/Code/MCU/tinyUSB/src" -I"C:/Users/AntovI/Desktop/Uni/DR/Code/MCU/tinyUSB/hw" -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-tinyUSB-2f-src-2f-portable-2f-espressif-2f-esp32sx

clean-tinyUSB-2f-src-2f-portable-2f-espressif-2f-esp32sx:
	-$(RM) ./tinyUSB/src/portable/espressif/esp32sx/dcd_esp32sx.cyclo ./tinyUSB/src/portable/espressif/esp32sx/dcd_esp32sx.d ./tinyUSB/src/portable/espressif/esp32sx/dcd_esp32sx.o ./tinyUSB/src/portable/espressif/esp32sx/dcd_esp32sx.su

.PHONY: clean-tinyUSB-2f-src-2f-portable-2f-espressif-2f-esp32sx

