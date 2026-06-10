---
title: "임베디드 기초 2편 - 메모리 구조와 변수 저장 원리"
date: 2026-05-10T20:43:00+09:00
tags: ["embedded", "STM32", "memory", "flash", "RAM", "linker"]
categories: ["Embedded Basic"]
description: "STM32의 메모리 구조를 Flash, RAM, 섹션(.text/.data/.bss) 개념부터 링커 스크립트, Memory Map까지 정리한다."
---

## 들어가며

1편에서 펌웨어가 플래시에 저장되고, 변수는 RAM에서 동작한다고 정리했다. 그런데 막상 "전역변수는 어디 저장돼요?", "const는요?" 라는 질문을 받으면 정확하게 대답하기가 쉽지 않다.

---

## Flash vs RAM 다시 짚기

**플래시(Flash)**
- 비휘발성(non-volatile) — 전원을 꺼도 데이터가 유지된다
- 읽기는 자유롭지만, 쓰기는 Erase → Write 순서로 페이지/섹터 단위로만 가능하다
- 속도가 RAM보다 느리다
- 코드(명령어), 상수, 전역변수 초기값이 저장된다

**RAM**
- 휘발성(volatile) — 전원을 끄면 데이터가 사라진다
- 자유롭게 읽기/쓰기 가능하고 속도가 빠르다
- 실행 중 변하는 데이터(전역변수, 지역변수, 동적 할당(dynamic allocation))가 올라간다

---

## 메모리 섹션: .text / .data / .bss

링커는 빌드 결과물을 목적에 따라 여러 섹션으로 분리해서 관리한다.

```c
const int MAX = 100;  // 상수
int count = 5;        // 초기값 있는 전역변수
int total;            // 초기값 없는 전역변수
```

이 세 가지는 모두 다른 섹션에 들어간다.

### .text 섹션

함수 코드(명령어)와 `const` 상수가 들어가는 영역이다. 실행 중에 값이 바뀌지 않는 것들이 모인다. 플래시에만 저장되고 RAM으로 복사되지 않는다.

`const int MAX = 100;` 은 `.rodata`(read-only data) 섹션으로 분리되기도 하지만, 결국 플래시에 저장된다는 점은 동일하다.

### .data 섹션

**초기값이 있는 전역변수**가 들어간다. `int count = 5;` 가 여기에 해당한다.

여기서 중요한 점이 있다. `.data` 섹션은 플래시와 RAM 두 곳에 모두 관여한다.

- **플래시**: 초기값(`5`)을 저장해둔다
- **RAM**: 실행 중 실제 값이 올라가는 곳

부팅 시 startup code가 플래시에 저장된 초기값을 RAM으로 복사하기 때문에, `count = 5` 로 초기화된 상태에서 `main()` 이 시작된다.

### .bss 섹션

**초기값이 없는 전역변수**가 들어간다. `int total;` 이 여기에 해당한다.

C 표준에서 초기화되지 않은 전역변수는 **무조건 0으로 초기화**된다. (지역변수는 garbage value이지만 전역변수는 다르다.)

덕분에 `.bss` 섹션은 플래시에 실제 값을 저장할 필요가 없다. **크기 정보만** 플래시에 기록하고, 부팅 시 startup code가 그 크기만큼 RAM을 0으로 밀어버린다. 플래시 공간을 아낄 수 있는 이유다.

### 정리

| 섹션 | 저장 내용 | 플래시 | RAM |
|---|---|---|---|
| `.text` | 함수 코드, 상수 | O | X |
| `.data` | 초기값 있는 전역변수 | O (초기값) | O (실행 중) |
| `.bss` | 초기값 없는 전역변수 | 크기만 | O (0으로 초기화) |

---

## Stack과 Heap

### Stack

함수 호출과 함께 자동으로 관리되는 영역이다.

- 지역변수, 함수 인자, return address가 저장된다
- 함수가 종료되면 자동으로 해제된다
- 인터럽트 발생 시 현재 Program Counter(return address)도 스택에 저장된다

STM32(Cortex-M)에서 스택은 **높은 주소에서 낮은 주소 방향으로 내려오며(Descending)** 쌓인다. 반면 힙은 낮은 주소에서 높은 주소 방향으로 올라간다. 스택이 계속 내려오다가 힙 영역과 충돌하는 순간이 바로 **Stack Overflow**다. 임베디드에서 RAM이 작을수록 이 충돌 위험이 커진다.

```c
void foo() {
    int a = 10;  // 스택에 올라감, 높은 주소 → 낮은 주소 방향
}                // foo() 종료 시 자동 해제
```

