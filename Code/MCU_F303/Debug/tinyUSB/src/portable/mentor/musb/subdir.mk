################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (11.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../tinyUSB/src/portable/mentor/musb/dcd_musb.c \
../tinyUSB/src/portable/mentor/musb/hcd_musb.c 

OBJS += \
./tinyUSB/src/portable/mentor/musb/dcd_musb.o \
./tinyUSB/src/portable/mentor/musb/hcd_musb.o 

C_DEPS += \
./tinyUSB/src/portable/mentor/musb/dcd_musb.d \
./tinyUSB/src/portable/mentor/musb/hcd_musb.d 


# Each subdirectory must supply rules for building sources it contributes
tinyUSB/src/portable/mentor/musb/%.o tinyUSB/src/portable/mentor/musb/%.su tinyUSB/src/portable/mentor/musb/%.cyclo: ../tinyUSB/src/portable/mentor/musb/%.c tinyUSB/src/portable/mentor/musb/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F303xE -c -I../Core/Inc -I../Drivers/STM32F3xx_HAL_Driver/Inc -I../Drivers/STM32F3xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32F3xx/Include -I../Drivers/CMSIS/Include -I"C:/Users/AntovI/Desktop/Uni/DR/Code/MCU/tinyUSB/src" -I"C:/Users/AntovI/Desktop/Uni/DR/Code/MCU/tinyUSB/hw" -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-tinyUSB-2f-src-2f-portable-2f-mentor-2f-musb

clean-tinyUSB-2f-src-2f-portable-2f-mentor-2f-musb:
	-$(RM) ./tinyUSB/src/portable/mentor/musb/dcd_musb.cyclo ./tinyUSB/src/portable/mentor/musb/dcd_musb.d ./tinyUSB/src/portable/mentor/musb/dcd_musb.o ./tinyUSB/src/portable/mentor/musb/dcd_musb.su ./tinyUSB/src/portable/mentor/musb/hcd_musb.cyclo ./tinyUSB/src/portable/mentor/musb/hcd_musb.d ./tinyUSB/src/portable/mentor/musb/hcd_musb.o ./tinyUSB/src/portable/mentor/musb/hcd_musb.su

.PHONY: clean-tinyUSB-2f-src-2f-portable-2f-mentor-2f-musb

