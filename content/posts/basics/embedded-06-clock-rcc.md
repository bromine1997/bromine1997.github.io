---
title: "[임베디드 기초] 6편 - 클럭 트리와 RCC: 주파수는 어디서 오는가"
date: 2026-06-16T20:00:00+09:00
tags: ["embedded", "STM32", "clock", "RCC", "PLL", "HSE", "HSI", "APB"]
categories: ["Embedded Basic"]
description: "크리스탈에서 168MHz까지 — STM32F4의 클럭 소스, PLL 동작 원리, AHB/APB 분주 구조를 정리한다."
---

## 들어가며

UART 보드레이트를 설정할 때 `115200`을 입력한다. SPI 속도를 설정할 때 분주비(prescaler)를 고른다. 이 숫자들의 근거가 뭘까.

전부 **클럭(Clock)** 에서 나온다. MCU 안의 모든 주변장치는 클럭 신호를 기반으로 동작하고, 그 클럭이 얼마인지에 따라 통신 속도가 결정된다.

STM32F4 기준으로 클럭이 어떻게 만들어지고, 어떻게 각 주변장치로 전달되는지 정리한다.

---

## 클럭 소스 (Clock Source)

MCU는 기준 클럭을 어딘가에서 공급받아야 한다. STM32F4의 주요 클럭 소스는 두 가지다.

### HSI (High Speed Internal)

- MCU **내부** RC 오실레이터
- **16 MHz** 고정
- 외부 부품 불필요
- 정밀도 낮음 — 온도와 전압에 따라 ±1% 수준의 오차
- 리셋 직후 기본으로 사용되는 클럭 소스

### HSE (High Speed External)

- 외부 **크리스탈** 또는 오실레이터를 보드에 연결
- 4 ~ 26 MHz 범위
- 정밀도 높음 — 크리스탈 기준 ±20ppm 수준
- STM32F4-NUCLEO 보드는 8 MHz 크리스탈 장착

리셋 직후에는 HSI로 동작하다가, `SystemInit()`이 HSE와 PLL을 설정해 원하는 속도로 올린다. 4편에서 Reset_Handler가 `main()` 전에 `SystemInit()`을 호출한다고 설명했다.

---

## PLL (Phase-Locked Loop)

8 MHz 크리스탈로 168 MHz를 만들려면 21배를 올려야 한다. 이를 담당하는 것이 PLL이다.

PLL은 입력 클럭을 분주(divide)하고 체배(multiply)해서 원하는 주파수를 만든다. STM32F4의 메인 PLL은 M, N, P 세 파라미터로 제어한다.

```
VCO 입력  = HSE / M
VCO 클럭  = VCO 입력 × N
SYSCLK    = VCO 클럭 / P
```

STM32F4 168 MHz 설정 예:

```
VCO 입력 = 8 MHz / 8    = 1 MHz
VCO 클럭 = 1 MHz × 336  = 336 MHz
SYSCLK   = 336 MHz / 2  = 168 MHz

→ M=8, N=336, P=2
```

VCO(Voltage Controlled Oscillator)가 내부에서 실제로 주파수를 만들고, P로 나눠 최종 SYSCLK를 출력한다. VCO 클럭은 192 ~ 432 MHz 범위여야 한다는 제약이 있다.

CubeMX를 쓰면 이 계산을 자동으로 해주지만, 값이 어떻게 나왔는지 이해하고 있어야 디버깅할 때 막히지 않는다.

---

## 클럭 트리 (Clock Tree)

SYSCLK 하나로 모든 주변장치가 동작하지는 않는다. 버스와 주변장치마다 허용 최대 클럭이 다르기 때문에 분주해서 여러 클럭을 만든다.

```
HSE (8MHz) → PLL → SYSCLK (168MHz)
                        │
              AHB Prescaler (÷1)
                        │
                   HCLK (168MHz) ─── CPU, DMA, Flash, SDIO
                        │
           ┌────────────┴────────────┐
  APB1 Prescaler (÷4)      APB2 Prescaler (÷2)
           │                         │
      PCLK1 (42MHz)             PCLK2 (84MHz)
      UART2/3/4/5               UART1/6
      SPI2/3                    SPI1/4/5
      I2C1/2/3                  ADC1/2/3
      TIM2/3/4/5/6/7            TIM1/8/9/10/11
```

같은 UART라도 번호에 따라 연결된 APB가 다르다. UART2는 APB1(42 MHz)을, UART1은 APB2(84 MHz)를 기준으로 보드레이트를 계산한다. 같은 `115200` 설정이어도 내부 레지스터 값이 다르다.

