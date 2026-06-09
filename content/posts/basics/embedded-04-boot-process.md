---
title: "[임베디드 기초] 4편 - ARM Cortex-M 부팅 과정: 전원 인가에서 main()까지"
date: 2026-05-21T20:51:00+09:00
tags: ["embedded", "ARM", "Cortex-M", "startup", "reset handler", "vector table", "boot"]
categories: ["Embedded Basic"]
description: "ARM Cortex-M MCU에 전원이 들어오는 순간부터 main()이 실행되기까지, 벡터 테이블과 Reset_Handler, startup code의 동작을 정리한다."
---

## 들어가며

3편에서 `.c` 파일이 `.elf`를 거쳐 플래시에 올라가는 빌드 과정을 정리했다. 이제 반대 방향을 볼 차례다. 플래시에 올라간 펌웨어를 MCU가 어떻게 실행하는가.

전원이 켜지는 순간 CPU는 어디서부터 코드를 시작할까? 내가 작성한 `main()`이 첫 번째로 실행되는 것일까?

그렇지 않다. `main()` 이전에 이미 여러 단계가 실행된다.

---

## ARM Cortex-M 메모리 맵

![ARM Cortex-M 메모리 맵 — ARMv7-M ARM Table B3-1](/images/basics/armv7m-address-map-full.png)

Cortex-M은 모든 제조사가 공통으로 따르는 표준 메모리 맵을 갖는다. STM32든 nRF52든 RP2040이든 코어 수준에서는 동일한 주소 배치를 사용한다.

| 주소 범위 | 영역 | 비고 |
|---|---|---|
| `0x00000000 ~ 0x1FFFFFFF` | 코드 영역 (Flash) | .text, .rodata, .data LMA |
| `0x20000000 ~ 0x3FFFFFFF` | SRAM | 스택, 힙, .data VMA, .bss |
| `0x40000000 ~ 0x5FFFFFFF` | 주변장치 레지스터 | GPIO, UART, SPI 등 MMIO |
| `0x60000000 ~ 0x7FFFFFFF` | 외부 RAM (WBWA) | 단순 MCU에서는 미사용 |
| `0x80000000 ~ 0x9FFFFFFF` | 외부 RAM (WT) | 단순 MCU에서는 미사용 |
| `0xA0000000 ~ 0xBFFFFFFF` | 외부 장치 (Shareable) | 단순 MCU에서는 미사용 |
| `0xC0000000 ~ 0xDFFFFFFF` | 외부 장치 (Non-shareable) | 단순 MCU에서는 미사용 |
| `0xE0000000 ~ 0xFFFFFFFF` | 시스템 영역 | NVIC, SysTick, SCB, PPB |

ARMv7-M은 4GB 주소 공간을 512MB씩 8개 파티션으로 나눈다. 단순 MCU에서는 Flash/SRAM/주변장치/시스템 4개 영역만 실제로 사용한다.

제조사마다 플래시 시작 주소는 다를 수 있다. STM32F4는 `0x08000000`에서 시작하지만, 리셋 직후 이 영역이 `0x00000000`에 미러링된다.

---

## 리셋이 일어나면

전원 인가, 리셋 핀, 소프트웨어 리셋 — 어떤 원인이든 리셋이 발생하면 Cortex-M은 정해진 순서로 동작한다.

1. `0x00000000` 번지를 읽어 **스택 포인터(MSP)** 초기값을 설정한다
2. `0x00000004` 번지를 읽어 **Reset_Handler** 주소를 가져온다
3. 그 주소로 점프한다

이 두 주소가 **벡터 테이블**의 첫 두 항목이다. CPU는 이 두 가지만 읽고 나머지는 전부 Reset_Handler에게 넘긴다.

ARMv7-M ARM B1.5.5에 수록된 TakeReset() 의사코드가 이 과정을 정확히 기술한다:

```
vectortable = VTOR<31:7>:'0000000';
SP_main = MemA[vectortable, 4] AND 0xFFFFFFFC   // [0] → MSP 초기값
tmp     = MemA[vectortable+4, 4]                // [1] → Reset_Handler 주소
EPSR.T  = tmp<0>                                // LSB → Thumb 모드 설정
BranchTo(tmp AND 0xFFFFFFFE)                    // 실제 주소로 점프
```

CPU가 하는 일은 정확히 이게 전부다. 벡터 테이블 두 항목을 읽고, Thumb 비트를 설정하고, Reset_Handler로 점프한다.

---

## 벡터 테이블

![벡터 테이블 구조 — ARMv7-M ARM B1.5.2~B1.5.3](/images/basics/armv7m-vector-table-full.png)

벡터 테이블은 예외/인터럽트 핸들러들의 주소를 모아둔 배열이다. 플래시의 맨 앞에 위치한다.

