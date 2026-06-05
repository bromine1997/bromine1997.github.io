---
title: "[ESP32] PSRAM 버퍼링과 센서 데이터 저장 구조"
date: 2026-05-23T20:53:00+09:00
draft: false
categories:
  - Embedded
tags:
  - ESP32
  - PSRAM
  - 로드셀
  - 데이터수집
  - 임베디드
  - 재활자전거
summary: "40 SPS로 4채널 센서 데이터를 최대 36분간 끊김 없이 기록하기 위해 PSRAM을 버퍼로 사용했다. 구조체 설계부터 포인터 기반 저장, 분할 전송, 실시간 표시 분리까지 정리했다."
---

하드웨어 편에서 ADS1232 4개로 로드셀을 동시에 샘플링하는 구조를 설명했다. 이번에는 그 데이터를 어떻게 저장하고 관리하는지, PSRAM 버퍼 구조부터 분할 전송까지 정리해보겠다.

## 왜 Flash가 아닌 PSRAM인가

처음에는 측정 데이터를 SD카드나 SPIFFS(Flash)에 직접 저장하는 방식을 생각했다.

세 가지 문제가 있었다.

**첫째, Flash 쓰기는 느리다.**

SPIFFS 기준으로 단순 쓰기도 수 ms가 걸린다. 40 SPS로 샘플링 중이라면 한 샘플마다 25ms 안에 모든 처리를 끝내야 하는데, Flash 쓰기가 이 시간을 잡아먹으면 샘플을 놓친다.

**둘째, 내부 SRAM이 부족하다.**

ESP32 내부 SRAM은 약 520KB다. 여기에 Wi-Fi 스택이 100~200KB를 점유하고, AsyncWebServer와 WebSocket 라이브러리까지 올라가면 여유가 거의 없다. 1.65MB짜리 버퍼를 내부 SRAM에 올리는 건 처음부터 불가능하다. `malloc` 대신 `ps_calloc`을 쓴 이유가 바로 이것이다.

**셋째, Wi-Fi 스택과 메모리를 두고 경쟁하면 crash가 난다.**

Wi-Fi는 내부 SRAM에서 동작한다. 데이터 버퍼까지 같은 공간을 쓰면 메모리 단편화가 쌓이다가 어느 순간 Wi-Fi 재연결 중 OOM(Out of Memory)으로 재부팅된다. 이 버그는 재현도 불규칙하고 로그만 봐서는 원인을 잡기 어렵다. PSRAM은 내부 SRAM과 완전히 별도 영역이라 이 경쟁 자체를 피할 수 있다.

반면 PSRAM은 ns 단위로 읽고 쓴다. 메인 루프에서 포인터 대입 한 번이면 끝이다. ESP32 Feather V2에는 **2MB PSRAM**이 탑재되어 있어 이걸 전부 측정 버퍼로 쓰기로 했다.

## 데이터 구조 설계

저장 단위는 한 번의 샘플, 즉 로드셀 4채널 + 각도 1채널이다.

```cpp
struct sensors {
  volatile long DATA1;        // 우측 팔 (4 bytes)
  volatile long DATA2;        // 좌측 팔 (4 bytes)
  volatile long DATA3;        // 우측 다리 (4 bytes)
  volatile long DATA4;        // 좌측 다리 (4 bytes)
  unsigned long encoderAngle; // 크랭크 각도 (4 bytes)
};
// 총 20 bytes / 샘플
```

`volatile`은 ISR 안에서 값이 바뀌기 때문에 컴파일러 최적화를 막기 위해 붙였다. 이게 없으면 컴파일러가 "이 값은 여기서 안 바뀌네"라고 판단하고 레지스터에 캐시해버려서 ISR이 업데이트한 최신 값을 못 읽을 수 있다.

최대 기록 시간을 36분으로 잡았을 때 필요한 샘플 수와 메모리는:

