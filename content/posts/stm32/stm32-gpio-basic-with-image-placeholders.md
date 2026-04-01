---
title: "[STM32] GPIO 기본개념 및 입출력 실습"
date: 2026-03-16T22:56:00+09:00
draft: false
categories:
  - Embedded
tags:
  - STM32
  - GPIO
  - HAL
  - Register
  - STM32F4
summary: "GPIO의 기본 개념과 Push-Pull, Open-Drain, Pull-up, Pull-down, 그리고 STM32F411 Nucleo에서 버튼 입력과 LED 출력을 실습한 글"
---

GPIO(General Purpose Input/Output)는 MCU가 외부 세계와 신호를 주고받는 가장 기본적인 수단이다.  
이름 그대로 특정 기능에 고정되지 않고, 소프트웨어 설정에 따라 입력 또는 출력으로 사용할 수 있다.

크게 두 가지 역할이 있다.

- **Input**: 외부 신호(버튼, 센서 등)를 MCU가 읽어들임
- **Output**: MCU가 외부 장치(LED, 모터 드라이버 등)에 신호를 인가함

## 출력 모드: Push-Pull vs Open-Drain

### Push-Pull

MCU가 핀을 **High와 Low 모두 직접 drive**하는 방식이다.
내부에 PMOS와 NMOS 트랜지스터가 한 쌍으로 연결되어 있어서,
High 명령이 오면 PMOS가 켜져 핀을 VDD에 연결하고,
Low 명령이 오면 NMOS가 켜져 핀을 GND에 연결한다.

외부 저항 없이도 원하는 레벨을 정확하게 출력할 수 있어서,
일반적인 LED 제어나 디지털 출력에 기본으로 사용한다.

### Open-Drain

NMOS 하나만 사용하는 방식이다.
Low는 직접 drive할 수 있지만, High는 스스로 만들지 못한다.
대신 핀을 그냥 놔버리는데(Hi-Z),
이때 외부에 연결된 Pull-up 저항이 핀을 High로 끌어올린다.

<!-- 이미지 삽입 위치: Push-Pull / Open-Drain 회로 비교 그림 -->
![Push-Pull과 Open-Drain 비교](/images/stm32/stm32-pushpull-open-drain.png)

### 왜 Open-Drain을 사용할까?

대표적인 예가 **I2C**다.
여러 장치가 같은 버스 선 하나를 공유할 때, 누군가 Low를 당기면 버스 전체가 Low가 된다.

만약 Push-Pull이었다면 문제가 생긴다.
장치 A가 High를 output하는 동시에 장치 B가 Low를 output하면,
VDD와 GND가 직접 연결되는 short가 발생하기 때문이다.

Open-Drain은 Pull-up 저항의 전압을 MCU VDD와 다르게 설정할 수도 있어서,
**3.3V MCU와 5V 버스를 연결**할 때도 별도 level shift 없이 쓸 수 있다.

---

## 입력 모드: Pull-up / Pull-down / Floating

버튼을 GPIO 입력으로 읽는다고 해보자.
버튼이 눌리지 않은 상태에서 핀이 아무 데도 연결되지 않으면 **Floating 상태**가 된다.

이 상태에서는 공중에 떠 있는 핀이 주변 noise를 그대로 받아들여서
IDR을 읽으면 0이 될지 1이 될지 예측할 수 없다.

그래서 평상시에 핀을 **확실한 레벨로 고정**해두는 것이 Pull-up / Pull-down이다.

<!-- 이미지 삽입 위치: Floating / Pull-up / Pull-down 회로 비교 그림 -->
![Pull-up과 Pull-down 개념도](/images/stm32/stm32-pullup-pulldown-floating.png)

| 설정 | 평상시 | 버튼 누를 때 |
|---|---|---|
| Pull-up | HIGH | LOW |
| Pull-down | LOW | HIGH |

STM32는 외부 저항 없이 내부 Pull-up / Pull-down을 `PUPDR` 레지스터로 설정할 수 있다.
이전 글에서 PC13 버튼을 읽을 때 Pull-up을 설정했던 것이 바로 이 이유다.

## STM32 GPIO 내부 블록 다이어그램

STM32 레퍼런스 매뉴얼에는 GPIO 핀 하나의 구조를 보여주는 블록 다이어그램이 있다.  
GPIO를 이해할 때 가장 중요한 그림 중 하나라서, 한 번 제대로 읽어두면 이후에 훨씬 덜 헷갈린다.

크게 세 부분으로 나눠서 볼 수 있다.

<!-- 이미지 삽입 위치: STM32 GPIO 블록 다이어그램 -->
![STM32 GPIO 내부 블록 다이어그램](/images/stm32/stm32-gpio-block-diagram.png)

### 1) 실제 핀 (I/O Pin)

핀 양쪽에는 **Protection Diode**가 붙어 있다.  
핀에 VDD보다 높거나 VSS보다 낮은 전압이 들어왔을 때 내부 회로를 보호하는 역할을 한다.

또한 Pull-up / Pull-down 저항이 스위치 형태로 표현되어 있는데, 이 스위치를 소프트웨어로 켜고 끄는 것이 `PUPDR` 레지스터다.

### 2) 입력 경로 (Input Driver)

핀 신호는 **TTL Schmitt Trigger**를 거쳐 **Input Data Register(IDR)** 로 들어간다.

