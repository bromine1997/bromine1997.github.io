---
title: "[ESP32] 로드셀 영점 잡기와 분동 캘리브레이션 - EEPROM으로 저장하기"
date: 2026-04-17T02:00:00+09:00
draft: false
categories:
  - Embedded
tags:
  - ESP32
  - ADS1232
  - AS5600
  - EEPROM
  - 캘리브레이션
  - 로드셀
  - 재활자전거
summary: "ADS1232 4채널 로드셀과 AS5600 각도 센서의 영점을 버튼 하나로 잡고, 분동으로 게인을 맞추고, EEPROM에 저장해 전원을 꺼도 유지되게 한 과정을 정리했다."
---
ISR 편에서 ADC 값을 어떻게 읽는지 다뤘다. 이번에는 읽어온 값이 실제 무게(kg)로 나오게 만드는 과정이다. 센서가 연결됐는지 확인하는 부분도 함께 정리한다.

## 왜 캘리브레이션이 필요한가

ADS1232는 24비트 ADC다. 로드셀에 아무 무게도 걸지 않아도 출력이 0이 아니다. 원인은 두 가지다.

첫째, **기계적 오프셋**이다. 로드셀 자체가 이미 자기 무게를 지지하는 구조에 설치되어 있다. 팔 받침대, 페달 구조물, 고정 볼트 — 이것들이 전부 로드셀을 누른다. 아무것도 없는 상태여도 출력이 0이 아닌 이유다.

둘째, **회로 오프셋**이다. 앰프와 ADC에는 제조 공차로 인한 오프셋 전압이 있다.

같은 모델의 로드셀을 4개 써도 각각 오프셋이 다르다. 게인도 미묘하게 다를 수 있다.

잡아야 할 게 두 가지다. 아무것도 없을 때 0이 나오게 하는 **오프셋**과, 1kg가 1.000으로 나오게 하는 **게인**이다.

## EEPROM 레이아웃

오프셋과 게인은 전원을 꺼도 남아 있어야 한다. EEPROM에 저장한다.

```cpp
#define EEPROM_SIZE             64

#define EEPROM_AngleOffset      0   // short, 2 bytes
#define EEPROM_LoadcellOffset1  2   // long,  4 bytes  (Right Arm)
#define EEPROM_LoadcellOffset2  6   // long,  4 bytes  (Left Arm)
#define EEPROM_LoadcellOffset3  10  // long,  4 bytes  (Right Leg)
#define EEPROM_LoadcellOffset4  14  // long,  4 bytes  (Left Leg)

#define EEPROM_SSID             32  // char[16]
#define EEPROM_PASS             48  // char[16]
```

```
주소  내용             크기
0x00  각도 오프셋      2 bytes (short)
0x02  로드셀1 오프셋   4 bytes (long)
0x06  로드셀2 오프셋   4 bytes (long)
0x0A  로드셀3 오프셋   4 bytes (long)
0x0E  로드셀4 오프셋   4 bytes (long)
  |
0x20  Wi-Fi SSID       16 bytes
0x30  Wi-Fi 비밀번호   16 bytes
```

총 64바이트. 오프셋 4개(short 1 + long 4)가 18바이트를 쓰고, 나머지 영역은 Wi-Fi 자격증명이 쓴다. 주소 18~31은 미사용 예약 구간이다.

Arduino의 EEPROM 라이브러리는 실제 EEPROM 칩이 아니라 ESP32의 NVS 플래시 파티션을 에뮬레이션한다. 그래서 두 가지가 필수다:

```cpp
EEPROM.begin(EEPROM_SIZE);  // setup()에서 한 번만
// ...
EEPROM.commit();            // writeXxx 뒤에 반드시 호출
```

`commit()`을 빠뜨리면 `writeXxx`를 아무리 해도 플래시에 반영되지 않는다. RAM 버퍼에만 쓴 것이고, 전원이 꺼지면 사라진다.

## AS5600 연결 확인

각도 센서 AS5600은 I2C로 연결된다. 작동 중에 케이블이 빠지는 상황을 대비해야 한다.

```cpp
Wire.begin();
as5600.begin();
isWire = as5600.isConnected();
```

연결됐으면 `isWire = true`, 안 됐으면 `false`. 루프에서 이 플래그를 보고 분기한다:

```cpp
if ( isWire ) {
    Sensors.encoderAngle = as5600.readAngle();
    encoderRaw = as5600.rawAngle();
} else {
    Sensors.encoderAngle = encoderRaw = 8192;
}
```

AS5600의 유효 출력 범위는 0~4095(12비트)다. 8192는 이 범위를 벗어난 값이라 "연결 안 됨"을 나타내는 센티넬로 쓸 수 있다.

WebSocket으로 클라이언트에 데이터를 보낼 때도 이 값을 확인한다:

```cpp
readings["s5"] = ( Sensors.encoderAngle == 8192.0 )
    ? "N.C."
    : String((float)Sensors.encoderAngle * AS5600_RAW_TO_DEGREES, 2);
```

웹 화면에서 각도 값 자리에 "N.C."가 뜨면 센서 연결을 확인하면 된다.

