################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (11.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../tinyUSB/src/portable/chipidea/ci_hs/dcd_ci_hs.c \
../tinyUSB/src/portable/chipidea/ci_hs/hcd_ci_hs.c 

OBJS += \
./tinyUSB/src/portable/chipidea/ci_hs/dcd_ci_hs.o \
./tinyUSB/src/portable/chipidea/ci_hs/hcd_ci_hs.o 

C_DEPS += \
./tinyUSB/src/portable/chipidea/ci_hs/dcd_ci_hs.d \
./tinyUSB/src/portable/chipidea/ci_hs/hcd_ci_hs.d 


# Each subdirectory must supply rules for building sources it contributes
tinyUSB/src/portable/chipidea/ci_hs/%.o tinyUSB/src/portable/chipidea/ci_hs/%.su tinyUSB/src/portable/chipidea/ci_hs/%.cyclo: ../tinyUSB/src/portable/chipidea/ci_hs/%.c tinyUSB/src/portable/chipidea/ci_hs/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F303xE -c -I../Core/Inc -I../Drivers/STM32F3xx_HAL_Driver/Inc -I../Drivers/STM32F3xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32F3xx/Include -I../Drivers/CMSIS/Include -I"C:/Users/AntovI/Desktop/Uni/DR/Code/MCU/tinyUSB/src" -I"C:/Users/AntovI/Desktop/Uni/DR/Code/MCU/tinyUSB/hw" -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-tinyUSB-2f-src-2f-portable-2f-chipidea-2f-ci_hs

clean-tinyUSB-2f-src-2f-portable-2f-chipidea-2f-ci_hs:
	-$(RM) ./tinyUSB/src/portable/chipidea/ci_hs/dcd_ci_hs.cyclo ./tinyUSB/src/portable/chipidea/ci_hs/dcd_ci_hs.d ./tinyUSB/src/portable/chipidea/ci_hs/dcd_ci_hs.o ./tinyUSB/src/portable/chipidea/ci_hs/dcd_ci_hs.su ./tinyUSB/src/portable/chipidea/ci_hs/hcd_ci_hs.cyclo ./tinyUSB/src/portable/chipidea/ci_hs/hcd_ci_hs.d ./tinyUSB/src/portable/chipidea/ci_hs/hcd_ci_hs.o ./tinyUSB/src/portable/chipidea/ci_hs/hcd_ci_hs.su

.PHONY: clean-tinyUSB-2f-src-2f-portable-2f-chipidea-2f-ci_hs

