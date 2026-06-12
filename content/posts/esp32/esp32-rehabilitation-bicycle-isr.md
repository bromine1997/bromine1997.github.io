---
title: "4개의 로드셀을 동시에 측정하기 - 소프트웨어"
date: 2026-05-27T20:28:00+09:00
draft: false
categories: ["ESP32"]
tags:
  - ESP32
  - ADS1232
  - ISR
  - 인터럽트
  - 비트뱅잉
  - 로드셀
  - 재활자전거
summary: "ADS1232 4채널을 왜 Hardware SPI 대신 GPIO 인터럽트로 읽었는가. IRAM_ATTR가 필요한 이유, 4채널 동시 비트 수집 구조, 24비트 2의 보수 부호 처리까지 정리했다."
---

하드웨어 편에서 ADS1232를 4개 사용해 외부 오실레이터로 동기화하는 구조를 설명했다. 이번에는 실제로 데이터를 어떻게 읽어오는지, ESP32 소프트웨어 측면을 정리한다.

## Hardware SPI를 쓰면 안 되나

회로도만 보면 SPI처럼 생겼다. SCLK과 DOUT가 있다. 그러면 `SPI.begin()`으로 읽으면 되지 않을까 싶다.

SPI는 CS(Chip Select) 핀을 각 슬레이브마다 달아 1대 다 통신이 가능하다. 그러면 ADS1232 4개에 CS 핀 4개를 연결하고 순서대로 읽으면 되지 않을까?

문제는 "순서대로"에 있다.

![Hardware SPI vs GPIO 인터럽트 방식 비교](/images/esp32/spi-vs-isr-comparison.png)

채널 1을 읽고, 채널 2를 읽는 사이에 시간이 존재한다. 순서대로 접근하는 구조이기 때문에 4채널 데이터가 동일한 시점의 값이라는 보장이 없다.

재활자전거에서는 팔과 다리에서 발생하는 힘을 **동일한 시점**에 비교해야 한다. 환자가 페달을 밟는 순간 좌우 균형이 어떤지, 팔과 다리의 협응이 어떤지를 보는 것이기 때문이다. 채널 간에 시간차가 있으면 분석 결과를 신뢰할 수 없게 된다.

하드웨어 편에서 외부 오실레이터로 4개의 ADS1232가 정확히 동시에 샘플링을 완료하도록 설계했다. 그런데 읽는 타이밍이 어긋나면 그 노력이 전부 무너진다.

GPIO 인터럽트 방식은 클럭 엣지 하나에서 4개 핀을 한꺼번에 읽으니 채널 간 시간 오차가 없다.

## IRAM_ATTR가 붙어 있는 이유

ISR 선언부를 보면 `IRAM_ATTR`라는 키워드가 있다.

```cpp
void IRAM_ATTR SPI_ISR()
{
  // ...
}
```

이게 왜 필요한지는 SPIFFS와 관련이 있다.

이 프로젝트는 SPIFFS를 사용해 `index.html`, `script.js`, `style.css`를 ESP32 내부 플래시에 올려두고 웹 서버로 서빙한다. SPIFFS가 파일을 읽을 때는 내부 플래시에 접근하는데, 이 순간 **ESP32의 명령어 캐시가 일시적으로 꺼진다**.

캐시가 꺼진 상태에서는 IRAM(내부 RAM)에 있는 코드만 실행 가능하고, 플래시에 있는 코드는 실행되지 않는다.

만약 ISR이 플래시에 있는 상태에서 SPIFFS 읽기 중에 인터럽트가 발생하면 CPU가 ISR 코드를 가져올 수 없어 크래시가 난다.

`IRAM_ATTR`를 붙이면 컴파일러가 해당 함수를 IRAM에 배치한다. SPIFFS가 캐시를 끄든 말든 ISR은 IRAM에 있으니 항상 안전하게 실행된다.

ISR 코드를 단순하게 유지한 이유도 여기에 있다. ISR 안에서 IRAM에 없는 외부 함수를 호출하면 결국 플래시에 있는 코드로 점프하게 되어 똑같은 문제가 생긴다. ISR은 GPIO 읽기와 산술 연산만 한다.

## ISR 구조

![ADS1232 SCLK 타이밍 다이어그램](/images/esp32/ads1232-sclk-timing.svg)
*SCLK 한 사이클마다 4채널 DOUT를 동시에 읽어 비트를 누적한다. 24클럭 후 값이 확정된다.*

