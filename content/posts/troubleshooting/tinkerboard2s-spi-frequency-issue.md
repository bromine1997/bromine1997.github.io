---
title: "SPI 파형이 왜곡됐던 이유 — Digital Isolator 주파수 제한"
date: 2026-05-30T20:41:00+09:00
draft: false
categories: ["Troubleshooting"]
  - Embedded
tags:
  - TinkerBoard
  - SPI
  - MRAA
  - ADUM1400
  - Android
  - 트러블슈팅
  - Digital Isolator
series: ["HBOT Troubleshooting"]
summary: "ASUS Tinker Board 2S에서 SPI 통신 파형이 왜곡되는 문제를 겪었다. 원인은 하드웨어가 아닌 Digital Isolator의 주파수 제한이었다."
---

ASUS Tinker Board 2S로 개발하다가 SPI 통신 파형이 이상하게 나오는 문제를 겪었다. 원인과 해결 과정을 정리해둔다.

## 개발 환경

Tinker Board 2S에서는 SPI1과 SPI5, 두 개의 SPI 버스를 사용할 수 있다.

<!-- 이미지: Tinker Board 2S GPIO Pin Map -->
![Tinker Board 2S GPIO Pin Map](/images/tinkerboard/tinkerboard2s-gpio-pinmap.png)
*Tinker Board 2S GPIO Pin Map*

개발 언어는 Java, GPIO 제어는 **MRAA 라이브러리**를 사용했다.

<!-- 이미지: MRAA Library SPI Index 설정 -->
![MRAA Library SPI Index](/images/tinkerboard/mraa-spi-index.png)
*MRAA 라이브러리에서 SPI Index 설정*

MRAA에서는 위 그림처럼 index를 설정해주면 SPI1과 SPI5를 각각 사용할 수 있다.

## 문제 상황

SPI를 초기화한 뒤, 파형 확인을 위해 `SPI.write()`를 호출하고 오실로스코프로 측정해봤다.

<!-- 이미지: Android Studio SPI Initialize 코드 -->
![SPI Initialize 코드](/images/tinkerboard/android-spi-init.png)
*Android Studio에서 작성한 SPI Initialize 코드*

결과는 예상과 달랐다.

<!-- 이미지: SPI1 버스 MOSI/CLK 파형 -->
![SPI1 버스 파형](/images/tinkerboard/spi1-waveform-before.png)
*SPI1 버스에서 측정한 MOSI와 CLK 파형 — 삼각파가 출력됨*

<!-- 이미지: SPI5 버스 MOSI/CLK 파형 -->
![SPI5 버스 파형](/images/tinkerboard/spi5-waveform-before.png)
*SPI5 버스에서 측정한 MOSI와 CLK 파형 — 오실레이션 발생*

- **SPI1**: 사각파가 아닌 삼각파가 출력됨
- **SPI5**: 파형에 오실레이션이 발생해 원본 데이터가 손상될 가능성이 커 보임

## 원인 분석

처음에는 하드웨어 문제를 의심했다. Bypass Capacitor를 하나씩 교체해가며 확인했지만 증상은 그대로였다.

그러다 전혀 생각하지 못했던 부분에서 원인을 찾았다.

<!-- 이미지: AD5420 SPI Class 코드 -->
![AD5420 SPI Class 코드](/images/tinkerboard/ad5420-spi-class.png)
*기존 AD5420 SPI Class — Frequency가 20MHz로 설정되어 있었다*

바로 `SPI1.Frequency`였다. 기존에 **20MHz**로 아무 생각 없이 설정해두고 있었다.

그런데 Tinker Board 2S와 AD5420 사이에는 **Digital Isolator(ADUM1400)** 가 삽입되어 있다. ADUM1400 데이터시트를 확인해보니 문제가 명확해졌다.

<!-- 이미지: ADUM1400 데이터시트 Maximum pulse width 항목 -->
![ADUM1400 데이터시트](/images/tinkerboard/adum1400-datasheet.png)
*ADUM1400 데이터시트 — Maximum pulse width 1000ns*

**ADUM1400의 Maximum pulse width는 1000ns**, 즉 최대 10MHz까지만 정상 동작을 보장한다. 20MHz 파형은 이 한계를 넘어서 왜곡이 발생한 것이었다.

## 수정 결과

코드에서 SPI1 Frequency를 **1MHz**로 낮춘 뒤 파형을 다시 확인했다.

<!-- 이미지: Frequency 수정 후 SPI1 MOSI/CLK 파형 -->
![SPI1 수정 후 파형](/images/tinkerboard/spi1-waveform-after.png)
*Frequency 1MHz로 수정 후 SPI1 파형 — 정상적인 사각파 확인*

정상 사각파가 나왔다.

다만 **SPI5(MAX1032)** 쪽은 1MHz로는 부족했고, **50kHz**까지 낮춰야 정상 파형이 나왔다. 같은 보드에서 두 SPI 라인이 이렇게 큰 차이를 보이는 이유는 아직 잘 모르겠다. 나중에 기회가 되면 더 파봐야겠다.

| 항목 | 기존 | 수정 후 |
|---|---|---|
| SPI1 Frequency | 20MHz | 1MHz |
| SPI1 파형 | 삼각파 (왜곡) | 정상 사각파 |
| SPI5 Frequency | 20MHz | 50kHz |
| SPI5 파형 | 오실레이션 | 정상 사각파 |

Digital Isolator를 쓸 때는 해당 소자의 Maximum pulse width를 먼저 확인해야 한다. 하드웨어를 의심하며 Bypass Capacitor를 하나씩 교체하느라 시간을 꽤 날렸는데, 데이터시트를 먼저 봤으면 금방 잡았을 문제였다.