```c
// startup_stm32f4xx.c (C로 작성하는 경우)
__attribute__((section(".isr_vector")))
const uint32_t vector_table[] = {
    (uint32_t)&_estack,          // [0] 스택 초기값 — RAM 끝 주소
    (uint32_t)Reset_Handler,     // [1] 리셋 핸들러
    (uint32_t)NMI_Handler,       // [2] Non-Maskable Interrupt
    (uint32_t)HardFault_Handler, // [3] 하드폴트
    // ... 이후 인터럽트 핸들러들
};
```

`[0]`은 함수 주소가 아니라 RAM의 끝 주소다. 스택은 높은 주소에서 아래로 내려오기 때문에 RAM 끝을 스택 시작점으로 쓴다. `_estack`은 링커 스크립트가 계산해서 넘겨주는 심볼이다.

### Thumb 모드와 LSB=1

벡터 테이블에 저장된 핸들러 주소를 직접 보면 실제 함수 주소보다 1이 크다.

```
Reset_Handler 실제 위치: 0x08000184
벡터 테이블에 저장된 값: 0x08000185
```

이 LSB 1비트는 Cortex-M이 **Thumb 모드**로 진입한다는 표시다. ARMv7-M ARM B1.5.3은 이렇게 명시한다:

> "All other entries must have bit[0] set to 1, because this bit defines the EPSR.T bit on exception entry."

Cortex-M은 Thumb-2 명령셋만 지원하므로 모든 함수 진입점의 LSB는 항상 1이다. CPU는 점프할 때 이 비트를 `EPSR.T`에 적용하고, 실제 주소 계산에서는 제거한다. LSB=0인 핸들러 주소가 벡터 테이블에 들어가면 UsageFault가 발생한다.

---

## Reset_Handler: startup code

Reset_Handler는 직접 작성하지 않아도 IDE나 CMSIS가 제공하는 startup 파일에 구현되어 있다. `startup_stm32f4xx.s`를 열어보면 어셈블리로 이런 흐름이다:

```asm
Reset_Handler:
    /* 1. .data 섹션 복사 (플래시 LMA → RAM VMA) */
    ldr  r0, =_sdata      /* RAM .data 시작 주소 (VMA) */
    ldr  r1, =_edata      /* RAM .data 끝 주소       */
    ldr  r2, =_sidata     /* 플래시 초기값 시작 (LMA) */
LoopCopyData:
    cmp  r0, r1
    ittt lt
    ldrlt r3, [r2], #4
    strlt r3, [r0], #4
    blt  LoopCopyData

    /* 2. .bss 섹션 0으로 초기화 */
    ldr  r0, =_sbss
    ldr  r1, =_ebss
    mov  r2, #0
LoopZeroBss:
    cmp  r0, r1
    itt  lt
    strlt r2, [r0], #4
    blt  LoopZeroBss

    /* 3. SystemInit() — 클럭 설정 */
    bl   SystemInit

    /* 4. main() 호출 */
    bl   main

    /* main()이 리턴되면 무한루프 (이론상 리턴 안 됨) */
LoopForever:
    b    LoopForever
```

2편에서 설명한 LMA/VMA 개념이 여기서 실제로 쓰인다. `_sdata`, `_edata`, `_sidata` 같은 심볼들은 링커 스크립트가 계산해서 넘겨준다. startup code와 링커 스크립트가 쌍으로 맞물려야 부팅이 제대로 동작하는 이유다.

---

## SystemInit()

Reset_Handler가 `main()`을 호출하기 전에 `SystemInit()`을 먼저 부른다. `system_stm32f4xx.c`에 정의된 함수로, MCU의 클럭 시스템을 초기화한다.

리셋 직후 Cortex-M은 내부 RC 오실레이터(HSI)로 낮은 클럭에서 시작한다. `SystemInit()`이 PLL을 설정해서 사용자가 지정한 속도(STM32F4 기준 최대 168 MHz)로 올려준다. `main()` 진입 시점에는 이미 클럭 설정이 완료된 상태다.

---

## main()까지의 전체 흐름

![Reset_Handler에서 main()까지](/images/basics/reset-handler-flow.svg)

```
전원 인가 / 리셋
  ↓
벡터 테이블 [0] 읽기 → MSP(스택 포인터) 설정
  ↓
벡터 테이블 [1] 읽기 → Reset_Handler 주소로 점프
  ↓
Reset_Handler
  ├─ .data 복사 (플래시 LMA → RAM VMA)
  ├─ .bss 초기화 (0으로)
  └─ SystemInit() (클럭 설정)
  ↓
main()
```

우리가 작성하는 `main()`이 시작되는 시점에는 이미:
- 스택이 설정되어 있고
- 전역변수 초기값이 RAM에 올라와 있고
- 클럭이 설정되어 있다

이 모든 것이 startup code가 미리 해준 일이다.