```cpp
volatile unsigned long uDATA1 = 0;
volatile unsigned long uDATA2 = 0;
volatile unsigned long uDATA3 = 0;
volatile unsigned long uDATA4 = 0;
volatile int idx = 0;

void IRAM_ATTR SPI_ISR()
{
  idx++;
  uDATA1 = (uDATA1 << 1) + digitalRead(pin_ADC_DRDY_DOUT_1);  // GPIO 27
  uDATA2 = (uDATA2 << 1) + digitalRead(pin_ADC_DRDY_DOUT_2);  // GPIO 15
  uDATA3 = (uDATA3 << 1) + digitalRead(pin_ADC_DRDY_DOUT_3);  // GPIO 32
  uDATA4 = (uDATA4 << 1) + digitalRead(pin_ADC_DRDY_DOUT_4);  // GPIO 14

  if (idx >= 24) {
    DATA1_Raw = (long)(uDATA1 << 8) >> 8;
    DATA2_Raw = (long)(uDATA2 << 8) >> 8;
    DATA3_Raw = (long)(uDATA3 << 8) >> 8;
    DATA4_Raw = (long)(uDATA4 << 8) >> 8;

    Sensors.DATA1 = (DATA1_Raw - LoadcellOffset1) >> 6;
    Sensors.DATA2 = (DATA2_Raw - LoadcellOffset2) >> 6;
    Sensors.DATA3 = (DATA3_Raw - LoadcellOffset3) >> 4;
    Sensors.DATA4 = (DATA4_Raw - LoadcellOffset4) >> 4;

    uDATA1 = uDATA2 = uDATA3 = uDATA4 = 0;
    digitalWrite(ESP32_LED, blinkFlag = !blinkFlag);
  }
}
```

SCLK의 Falling Edge마다 이 ISR이 호출된다. 호출될 때마다 각 채널의 DOUT 핀에서 비트 1개를 읽어 `uDATA`에 누적한다.

```cpp
uDATA1 = (uDATA1 << 1) + digitalRead(pin_ADC_DRDY_DOUT_1);
```

`uDATA1`을 왼쪽으로 1비트 시프트하고, 새로 읽은 비트를 LSB에 더하는 방식이다. 이걸 24번 반복하면 24비트 데이터가 완성된다.

`idx`가 24에 도달하면 4채널이 모두 완성됐다는 뜻이다. 이 시점에 최종 처리를 하고 `uDATA`들을 다시 0으로 리셋한다.

## 24비트 2의 보수 처리

ADS1232는 24비트 부호 있는 정수를 2의 보수 형식으로 출력한다. 그런데 ESP32의 `long`은 32비트다. 단순히 `(long)uDATA`로 캐스팅하면 MSB가 부호 비트로 해석되지 않는다.

이걸 처리하는 코드가 아래 한 줄이다.

```cpp
DATA1_Raw = (long)(uDATA1 << 8) >> 8;
```

`uDATA1`은 24비트 데이터가 들어있는 32비트 변수다.

먼저 왼쪽으로 8비트 시프트(`<< 8`)하면 24비트 데이터가 32비트의 상위 24비트 위치로 올라간다. 이 상태에서 원래 데이터의 MSB(비트 23)가 32비트의 MSB(비트 31), 즉 부호 비트 위치에 놓인다.

그 다음 `(long)`으로 캐스팅하면 비트 31이 부호 비트로 인식된다. 이 상태에서 산술 오른쪽 시프트(`>> 8`)를 하면 부호 비트가 유지되면서 상위로 채워진다(부호 확장). 결과적으로 원래 24비트 값이 32비트 부호 있는 정수로 올바르게 변환된다.

```
원래 uDATA1 = 0xFF1234 (부정적인 값, MSB=1)

<< 8 → 0xFF123400  (비트 31이 1, 부호 비트 위치)
(long) → 해석: 음수
>> 8 → 0xFFFF1234  (산술 시프트, 부호 확장)

결과: -61900 (올바른 부호 있는 24비트 해석)
```

만약 `(long)uDATA1`로 단순 캐스팅했다면, MSB가 1인 경우 음수가 아닌 양수로 잘못 해석된다.

![24비트 부호 확장 과정](/images/esp32/24bit-sign-extension.svg)
*uDATA1 원본 → 왼쪽 8비트 시프트 → 산술 오른쪽 시프트로 부호 확장이 이루어지는 과정.*

## 오프셋과 스케일링

```cpp
Sensors.DATA1 = (DATA1_Raw - LoadcellOffset1) >> 6;
Sensors.DATA3 = (DATA3_Raw - LoadcellOffset3) >> 4;
```

`LoadcellOffset`은 캘리브레이션 시 EEPROM에 저장해둔 영점 값이다. 무부하 상태의 Raw값을 저장해두고, 측정할 때마다 빼서 영점을 맞춘다.

