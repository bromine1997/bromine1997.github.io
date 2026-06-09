---
title: "[임베디드 기초] 5편 - 인터럽트와 NVIC: CPU를 기다리게 하지 마라"
date: 2026-05-28T20:38:00+09:00
tags: ["embedded", "ARM", "Cortex-M", "interrupt", "NVIC", "ISR", "STM32", "volatile"]
categories: ["Embedded Basic"]
description: "폴링과 인터럽트의 차이, Cortex-M NVIC 구조와 우선순위 시스템, volatile 키워드의 필요성까지 인터럽트의 핵심 개념을 정리한다."
---

## 들어가며

4편에서 벡터 테이블을 다뤘다. `[0]`은 MSP, `[1]`은 Reset_Handler 주소였고, 나머지 항목들(NMI_Handler, HardFault_Handler, TIM2_IRQHandler...)은 그냥 지나쳤다.

이것들이 전부 **인터럽트 핸들러**다. 임베디드 코드의 상당 부분이 이 핸들러들 안에서 돌아간다.

---

## 폴링 vs 인터럽트

외부 이벤트(버튼 입력, 센서 데이터 도착 등)를 처리하는 방법은 두 가지다.

### 폴링 (Polling)

```c
while (1) {
    if (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == GPIO_PIN_RESET) {
        // 버튼 눌림 처리
    }
    do_something_else();
}
```

CPU가 주기적으로 상태를 직접 확인한다. CPU가 루프를 돌며 GPIO를 계속 읽어야 하고, 짧은 펄스나 빠른 이벤트를 놓칠 수 있다. 확인할 이벤트가 늘어날수록 반응 속도도 느려진다.

### 인터럽트 (Interrupt)

하드웨어가 이벤트 발생 시 CPU에게 직접 신호를 보낸다. CPU는 하던 작업을 멈추고 핸들러를 실행한 뒤 원래 위치로 돌아온다.

```
메인 코드 실행 중
  ↓
이벤트 발생 (버튼, UART 수신, 타이머 만료...)
  ↓
하드웨어가 CPU에 인터럽트 신호 전달
  ↓
CPU: 현재 컨텍스트 저장 (PC, xPSR, R0-R3, R12, LR)
  ↓
벡터 테이블에서 핸들러 주소 읽기 → 핸들러 실행
  ↓
핸들러 완료 → 컨텍스트 복원 → 원래 코드로 복귀
```

Cortex-M은 컨텍스트 저장/복원을 **하드웨어가 자동으로** 처리한다. 핸들러는 일반 C 함수처럼 작성하면 된다.

---

## Cortex-M 예외 모델

4편에서 벡터 테이블의 항목이 예외 번호(exception number) 순으로 배치된다고 설명했다.

**예외(Exception)** 는 인터럽트를 포함하는 더 넓은 개념이다.

| 예외 번호 | 이름 | 발생 원인 |
|---|---|---|
| 1 | Reset | 전원 인가, 리셋 핀 |
| 2 | NMI | Non-Maskable Interrupt — 무조건 처리 |
| 3 | HardFault | 처리되지 않은 예외의 에스컬레이션 |
| 4 | MemManage | MPU 위반 |
| 5 | BusFault | 버스 접근 오류 |
| 6 | UsageFault | 미정의 명령어, 정렬 오류 등 |
| 11 | SVCall | `SVC` 명령어 (RTOS에서 시스템 콜) |
| 14 | PendSV | RTOS 컨텍스트 스위칭 |
| 15 | SysTick | 시스템 타이머 (HAL_Delay 기반) |
| 16+ | IRQ0~ | 외부 주변장치 인터럽트 (UART, TIM, EXTI...) |

예외 번호 16번부터가 MCU 제조사가 정의하는 영역이다. STM32F4에서 EXTI0는 IRQ 6번(예외 번호 22번)이다.

---

## NVIC (Nested Vectored Interrupt Controller)

모든 인터럽트는 NVIC를 통해 관리된다. Cortex-M 코어에 내장된 하드웨어 모듈이다.

### 인터럽트 활성화

```c
// HAL 방식
HAL_NVIC_SetPriority(EXTI0_IRQn, 1, 0);
HAL_NVIC_EnableIRQ(EXTI0_IRQn);

// 레지스터 직접 접근 (CMSIS)
NVIC_SetPriority(EXTI0_IRQn, 1);
NVIC_EnableIRQ(EXTI0_IRQn);
```

활성화하지 않으면 인터럽트 요청이 발생해도 CPU가 처리하지 않는다.

### 우선순위

STM32F4는 **4비트(0~15단계)** 우선순위를 사용한다. **숫자가 낮을수록 우선순위가 높다.**