---

## RCC (Reset and Clock Control)

클럭 트리를 설정하는 STM32 모듈이다. 이름대로 리셋 제어와 클럭 제어를 담당한다.

### 클럭 활성화

각 주변장치는 RCC에서 클럭을 켜줘야 동작한다. 이걸 빠뜨리면 레지스터에 값을 써도 아무 반응이 없다.

```c
// GPIO 클럭 활성화
__HAL_RCC_GPIOA_CLK_ENABLE();

// UART2 클럭 활성화
__HAL_RCC_USART2_CLK_ENABLE();

// SPI1 클럭 활성화
__HAL_RCC_SPI1_CLK_ENABLE();
```

HAL 라이브러리의 `HAL_UART_Init()` 같은 함수는 내부에서 자동으로 클럭을 켜주는 경우가 있다. 하지만 `MX_USART2_UART_Init()`처럼 CubeMX가 생성하는 코드는 따로 `__HAL_RCC_USART2_CLK_ENABLE()`을 호출한다. 레지스터를 직접 다룰 때는 반드시 수동으로 켜야 한다.

### PLL 설정 코드

`system_stm32f4xx.c`의 `SystemInit()` 혹은 CubeMX가 생성하는 `SystemClock_Config()`에서 실제 설정이 이루어진다.

```c
RCC_OscInitTypeDef RCC_OscInitStruct = {0};
RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

// HSE + PLL 설정
RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
RCC_OscInitStruct.HSEState       = RCC_HSE_ON;
RCC_OscInitStruct.PLL.PLLState   = RCC_PLL_ON;
RCC_OscInitStruct.PLL.PLLSource  = RCC_PLLSOURCE_HSE;
RCC_OscInitStruct.PLL.PLLM       = 8;
RCC_OscInitStruct.PLL.PLLN       = 336;
RCC_OscInitStruct.PLL.PLLP       = RCC_PLLP_DIV2;
RCC_OscInitStruct.PLL.PLLQ       = 7;
HAL_RCC_OscConfig(&RCC_OscInitStruct);

// AHB/APB 분주비 설정
RCC_ClkInitStruct.ClockType      = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
RCC_ClkInitStruct.SYSCLKSource   = RCC_SYSCLKSOURCE_PLLCLK;
RCC_ClkInitStruct.AHBCLKDivider  = RCC_SYSCLK_DIV1;   // HCLK  = 168MHz
RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;     // PCLK1 = 42MHz
RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;     // PCLK2 = 84MHz
HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5);
```

---

## 클럭 설정 실수

### HSE_VALUE 불일치

`stm32f4xx_hal_conf.h`에 HSE 주파수를 정의하는 매크로가 있다.

```c
#define HSE_VALUE  8000000U  // 보드 크리스탈 주파수와 일치해야 함
```

보드에 12 MHz 크리스탈이 달려있는데 이 값이 8000000이면, PLL M/N/P 계산 기준이 틀려서 SYSCLK가 엉뚱한 값이 된다. `HAL_Delay(1000)`이 1초가 아니거나, UART 보드레이트가 맞지 않는 증상으로 나타난다.

### 주변장치 클럭 미활성화

```c
// 이 줄 없으면 GPIOA 핀이 동작 안 함
__HAL_RCC_GPIOA_CLK_ENABLE();
GPIOA->MODER |= (1 << 10);
```

HAL 초기화 함수를 쓰지 않고 레지스터를 직접 건드릴 때 가장 자주 만나는 실수다. 클럭이 꺼진 주변장치는 레지스터 접근 자체가 무시되거나 버스 오류를 일으킨다.

---

## 정리

- **HSI**: 내부 16 MHz RC 오실레이터. 외부 부품 불필요, 정밀도 낮음
- **HSE**: 외부 크리스탈. 정밀도 높음, 보드에 크리스탈 필요
- **PLL**: HSE/M × N / P = SYSCLK. STM32F4 최대 168 MHz
- **클럭 트리**: SYSCLK → AHB(HCLK) → APB1(PCLK1) / APB2(PCLK2). 주변장치마다 연결된 버스가 다름
- **RCC**: 클럭 설정 모듈. 각 주변장치 클럭은 사용 전 개별 활성화 필요
- **HSE_VALUE**: 실제 보드 크리스탈 주파수와 반드시 일치해야 함

다음 편(심화)에서는 PCLK에서 실제 보드레이트가 어떻게 계산되는지, SPI 클럭 선택은 어떻게 하는지를 정리한다.