```cpp
#define PACKET_SIZE (36 * 60 * 40)  // 86,400 샘플

// 86,400 샘플 × 20 bytes = 1,728,000 bytes ≈ 1.65 MB
```

2MB PSRAM 안에 들어온다.

## PSRAM 초기화

`setup()` 안에서 PSRAM을 확인하고 메모리를 할당한다.

```cpp
Serial.print("PSRAM found : ");
Serial.println(isPsram = psramFound());

if (isPsram) {
  if (psramInit()) {
    Serial.println((String)"Memory available in PSRAM : " + ESP.getFreePsram());
    workingPointer = packetPointer =
        (struct sensors *)ps_calloc(PACKET_SIZE, sizeof(struct sensors));
  } else {
    Serial.println("PSRAM initilization failed");
    isPsram = false;
  }
}
```

`ps_calloc`은 PSRAM에서 메모리를 할당하는 함수다. 일반 `malloc`을 쓰면 내부 SRAM에서 할당을 시도하는데, 앞서 말했듯 1.65MB는 처음부터 들어가지 않는다. `calloc`이기 때문에 할당과 동시에 0으로 초기화된다.

포인터는 두 개를 사용한다.

```cpp
struct sensors *packetPointer;   // 버퍼 시작 주소 (고정)
struct sensors *workingPointer;  // 현재 쓰기 위치 (이동)
```

`packetPointer`는 버퍼의 시작점을 가리키며 절대 바뀌지 않는다. `workingPointer`는 데이터를 쓸 때마다 앞으로 이동한다. 나중에 SAVE 명령이 오면 `workingPointer`를 `packetPointer`로 되돌려 처음부터 순서대로 전송한다.

## 메인 루프와 40 SPS

`loop()`의 핵심은 DRDY 핀의 **Falling Edge** 감지다.

ADS1232는 새 데이터가 준비되면 DRDY/DOUT 핀을 HIGH → LOW로 내린다. 이걸 소프트웨어 polling으로 감지한다.

```cpp
void loop() {
  c = digitalRead(pin_ADC_DRDY_DOUT_1);

  if ((t == HIGH) && (c == LOW)) {   // Falling Edge 감지
    DatSampleIdx++;
    WebSampleIdx++;

    if (DatSampleIdx >= DataSubSamplePoint) {  // 2번마다 1번 처리
      DatSampleIdx = 0;
      // 데이터 처리
    }
  }

  t = c;
}
```

ADS1232는 최대 80 SPS로 동작한다. `DataSubSamplePoint = 2`로 설정해두었기 때문에 Falling Edge 2번 중 1번만 실제로 처리한다. 결과적으로 40 SPS가 된다.

```cpp
#define DataSubSamplePoint 2   // 80 / 2 = 40 SPS
```

80 SPS를 전부 쓰지 않은 이유는, 40 SPS면 재활 운동 데이터 수집에 충분하고 처리 시간과 저장 용량이 절반으로 줄기 때문이다. 80 SPS를 그대로 쓰면 36분이 아니라 18분 제한이 된다.

## Falling Edge마다 일어나는 일

Falling Edge를 감지하고 `DatSampleIdx`가 조건을 만족하면 다음 순서로 처리된다.

```cpp
// 1. 클럭 펄스 24회 발생 → ISR이 4채널 데이터 수집
idx = 0;
for (int i = 0; i < 24; i++) {
  digitalWrite(pin_SCLK_OUT, HIGH);  delayMicroseconds(10);
  digitalWrite(pin_SCLK_OUT, LOW);   delayMicroseconds(10);
}

// 2. 각도 읽기 (I2C)
if (isWire) {
  Sensors.encoderAngle = as5600.readAngle();
} else {
  Sensors.encoderAngle = 8192;  // 미연결 표시
}

// 3. NeoPixel로 실시간 시각화 (디버깅용)
pixel.setPixelColor(0, Sensors.DATA1 << 8);
pixel.show();

// 4. PSRAM에 저장 (START 명령 이후에만)
if (isPsram) {
  if (!quit && packetCounter < PACKET_SIZE) {
    *workingPointer++ = Sensors;
    packetCounter++;
  }
}
```

