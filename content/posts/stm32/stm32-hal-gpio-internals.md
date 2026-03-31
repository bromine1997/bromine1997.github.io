---
title: "[STM32] HAL GPIO 내부 뜯어보기 및 레지스터 직접 제어"
date: 2026-03-31T21:00:00+09:00
draft: false
categories:
  - Embedded
tags:
  - STM32
  - GPIO
  - HAL
  - Register
  - STM32F4
  - BSRR
  - IDR
summary: "HAL_GPIO_ReadPin()과 HAL_GPIO_WritePin()이 내부에서 어떻게 동작하는지 분석하고, ODR 대신 BSRR을 사용하는 이유와 레지스터 직접 제어 방법까지 정리한 글"
---

이전 글에서 `HAL_GPIO_ReadPin()`과 `HAL_GPIO_WritePin()`을 사용해서 버튼 입력과 LED 출력을 제어했다.
그런데 실제로 이 함수들이 내부에서 어떤 레지스터를 건드리는지, 그리고 왜 `ODR` 대신 `BSRR`을 쓰는지는 따로 설명하지 않았다.

이번 글에서는 HAL 소스 코드를 직접 뜯어보면서 그 안에서 무슨 일이 일어나는지 정리해보려 한다.

## HAL 소스 코드 어디서 보나?

CubeIDE 기준으로, 함수 이름 위에 커서를 올리고 **F3** 를 누르거나 **Ctrl+클릭** 하면 정의로 이동할 수 있다.

GPIO 관련 HAL 소스 파일의 위치는 다음과 같다.

```
Drivers/
└── STM32F4xx_HAL_Driver/
    ├── Inc/
    │   └── stm32f4xx_hal_gpio.h     ← 타입 및 매크로 정의
    └── Src/
        └── stm32f4xx_hal_gpio.c     ← 함수 구현
```

직접 열어보면 생각보다 코드가 짧고 명확하다.

## HAL_GPIO_ReadPin() 뜯어보기

### 함수 시그니처

```c
GPIO_PinState HAL_GPIO_ReadPin(GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin);
```

반환 타입인 `GPIO_PinState`는 `stm32f4xx_hal_gpio.h`에 다음과 같이 정의되어 있다.

```c
typedef enum
{
    GPIO_PIN_RESET = 0,
    GPIO_PIN_SET
} GPIO_PinState;
```

### 내부 동작

함수 본문은 단순하다.
**IDR(Input Data Register)** 에서 해당 핀에 해당하는 비트를 읽어서 반환한다.

```c
GPIO_PinState HAL_GPIO_ReadPin(GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin)
{
    GPIO_PinState bitstatus;

    if ((GPIOx->IDR & GPIO_Pin) != (uint32_t)GPIO_PIN_RESET)
    {
        bitstatus = GPIO_PIN_SET;
    }
    else
    {
        bitstatus = GPIO_PIN_RESET;
    }

    return bitstatus;
}
```

`GPIOx->IDR & GPIO_Pin` 은 IDR 레지스터에서 특정 핀 비트만 마스킹해서 읽는 것이다.
예를 들어 `PC13`이라면 `GPIOC->IDR & (1 << 13)` 이 된다.

### 이전 글 코드와 연결

이전 글에서 썼던 코드를 다시 보면 이렇다.

```c
if (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == GPIO_PIN_RESET)
```

이게 실질적으로 하는 일은 **IDR의 13번 비트가 0인지 확인**하는 것이다.
PC13이 Active Low 버튼이므로, 버튼이 눌리면 핀이 GND로 당겨져 IDR 비트가 0이 되고 `GPIO_PIN_RESET`이 반환된다.

<!-- 이미지 삽입 위치: IDR 레지스터 비트 구조 그림 -->
![GPIO IDR 레지스터 비트 구조](/images/stm32/stm32-gpio-idr-register.png)
*예시: IDR 레지스터의 각 비트가 핀 상태를 나타내는 구조 그림*

## HAL_GPIO_WritePin() 뜯어보기

### 함수 시그니처

```c
void HAL_GPIO_WritePin(GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin, GPIO_PinState PinState);
```

### 내부 동작

이 함수는 `ODR`이 아닌 **BSRR(Bit Set/Reset Register)** 을 사용한다.

```c
void HAL_GPIO_WritePin(GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin, GPIO_PinState PinState)
{
    if (PinState != GPIO_PIN_RESET)
    {
        GPIOx->BSRR = GPIO_Pin;                    // Set: 하위 16비트에 핀 마스크 기록
    }
    else
    {
        GPIOx->BSRR = (uint32_t)GPIO_Pin << 16U;   // Reset: 상위 16비트에 핀 마스크 기록
    }
}
```

### BSRR 레지스터 구조

BSRR은 32비트 레지스터인데, 상위 16비트와 하위 16비트의 역할이 다르다.

```text
BSRR [31:16]  →  BR (Bit Reset): 해당 비트가 1이면 핀을 LOW로
BSRR [15:0]   →  BS (Bit Set)  : 해당 비트가 1이면 핀을 HIGH로
```

| 동작 | BSRR에 쓰는 값 | 예시 (PA5) |
|---|---|---|
| PA5 HIGH (Set) | `GPIO_Pin` | `0x0000_0020` |
| PA5 LOW (Reset) | `GPIO_Pin << 16` | `0x0020_0000` |

Set과 Reset이 동시에 요청되면 Set이 우선된다.

<!-- 이미지 삽입 위치: BSRR 레지스터 비트 구조 그림 -->
![GPIO BSRR 레지스터 비트 구조](/images/stm32/stm32-gpio-bsrr-register.png)
*예시: BSRR의 상위 16비트(BR)와 하위 16비트(BS) 역할을 나타낸 그림*