## 버튼 하나로 영점 잡기

로드셀 4개와 각도 센서의 영점을 한 번에 잡을 수 있게 했다. 회로를 건드리거나 시리얼 모니터를 열 필요 없다. 버튼 하나다.

```cpp
// loop()에서
if ( !digitalRead(ESP32_BUTTON) && !digitalRead(ESP32_BUTTON) && !digitalRead(ESP32_BUTTON) ) {
    digitalWrite(pin_PDWN, LOW);    // ADS1232 파워다운 → 샘플링 정지
    digitalWrite(ESP32_LED, HIGH);  // LED 점등 → 진행 중 표시

    if ( isWire ) {
        as5600.setOffset( -encoderRaw * AS5600_RAW_TO_DEGREES );
        EEPROM.writeShort(EEPROM_AngleOffset, (short)encoderRaw );
    }
    EEPROM.writeLong(EEPROM_LoadcellOffset1, DATA1_Raw );  LoadcellOffset1 = DATA1_Raw;
    EEPROM.writeLong(EEPROM_LoadcellOffset2, DATA2_Raw );  LoadcellOffset2 = DATA2_Raw;
    EEPROM.writeLong(EEPROM_LoadcellOffset3, DATA3_Raw );  LoadcellOffset3 = DATA3_Raw;
    EEPROM.writeLong(EEPROM_LoadcellOffset4, DATA4_Raw );  LoadcellOffset4 = DATA4_Raw;
    EEPROM.commit();
}
while ( !digitalRead(ESP32_BUTTON) )  c = digitalRead(pin_ADC_DRDY_DOUT_1);
digitalWrite(pin_PDWN, HIGH);  // 샘플링 재개
```

순서대로 보면:

1. 버튼 눌림 감지 — 세 번 연속 확인은 채터링 방지용이다
2. `pin_PDWN = LOW` → ADS1232가 파워다운 모드로 진입, SCLK 클록을 보내도 변환이 일어나지 않는다
3. LED 점등 → 지금 캘리브레이션 중이라는 시각적 신호
4. **이 순간의 raw 값**을 오프셋으로 저장한다. 전제는 "지금 로드셀에 아무 부하가 없어야 한다"
5. `EEPROM.commit()` → 플래시에 기록
6. 버튼 뗄 때까지 대기 (뗄 때도 DRDY를 폴링해서 신호를 놓치지 않는다)
7. `pin_PDWN = HIGH` → ADS1232 재개

캘리브레이션 순서는 간단하다:

- 로드셀에서 모든 부하 제거
- 페달도 발 없이, 팔 받침대도 팔 올리지 않은 상태
- 버튼 꾹 누름 → LED 켜짐 → 뗌 → 완료

## ISR 안에서 오프셋 적용

저장된 오프셋은 인터럽트 핸들러에서 바로 적용된다:

```cpp
void IRAM_ATTR SPI_ISR() {
    // ... 24비트 수집 ...
    if ( idx >= 24 ) {
        DATA1_Raw = (long)(uDATA1 << 8) >> 8;
        Sensors.DATA1 = (DATA1_Raw - LoadcellOffset1) >> 6;

        DATA2_Raw = (long)(uDATA2 << 8) >> 8;
        Sensors.DATA2 = (DATA2_Raw - LoadcellOffset2) >> 6;

        DATA3_Raw = (long)(uDATA3 << 8) >> 8;
        Sensors.DATA3 = (DATA3_Raw - LoadcellOffset3) >> 4;

        DATA4_Raw = (long)(uDATA4 << 8) >> 8;
        Sensors.DATA4 = (DATA4_Raw - LoadcellOffset4) >> 4;
    }
}
```

팔 채널은 오프셋 제거 후 `>> 6`(64로 나누기), 다리 채널은 `>> 4`(16으로 나누기)로 스케일을 줄인다. 게인이 다른 이유 중 하나가 이 오른쪽 시프트 차이다 — 다리 채널은 분해능을 더 살렸다.

## 분동으로 게인 맞추기

오프셋이 0으로 잡혔으면 이제 1kg가 1.000이 되게 스케일을 맞춰야 한다.

1kg, 3kg, 5kg 분동 세트를 준비했다. 영점 잡기 완료 후 분동을 로드셀 위에 올리고 시리얼 모니터에서 `Sensors.DATA` 값을 읽는다.

### 직선의 기울기로 게인 계산

로드셀은 스트레인 게이지 기반이라 무게와 출력 사이에 선형 관계가 성립한다. 영점을 0으로 잡았으니 원점을 통과하는 직선이다.

```
무게(kg) = Sensors.DATA × Gain
```

분동 3개로 측정 포인트를 얻는다:

```
x축: Sensors.DATA 값 (ADC 출력)
y축: 무게 (kg)

(DATA_1kg, 1.0)
(DATA_3kg, 3.0)
(DATA_5kg, 5.0)
```

원점을 통과하는 직선의 기울기는:

```
Gain = Σ(DATA_i × weight_i) / Σ(DATA_i²)
```

