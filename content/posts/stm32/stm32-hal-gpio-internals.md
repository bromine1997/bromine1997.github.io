---
title: "[STM32] HAL GPIO 내부 뜯어보기 및 레지스터 직접 제어"
date: 2026-04-22T20:19:00+09:00
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

1편에서는 GPIO의 구조와 내부 블록 다이어그램, 데이터시트 읽는 법까지 다뤘다. 마지막에는 아래 코드로 User Button을 눌렀을 때 LED가 켜지는 실습도 해봤는데,

```c
if (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == GPIO_PIN_RESET)
{
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);
}
```

사실 이 코드가 내부에서 뭘 하는지는 설명 안 하고 넘어갔다. `HAL_GPIO_ReadPin()`이 IDR을 읽는다는 건 알겠는데, 어떤 방식으로? `HAL_GPIO_WritePin()`은 왜 ODR 대신 BSRR을 쓰는 건지, 그리고 그게 왜 중요한지.

## HAL 소스 어떻게 보나

CubeIDE에서 함수에 커서를 올리고 **F3** 누르면 해당 함수 정의로 바로 이동한다. 또는 함수명에서 **Ctrl + 클릭**.

파일 위치는 프로젝트마다 다르지만 보통 이쪽이다.

```
Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_gpio.c
Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_gpio.h
```

여기가 HAL GPIO 관련 로직이 다 모여있는 곳이다.

## HAL_GPIO_ReadPin() 내부

1편에서 쓴 코드:

```c
HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13)
```

F3 눌러서 소스 열어보면 이렇다.

<!-- 이미지: CubeIDE에서 F3으로 이동한 HAL_GPIO_ReadPin() 소스 화면 캡처 -->
![HAL_GPIO_ReadPin 소스](/images/stm32/hal-gpio-readpin-source.png)

함수 본문은 생각보다 단순하다. **IDR(Input Data Register)** 에서 해당 핀 비트를 읽어서 반환하는 게 전부다.

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

반환 타입인 `GPIO_PinState`는 `stm32f4xx_hal_gpio.h`에 아래처럼 정의돼 있다.

<!-- 이미지: stm32f4xx_hal_gpio.h에서 GPIO_PinState enum 정의 화면 캡처 -->
![GPIO_PinState 정의](/images/stm32/gpio-pinstate-enum.png)

```c
typedef enum
{
    GPIO_PIN_RESET = 0,
    GPIO_PIN_SET
} GPIO_PinState;
```

`GPIOx->IDR & GPIO_Pin`은 IDR 레지스터에서 특정 핀 비트만 마스킹해서 읽는 것이다. `PC13`이라면 `GPIOC->IDR & (1 << 13)` 이 된다.

그래서 1편에서 `== GPIO_PIN_RESET`으로 버튼 눌림을 판단한 게, 실제로는 **IDR의 13번 비트가 0인지 확인**하는 거다. Active Low 버튼이니까 눌렸을 때 핀이 GND로 당겨지고 → IDR 비트가 0 → `GPIO_PIN_RESET` 반환.

## HAL_GPIO_WritePin() 내부

```c
HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);
```

소스를 열면 `ODR`이 아닌 **BSRR(Bit Set/Reset Register)** 을 쓰고 있다.

<!-- 이미지: HAL_GPIO_WritePin() 소스 화면 캡처 -->
![HAL_GPIO_WritePin 소스](/images/stm32/hal-gpio-writepin-source.png)

```c
void HAL_GPIO_WritePin(GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin, GPIO_PinState PinState)
{
    if (PinState != GPIO_PIN_RESET)
    {
        GPIOx->BSRR = GPIO_Pin;                   // Set: 하위 16비트에 핀 마스크 기록
    }
    else
    {
        GPIOx->BSRR = (uint32_t)GPIO_Pin << 16U;  // Reset: 상위 16비트에 핀 마스크 기록
    }
}
```

Set할 때는 `GPIO_Pin`(= `1 << 5` = `0x0020`)을 그대로 쓰고, Reset할 때는 `GPIO_Pin << 16`(= `0x00200000`)을 써서 상위 16비트에 넣는다.