## 왜 ODR 대신 BSRR인가? — Race Condition

### ODR의 문제점

`ODR(Output Data Register)`로 핀을 제어하는 방법은 흔히 이렇게 쓴다.

```c
GPIOA->ODR |= (1 << 5);   // PA5 HIGH
GPIOA->ODR &= ~(1 << 5);  // PA5 LOW
```

문제는 이 한 줄이 실제로는 **세 단계**로 실행된다는 점이다.

```text
1. Read   → 현재 ODR 값을 읽어서 CPU 레지스터에 올림
2. Modify → 특정 비트를 수정
3. Write  → 수정한 값을 ODR에 다시 씀
```

이걸 **Read-Modify-Write** 라고 한다.

### 인터럽트가 끼어들면

Read와 Write 사이, 즉 아직 ODR에 새 값을 쓰기 전에 **인터럽트가 발생**했다고 가정해보자.

```text
[메인 루프]
  1. ODR 읽음 → PA5=0, PA6=0 (0x0000)
  2. PA5 수정 준비 중 → 0x0020

[인터럽트 발생]
  → 인터럽트 핸들러에서 PA6을 HIGH로 세트
  → ODR에 0x0040 기록 (PA6=1)

[메인 루프 재개]
  3. 준비했던 0x0020을 ODR에 씀
  → PA6이 다시 0으로 덮어씌워짐!
```

인터럽트가 설정한 **PA6 상태가 증발**해버린다.
이게 **Race Condition**이다.

<!-- 이미지 삽입 위치: Race Condition 발생 흐름 다이어그램 -->
![ODR Read-Modify-Write Race Condition 다이어그램](/images/stm32/stm32-gpio-odr-race-condition.png)
*예시: 메인 루프와 인터럽트 사이에서 ODR 값이 덮어씌워지는 상황을 타임라인으로 표현한 그림*

### BSRR이 해결하는 방법

BSRR은 **Write 한 번**만으로 완료된다.

```c
GPIOA->BSRR = (1 << 5);  // PA5만 HIGH → 단 한 번의 쓰기
```

CPU가 BSRR에 값을 쓰는 순간, 하드웨어가 해당 비트만 세트 또는 리셋한다.
Read 단계가 없으므로 인터럽트가 끼어들 타이밍 자체가 없다.

이런 연산을 **Atomic 연산**이라고 한다.

> **Atomic** 이란, 연산이 중간에 분리되지 않고 한 번에 완료된다는 의미다.
> 인터럽트 기반 시스템에서 공유 자원에 안전하게 접근하기 위해 반드시 필요한 개념이다.

| 방식 | 동작 단계 | 인터럽트 안전 |
|---|---|---|
| `ODR \|=` | Read → Modify → Write | ❌ 위험 |
| `BSRR =` | Write | ✅ 안전 (Atomic) |

## 레지스터 직접 접근 코드

HAL 없이 레지스터만으로 동일한 동작을 구현하면 다음과 같다.

```c
while (1)
{
    if (!(GPIOC->IDR & (1 << 13)))  // PC13 LOW → 버튼 눌림 (Active Low)
    {
        GPIOA->BSRR = (1 << 5);          // PA5 Set → LED ON
    }
    else
    {
        GPIOA->BSRR = (1 << 5) << 16;   // PA5 Reset → LED OFF
    }
}
```

HAL 함수를 쓸 때와 동작은 완전히 동일하다.
HAL은 이 레지스터 접근을 조금 더 읽기 좋게 감싸놓은 것일 뿐이다.

<!-- 이미지 삽입 위치: HAL 코드 vs 레지스터 직접 접근 코드 비교 -->
![HAL 코드와 레지스터 직접 접근 비교](/images/stm32/stm32-gpio-hal-vs-register.png)
*예시: HAL 함수와 레지스터 직접 접근 코드를 나란히 놓고 대응 관계를 표시한 그림*

## HAL을 쓰면서도 레지스터를 알아야 하는 이유

정상적으로 동작하는 상황에서는 HAL과 레지스터 직접 접근 사이에 체감 차이가 없다.
하지만 문제가 생겼을 때 이야기가 달라진다.

예를 들어 이런 상황이 있을 수 있다.

- 핀이 설정대로 동작하지 않을 때 → `MODER`, `ODR`, `IDR`을 디버거로 직접 확인
- 인터럽트 핸들러에서 GPIO 상태가 이상하게 바뀔 때 → Race Condition 의심
- 타이밍이 극도로 빡빡한 루프에서 HAL 오버헤드를 줄이고 싶을 때 → 레지스터 직접 접근

레지스터를 이해하면 HAL 함수 뒤에 어떤 하드웨어 동작이 숨어있는지 보이기 시작하고,
이게 디버깅할 때 기반이 된다.

## 핵심 키워드

- IDR (Input Data Register)
- ODR (Output Data Register)
- BSRR (Bit Set/Reset Register)
- Read-Modify-Write
- Race Condition
- Atomic 연산
- HAL 추상화

## 마무리

이번 글에서는 `HAL_GPIO_ReadPin()`과 `HAL_GPIO_WritePin()`이 내부에서 어떤 레지스터를 어떻게 건드리는지, 그리고 왜 `ODR` 직접 수정이 아닌 `BSRR`을 써야 하는지까지 정리했다.

다음 글에서는 **EXTI(External Interrupt)** 를 통해 GPIO 입력을 인터럽트 방식으로 처리하는 방법을 정리할 예정이다.
폴링 방식과 어떻게 다른지, 그리고 NVIC 설정은 어떻게 연결되는지까지 이어서 다룰 생각이다.
