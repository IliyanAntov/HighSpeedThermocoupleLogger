/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "usb_device.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "usbd_cdc_if.h"
#include "stm32g4xx_ll_usb.h"
#include <string.h>
#include <stdio.h>
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */
extern USBD_HandleTypeDef hUsbDeviceFS;
/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc1;
ADC_HandleTypeDef hadc2;
ADC_HandleTypeDef hadc3;
ADC_HandleTypeDef hadc4;
DMA_HandleTypeDef hdma_adc1;
DMA_HandleTypeDef hdma_adc2;
DMA_HandleTypeDef hdma_adc3;
DMA_HandleTypeDef hdma_adc4;

DAC_HandleTypeDef hdac1;

I2C_HandleTypeDef hi2c3;

TIM_HandleTypeDef htim2;

/* USER CODE BEGIN PV */
int current_packet_count = 0;
int target_packet_count = 0;
int dropped_packet_count = 0;

uint16_t adc_buffers[MAX_CHANNEL_COUNT][ADC_BUFFER_SIZE];
int8_t rx_buffer[USB_RX_BUFFER_SIZE];

volatile enum PROG_STATE prog_state = IDLE;
volatile float cold_junction_temp = 0;			// [°C]
volatile float analog_reference_voltage = 2.9;	// [V]
volatile float applied_voltage_offset = 0;		// [V]

uint16_t record_length_ms = 100;
uint16_t record_interval_us = 10;
char tc_type = 'J';
enum ADC_BUFFER_STATE usb_transmition_state = EMPTY;
enum ADC_BUFFER_STATE adc_states[MAX_CHANNEL_COUNT] = {EMPTY, EMPTY, EMPTY, EMPTY};
unsigned int channel_enabled_count = 0;
unsigned int channel_enabled_status[MAX_CHANNEL_COUNT] = {0, 0, 0, 0};

volatile int transmission_error = 0;
volatile int conv_count_reached = 0;
volatile int measurement_activated = 0;

// -210 to 760°C
const uint8_t type_j_coefficients_count = 9;
const double type_j_coefficients[9] = {0,
									   5.0381187815 * pow(10, 1),
									   3.0475836930 * pow(10, -2),
									  -8.5681065720 * pow(10, -5),
									   1.3228195295 * pow(10, -7),
									  -1.7052958337 * pow(10, -10),
									   2.0948090697 * pow(10, -13),
									  -1.2538395336 * pow(10, -16),
									   1.5631725697 * pow(10, -20)

};

// -270 to 0°C
const uint8_t type_k_coefficients_count = 11;
const double type_k_coefficients[11] = {0,
										3.9450128025 * pow(10, 1),
										2.3622373598 * pow(10, -2),
									   -3.2858906784 * pow(10, -4),
									   -4.9904828777 * pow(10, -6),
									   -6.7509059173 * pow(10, -8),
									   -5.7410327428 * pow(10, -10),
									   -3.1088872894 * pow(10, -12),
									   -1.0451609365 * pow(10, -14),
									   -1.9889266878 * pow(10, -17),
									   -1.6322697486 * pow(10, -20)

};

// -270 to 0°C
const uint8_t type_t_coefficients_count = 15;
const double type_t_coefficients[15] = {0,
		 	 	 	 	 	 	 	 	3.8748106364 * pow(10, 1),
										4.4194434347 * pow(10, -2),
										1.1844323105 * pow(10, -4),
										2.0032973554 * pow(10, -5),
										9.0138019559 * pow(10, -7),
										2.2651156593 * pow(10, -8),
										3.6071154205 * pow(10, -10),
										3.8493939883 * pow(10, -12),
										2.8213521925 * pow(10, -14),
										1.4251594779 * pow(10, -16),
										4.8768662286 * pow(10, -19),
										1.0795539270 * pow(10, -21),
										1.3945027062 * pow(10, -24),
										7.9795153927 * pow(10, -28)
};