1번에서 SCLK_OUT으로 24개의 클럭 펄스를 직접 발생시킨다. 이 펄스마다 SCLK_IN 핀에 인터럽트가 걸려 `SPI_ISR()`이 실행되고, 4채널 데이터가 1비트씩 수집된다. 24클럭이 끝나면 `Sensors.DATA1~4`에 최종 값이 들어있다.

2번에서 AS5600 각도를 I2C로 읽는다. 미연결 상태면 `8192`라는 예약값을 넣어 웹 UI에서 "N.C."로 표시하게 했다.

3번은 디버깅 용도다. NeoPixel의 G채널에 `DATA1` 값을 매핑하면 오른팔에 힘이 들어갈수록 LED가 밝아진다. 오실로스코프 없이 센서 동작을 육안으로 확인할 수 있어서 개발 중에 유용했다.

## PSRAM 저장 핵심 한 줄

```cpp
*workingPointer++ = Sensors;
```

C 포인터 문법이 익숙하지 않으면 낯설어 보이지만, 풀어쓰면 이렇다.

```cpp
*workingPointer = Sensors;   // workingPointer가 가리키는 주소에 Sensors 구조체 복사
workingPointer++;            // 포인터를 다음 구조체 위치로 이동
```

`++`는 바이트 단위가 아니라 **타입 크기 단위**로 이동한다. `struct sensors`가 20 bytes이므로 `workingPointer++`는 주소를 20 증가시킨다. 이렇게 하면 배열처럼 PSRAM에 구조체가 순서대로 쌓인다.

```
PSRAM
┌──────────────────────────────────────────────┐
│ Sensors[0] │ Sensors[1] │ ... │ Sensors[N]   │
└──────────────────────────────────────────────┘
↑                                              ↑
packetPointer                       workingPointer
```

## 실시간 화면 표시와 PSRAM 저장은 분리되어 있다

여기서 한 가지 흥미로운 점이 있다. 웹 화면을 열면 START를 누르지 않아도 센서 값이 실시간으로 표시된다. PSRAM에 저장하는 것과 화면에 보여주는 것이 완전히 분리된 구조이기 때문이다.

```cpp
if ((t == HIGH) && (c == LOW)) {
    DatSampleIdx++;
    WebSampleIdx++;  // quit 상태와 무관하게 항상 증가

    if (DatSampleIdx >= DataSubSamplePoint) {
        // PSRAM 저장: quit = false (START 이후)일 때만
        if (!quit && packetCounter < PACKET_SIZE) {
            *workingPointer++ = Sensors;
        }
    }

    // 화면 전송: 항상 동작, 16샘플(0.4초)마다 JSON 전송
    if (!NoNetwork && (WebSampleIdx >= 16)) {
        WebSampleIdx = 0;
        sendSensorsWs(null);
    }
}
```

`WebSampleIdx`는 `quit` 여부와 상관없이 Falling Edge마다 계속 증가한다. 16샘플(= 0.4초)마다 현재 `Sensors` 구조체 값을 JSON으로 브라우저에 보낸다. ISR은 항상 돌고 있으니 `Sensors`에는 항상 최신 값이 들어있다.

정리하면:
- **PSRAM 저장** → START 버튼을 눌러야 시작 (`quit = false`)
- **화면 실시간 표시** → 항상 동작, 0.4초마다 갱신

## STOP 후 SAVE: 데이터 전송 흐름

측정을 마치고 SAVE 버튼을 누르면 PSRAM에 쌓인 데이터를 처음부터 끝까지 브라우저로 전송한다.

```
STOP → quit = true  (측정 중단)
SAVE → save = true  (전송 시작)

PSRAM [샘플0][샘플1]...[샘플N]
         ↓ 5분치(12,000 샘플)씩
      1구간 전송 → 500ms 대기
      2구간 전송 → 500ms 대기
      ...
      나머지 전송
      1바이트 종료 신호
```

