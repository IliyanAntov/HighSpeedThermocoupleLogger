/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
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

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32g4xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <math.h>
/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */
enum CONV_STATE {
  IDLE,
  CFG_RECEIVED,
  CFG_INTERPRETED,
  PARAMETERS_SET,
  ARMED,
  MEASURING,
  DONE,
  SENDING
};

enum ADC_BUFFER_STATE {
	EMPTY,
	START_FULL,
	END_FULL
};

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define ERRATA_FIX1_Pin GPIO_PIN_10
#define ERRATA_FIX1_GPIO_Port GPIOB
#define ERRATA_FIX2_Pin GPIO_PIN_11
#define ERRATA_FIX2_GPIO_Port GPIOB
#define ERRATA_FIX3_Pin GPIO_PIN_13
#define ERRATA_FIX3_GPIO_Port GPIOB
#define ERRATA_FIX4_Pin GPIO_PIN_14
#define ERRATA_FIX4_GPIO_Port GPIOB
#define TEMP_SCL_Pin GPIO_PIN_8
#define TEMP_SCL_GPIO_Port GPIOC
#define TEMP_SDA_Pin GPIO_PIN_9
#define TEMP_SDA_GPIO_Port GPIOC
#define TEMP_ALERT_Pin GPIO_PIN_8
#define TEMP_ALERT_GPIO_Port GPIOA
#define T_SWDIO_Pin GPIO_PIN_13
#define T_SWDIO_GPIO_Port GPIOA
#define T_SWCLK_Pin GPIO_PIN_14
#define T_SWCLK_GPIO_Port GPIOA
#define IND_LED_R_Pin GPIO_PIN_10
#define IND_LED_R_GPIO_Port GPIOC
#define IND_LED_G_Pin GPIO_PIN_11
#define IND_LED_G_GPIO_Port GPIOC
#define IND_LED_B_Pin GPIO_PIN_12
#define IND_LED_B_GPIO_Port GPIOC
#define T_SWO_Pin GPIO_PIN_3
#define T_SWO_GPIO_Port GPIOB
#define TRIG_SHORT_Pin GPIO_PIN_5
#define TRIG_SHORT_GPIO_Port GPIOB
#define TRIG_SHORT_EXTI_IRQn EXTI9_5_IRQn
#define TRIG_EXT_2_Pin GPIO_PIN_6
#define TRIG_EXT_2_GPIO_Port GPIOB
#define TRIG_EXT_2_EXTI_IRQn EXTI9_5_IRQn
#define TRIG_EXT_1_Pin GPIO_PIN_7
#define TRIG_EXT_1_GPIO_Port GPIOB
#define TRIG_EXT_1_EXTI_IRQn EXTI9_5_IRQn

/* USER CODE BEGIN Private defines */
#define TEMP_SENSOR_ADDR 0b1001000

#define INAMP_OUTPUT_BUFFER_OFFSET 0.2		// Compensating for the opamp minimum output voltage
#define MINIMUM_TEMPERATURE -20				// °C
#define INAMP_GAIN ((9900 / 54.9) + 1)

#define MAX_CHANNEL_COUNT 4
#define ADC_BUFFER_SIZE 1000									// uint16
#define USB_TX_BUFFER_SIZE ADC_BUFFER_SIZE * MAX_CHANNEL_COUNT	// uint8
#define USB_TX_HEADER_SIZE 256
#define USB_RX_BUFFER_SIZE 256 									// uint8
#define CFG_VAR_SIZE 64
/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
