---
title: "[임베디드 기초] 7편 - 클럭 심화: 보드레이트와 SPI 속도는 어떻게 계산되는가"
date: 2026-06-09T20:46:00+09:00
tags: ["embedded", "STM32", "UART", "SPI", "baud rate", "clock", "RCC", "APB"]
categories: ["Embedded Basic"]
description: "APB 클럭에서 UART 보드레이트와 SPI 속도가 계산되는 원리, 오차 계산, 실무에서 만나는 클럭 관련 문제들을 정리한다."
---

## 들어가며

---

## UART 보드레이트 계산

### BRR 레지스터

STM32 UART는 BRR(Baud Rate Register)로 분주비를 설정한다. 기본 16배 오버샘플링(OVER8=0) 기준:

```
Baud Rate = f_PCLK / (16 × USARTDIV)
```

`USARTDIV`는 정수부(12비트)와 소수부(4비트)로 구성된다. 소수점 이하 4비트이므로 1/16 단위까지 설정 가능하다.

### 계산 예시

**UART2, APB1 = 42 MHz, 목표: 115200 bps**

```
USARTDIV = 42,000,000 / (16 × 115,200) = 22.786...

정수부: 22
소수부: 0.786 × 16 = 12.576 → 반올림 → 13

BRR = (22 << 4) | 13 = 0x016D
```

실제 보드레이트 역산:

```
USARTDIV_actual = 22 + 13/16 = 22.8125
Baud Rate       = 42,000,000 / (16 × 22.8125) = 114,942 bps

오차 = |115,200 - 114,942| / 115,200 × 100 ≈ 0.22%
```

UART는 일반적으로 오차 **±2% 이내**면 통신 가능하다. 0.22%는 문제없다.

HAL 라이브러리가 이 계산을 자동으로 처리한다. 하지만 APB 클럭이 틀리면 HAL이 계산한 BRR 값도 틀리고, 그러면 상대방과 보드레이트가 맞지 않아 데이터가 깨진다.

### UART1 vs UART2

```c
// UART2: APB1 42MHz 기준
// UART1: APB2 84MHz 기준
// 같은 115200을 설정해도 BRR 값이 다르다
```

| | UART2 (APB1=42MHz) | UART1 (APB2=84MHz) |
|---|---|---|
| USARTDIV | 22.8125 | 45.5625 |
| BRR | 0x016D | 0x02D9 |
| 실제 보드레이트 | 114,942 bps | 115,108 bps |
| 오차 | 0.22% | 0.08% |

APB2가 더 높으니 오차가 더 작다.

---

## SPI 클럭 계산

UART와 달리 SPI는 소수점 분주가 없다. **2의 거듭제곱 분주비**만 지원한다.

```c
// SPI1: APB2(84MHz) 기준
// SPI_BAUDRATEPRESCALER_2   → 84 / 2  = 42 MHz
// SPI_BAUDRATEPRESCALER_4   → 84 / 4  = 21 MHz
// SPI_BAUDRATEPRESCALER_8   → 84 / 8  = 10.5 MHz
// SPI_BAUDRATEPRESCALER_16  → 84 / 16 = 5.25 MHz
// ...
// SPI_BAUDRATEPRESCALER_256 → 84 / 256 ≈ 328 kHz
```

원하는 정확한 속도를 만들 수 없는 경우가 많다. 연결하는 장치의 **최대 SPI 클럭보다 낮은 쪽으로 내림**해서 선택한다.

**예: ADS1232 ADC, 최대 SPI 클럭 1 MHz**

```
SPI1(APB2 84MHz) 기준
→ DIV128: 84/128 ≈ 656 kHz  ✓ (1MHz 이하)
→ DIV64:  84/64  ≈ 1.3 MHz  ✗ (초과)
```

DIV128을 선택해야 한다.

```c
hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_128;
```

---

## 클럭 관련 실무 문제들

### 보드레이트가 맞는데 데이터가 깨진다

원인 후보:
1. `HSE_VALUE`가 실제 크리스탈 주파수와 다름
2. APB 분주비가 예상과 다름 (CubeMX 설정 확인)
3. 상대방 장치의 클럭 오차 누적

확인 방법: 오실로스코프로 실제 전송 주기 측정. 115200 bps면 1비트당 약 8.68 μs여야 한다.

### SPI 통신이 간헐적으로 실패한다

SPI 속도가 너무 빠를 때 자주 발생한다. 배선 길이와 커패시턴스로 인한 신호 열화가 원인인 경우가 많다.

→ 분주비를 한 단계 낮춰서(속도를 절반으로) 테스트.

### SystemClock_Config() 이후 HAL_Delay()가 부정확하다

`HAL_RCC_ClockConfig()` 호출 후 `SystemCoreClock` 변수가 업데이트된다. 이 변수 기반으로 SysTick이 재설정되는데, 순서가 틀리면 Delay가 부정확해진다.

CubeMX가 생성하는 코드 순서를 바꾸지 않는 것이 안전하다.

