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

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */
enum PROG_STATE {
  IDLE,
  CFG_RECEIVED,
  CFG_INTERPRETED,
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

enum TRIG_SOURCE {
	TRIG_SHORT,
	TRIG_EXT_1,
	TRIG_EXT_2
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
#define B1_Pin GPIO_PIN_13
#define B1_GPIO_Port GPIOC
#define B1_EXTI_IRQn EXTI15_10_IRQn
#define USB_EN_Pin GPIO_PIN_0
#define USB_EN_GPIO_Port GPIOC
#define TEST_OUT2_Pin GPIO_PIN_1
#define TEST_OUT2_GPIO_Port GPIOC
#define TEST_OUT_Pin GPIO_PIN_1
#define TEST_OUT_GPIO_Port GPIOA
#define LPUART1_TX_Pin GPIO_PIN_2
#define LPUART1_TX_GPIO_Port GPIOA
#define LPUART1_RX_Pin GPIO_PIN_3
#define LPUART1_RX_GPIO_Port GPIOA
#define LD2_Pin GPIO_PIN_5
#define LD2_GPIO_Port GPIOA
#define T_SWDIO_Pin GPIO_PIN_13
#define T_SWDIO_GPIO_Port GPIOA
#define T_SWCLK_Pin GPIO_PIN_14
#define T_SWCLK_GPIO_Port GPIOA
#define T_SWO_Pin GPIO_PIN_3
#define T_SWO_GPIO_Port GPIOB

/* USER CODE BEGIN Private defines */
#define MAX_CHANNEL_COUNT 4
#define ADC_BUFFER_SIZE 2000														// uint16
#define USB_HEADER_SIZE 20															// uint8
#define USB_TX_BUFFER_SIZE USB_HEADER_SIZE + (ADC_BUFFER_SIZE * MAX_CHANNEL_COUNT) 	// uint8
#define USB_RX_BUFFER_SIZE 64 														// uint8
#define CFG_VAR_SIZE 64
/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