### Heap

개발자가 직접 관리하는 동적 할당 영역이다.

- `malloc()` 으로 할당, `free()` 로 해제
- 해제를 안 하면 Memory Leak 발생

```c
int *p = (int *)malloc(sizeof(int) * 10);  // 힙에 할당
free(p);                                    // 직접 해제 필수
```

### 임베디드에서 malloc을 지양하는 이유

일반 PC에서는 메모리가 넉넉하지만, MCU는 RAM이 수십~수백 KB 수준이다. STM32F4 기준 RAM이 128KB밖에 안 된다.

이 제한된 환경에서 `malloc` 을 남용하면:

- **Fragmentation**: 할당과 해제를 반복하다 보면 작은 빈 공간들이 흩어져서 큰 메모리를 할당하지 못하는 상황이 발생한다
- **예측 불가능한 동작**: 할당 실패 시 NULL을 반환하는데, 임베디드에서 이를 제대로 처리하지 않으면 시스템이 뻗는다
- **real-time 성능 저하**: `malloc` 실행 시간이 일정하지 않아 Hard Real-Time 시스템에서 문제가 된다

그래서 임베디드에서는 가능하면 정적 할당(static allocation)을 쓰고, 동적 할당(dynamic allocation)이 필요하면 Memory Pool 방식을 사용한다.

---

## 링커 스크립트 (.ld)

링커 스크립트는 링커에게 메모리 구조를 알려주는 **설계도 파일**이다. STM32CubeIDE 프로젝트를 열면 `STM32xxx_FLASH.ld` 같은 파일이 있다.

```
MEMORY
{
  FLASH (rx) : ORIGIN = 0x08000000, LENGTH = 512K
  RAM (rwx)  : ORIGIN = 0x20000000, LENGTH = 128K
}

SECTIONS
{
  .text : { *(.text) } > FLASH
  .data : { *(.data) } > RAM AT > FLASH
  .bss  : { *(.bss)  } > RAM
}
```

여기서 `.data : > RAM AT > FLASH` 가 핵심이다.

- `> RAM`: 실행 중 주소는 RAM → **VMA (Virtual Memory Address)**, 코드가 실제로 참조하는 주소
- `AT > FLASH`: 초기값은 플래시에 저장 → **LMA (Load Memory Address)**, 데이터가 물리적으로 저장된 주소

즉 `.data` 섹션은 LMA(플래시)에 저장되어 있다가, 부팅 시 startup code가 VMA(RAM)로 복사한다. 링커 스크립트는 이 두 주소를 모두 계산해서 startup code에게 "어디서 어디로 복사해라"를 알려주는 역할을 한다.

---

## Memory Map과 Memory-Mapped I/O

STM32는 플래시, RAM, 주변장치 레지스터를 **하나의 주소 공간**으로 관리한다. 이를 **Memory Map** 이라고 한다.

| 주소 범위 | 영역 |
|---|---|
| `0x08000000~` | 플래시 (코드, 상수) |
| `0x20000000~` | RAM |
| `0x40000000~` | 주변장치 레지스터 (GPIO, UART 등) |

덕분에 CPU는 주소만 보고 어떤 메모리/장치에 접근하는지 구분할 수 있다.

주변장치 레지스터도 이 주소 공간에 매핑되어 있는데, 이를 **Memory-Mapped I/O** 라고 한다. 우리가 흔히 쓰는 코드가 실제로는 특정 메모리 주소에 값을 쓰는 것이다.

```c
GPIOA->ODR = 1;
// 실제로는 0x40020014 번지에 0x01을 쓰는 것
```

HAL 라이브러리나 CMSIS가 이 주소들을 구조체로 추상화해놓았기 때문에 우리는 `GPIOA->ODR` 처럼 직관적으로 쓸 수 있는 것이다.

CMSIS 헤더를 열어보면 레지스터 접근 구조체에 `volatile` 키워드가 붙어있다.

```c
typedef struct {
  volatile uint32_t ODR;  // volatile 없으면 컴파일러가 최적화로 생략할 수 있다
} GPIO_TypeDef;
```

`volatile` 은 컴파일러에게 "이 변수는 언제든 외부에서 값이 바뀔 수 있으니 최적화로 접근을 생략하지 마라"라고 알려주는 키워드다. 하드웨어 레지스터는 CPU가 모르는 사이에 하드웨어가 값을 바꿀 수 있기 때문에, `volatile` 없이는 컴파일러가 임의로 최적화해서 해당 접근을 제거할 수 있다. 자세한 내용은 이후 편에서 별도로 다룬다.