Schmitt Trigger가 있는 이유는 noise 때문이다.  
신호가 천천히 변하거나 noise가 섞여 있어도, hysteresis 특성을 통해 보다 명확하게 0과 1로 해석할 수 있다.

Analog 모드에서는 이 디지털 입력 경로 자체를 끄기도 한다.

즉, 펌웨어에서 입력을 읽는다는 것은 결국 **IDR 값을 읽는 것**이다.

### 3) 출력 경로 (Output Driver)

출력은 `ODR(Output Data Register)`에 값을 쓰거나, `BSRR(Bit Set/Reset Register)`를 통해 제어된다.  
이 값이 Output Control을 거쳐 P-MOS / N-MOS 조합으로 전달된다.

- **Push-Pull 모드**: P-MOS와 N-MOS가 번갈아 동작하며 High / Low를 직접 drive
- **Open-Drain 모드**: N-MOS만 동작하고 P-MOS는 꺼짐

핵심은 **MUX**다.  
`MODER` 레지스터를 통해 이 핀이 GPIO로 동작할지, UART / SPI 같은 Alternate Function으로 동작할지 선택한다.  
AF(Alternate Function) 모드로 설정하면 MCU 내부 peripheral(USART, SPI, TIM 등)이 해당 핀을 직접 제어한다.

## 실습: User Button으로 LED 제어 (STM32F411 Nucleo)

### 보드 기본 핀 정보

코드를 작성하기 전에 보드 회로도에서 먼저 확인해야 할 정보는 다음과 같다.

| 기능 | 핀 | 특이사항 |
|---|---|---|
| User LED (LD2) | PA5 | Active High |
| User Button (B1) | PC13 | Active Low, 보드 내부 Pull-up 연결 |

여기서 중요한 점은 **버튼이 Active Low**라는 것이다.  
즉, 버튼을 누르지 않았을 때는 `PC13 = High`, 버튼을 눌렀을 때는 `PC13 = Low`가 된다.

따라서 코드에서 `GPIO_PIN_RESET`은 버튼이 눌린 상태를 의미한다.

<!-- 이미지 삽입 위치: Nucleo 보드 LED / Button 위치 사진 -->
![STM32F411 Nucleo 보드의 LED와 버튼 위치](/images/stm32/stm32f411-nucleo-led-button.jpg)
*예시: STM32F411 Nucleo 보드에서 LD2와 B1의 위치를 표시한 사진*

### CubeMX 핀 설정

- `PA5` → `GPIO_Output`
- `PC13` → `GPIO_Input`

`PC13`의 Pull-up은 보드 하드웨어에 이미 연결되어 있으므로, CubeMX에서는 `No pull`로 두어도 된다.

<!-- 이미지 삽입 위치: CubeMX GPIO 설정 화면 -->
![CubeMX GPIO 설정 화면](/images/stm32/stm32-cubemx-gpio-config.png)
*PA5를 출력, PC13을 입력으로 설정한 CubeMX 화면*

### HAL 코드
```c
while (1)
{
    if (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == GPIO_PIN_RESET)
    {
        // 버튼 눌림 (Active Low)
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);
    }
    else
    {
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);
    }
}
```

동작은 단순하다.

- 버튼 상태를 읽고
- 눌려 있으면 LED를 켜고
- 아니면 LED를 끈다

<!-- 이미지 삽입 위치: 실행 결과 사진 또는 GIF -->
![버튼 입력에 따라 LED가 켜지는 실행 결과](/images/stm32/stm32-gpio-button-led-result.jpg)
*버튼을 누르면 LED가 켜지는 실행 결과*

### 실행 결과

버튼을 누르고 있는 동안 LD2(초록 LED)가 켜지고, 버튼에서 손을 떼면 꺼진다.

> 이 정도의 간단한 실습에서는 debouncing을 따로 넣지 않았다.  
> 버튼을 누르고 있는 동안 계속 켜는 구조라서 chattering이 큰 문제가 되지 않는다.  
> 다만 버튼을 한 번 눌렀다 뗐을 때 상태가 토글되는 구조로 바꾸면 debouncing이 필요해진다.

## 추가 학습: OSPEEDR를 왜 설정할까?

출력 속도 설정은 **slew rate(신호가 바뀌는 속도)** 와 관련이 있다.  
속도가 빠를수록 엣지가 가팔라지고, 그만큼 **EMI** 도 커질 수 있다.

그래서 고속 SPI 클럭처럼 빠른 신호가 필요한 경우에는 High Speed가 필요할 수 있지만,  
단순한 LED 제어 같은 저속 신호에 Very High Speed를 쓰면 불필요한 noise만 증가시킬 수 있다.

<!--  OSPEEDR 그림 -->
![OSPEEDR 레지스터](/images/stm32/stm32-gpio-ospeedr-slew-rate.png)

## 핵심 키워드

- Floating
- Pull-up
- Pull-down
- Push-Pull
- Open-Drain
- Active Low
- Schmitt Trigger
- Slew Rate
- Debouncing

## 마무리

이번 글에서는 GPIO의 기본 개념과 입력/출력 구조, 그리고 STM32F411 Nucleo에서 버튼 입력과 LED 출력을 제어하는 간단한 실습까지 정리했다.

다음 글에서는 `HAL_GPIO_ReadPin()` 과 `HAL_GPIO_WritePin()` 이 실제로 내부에서 어떻게 동작하는지, 그리고 왜 `ODR` 대신 `BSRR`를 사용하는지까지 이어서 정리할 예정이다.