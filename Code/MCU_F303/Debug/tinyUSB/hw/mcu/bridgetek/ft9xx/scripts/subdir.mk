################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (11.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
S_UPPER_SRCS += \
../tinyUSB/hw/mcu/bridgetek/ft9xx/scripts/crt0.S 

OBJS += \
./tinyUSB/hw/mcu/bridgetek/ft9xx/scripts/crt0.o 

S_UPPER_DEPS += \
./tinyUSB/hw/mcu/bridgetek/ft9xx/scripts/crt0.d 


# Each subdirectory must supply rules for building sources it contributes
tinyUSB/hw/mcu/bridgetek/ft9xx/scripts/%.o: ../tinyUSB/hw/mcu/bridgetek/ft9xx/scripts/%.S tinyUSB/hw/mcu/bridgetek/ft9xx/scripts/subdir.mk
	arm-none-eabi-gcc -mcpu=cortex-m4 -g3 -DDEBUG -c -x assembler-with-cpp -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@" "$<"

clean: clean-tinyUSB-2f-hw-2f-mcu-2f-bridgetek-2f-ft9xx-2f-scripts

clean-tinyUSB-2f-hw-2f-mcu-2f-bridgetek-2f-ft9xx-2f-scripts:
	-$(RM) ./tinyUSB/hw/mcu/bridgetek/ft9xx/scripts/crt0.d ./tinyUSB/hw/mcu/bridgetek/ft9xx/scripts/crt0.o

.PHONY: clean-tinyUSB-2f-hw-2f-mcu-2f-bridgetek-2f-ft9xx-2f-scripts