`>> 6`은 64로 나누기, `>> 4`는 16으로 나누기다. 채널마다 분해능이 다르게 설정되어 있어서 스케일을 다르게 줄였다. 비트 시프트를 쓴 이유는 나눗셈보다 빠르기 때문이다. ISR 안에서는 연산 시간이 짧을수록 좋다.

이후 웹 UI에 표시할 때 kg 단위로 환산하는 과정은 ISR 밖에서 게인 값을 곱해 처리한다.

```cpp
#define LoadcellCalGain1  0.0006    // R.A
#define LoadcellCalGain3  0.000965  // R.L
```

## 루프에서 클럭 직접 발생

ISR은 SCLK Falling Edge에 반응한다. 그러면 이 SCLK은 어디서 오는가?

ESP32가 직접 GPIO를 올렸다 내렸다 해서 생성한다. `setup()`에서 두 핀을 선언한다.

```cpp
pinMode(pin_SCLK_IN, INPUT);    // GPIO 25 — ISR 트리거용 입력
attachInterrupt(digitalPinToInterrupt(pin_SCLK_IN), SPI_ISR, FALLING);

pinMode(pin_SCLK_OUT, OUTPUT);  // GPIO 5 — ESP32가 클럭 출력
```

SCLK_OUT(GPIO 5)은 ESP32가 클럭을 내보내는 출력 핀이고, SCLK_IN(GPIO 25)은 그 신호를 받아 ISR을 트리거하는 입력 핀이다. 두 핀은 하드웨어에서 같은 SCLK 라인에 연결되어 있다.

```
ESP32 GPIO 5 (SCLK_OUT) ──┬──→ ADS1232 × 4 SCLK 핀
                           └──→ ESP32 GPIO 25 (SCLK_IN) → ISR 트리거
```

참고로 하드웨어 편에서 언급한 외부 오실레이터(4.9152 MHz)는 SCLK과 전혀 다른 신호다. ADS1232 내부 ADC의 샘플링 주기를 결정하는 CLKIN 핀에 연결되어 있고, 4개의 ADS1232가 동일한 타이밍에 변환을 완료하도록 동기화하는 역할이다. 변환이 완료됐다는 신호(DRDY)를 보내는 것과, 그 데이터를 읽어오기 위한 SCLK은 별개다.

`loop()`에서 채널 1의 DRDY 핀이 LOW로 떨어지는 Falling Edge를 소프트웨어로 감지한다. 4개의 ADS1232가 같은 오실레이터 클럭을 공유하므로, 채널 1이 준비됐다면 나머지 3개도 동시에 준비된 상태다.

```cpp
bool t, c;

void loop() {
  c = digitalRead(pin_ADC_DRDY_DOUT_1);

  if ((t == HIGH) && (c == LOW)) {  // Falling Edge 감지
    DatSampleIdx++;

    if (DatSampleIdx >= DataSubSamplePoint) {
      DatSampleIdx = 0;

      idx = 0;
      for (int i = 0; i < 24; i++) {
        digitalWrite(pin_SCLK_OUT, HIGH);  delayMicroseconds(10);
        digitalWrite(pin_SCLK_OUT, LOW);   delayMicroseconds(10);
      }
      // 이 시점에 Sensors.DATA1~4에 최신 값이 들어있다
    }
  }

  t = c;
}
```

`t`는 이전 상태, `c`는 현재 상태다. 이전이 HIGH이고 지금이 LOW면 Falling Edge가 발생한 것이다.

Falling Edge를 감지하면 SCLK_OUT 핀으로 HIGH-LOW 펄스를 24번 발생시킨다. 각 LOW 구간에 ISR이 호출되어 비트가 수집된다. 24번이 끝나면 `idx >= 24` 조건이 맞아 ISR 내부에서 데이터가 확정된다.

`delayMicroseconds(10)`은 클럭 한 상태당 10μs, 즉 50 kHz 클럭이다. ADS1232 데이터시트의 최대 SCLK 주파수(약 2 MHz) 대비 충분히 여유 있는 속도다.

## 80 SPS를 40 SPS로 쓰는 이유

ADS1232는 최대 80 SPS로 데이터를 출력한다. Falling Edge도 초당 80번 발생한다는 뜻이다.

`DataSubSamplePoint = 2`로 설정해두었기 때문에, 감지한 Falling Edge 2번 중 1번만 실제로 클럭을 발생시키고 데이터를 처리한다. 결과적으로 40 SPS가 된다.

```cpp
#define DataSubSamplePoint 2   // 80 / 2 = 40 SPS
```

40 SPS면 재활 운동처럼 느린 동작을 분석하기에 충분하다. 그리고 80 SPS를 전부 쓰면 36분 기록이 아니라 18분 기록으로 줄어든다. PSRAM 용량과의 균형을 맞춘 결과다.

