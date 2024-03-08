################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (11.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../tinyUSB/src/typec/usbc.c 

OBJS += \
./tinyUSB/src/typec/usbc.o 

C_DEPS += \
./tinyUSB/src/typec/usbc.d 


# Each subdirectory must supply rules for building sources it contributes
tinyUSB/src/typec/%.o tinyUSB/src/typec/%.su tinyUSB/src/typec/%.cyclo: ../tinyUSB/src/typec/%.c tinyUSB/src/typec/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F303xE -c -I../Core/Inc -I../Drivers/STM32F3xx_HAL_Driver/Inc -I../Drivers/STM32F3xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32F3xx/Include -I../Drivers/CMSIS/Include -I"C:/Users/AntovI/Desktop/Uni/DR/Code/MCU/tinyUSB/src" -I"C:/Users/AntovI/Desktop/Uni/DR/Code/MCU/tinyUSB/hw" -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-tinyUSB-2f-src-2f-typec

clean-tinyUSB-2f-src-2f-typec:
	-$(RM) ./tinyUSB/src/typec/usbc.cyclo ./tinyUSB/src/typec/usbc.d ./tinyUSB/src/typec/usbc.o ./tinyUSB/src/typec/usbc.su

.PHONY: clean-tinyUSB-2f-src-2f-typec

