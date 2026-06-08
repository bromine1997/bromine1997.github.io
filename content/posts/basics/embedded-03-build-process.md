---
title: "[임베디드 기초] 3편 - 빌드 과정: 소스 코드가 플래시에 올라가기까지"
date: 2026-06-06T21:00:00+09:00
tags: ["embedded", "ARM", "Cortex-M", "toolchain", "linker", "ELF", "build"]
categories: ["Embedded Basic"]
description: "C 소스 파일이 MCU 플래시에 올라가기까지 전처리→컴파일→어셈블→링크 과정과 ARM Cortex-M 툴체인, ELF 포맷을 정리한다."
---
## 들어가며

2편에서 `.text`/`.data`/`.bss` 섹션과 링커 스크립트를 다뤘다. `.data > RAM AT > FLASH` 구문이 LMA와 VMA를 분리한다는 것까지 정리했다.

그런데 이 링커 스크립트는 누가, 언제, 어떻게 처리하는 걸까. `main.c` 하나를 작성하고 빌드 버튼을 누르면 어떤 일이 일어나는지 정확히 알지 못한 채로 쓰고 있었다.

3편에서는 소스 코드 한 줄이 MCU 플래시에 올라가기까지의 전체 과정을 짚어본다.

---

## ARM Cortex-M 툴체인

ARM Cortex-M을 타겟으로 빌드할 때 쓰는 컴파일러는 `arm-none-eabi-gcc`다.

이름을 뜯어보면:

- `arm`: 타겟 아키텍처
- `none`: 운영체제 없음 (bare-metal)ㄱ
- `eabi`: Embedded ABI — 함수 호출 규약, 데이터 정렬 방식 표준
- `gcc`: GNU Compiler Collection

STM32CubeIDE나 PlatformIO 같은 IDE를 쓰면 이 툴체인이 자동으로 설정된다. 직접 Makefile이나 CMake를 구성할 때는 직접 지정해야 한다.

툴체인에 포함된 주요 도구들:

| 도구                      | 역할                          |
| ------------------------- | ----------------------------- |
| `arm-none-eabi-gcc`     | C/C++ 컴파일러                |
| `arm-none-eabi-as`      | 어셈블러                      |
| `arm-none-eabi-ld`      | 링커                          |
| `arm-none-eabi-objcopy` | 포맷 변환 (.elf → .hex/.bin) |
| `arm-none-eabi-size`    | 섹션별 크기 출력              |
| `arm-none-eabi-objdump` | 역어셈블, 섹션 정보 확인      |

---

![빌드 과정 전체 흐름](/images/basics/build-flow.svg)

## 빌드 4단계

`.c` 파일 하나를 MCU에 올릴 수 있는 형태로 만들기까지 네 단계를 거친다.

### 1단계. 전처리 (Preprocessing)

`#include`, `#define`, `#ifdef` 같은 전처리 지시문을 처리한다. 헤더 파일을 소스에 붙여넣고, 매크로를 치환한다. 결과물은 `.i` 파일이다.

```bash
arm-none-eabi-gcc -E main.c -o main.i
```

전처리 결과를 직접 보면 헤더 파일이 통째로 붙어서 수천 줄짜리 파일이 되는 걸 확인할 수 있다. 컴파일러가 실제로 보는 것은 이 상태다.

### 2단계. 컴파일 (Compilation)

전처리된 C 코드를 어셈블리(`.s`)로 변환한다. 이 단계에서 컴파일러 최적화가 적용된다.

```bash
arm-none-eabi-gcc -S main.c -o main.s -mcpu=cortex-m4 -mthumb
```

`-mcpu=cortex-m4 -mthumb`가 중요하다. ARM Cortex-M은 Thumb-2 명령셋만 사용하기 때문에 `-mthumb` 없이 빌드하면 A32(ARM) 명령어가 생성되고 MCU에서 실행되지 않는다.

`-O0`(최적화 없음)과 `-O2`(최적화 켜짐)로 컴파일한 어셈블리를 비교하면 코드 양 차이가 꽤 크다. 최적화가 어떻게 동작하는지는 5편에서 따로 다룬다.

### 3단계. 어셈블 (Assembly)

어셈블리(`.s`)를 기계어로 변환한다. 결과물은 오브젝트 파일(`.o`)이다.