// -270 to 0°C
const uint8_t type_e_coefficients_count = 14;
const double type_e_coefficients[14] = {0,
										5.8665508708 * pow(10, 1),
										4.5410977124 * pow(10, -2),
									   -7.7998048686 * pow(10, -4),
									   -2.5800160843 * pow(10, -5),
									   -5.9452583057 * pow(10, -7),
									   -9.3214058667 * pow(10, -9),
									   -1.0287605534 * pow(10, -10),
									   -8.0370123621 * pow(10, -13),
									   -4.3979497391 * pow(10, -15),
									   -1.6414776355 * pow(10, -17),
									   -3.9673619516 * pow(10, -20),
									   -5.5827328721 * pow(10, -23),
									   -3.4657842013 * pow(10, -26)
};

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_DMA_Init(void);
static void MX_ADC1_Init(void);
static void MX_ADC3_Init(void);
static void MX_ADC4_Init(void);
static void MX_TIM2_Init(void);
static void MX_I2C3_Init(void);
static void MX_DAC1_Init(void);
static void MX_ADC2_Init(void);
/* USER CODE BEGIN PFP */
int InterpretConfig(void);
int InterpretVariable(char name[CFG_VAR_SIZE], char value[CFG_VAR_SIZE]);
int SetupMeasurement(void);
int SendParameters(void);
float MeasureVref(void);
int StartMeasurement(void);
int SendData(enum ADC_BUFFER_STATE usb_transmition_state);
int SendTrasmissionReport(void);
int ResetStates(void);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_ADC1_Init();
  MX_ADC3_Init();
  MX_ADC4_Init();
  MX_TIM2_Init();
  MX_USB_Device_Init();
  MX_I2C3_Init();
  MX_DAC1_Init();
  MX_ADC2_Init();
  /* USER CODE BEGIN 2 */
  ResetStates();

  int full_channels = 0;
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */

  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
	  if(prog_state == CFG_RECEIVED){
		  InterpretConfig();
	  }
	  if(prog_state == CFG_INTERPRETED){
		  SetupMeasurement();
	  }
	  if(prog_state == PARAMETERS_SET){
		  SendParameters();
	  }
	  if(prog_state == ARMED){
		  while(!measurement_activated);
		  StartMeasurement();
	  }
	  if(prog_state == MEASURING){
		 full_channels = 0;
		 for(int i = 0; i < MAX_CHANNEL_COUNT; i++){
			 if(!channel_enabled_status[i])
				 continue;
			 if(adc_states[i] == EMPTY)
				 break;

			 if(usb_transmition_state == EMPTY){
				 usb_transmition_state = adc_states[i];
			 }
			 else if(adc_states[i] != usb_transmition_state){
				 transmission_error = 1;
				 break;
			 }

			 full_channels++;
		 }

		 if(full_channels == channel_enabled_count){
			 SendData(usb_transmition_state);
			 usb_transmition_state = EMPTY;
		 }

		 if(current_packet_count >= target_packet_count) {
			 prog_state = REPORTING;
		 }
	  }
	  if(prog_state == REPORTING){
		  SendTrasmissionReport();
		  prog_state = DONE;
	  }
	  if(prog_state == DONE){

		  ResetStates();
	  }


  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1_BOOST);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI48|RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSI48State = RCC_HSI48_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = RCC_PLLM_DIV2;
  RCC_OscInitStruct.PLL.PLLN = 78;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV6;
  RCC_OscInitStruct.PLL.PLLQ = RCC_PLLQ_DIV2;
  RCC_OscInitStruct.PLL.PLLR = RCC_PLLR_DIV2;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_4) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief ADC1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC1_Init(void)
{

  /* USER CODE BEGIN ADC1_Init 0 */

  /* USER CODE END ADC1_Init 0 */

  ADC_MultiModeTypeDef multimode = {0};
  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC1_Init 1 */

  /* USER CODE END ADC1_Init 1 */

  /** Common config
  */
  hadc1.Instance = ADC1;
  hadc1.Init.ClockPrescaler = ADC_CLOCK_ASYNC_DIV1;
  hadc1.Init.Resolution = ADC_RESOLUTION_12B;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.GainCompensation = 0;
  hadc1.Init.ScanConvMode = ADC_SCAN_DISABLE;
  hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  hadc1.Init.LowPowerAutoWait = DISABLE;
  hadc1.Init.ContinuousConvMode = DISABLE;
  hadc1.Init.NbrOfConversion = 1;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConv = ADC_EXTERNALTRIG_T2_TRGO;
  hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_RISING;
  hadc1.Init.DMAContinuousRequests = ENABLE;
  hadc1.Init.Overrun = ADC_OVR_DATA_PRESERVED;
  hadc1.Init.OversamplingMode = ENABLE;
  hadc1.Init.Oversampling.Ratio = ADC_OVERSAMPLING_RATIO_32;
  hadc1.Init.Oversampling.RightBitShift = ADC_RIGHTBITSHIFT_1;
  hadc1.Init.Oversampling.TriggeredMode = ADC_TRIGGEREDMODE_SINGLE_TRIGGER;
  hadc1.Init.Oversampling.OversamplingStopReset = ADC_REGOVERSAMPLING_CONTINUED_MODE;
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure the ADC multi-mode
  */
  multimode.Mode = ADC_MODE_INDEPENDENT;
  if (HAL_ADCEx_MultiModeConfigChannel(&hadc1, &multimode) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_1;
  sConfig.Rank = ADC_REGULAR_RANK_1;
  sConfig.SamplingTime = ADC_SAMPLETIME_2CYCLES_5;
  sConfig.SingleDiff = ADC_SINGLE_ENDED;
  sConfig.OffsetNumber = ADC_OFFSET_NONE;
  sConfig.Offset = 0;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC1_Init 2 */

  /* USER CODE END ADC1_Init 2 */

}

/**
  * @brief ADC2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC2_Init(void)
{

  /* USER CODE BEGIN ADC2_Init 0 */

  /* USER CODE END ADC2_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC2_Init 1 */

  /* USER CODE END ADC2_Init 1 */

  /** Common config
  */
  hadc2.Instance = ADC2;
  hadc2.Init.ClockPrescaler = ADC_CLOCK_ASYNC_DIV1;
  hadc2.Init.Resolution = ADC_RESOLUTION_12B;
  hadc2.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc2.Init.GainCompensation = 0;
  hadc2.Init.ScanConvMode = ADC_SCAN_DISABLE;
  hadc2.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  hadc2.Init.LowPowerAutoWait = DISABLE;
  hadc2.Init.ContinuousConvMode = DISABLE;
  hadc2.Init.NbrOfConversion = 1;
  hadc2.Init.DiscontinuousConvMode = DISABLE;
  hadc2.Init.ExternalTrigConv = ADC_EXTERNALTRIG_T2_TRGO;
  hadc2.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_RISING;
  hadc2.Init.DMAContinuousRequests = ENABLE;
  hadc2.Init.Overrun = ADC_OVR_DATA_PRESERVED;
  hadc2.Init.OversamplingMode = ENABLE;
  hadc2.Init.Oversampling.Ratio = ADC_OVERSAMPLING_RATIO_32;
  hadc2.Init.Oversampling.RightBitShift = ADC_RIGHTBITSHIFT_1;
  hadc2.Init.Oversampling.TriggeredMode = ADC_TRIGGEREDMODE_SINGLE_TRIGGER;
  hadc2.Init.Oversampling.OversamplingStopReset = ADC_REGOVERSAMPLING_CONTINUED_MODE;
  if (HAL_ADC_Init(&hadc2) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_3;
  sConfig.Rank = ADC_REGULAR_RANK_1;
  sConfig.SamplingTime = ADC_SAMPLETIME_2CYCLES_5;
  sConfig.SingleDiff = ADC_SINGLE_ENDED;
  sConfig.OffsetNumber = ADC_OFFSET_NONE;
  sConfig.Offset = 0;
  if (HAL_ADC_ConfigChannel(&hadc2, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC2_Init 2 */

  /* USER CODE END ADC2_Init 2 */

}

/**
  * @brief ADC3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC3_Init(void)
{

  /* USER CODE BEGIN ADC3_Init 0 */

  /* USER CODE END ADC3_Init 0 */

  ADC_MultiModeTypeDef multimode = {0};
  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC3_Init 1 */

  /* USER CODE END ADC3_Init 1 */

  /** Common config
  */
  hadc3.Instance = ADC3;
  hadc3.Init.ClockPrescaler = ADC_CLOCK_ASYNC_DIV1;
  hadc3.Init.Resolution = ADC_RESOLUTION_12B;
  hadc3.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc3.Init.GainCompensation = 0;
  hadc3.Init.ScanConvMode = ADC_SCAN_DISABLE;
  hadc3.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  hadc3.Init.LowPowerAutoWait = DISABLE;
  hadc3.Init.ContinuousConvMode = DISABLE;
  hadc3.Init.NbrOfConversion = 1;
  hadc3.Init.DiscontinuousConvMode = DISABLE;
  hadc3.Init.ExternalTrigConv = ADC_EXTERNALTRIG_T2_TRGO;
  hadc3.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_RISING;
  hadc3.Init.DMAContinuousRequests = ENABLE;
  hadc3.Init.Overrun = ADC_OVR_DATA_PRESERVED;
  hadc3.Init.OversamplingMode = ENABLE;
  hadc3.Init.Oversampling.Ratio = ADC_OVERSAMPLING_RATIO_32;
  hadc3.Init.Oversampling.RightBitShift = ADC_RIGHTBITSHIFT_1;
  hadc3.Init.Oversampling.TriggeredMode = ADC_TRIGGEREDMODE_SINGLE_TRIGGER;
  hadc3.Init.Oversampling.OversamplingStopReset = ADC_REGOVERSAMPLING_CONTINUED_MODE;
  if (HAL_ADC_Init(&hadc3) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure the ADC multi-mode
  */
  multimode.Mode = ADC_MODE_INDEPENDENT;
  if (HAL_ADCEx_MultiModeConfigChannel(&hadc3, &multimode) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_1;
  sConfig.Rank = ADC_REGULAR_RANK_1;
  sConfig.SamplingTime = ADC_SAMPLETIME_2CYCLES_5;
  sConfig.SingleDiff = ADC_SINGLE_ENDED;
  sConfig.OffsetNumber = ADC_OFFSET_NONE;
  sConfig.Offset = 0;
  if (HAL_ADC_ConfigChannel(&hadc3, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC3_Init 2 */

  /* USER CODE END ADC3_Init 2 */

}

/**
  * @brief ADC4 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC4_Init(void)
{

  /* USER CODE BEGIN ADC4_Init 0 */

  /* USER CODE END ADC4_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC4_Init 1 */

  /* USER CODE END ADC4_Init 1 */

  /** Common config
  */
  hadc4.Instance = ADC4;
  hadc4.Init.ClockPrescaler = ADC_CLOCK_ASYNC_DIV1;
  hadc4.Init.Resolution = ADC_RESOLUTION_12B;
  hadc4.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc4.Init.GainCompensation = 0;
  hadc4.Init.ScanConvMode = ADC_SCAN_DISABLE;
  hadc4.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  hadc4.Init.LowPowerAutoWait = DISABLE;
  hadc4.Init.ContinuousConvMode = DISABLE;
  hadc4.Init.NbrOfConversion = 1;
  hadc4.Init.DiscontinuousConvMode = DISABLE;
  hadc4.Init.ExternalTrigConv = ADC_EXTERNALTRIG_T2_TRGO;
  hadc4.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_RISING;
  hadc4.Init.DMAContinuousRequests = ENABLE;
  hadc4.Init.Overrun = ADC_OVR_DATA_PRESERVED;
  hadc4.Init.OversamplingMode = ENABLE;
  hadc4.Init.Oversampling.Ratio = ADC_OVERSAMPLING_RATIO_32;
  hadc4.Init.Oversampling.RightBitShift = ADC_RIGHTBITSHIFT_1;
  hadc4.Init.Oversampling.TriggeredMode = ADC_TRIGGEREDMODE_SINGLE_TRIGGER;
  hadc4.Init.Oversampling.OversamplingStopReset = ADC_REGOVERSAMPLING_CONTINUED_MODE;
  if (HAL_ADC_Init(&hadc4) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_5;
  sConfig.Rank = ADC_REGULAR_RANK_1;
  sConfig.SamplingTime = ADC_SAMPLETIME_2CYCLES_5;
  sConfig.SingleDiff = ADC_SINGLE_ENDED;
  sConfig.OffsetNumber = ADC_OFFSET_NONE;
  sConfig.Offset = 0;
  if (HAL_ADC_ConfigChannel(&hadc4, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC4_Init 2 */

  /* USER CODE END ADC4_Init 2 */

}

/**
  * @brief DAC1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_DAC1_Init(void)
{

  /* USER CODE BEGIN DAC1_Init 0 */

  /* USER CODE END DAC1_Init 0 */

  DAC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN DAC1_Init 1 */

  /* USER CODE END DAC1_Init 1 */

  /** DAC Initialization
  */
  hdac1.Instance = DAC1;
  if (HAL_DAC_Init(&hdac1) != HAL_OK)
  {
    Error_Handler();
  }

  /** DAC channel OUT1 config
  */
  sConfig.DAC_HighFrequency = DAC_HIGH_FREQUENCY_INTERFACE_MODE_AUTOMATIC;
  sConfig.DAC_DMADoubleDataMode = DISABLE;
  sConfig.DAC_SignedFormat = DISABLE;
  sConfig.DAC_SampleAndHold = DAC_SAMPLEANDHOLD_DISABLE;
  sConfig.DAC_Trigger = DAC_TRIGGER_NONE;
  sConfig.DAC_Trigger2 = DAC_TRIGGER_NONE;
  sConfig.DAC_OutputBuffer = DAC_OUTPUTBUFFER_ENABLE;
  sConfig.DAC_ConnectOnChipPeripheral = DAC_CHIPCONNECT_EXTERNAL;
  sConfig.DAC_UserTrimming = DAC_TRIMMING_USER;
  sConfig.DAC_TrimmingValue = 1;
  if (HAL_DAC_ConfigChannel(&hdac1, &sConfig, DAC_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN DAC1_Init 2 */

  /* USER CODE END DAC1_Init 2 */

}

/**
  * @brief I2C3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_I2C3_Init(void)
{

  /* USER CODE BEGIN I2C3_Init 0 */

  /* USER CODE END I2C3_Init 0 */

  /* USER CODE BEGIN I2C3_Init 1 */

  /* USER CODE END I2C3_Init 1 */
  hi2c3.Instance = I2C3;
  hi2c3.Init.Timing = 0x40707EB4;
  hi2c3.Init.OwnAddress1 = 144;
  hi2c3.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c3.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c3.Init.OwnAddress2 = 0;
  hi2c3.Init.OwnAddress2Masks = I2C_OA2_NOMASK;
  hi2c3.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c3.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c3) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Analogue filter
  */
  if (HAL_I2CEx_ConfigAnalogFilter(&hi2c3, I2C_ANALOGFILTER_ENABLE) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Digital filter
  */
  if (HAL_I2CEx_ConfigDigitalFilter(&hi2c3, 0) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN I2C3_Init 2 */

  /* USER CODE END I2C3_Init 2 */

}

/**
  * @brief TIM2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM2_Init(void)
{

  /* USER CODE BEGIN TIM2_Init 0 */

  /* USER CODE END TIM2_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM2_Init 1 */

  /* USER CODE END TIM2_Init 1 */
  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 156 - 1;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 9;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim2) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim2, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_UPDATE;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM2_Init 2 */

  /* USER CODE END TIM2_Init 2 */

}

/**
  * Enable DMA controller clock
  */
static void MX_DMA_Init(void)
{

  /* DMA controller clock enable */
  __HAL_RCC_DMAMUX1_CLK_ENABLE();
  __HAL_RCC_DMA1_CLK_ENABLE();

  /* DMA interrupt init */
  /* DMA1_Channel1_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA1_Channel1_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(DMA1_Channel1_IRQn);
  /* DMA1_Channel2_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA1_Channel2_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(DMA1_Channel2_IRQn);
  /* DMA1_Channel3_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA1_Channel3_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(DMA1_Channel3_IRQn);
  /* DMA1_Channel4_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA1_Channel4_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(DMA1_Channel4_IRQn);

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
/* USER CODE BEGIN MX_GPIO_Init_1 */
/* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOF_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();
  __HAL_RCC_GPIOC_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOB, ERRATA_FIX1_Pin|ERRATA_FIX2_Pin|ERRATA_FIX3_Pin|ERRATA_FIX4_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOC, IND_LED_R_Pin|IND_LED_G_Pin|IND_LED_B_Pin, GPIO_PIN_SET);

  /*Configure GPIO pins : ERRATA_FIX1_Pin ERRATA_FIX2_Pin ERRATA_FIX3_Pin ERRATA_FIX4_Pin */
  GPIO_InitStruct.Pin = ERRATA_FIX1_Pin|ERRATA_FIX2_Pin|ERRATA_FIX3_Pin|ERRATA_FIX4_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  /*Configure GPIO pin : TEMP_ALERT_Pin */
  GPIO_InitStruct.Pin = TEMP_ALERT_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(TEMP_ALERT_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pins : IND_LED_R_Pin IND_LED_G_Pin IND_LED_B_Pin */
  GPIO_InitStruct.Pin = IND_LED_R_Pin|IND_LED_G_Pin|IND_LED_B_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pin : TRIG_SHORT_Pin */
  GPIO_InitStruct.Pin = TRIG_SHORT_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(TRIG_SHORT_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : TRIG_EXT_2_Pin */
  GPIO_InitStruct.Pin = TRIG_EXT_2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(TRIG_EXT_2_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : TRIG_EXT_1_Pin */
  GPIO_InitStruct.Pin = TRIG_EXT_1_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
  GPIO_InitStruct.Pull = GPIO_PULLDOWN;
  HAL_GPIO_Init(TRIG_EXT_1_GPIO_Port, &GPIO_InitStruct);

  /* EXTI interrupt init*/
  HAL_NVIC_SetPriority(EXTI9_5_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(EXTI9_5_IRQn);

/* USER CODE BEGIN MX_GPIO_Init_2 */
/* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */

int InterpretConfig(void) {
	char variable_name[CFG_VAR_SIZE];
	char variable_value[CFG_VAR_SIZE];
	memset(variable_name, 0, sizeof(variable_name));
	memset(variable_value, 0, sizeof(variable_value));
	int variable_name_indexes[2] = {0, 0};
	int variable_value_indexes[2] = {0, 0};
	char reading_status = 'n';
	for(int i = 0; i < USB_RX_BUFFER_SIZE; i++){
		if(rx_buffer[i] == '\0'){
			break;
		}
		// Reading the variable name
		if(reading_status == 'n'){
			if(rx_buffer[i] == ':') {
				variable_name_indexes[1] = i;
				variable_value_indexes[0] = i+1;
				reading_status = 'v';
			}
		}
		// Reading the variable value
		else if(reading_status == 'v'){
			if(rx_buffer[i] == ';') {
				variable_value_indexes[1] = i;

				strncpy(variable_name, ((char*)rx_buffer + variable_name_indexes[0]), (variable_name_indexes[1] - variable_name_indexes[0]));
				variable_name[variable_name_indexes[1] + 1] = '\0';
				strncpy(variable_value, ((char*)rx_buffer + variable_value_indexes[0]), (variable_value_indexes[1] - variable_value_indexes[0]));
				variable_value[variable_value_indexes[1] + 1] = '\0';

				InterpretVariable(variable_name, variable_value);
				memset(variable_name, 0, sizeof(variable_name));
				memset(variable_value, 0, sizeof(variable_value));
				variable_name_indexes[0] = i + 1;
				reading_status = 'n';
			}
		}
	}

	prog_state = CFG_INTERPRETED;
	return 1;
}

int InterpretVariable(char name[CFG_VAR_SIZE], char value[CFG_VAR_SIZE]) {
	if(strcmp(name, "RecLen") == 0) {
		record_length_ms = (uint16_t)atoi(value);
	}
	else if(strcmp(name, "RecInt") == 0) {
		record_interval_us = (uint16_t)atoi(value);
	}
	else if(strcmp(name, "TcType") == 0) {
		tc_type = value[0];
	}
	else if(strcmp(name, "EnChan") == 0) {
		int channel_index = 0;
		char *channel_status = strtok(value, "|");

		while(channel_status != NULL) {
			channel_enabled_status[channel_index] = channel_status[0] - '0';
			channel_status = strtok(NULL, "|");
			channel_index++;
		}

		for(int i = 0; i < MAX_CHANNEL_COUNT; i++){
			channel_enabled_count += channel_enabled_status[i];
		}
	}

	return 1;
}

int SetupMeasurement(void){
	// > Set the correct analog reference voltage and get the relevant coefficients

	const double *used_coefficients;
	uint8_t coefficients_count;
	if(tc_type == 'E') {
		HAL_SYSCFG_VREFBUF_VoltageScalingConfig(SYSCFG_VREFBUF_VOLTAGE_SCALE2); // 2.9V
		used_coefficients = type_e_coefficients;
		coefficients_count = type_e_coefficients_count;
	}
	else if(tc_type == 'J') {
		HAL_SYSCFG_VREFBUF_VoltageScalingConfig(SYSCFG_VREFBUF_VOLTAGE_SCALE1); // 2.5V
		used_coefficients = type_j_coefficients;
		coefficients_count = type_j_coefficients_count;
	}
	else if(tc_type == 'K') {
		HAL_SYSCFG_VREFBUF_VoltageScalingConfig(SYSCFG_VREFBUF_VOLTAGE_SCALE0); // 2.048V
		used_coefficients = type_k_coefficients;
		coefficients_count = type_k_coefficients_count;
	}
	else if(tc_type == 'T') {
		HAL_SYSCFG_VREFBUF_VoltageScalingConfig(SYSCFG_VREFBUF_VOLTAGE_SCALE0); // 2.048V
		used_coefficients = type_t_coefficients;
		coefficients_count = type_t_coefficients_count;
	}

	// Measure the actual analog reference voltage
	HAL_Delay(100);
	analog_reference_voltage = MeasureVref();
	adc_states[0] = EMPTY;
	dropped_packet_count = 0;

	// > Calculate and set ADC sync timer
	__HAL_TIM_SET_AUTORELOAD(&htim2, record_interval_us - 1);
	__HAL_TIM_SET_COUNTER(&htim2, record_interval_us - 1);

	// > Calculate and set DAC value

	// Initiate a one shot temperature conversion
	uint8_t one_shot_conversion_command = 0b01000100;
	HAL_I2C_Mem_Write(&hi2c3, (TEMP_SENSOR_ADDR << 1), 0x1, I2C_MEMADD_SIZE_8BIT, &one_shot_conversion_command, 1, HAL_MAX_DELAY);
	// Read the temperature
	uint8_t temp_buffer[2];
	HAL_I2C_Mem_Read(&hi2c3, (TEMP_SENSOR_ADDR << 1), 0x0, I2C_MEMADD_SIZE_8BIT, temp_buffer, 2, HAL_MAX_DELAY);

	// Calculate the temperature in C
	uint8_t negative_temperature_flag = temp_buffer[0] >> 7;
	temp_buffer[0] &= 0b01111111;
	uint16_t sensor_output = (temp_buffer[0] << 2) | (temp_buffer[1] >> 6);

	if(negative_temperature_flag) {
		cold_junction_temp = (sensor_output - 512)/4.0;
	}
	else{
		cold_junction_temp = (sensor_output)/4.0;
	}

	// Calculate the required DAC offset
	float cjc_offset_temperature = MINIMUM_TEMPERATURE - cold_junction_temp;
	double cjc_offset_voltage = 0;
	for(int i = 0; i < coefficients_count; i++) {
		cjc_offset_voltage += used_coefficients[i] * pow(cjc_offset_temperature, i);
	}

	double total_offset_calc = INAMP_OUTPUT_BUFFER_OFFSET + ((-1) * (cjc_offset_voltage * pow(10, -6)) * INAMP_GAIN);
	uint32_t offset = (uint32_t)(total_offset_calc * 4096) / analog_reference_voltage;
	applied_voltage_offset = (float)(offset * analog_reference_voltage) / 4096;

	// Calibrate the DAC
	DAC_ChannelConfTypeDef sConfig = {0};
	sConfig.DAC_HighFrequency = DAC_HIGH_FREQUENCY_INTERFACE_MODE_AUTOMATIC;
	sConfig.DAC_DMADoubleDataMode = DISABLE;
	sConfig.DAC_SignedFormat = DISABLE;
	sConfig.DAC_SampleAndHold = DAC_SAMPLEANDHOLD_DISABLE;
	sConfig.DAC_Trigger = DAC_TRIGGER_NONE;
	sConfig.DAC_Trigger2 = DAC_TRIGGER_NONE;
	sConfig.DAC_OutputBuffer = DAC_OUTPUTBUFFER_ENABLE;
	sConfig.DAC_ConnectOnChipPeripheral = DAC_CHIPCONNECT_EXTERNAL;
	sConfig.DAC_UserTrimming = DAC_TRIMMING_USER;
	if (HAL_DAC_ConfigChannel(&hdac1, &sConfig, DAC_CHANNEL_1) != HAL_OK)
	{
	Error_Handler();
	}
	HAL_DACEx_SelfCalibrate(&hdac1, &sConfig, DAC_CHANNEL_1);

	// Set the DAC voltage
	HAL_DAC_SetValue(&hdac1, DAC_CHANNEL_1, DAC_ALIGN_12B_R, offset);
	HAL_DAC_Start(&hdac1, DAC_CHANNEL_1);


	// Calculate the target packet number
	target_packet_count = (record_length_ms * 1000.0 / record_interval_us) / (ADC_BUFFER_SIZE / 2);
	if((int)(record_length_ms * 1000.0 / record_interval_us) % (ADC_BUFFER_SIZE / 2) != 0){
		target_packet_count += 1;
	}

	prog_state = PARAMETERS_SET;
	return 1;
}

float MeasureVref(void) {
	HAL_ADC_DeInit(&hadc1);

	// Measure Vref
	hadc1.Instance = ADC1;
	hadc1.Init.ClockPrescaler = ADC_CLOCK_ASYNC_DIV1;
	hadc1.Init.Resolution = ADC_RESOLUTION_12B;
	hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
	hadc1.Init.GainCompensation = 0;
	hadc1.Init.ScanConvMode = ADC_SCAN_DISABLE;
	hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
	hadc1.Init.LowPowerAutoWait = DISABLE;
	hadc1.Init.ContinuousConvMode = DISABLE;
	hadc1.Init.NbrOfConversion = 1;
	hadc1.Init.DiscontinuousConvMode = DISABLE;
	hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
	hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
	hadc1.Init.DMAContinuousRequests = ENABLE;
	hadc1.Init.Overrun = ADC_OVR_DATA_PRESERVED;
	hadc1.Init.OversamplingMode = DISABLE;
	if (HAL_ADC_Init(&hadc1) != HAL_OK) {
		Error_Handler();
	}

	ADC_MultiModeTypeDef multimode = {0};

	multimode.Mode = ADC_MODE_INDEPENDENT;
	if (HAL_ADCEx_MultiModeConfigChannel(&hadc1, &multimode) != HAL_OK) {
		Error_Handler();
	}

	ADC_ChannelConfTypeDef sConfig = {0};

	sConfig.Channel = ADC_CHANNEL_VREFINT;
	sConfig.Rank = ADC_REGULAR_RANK_1;
	sConfig.SamplingTime = ADC_SAMPLETIME_640CYCLES_5;
	sConfig.SingleDiff = ADC_SINGLE_ENDED;
	sConfig.OffsetNumber = ADC_OFFSET_NONE;
	sConfig.Offset = 0;
	if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK) {
		Error_Handler();
	}

	uint16_t vrefint_data = 0;
	HAL_ADCEx_Calibration_Start(&hadc1, ADC_SINGLE_ENDED);
	HAL_ADC_Start_DMA(&hadc1, (uint32_t*)&vrefint_data, 1);
	HAL_Delay(1);
	HAL_ADC_Stop_DMA(&hadc1);

	uint16_t vrefint_cal;
	vrefint_cal= *((uint16_t*)VREFINT_CAL_ADDR);

	float vref = (VREFINT_CAL_VREF / 1000.0) * (float)vrefint_cal / (float)vrefint_data;

	// Return ADC to initial state
	HAL_ADC_DeInit(&hadc1);
	MX_ADC1_Init();

	return vref;
}

int SendParameters(void) {
	unsigned char parameters_msg[PARAMETERS_MSG_SIZE];

	sprintf((char *)parameters_msg, "CjcTmp:%.2f;AlgRfr:%.3f;AplOfs:%.4f;AdcBuf:%d;PktCnt:%d\n",
									cold_junction_temp,
									analog_reference_voltage,
									applied_voltage_offset,
									ADC_BUFFER_SIZE,
									target_packet_count);
	uint16_t line_len = strlen((char *)parameters_msg);
	while(CDC_Transmit_FS(parameters_msg, line_len) != USBD_OK);

	HAL_GPIO_WritePin(IND_LED_G_GPIO_Port, IND_LED_G_Pin, GPIO_PIN_SET);
	HAL_GPIO_WritePin(IND_LED_R_GPIO_Port, IND_LED_R_Pin, GPIO_PIN_SET);
	HAL_GPIO_WritePin(IND_LED_B_GPIO_Port, IND_LED_B_Pin, GPIO_PIN_RESET);
	measurement_activated = 0;
	prog_state = ARMED;

	return 1;
}

int StartMeasurement(void) {
	HAL_GPIO_WritePin(IND_LED_G_GPIO_Port, IND_LED_G_Pin, GPIO_PIN_SET);
	HAL_GPIO_WritePin(IND_LED_R_GPIO_Port, IND_LED_R_Pin, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(IND_LED_B_GPIO_Port, IND_LED_B_Pin, GPIO_PIN_SET);

	// Setup ADCs
	if(channel_enabled_status[0]){
		HAL_ADCEx_Calibration_Start(&hadc1, ADC_SINGLE_ENDED);
		HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buffers[0], ADC_BUFFER_SIZE);
	}
	if(channel_enabled_status[1]){
		HAL_ADCEx_Calibration_Start(&hadc2, ADC_SINGLE_ENDED);
		HAL_ADC_Start_DMA(&hadc2, (uint32_t*)adc_buffers[1], ADC_BUFFER_SIZE);
	}
	if(channel_enabled_status[2]){
		HAL_ADCEx_Calibration_Start(&hadc3, ADC_SINGLE_ENDED);
		HAL_ADC_Start_DMA(&hadc3, (uint32_t*)adc_buffers[2], ADC_BUFFER_SIZE);
	}
	if(channel_enabled_status[3]){
		HAL_ADCEx_Calibration_Start(&hadc4, ADC_SINGLE_ENDED);
		HAL_ADC_Start_DMA(&hadc4, (uint32_t*)adc_buffers[3], ADC_BUFFER_SIZE);
	}

	HAL_TIM_Base_Start_IT(&htim2);

	prog_state = MEASURING;

	return 1;
}

// Called when first half of buffer is filled
void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef* hadc) {
	int adc_index;

	if (hadc == &hadc1){
		adc_index = 0;
	}
	else if(hadc == &hadc2){
		adc_index = 1;
	}
	else if(hadc == &hadc3){
		adc_index = 2;
	}
	else if(hadc == &hadc4){
		adc_index = 3;
	}

	if (adc_states[adc_index] != EMPTY)
		dropped_packet_count++;
	adc_states[adc_index] = START_FULL;
}

// Called when buffer is completely filled
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef* hadc) {
	int adc_index;

	if (hadc == &hadc1){
		adc_index = 0;
	}
	else if(hadc == &hadc2){
		adc_index = 1;
	}
	else if(hadc == &hadc3){
		adc_index = 2;
	}
	else if(hadc == &hadc4){
		adc_index = 3;
	}

	if (adc_states[adc_index] != EMPTY)
		dropped_packet_count++;
	adc_states[adc_index] = END_FULL;
}

unsigned char usb_buffer[USB_BUFFER_SIZE];
unsigned int usb_buffer_index;
unsigned int adc_buffer_start_index;

int SendData(enum ADC_BUFFER_STATE usb_transmition_state) {
	// > Create the USB buffer data
	if(usb_transmition_state == START_FULL){
		adc_buffer_start_index = 0;
	}
	else if(usb_transmition_state == END_FULL){
		adc_buffer_start_index = ADC_BUFFER_SIZE/2;
	}

	usb_buffer_index = 0;
	for(int channel_index = 0; channel_index < MAX_CHANNEL_COUNT; channel_index++) {
		if(!channel_enabled_status[channel_index])
			continue;

		for(int i = 0; i < ADC_BUFFER_SIZE/2; i++){
			usb_buffer[usb_buffer_index + (i*2) + 1] = (uint8_t)(adc_buffers[channel_index][adc_buffer_start_index + i] & 0x00FF);
			usb_buffer[usb_buffer_index + i*2] = (uint8_t)((adc_buffers[channel_index][adc_buffer_start_index + i] >> 8) & 0x00FF);
		}
		adc_states[channel_index] = EMPTY;
		usb_buffer_index += ADC_BUFFER_SIZE;
	}

	while(CDC_Transmit_FS(usb_buffer, usb_buffer_index) != USBD_OK);

	current_packet_count++;

	return 1;
}

int SendTrasmissionReport(void) {
	unsigned char report_msg[REPORT_MSG_SIZE];

	sprintf((char *)report_msg, "TrsErr:%d;DrpPkt:%d\n",
									transmission_error,
									dropped_packet_count);
	uint16_t line_len = strlen((char *)report_msg);
	while(CDC_Transmit_FS(report_msg, line_len) != USBD_OK);

	prog_state = DONE;

	return 1;
}

int ResetStates(void) {
	  HAL_TIM_Base_Stop_IT(&htim2);
	  HAL_ADC_Stop_DMA(&hadc1);
	  HAL_ADC_Stop_DMA(&hadc2);
	  HAL_ADC_Stop_DMA(&hadc3);
	  HAL_ADC_Stop_DMA(&hadc4);
	  memset(adc_buffers, 0, sizeof(adc_buffers));
	  prog_state = IDLE;
	  conv_count_reached = 0;
	  target_packet_count = 0;
	  current_packet_count = 0;
	  measurement_activated = 0;
	  channel_enabled_count = 0;
	  dropped_packet_count = 0;
	  transmission_error = 0;

	  HAL_GPIO_WritePin(IND_LED_G_GPIO_Port, IND_LED_G_Pin, GPIO_PIN_RESET);
	  HAL_GPIO_WritePin(IND_LED_R_GPIO_Port, IND_LED_R_Pin, GPIO_PIN_SET);
	  HAL_GPIO_WritePin(IND_LED_B_GPIO_Port, IND_LED_B_Pin, GPIO_PIN_SET);

	  return 1;
}


/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
