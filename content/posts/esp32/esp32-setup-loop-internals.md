---
title: "setup()과 loop()는 어떻게 실행되는가"
date: 2026-04-11T20:55:00+09:00
draft: false
categories: ["ESP32"]
  - Embedded
tags:
  - ESP32
  - Arduino
  - C++
  - 임베디드
  - 부트로더
  - main
summary: "ESP32를 Arduino IDE로 개발하면 setup()과 loop()만 보인다. 그런데 실제로 전원이 켜진 순간부터 loop()가 돌기까지, 내부에서는 어떤 일이 일어날까."
---

ESP32를 Arduino IDE로 개발하면 처음에 다음 두 함수만 보인다.

```cpp
void setup() {
  // put your setup code here, to run once:
}

void loop() {
  // put your main code here, to run repeatedly:
}
```

단순해 보이지만, 이 구조가 왜 이렇게 생겼는지 알고 쓰는 것과 모르고 쓰는 건 다르다고 생각한다.

## 전원이 들어오면 실제로 무슨 일이 일어날까

### 1) MCU 리셋

전원을 연결하거나 리셋 버튼을 누르면, MCU 내부에서 가장 먼저 일어나는 일은 **프로그램 카운터(PC) 초기화**다.

프로그램 카운터가 초기화되지 않으면 이전 실행 주소가 남아있게 된다. 그러면 엉뚱한 위치부터 코드가 실행되거나 무한루프에 빠져 예측할 수 없는 동작이 발생한다.

### 2) 부트로더 실행

프로그램 카운터가 초기화되면, 플래시 메모리에 저장된 **부트로더** 코드가 먼저 실행된다.

부트로더가 하는 일:
- 새로운 프로그램 업로드 요청이 있는지 확인
- 업로드가 없으면 → 사용자 프로그램으로 점프

## Arduino Core가 숨겨놓은 진짜 시작점

사용자는 `main()`을 작성하지 않는다. 하지만 Arduino Core 내부에는 실제로 `main` 함수가 존재한다.

다음은 Arduino의 `main.cpp`다.

```cpp
#include <Arduino.h>

int atexit(void (* /*func*/ )()) { return 0; }

void initVariant() __attribute__((weak));
void initVariant() { }

void setupUSB() __attribute__((weak));
void setupUSB() { }

int main(void)
{
    init();
    initVariant();

#if defined(USBCON)
    USBDevice.attach();
#endif

    setup();

    for (;;) {
        loop();
        if (serialEventRun) serialEventRun();
    }

    return 0;
}
```

`setup()`은 단 한 번 호출되고, 그 다음 `for(;;)` 안에서 `loop()`가 무한히 반복되는 구조다.

## setup()은 왜 한 번만 실행될까

`setup()`은 **초기화 전용 함수**다. 여기서 주로 하는 일은 이렇다.

- GPIO 방향 설정 (`pinMode`)
- 통신 초기화 (`Serial.begin`, `Wire.begin` 등)
- 센서 초기 설정
- 변수 초기값 세팅

임베디드 개발 관점에서 보면 `setup()`은 시스템 초기화 단계에 해당한다.

만약 `setup()`이 반복 실행된다면 통신이 계속 초기화되고, 핀 상태가 계속 리셋된다. 시스템이 제대로 동작할 수가 없다. 그래서 Arduino Core는 `setup`은 1회, `loop`는 무한 반복이라는 구조를 강제한다.

## loop()에서 delay()를 쓰면 안 되는 이유

`loop()`의 실행 구조를 다시 보면:

```cpp
for (;;) {
    loop();
    if (serialEventRun) serialEventRun();
}
```

`loop()`는 `for(;;)` 안에서 계속 호출된다. 여기서 `delay()`를 사용하면 **CPU가 그 시간 동안 아무것도 하지 못하고 멈춰버린다**. 이걸 **Blocking**이라 부른다.

LED 하나 깜빡이는 수준에서는 문제가 없다. 하지만 센서를 읽으면서 Wi-Fi 통신도 처리하고 웹 서버도 돌려야 하는 상황이라면 `delay()` 하나가 전체 흐름을 막아버린다. ESP32처럼 많은 걸 동시에 처리해야 하는 환경에서는 특히 문제가 된다.

**인터럽트**를 쓰면 특정 이벤트가 발생했을 때만 CPU가 반응하도록 할 수 있고, **RTOS**를 쓰면 여러 작업을 시분할로 나눠 실행할 수 있다. ESP32는 FreeRTOS가 기본 탑재되어 있다.

취미로 ESP32를 쓴다면 `setup`에 초기화, `loop`에 반복 동작을 넣는 정도로도 충분하다.

하지만 조금 더 나아가려면 이 구조가 왜 이렇게 설계됐는지, 내부에서 어떤 순서로 실행되는지를 이해하는 게 도움이 된다. 특히 `delay()` 대신 인터럽트나 타이머를 쓰기 시작하면, 결국 이 실행 구조를 알고 있어야 제대로 활용할 수 있다.