```bash
arm-none-eabi-as main.s -o main.o
```

오브젝트 파일은 아직 완전한 실행 파일이 아니다. 다른 파일에 정의된 함수나 변수의 주소가 미확정 상태로 남아 있다. 예를 들어 `printf()`를 호출하면 `printf`의 실제 주소는 이 단계에서 모른다.

### 4단계. 링킹 (Linking)

여러 `.o` 파일과 라이브러리를 하나로 합쳐 실행 파일을 만든다.

```bash
arm-none-eabi-ld -T STM32F4.ld main.o startup.o -o firmware.elf
```

이 단계에서 세 가지 일이 일어난다:

- **섹션 병합**: 여러 `.o`의 `.text`, `.data`, `.bss`를 하나로 합친다
- **주소 확정**: 미완성이던 함수/변수 주소를 실제 주소로 채운다
- **메모리 배치**: 링커 스크립트에 따라 각 섹션을 메모리 주소에 배치한다

결과물은 `.elf` 파일이다.

---

## ELF 포맷

![ELF 파일 구조와 메모리 배치](/images/basics/elf-structure.svg)

링킹 결과물인 `.elf`는 **Executable and Linkable Format**의 약자다. 리눅스 실행 파일과 동일한 포맷이다.

ELF 파일 안에는:

- `.text`, `.data`, `.bss` 섹션과 각각의 LMA/VMA 주소
- 심볼 테이블 (함수/변수 이름과 주소 매핑)
- 디버그 정보 (소스 파일 이름, 줄 번호)

가 들어 있다. 디버거(GDB)가 ELF를 읽으면 소스 코드의 어느 줄이 어느 주소에 해당하는지 알 수 있는 이유다.

`arm-none-eabi-size`로 섹션 크기를 확인할 수 있다:

```
$ arm-none-eabi-size firmware.elf
   text    data     bss     dec     hex filename
  12480     124    1536   14140    373c firmware.elf
```

- `text + data` = 플래시 사용량
- `data + bss` = RAM 사용량

빌드 후 이 숫자를 보는 습관이 있으면 메모리 초과를 미리 잡을 수 있다.

---

## .hex / .bin 변환

플래시에 올리려면 ELF를 `.hex` 또는 `.bin` 형식으로 변환해야 한다. `objcopy`가 이 역할을 한다.

```bash
arm-none-eabi-objcopy -O ihex   firmware.elf firmware.hex
arm-none-eabi-objcopy -O binary firmware.elf firmware.bin
```

- `.hex`: Intel HEX 포맷. 주소 정보와 데이터가 텍스트로 저장된다. ST-Link, J-Link 같은 디버거가 이 포맷을 주로 쓴다.
- `.bin`: 순수 바이너리. 주소 정보 없이 데이터만 있다. DFU나 부트로더를 통해 올릴 때 자주 쓴다.

---

## 전체 흐름 정리

```
main.c
  ↓ 전처리 (gcc -E)      → 헤더 병합, 매크로 치환
main.i
  ↓ 컴파일 (gcc -S)      → ARM Thumb-2 어셈블리
main.s
  ↓ 어셈블 (as)          → 기계어, 주소 미확정
main.o
  ↓ 링크 (ld + .ld)      → 섹션 배치, 주소 확정
firmware.elf
  ↓ objcopy              → 플래시에 올릴 수 있는 형태
firmware.hex / .bin
```

---

## 정리

- **툴체인**: `arm-none-eabi-gcc`가 Cortex-M 표준. bare-metal, Thumb-2 명령셋 타겟.
- **4단계**: 전처리 → 컴파일 → 어셈블 → 링크.
- **오브젝트 파일**: 기계어이지만 주소가 미확정. 링커가 여러 `.o`를 합치면서 주소를 확정한다.
- **ELF**: 섹션, 심볼, 디버그 정보를 모두 담은 링크 결과물.
- **`arm-none-eabi-size`**: text/data/bss 크기로 플래시·RAM 사용량 확인.

다음 편에서는 이렇게 만들어진 펌웨어가 MCU에서 실제로 어떻게 시작되는지 들여다본다. 전원이 켜지는 순간부터 `main()`이 시작되기까지, Cortex-M의 벡터 테이블과 Reset_Handler가 하는 일을 정리한다.
