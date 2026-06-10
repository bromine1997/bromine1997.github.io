---
title: "AD5420 Daisy Chain 출력이 안 나온 이유 — 오실로스코프로 쓰레기값을 잡기까지"
date: 2026-06-10T23:00:00+09:00
draft: false
categories:
  - Embedded
tags:
  - AD5420
  - SPI
  - DAC
  - 트러블슈팅
  - 오실로스코프
  - DaisyChain
series: ["HBOT Troubleshooting"]
summary: "AD5420 두 개를 Daisy Chain으로 연결했는데 출력이 아예 안 나왔다. 오실로스코프로 MISO를 확인했더니 쓰레기값이 보였다. 데이터시트에는 이미 UNDEFINED라고 적혀 있었다."
---

HBOT 챔버 제어 시스템에서 압력 밸브와 환기 밸브를 각각 4~20mA 전류로 제어해야 했다. 소자를 두 개 쓰면 SPI 핀을 두 세트 써야 하는데, Tinker Board 2S의 핀 구성상 여유가 없어서 AD5420 두 개를 Daisy Chain으로 연결하기로 했다.

회로를 구성하고 코드를 짰는데, 출력이 아예 안 나왔다.

---

## AD5420 Daisy Chain 구성

AD5420은 SPI로 제어하는 4~20mA 전류 출력 DAC이다. 24비트(3바이트) 단위로 명령을 받는다.

Daisy Chain은 여러 SPI 소자를 하나의 SPI 버스에 직렬로 연결하는 방식이다. 별도의 CS 핀 없이 첫 번째 소자의 SDO를 다음 소자의 SDIN에 연결한다. SCLK와 LATCH는 모든 소자에 공통으로 연결한다.

실제 회로는 아래와 같다. ADUM1400/1200 디지털 아이솔레이터를 거쳐 두 AD5420(U9, U14)이 직렬로 연결되어 있다. 상단 U9의 SDO1이 하단 U14의 SDIN으로 이어지는 게 Daisy Chain의 핵심 연결이다.

![AD5420 Daisy Chain 회로도](/images/troubleshooting/ad5420-daisy-chain/ad5420-circuit.png)

데이터시트 Figure 35는 이 연결 방식을 추상적으로 나타낸 것이다. Table 8에는 레지스터 주소별 동작도 정리되어 있다.

![Figure 35. Daisy Chaining the AD5420 / Table 8. Control Word Functions](/images/troubleshooting/ad5420-daisy-chain/shift-register-format.png)

48비트(6바이트)를 한 번에 전송하면 shift register 방식으로 데이터가 밀려 들어간다. LATCH가 내려올 때:

- **처음 24비트** → 칩2에 래치
- **나중 24비트** → 칩1에 래치

---

## 문제: 출력이 아예 안 나온다

초기화 코드를 짜고 전류를 출력해봤는데 두 채널 모두 반응이 없었다. SPI 통신 자체는 오류 없이 진행됐다. 레지스터 주소, 데이터 값, LATCH 타이밍을 다 확인했는데 특별히 이상한 게 없었다.

---

## 오실로스코프로 확인

SPI 신호를 직접 확인하기 위해 오실로스코프를 연결했다. MOSI, MISO, SCLK, LATCH 네 채널을 동시에 찍었다.

첫 번째 전송을 보는 순간 문제가 보였다. **MISO에 이상한 데이터가 찍혔다.**

AD5420은 전송이 끝나면 MISO(SDO)로 직전에 수신한 데이터를 돌려준다. 정상 초기화 상태라면 깔끔한 값이 나와야 하는데, 전혀 예상하지 못한 값이 나오고 있었다. 쓰레기값이었다.

---

## 원인: 데이터시트에 이미 UNDEFINED라고 적혀 있었다

이상하다 싶어서 데이터시트를 다시 꼼꼼히 봤다. Daisy-Chain Mode Timing Diagram을 보는 순간 바로 이해가 됐다.

![Figure 4. Daisychain Mode Timing Diagram](/images/troubleshooting/ad5420-daisy-chain/daisy-chain-timing.png)

SDO 라인 첫 번째 24비트 구간에 **UNDEFINED** 라고 명시돼 있다.

Daisy Chain에서 칩1의 SDO는 칩2의 SDIN에 연결된다. 칩1은 자신이 받은 데이터를 처리하면서 동시에 직전 shift register 내용을 SDO로 밀어낸다. 문제는 **전원 인가 직후 shift register 초기값이 보장되지 않는다는 것**이다.

처음 48비트를 보낼 때의 상황:

```
전송: [칩2용 명령 24비트] [칩1용 명령 24비트]
```

칩1이 명령을 받아 처리하는 동시에, 칩1은 이전에 shift register에 남아 있던 **쓰레기값**을 SDO로 내보낸다. 이 값이 칩2의 SDIN으로 들어가서 칩2가 전혀 엉뚱한 명령을 받게 된다. 칩2가 제대로 초기화되지 않았으니 출력이 안 나오는 게 당연했다.

---

## 해결: 더미 데이터로 shift register flush

해결 방법은 명령을 보내기 전에 6바이트짜리 더미 데이터를 먼저 전송해서 두 칩의 shift register를 모두 0으로 채우는 것이다.

```java
private void clearSpiBuffer() {
    byte[] dummy = new byte[] {0, 0, 0, 0, 0, 0};
    spi1.write(dummy);
}
```

0x00을 NOP으로 쓸 수 있는 근거는 위 데이터시트 Table 8에 명시돼 있다. Address Word `00000000`이 No Operation (NOP)이다. 즉, 0x00을 6바이트 보내면 두 칩의 shift register가 0으로 채워지면서도 실제 레지스터에는 아무 영향을 주지 않는다.

flush 이후 초기화 순서:

```java
clearSpiBuffer();   // shift register flush — 쓰레기값 제거
Daisy_reset();      // 소프트웨어 리셋
Daisy_Setup();      // CONTROL 레지스터 설정
```

더미 데이터를 추가하고 나서 오실로스코프로 다시 확인했더니 MISO가 깔끔하게 나왔고, 전류 출력도 정상으로 동작했다.

---

## 정리

Daisy Chain은 핀을 아끼면서 소자를 늘릴 수 있는 효율적인 방식이지만, shift register 기반 동작 특성상 전원 인가 후 초기 상태가 보장되지 않는다.

유효한 명령을 보내기 전에 반드시 더미 데이터로 shift register를 flush해야 한다. 데이터시트 Figure 4에 SDO 초기값이 UNDEFINED라고 명시돼 있으니, 처음부터 꼼꼼히 읽었다면 바로 알 수 있었던 내용이다. 오실로스코프로 MISO를 직접 찍어보지 않았다면 원인을 찾는 데 훨씬 오래 걸렸을 것이다.