```cpp
#define PACKET_LENGTH (5 * 60 * 40)  // 5분치 = 12,000 샘플 = 240 KB

workingPointer = packetPointer;  // 포인터를 처음으로 되돌림

int pn = packetCounter / PACKET_LENGTH;  // 완전한 구간 수
int pr = packetCounter % PACKET_LENGTH;  // 나머지

for (int p = 0; p < pn; p++) {
  ws.binary(client_id, (uint8_t*)workingPointer, PACKET_LENGTH * sizeof(struct sensors));
  workingPointer += PACKET_LENGTH;
  delay(500);
}
if (pr) {
  ws.binary(client_id, (uint8_t*)workingPointer, pr * sizeof(struct sensors));
}
ws.binary(client_id, (uint8_t*)workingPointer, 1);  // 종료 신호
```

한 번에 전부 보내지 않고 5분치씩 나눠 보내는 이유는 WebSocket이 결국 TCP 위에서 동작하기 때문이다. ESP32의 TCP 송신 버퍼는 작아서 1.65MB를 한 번에 큐에 넣으면 버퍼가 넘친다. 5분치를 보내고 500ms를 기다리는 동안 TCP 스택이 실제로 데이터를 전송할 시간을 주는 것이다.

`delay(500)` 동안 `loop()`가 멈추기 때문에 이 시간에 Falling Edge가 와도 샘플을 놓친다. 그래서 SAVE는 반드시 STOP 이후에만 의미가 있고, 코드에서도 `quit && save` 조건일 때만 전송 로직이 실행된다.

브라우저 쪽에서는 데이터를 받을 때마다 `ArrayBuffer`에 누적하다가, 마지막 1바이트 종료 신호가 오면 파일로 저장한다.

## 상태 플래그 관리

```cpp
bool quit = true;   // 초기 상태: 측정 안 함
bool save = false;  // 저장 명령 플래그
```

WebSocket 명령에 따라 상태가 바뀐다.

```cpp
if (strcmp((char*)data, "START") == 0) {
  workingPointer = packetPointer;  // 포인터를 처음으로
  packetCounter = 0;
  quit = false;                    // 측정 시작
}
else if (strcmp((char*)data, "STOP") == 0) {
  quit = true;
}
else if (strcmp((char*)data, "SAVE") == 0) {
  client_id = client->id();
  save = true;
}
```

START 명령을 받으면 `workingPointer`를 `packetPointer`로 되돌리고 `packetCounter`를 0으로 리셋한다. 버퍼를 따로 초기화하지 않아도 이전 데이터는 논리적으로 없는 것과 같다. 36분이 지나 버퍼가 꽉 차면 자동으로 측정을 중단한다.

```cpp
if (packetCounter == PACKET_SIZE) quit = true;
```

## 마무리

이번 글에서 다룬 내용을 정리하면:

- **왜 PSRAM**: Flash 쓰기 지연, 내부 SRAM 용량 한계, Wi-Fi 스택과의 메모리 경쟁 세 가지를 동시에 해결
- **데이터 구조**: `struct sensors` 20 bytes × 86,400 샘플 = 1.65 MB
- **40 SPS**: `DataSubSamplePoint = 2`로 80 SPS를 절반만 처리
- **저장 방식**: `*workingPointer++ = Sensors`로 구조체를 순서대로 저장
- **화면 표시와 저장 분리**: `WebSampleIdx`는 항상 증가, 0.4초마다 JSON 전송
- **SAVE 전송**: 5분 단위로 나눠 전송, 1바이트 종료 신호로 완료 통보

다음 글에서는 측정 전 반드시 해야 하는 영점 보정(캘리브레이션) 로직과 EEPROM 레이아웃, 그리고 AS5600 각도 센서 연동 방법을 자세히 설명하겠다.