```c
HAL_NVIC_SetPriority(EXTI0_IRQn,   0, 0);  // 가장 높음
HAL_NVIC_SetPriority(USART1_IRQn,  5, 0);
HAL_NVIC_SetPriority(TIM2_IRQn,   15, 0);  // 가장 낮음
```

우선순위는 두 부분으로 나뉜다.

- **Preemption Priority**: 현재 실행 중인 핸들러를 중단하고 끼어들 수 있는지 결정
- **Sub-Priority**: 같은 Preemption Priority에서 대기 중인 인터럽트들의 처리 순서

```c
// 상위 2비트 = Preemption, 하위 2비트 = Sub
HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_2);

HAL_NVIC_SetPriority(EXTI0_IRQn,  1, 0);  // preemption=1
HAL_NVIC_SetPriority(USART1_IRQn, 2, 0);  // preemption=2
```

USART1 핸들러 실행 중 EXTI0 인터럽트가 발생하면? EXTI0의 Preemption Priority(1)가 더 높으므로 USART1을 중단하고 EXTI0를 먼저 처리한다. 이것이 **Nested(중첩)** 인터럽트다.

---

## 인터럽트 핸들러 작성

### EXTI (외부 핀 인터럽트)

```c
// startup 파일에 이미 약하게 정의된 이름을 override
void EXTI0_IRQHandler(void) {
    // pending bit를 클리어하지 않으면 인터럽트가 계속 발생한다
    HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_0);
}

// HAL이 pending bit 클리어 후 이 콜백을 호출한다
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == GPIO_PIN_0) {
        // 처리
    }
}
```

### 핸들러 안에서 하면 안 되는 것들

```c
void EXTI0_IRQHandler(void) {
    HAL_Delay(100);        // 금지: SysTick 기반 → 데드락
    printf("triggered\n"); // 금지: 느리고 재진입 불안전
    HAL_UART_Transmit(...); // 금지: blocking 함수
    malloc(size);           // 금지: 재진입 불안전
    HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_0);
}
```

핸들러는 **최대한 짧게** 작성한다. 플래그만 세우고 실제 처리는 메인 루프에서 한다.

```c
volatile uint8_t button_flag = 0;

void EXTI0_IRQHandler(void) {
    button_flag = 1;  // 플래그만 세운다
    HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_0);
}

int main(void) {
    while (1) {
        if (button_flag) {
            button_flag = 0;
            do_heavy_work();  // 메인 루프에서 처리
        }
    }
}
```

---

## volatile — 인터럽트에서 왜 중요한가

2편에서 `volatile`을 레지스터 접근에서 언급했다. 인터럽트에서도 같은 이유로 필요하다.

```c
uint8_t flag = 0;  // volatile 없음

void EXTI0_IRQHandler(void) {
    flag = 1;
    HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_0);
}

int main(void) {
    while (!flag) { }  // -O2 이상에서 무한루프 탈출 불가
}
```

`-O2`로 컴파일하면 컴파일러는 `flag`가 루프 안에서 변경되지 않는다고 판단한다. 처음 읽은 값 0을 레지스터에 유지하고, 인터럽트에서 메모리의 `flag`를 1로 바꿔도 CPU는 레지스터의 0을 계속 본다.

```c
volatile uint8_t flag = 0;  // 매번 메모리에서 읽도록 강제
```

**인터럽트와 메인 루프 사이에서 공유되는 모든 변수는 `volatile`이어야 한다.**

최적화 없이(`-O0`) 개발하다가 릴리즈 빌드(`-O2`)로 바꿀 때 갑자기 버그가 생기는 경우, `volatile` 누락이 원인인 경우가 많다.

---

## 실무에서 자주 만나는 상황

### SysTick과 HAL_Delay

`HAL_Delay()`는 SysTick 인터럽트(예외 번호 15)가 발생할 때마다 내부 카운터를 증가시키는 방식으로 동작한다. 인터럽트 핸들러 안에서 `HAL_Delay()`를 호출하면?

SysTick 인터럽트가 현재 핸들러보다 우선순위가 낮으면 SysTick이 발생하지 않아 카운터가 증가하지 않는다 → **무한 대기**.

해결: 핸들러 안에서 delay가 필요하면 하드웨어 타이머를 쓰거나, 구조를 바꿔서 핸들러 밖에서 처리한다.

### UART 수신 인터럽트

```c
uint8_t rx_buf[64];
volatile uint8_t rx_len = 0;

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    rx_len++;
    HAL_UART_Receive_IT(&huart1, &rx_buf[rx_len], 1);
}
```

수신 완료마다 콜백이 호출되고, 다음 1바이트 수신을 다시 등록한다. 인터럽트 기반으로 CPU 점유 없이 데이터를 받을 수 있다.