분동이 몇 개 없으니 복잡하게 할 필요는 없다. 각 포인트에서 기울기를 구하고 평균 내도 비슷한 결과가 나온다:

```
Gain = mean( weight_i / DATA_i )
     = (1/DATA_1kg + 3/DATA_3kg + 5/DATA_5kg) / 3
```

세 포인트가 완벽한 직선 위에 있지는 않다. 로드셀 설치 각도, 분동 올리는 위치, 측정 시 노이즈 등으로 약간의 산포가 생긴다. 하지만 선형 재료인 스트레인 게이지 특성상 충분히 수렴하고, 임상 재활 데이터 수준에서는 이 오차가 문제가 되지 않는다고 판단했다.

### 팔 로드셀 (채널 1, 2)

세 포인트에서 기울기를 구하면 모두 0.0006 근방으로 수렴했다. 팔 두 채널은 같은 구조로 설치됐고 결과도 일치해 게인을 공유한다.

### 다리 로드셀 (채널 3, 4)

다리 채널은 로드셀 설치 위치와 페달 구조 때문에 팔과 다른 게인이 나온다. 좌/우 페달 구조가 대칭이 아니라 채널 3과 4의 기울기도 서로 다르게 나왔다.

```
채널 3 (Right Leg): Gain ≈ 0.000965
채널 4 (Left Leg):  Gain ≈ 0.000871
```

팔보다 다리 채널 게인이 큰 이유는 ISR에서 `>> 4`(16으로 나누기)만 해서 `Sensors.DATA` 값이 상대적으로 작기 때문이다. 팔은 64로 나눠 값이 더 크고 게인이 작다.

### 코드에 하드코딩

게인은 한 번 정해지면 변경할 일이 없어서 매크로 상수로 박아뒀다:

```cpp
#define LoadcellCalGain1  0.0006    // Right Arm
#define LoadcellCalGain2  0.0006    // Left Arm
#define LoadcellCalGain3  0.000965  // Right Leg
#define LoadcellCalGain4  0.000871  // Left Leg
```

실제 출력 변환:

```cpp
readings["s1"] = String((float)Sensors.DATA1 * LoadcellCalGain1, 3);  // kg, 소수점 3자리
readings["s2"] = String((float)Sensors.DATA2 * LoadcellCalGain2, 3);
readings["s3"] = String((float)Sensors.DATA3 * LoadcellCalGain3, 3);
readings["s4"] = String((float)Sensors.DATA4 * LoadcellCalGain4, 3);
```

## 전원 켤 때마다 자동 복원

전원을 끄면 RAM 변수는 모두 사라진다. setup()에서 EEPROM을 읽어 복원한다:

```cpp
EEPROM.begin(EEPROM_SIZE);

if ( isWire ) {
    encoderOffset = EEPROM.readShort(EEPROM_AngleOffset);
    as5600.setOffset( -encoderOffset * AS5600_RAW_TO_DEGREES );
    Serial.println((String)"Angle Offset read : " + encoderOffset);
}

LoadcellOffset1 = EEPROM.readLong(EEPROM_LoadcellOffset1);
LoadcellOffset2 = EEPROM.readLong(EEPROM_LoadcellOffset2);
LoadcellOffset3 = EEPROM.readLong(EEPROM_LoadcellOffset3);
LoadcellOffset4 = EEPROM.readLong(EEPROM_LoadcellOffset4);
```

전원을 켜는 순간 이전에 저장한 오프셋이 그대로 살아난다. 시리얼 모니터를 열면 읽어온 오프셋 값이 출력되어 저장이 제대로 됐는지 확인할 수 있다.

## 부팅 중 버튼으로 단독 모드 진입

캘리브레이션 작업은 Wi-Fi 연결 없이 시리얼 모니터만으로도 충분하다. 부팅 중 버튼을 누른 채로 켜면 네트워크 없이 동작하는 모드가 있다:

```cpp
if ( !digitalRead(ESP32_BUTTON) ) {
    NoNetwork = true;
    isPsram = false;
}
```

NeoPixel로 상태를 구분한다:

- **초록**: 정상 모드, Wi-Fi 연결 시도
- **빨강**: 단독 모드, Wi-Fi 없이 시리얼만

단독 모드에서는 `Sensors.DATA` 값이 시리얼로 출력된다. 분동을 올리고 내리면서 숫자를 직접 읽을 수 있어 게인 측정이 편하다.

## 정리

캘리브레이션 전체 흐름이다:

```
1. 단독 모드로 부팅 (부팅 중 버튼 꾹)
2. 로드셀 부하 없는 상태에서 버튼 꾹 → 오프셋 저장
3. 분동 올리고 시리얼 출력 읽기
4. Gain = 무게 / Sensors.DATA 계산
5. 코드에 게인 하드코딩 후 다시 플래시
6. 이후 운용 시에는 전원 켜면 EEPROM 오프셋 자동 복원
```

게인은 로드셀 교체나 기구 재설치가 없으면 다시 할 필요 없다. 오프셋은 기구 상태가 바뀔 때마다 버튼 꾹으로 재설정한다.
