################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (11.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../tinyUSB/src/portable/ti/msp430x5xx/dcd_msp430x5xx.c 

OBJS += \
./tinyUSB/src/portable/ti/msp430x5xx/dcd_msp430x5xx.o 

C_DEPS += \
./tinyUSB/src/portable/ti/msp430x5xx/dcd_msp430x5xx.d 


# Each subdirectory must supply rules for building sources it contributes
tinyUSB/src/portable/ti/msp430x5xx/%.o tinyUSB/src/portable/ti/msp430x5xx/%.su tinyUSB/src/portable/ti/msp430x5xx/%.cyclo: ../tinyUSB/src/portable/ti/msp430x5xx/%.c tinyUSB/src/portable/ti/msp430x5xx/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F303xE -c -I../Core/Inc -I../Drivers/STM32F3xx_HAL_Driver/Inc -I../Drivers/STM32F3xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32F3xx/Include -I../Drivers/CMSIS/Include -I"C:/Users/AntovI/Desktop/Uni/DR/Code/MCU/tinyUSB/src" -I"C:/Users/AntovI/Desktop/Uni/DR/Code/MCU/tinyUSB/hw" -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-tinyUSB-2f-src-2f-portable-2f-ti-2f-msp430x5xx

clean-tinyUSB-2f-src-2f-portable-2f-ti-2f-msp430x5xx:
	-$(RM) ./tinyUSB/src/portable/ti/msp430x5xx/dcd_msp430x5xx.cyclo ./tinyUSB/src/portable/ti/msp430x5xx/dcd_msp430x5xx.d ./tinyUSB/src/portable/ti/msp430x5xx/dcd_msp430x5xx.o ./tinyUSB/src/portable/ti/msp430x5xx/dcd_msp430x5xx.su

.PHONY: clean-tinyUSB-2f-src-2f-portable-2f-ti-2f-msp430x5xx