BSRR은 32비트 레지스터인데 상위/하위 16비트의 역할이 다르다.

```
BSRR [31:16]  →  BR (Bit Reset): 해당 비트가 1이면 핀을 LOW로
BSRR [15:0]   →  BS (Bit Set)  : 해당 비트가 1이면 핀을 HIGH로
```

| 동작 | BSRR에 쓰는 값 | 예시 (PA5) |
|---|---|---|
| PA5 HIGH | `GPIO_Pin` | `0x00000020` |
| PA5 LOW | `GPIO_Pin << 16` | `0x00200000` |

ODR은 "핀 상태 전체를 이 값으로 덮어써라"이고, BSRR은 "이 핀만 Set해라" 또는 "이 핀만 Reset해라"다. 건드리지 않을 핀은 0을 쓰면 그냥 무시된다.

## 왜 HAL은 ODR 대신 BSRR을 쓰나

ODR로 특정 핀만 바꾸려면 이렇게 된다.

```c
GPIOA->ODR |= (1 << 5);   // Read → Modify → Write
```

겉으로는 한 줄이지만 실제로는 세 단계다.

```
① ODR 읽기      (Read)
② 5번 비트 수정  (Modify)
③ ODR에 쓰기    (Write)
```

문제는 ①과 ③ 사이에 인터럽트가 끼어드는 경우다. 메인 루프에서 PA5를 SET하려는 도중, 인터럽트 핸들러가 PA6을 RESET했다고 하면:

```
[메인]      ODR 읽음 → PA5, PA6 모두 HIGH 상태
[인터럽트]  PA6 RESET → ODR 반영됨
[메인 재개] Modify한 값 씀 → PA6이 다시 HIGH로 덮어씌워짐
```

인터럽트에서 바꾼 PA6 상태가 날아간다. 이게 **Race Condition**이다.

BSRR은 Write 한 번으로 끝난다. 하드웨어가 해당 비트만 건드리기 때문에 Read → Modify → Write 과정 자체가 없다. 인터럽트가 끼어들 틈이 없다는 뜻이다. 이게 **Atomic**한 이유고, HAL이 BSRR을 쓰는 이유다.

| 방식 | 동작 단계 | 인터럽트 안전 |
|---|---|---|
| `ODR \|=` | Read → Modify → Write | ❌ 위험 |
| `BSRR =` | Write | ✅ 안전 (Atomic) |

> 추후에 저런 Critical Section을 어떻게 관리해야 하는지도 따로 글을 써보려고 한다.

## 레지스터 직접 접근 버전

HAL 없이 똑같이 동작하는 코드:

```c
while (1)
{
    if (!(GPIOC->IDR & (1 << 13)))  // PC13 LOW = 버튼 눌림
    {
        GPIOA->BSRR = (1 << 5);         // PA5 Set (LED ON)
    }
    else
    {
        GPIOA->BSRR = (1 << 5) << 16;   // PA5 Reset (LED OFF)
    }
}
```

HAL은 결국 이걸 함수로 감싼 것뿐이다. 이걸 알고 쓰는 것과 모르고 쓰는 건, 뭔가 이상하게 동작할 때 어디서부터 파고들지가 달라진다.

HAL로 간단한 동작을 구현하는 데 있어서는 충분하다. 함수 이름만 봐도 뭘 하는지 알 수 있고, 포팅도 쉽다.

하지만 막상 뭔가 원하는 대로 안 동작할 때 얘기가 달라진다. 핀이 왜 안 켜지는지, 인터럽트에서 왜 상태가 깨지는지 — 이걸 파고들려면 결국 IDR이 뭘 읽고 있는지, BSRR에 어떤 값이 들어가고 있는지를 봐야 한다. HAL 함수 이름만 알고 있으면 거기서 막히게 된다.

레지스터 수준을 알고 쓰는 것과 모르고 쓰는 건, 코드가 잘 돌아갈 때는 차이가 없다. 차이는 안 돌아갈 때 난다.
