################################################################################
# Automatically-generated file. Do not edit!
################################################################################

C_FILES += "C:/Users/hmidenen/Desktop/Sanity Check/AN2668_FW_V3.0.0/Libraries/CMSIS/Device/ST/STM32L1xx/Source/Templates/system_stm32l1xx.c"
OBJ_FILES += "CMSIS\system_stm32l1xx.obj"
"CMSIS\system_stm32l1xx.obj" : "C:/Users/hmidenen/Desktop/Sanity Check/AN2668_FW_V3.0.0/Libraries/CMSIS/Device/ST/STM32L1xx/Source/Templates/system_stm32l1xx.c" "CMSIS\.system_stm32l1xx.obj.opt"
	@echo Compiling ${<F}
	@"${PRODDIR}\bin\ccarm" -f "CMSIS\.system_stm32l1xx.obj.opt"

"CMSIS\.system_stm32l1xx.obj.opt" : .refresh
	@argfile "CMSIS\.system_stm32l1xx.obj.opt" -o "CMSIS\system_stm32l1xx.obj" "C:/Users/hmidenen/Desktop/Sanity Check/AN2668_FW_V3.0.0/Libraries/CMSIS/Device/ST/STM32L1xx/Source/Templates/system_stm32l1xx.c" -Cstm32l152vb -t -Wa-gAHLs -Wa--no-warnings -Wa--error-limit=42 -DVECT_TAB_FLASH -DUSE_STDPERIPH_DRIVER -DUSE_STM32L152_EVAL -DSTM32L1XX_MD -I..\..\..\inc -I..\..\..\..\..\..\Libraries\STM32L1xx_StdPeriph_Driver\inc -I..\..\..\..\..\..\Libraries\CMSIS\Device\ST\STM32L1xx\Include -I..\..\..\..\..\..\Libraries\CMSIS\Include --language=-gcc,-volatile,+strings -O3 --tradeoff=4 --compact-max-size=200 -g -Wc-w557 -Wc-w529 -Wc-w588 --source -c --dep-file="CMSIS\.system_stm32l1xx.obj.d" -Wc--make-target="CMSIS\system_stm32l1xx.obj"
DEPENDENCY_FILES += "CMSIS\.system_stm32l1xx.obj.d"


GENERATED_FILES += "CMSIS\system_stm32l1xx.obj" "CMSIS\.system_stm32l1xx.obj.opt" "CMSIS\.system_stm32l1xx.obj.d" "CMSIS\system_stm32l1xx.src" "CMSIS\system_stm32l1xx.lst"
