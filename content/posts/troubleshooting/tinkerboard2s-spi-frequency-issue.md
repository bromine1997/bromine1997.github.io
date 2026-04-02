---
title: "[Tinker Board 2S] SPI 파형 왜곡 문제와 Digital Isolator 주파수 제한"
date: 2026-04-03T00:00:00+09:00
draft: false
categories:
  - Embedded
tags:
  - TinkerBoard
  - SPI
  - MRAA
  - ADUM1400
  - Android
  - 트러블슈팅
  - Digital Isolator
summary: "ASUS Tinker Board 2S에서 SPI 통신 파형이 왜곡되는 문제를 겪었다. 원인은 하드웨어가 아닌 Digital Isolator의 주파수 제한이었다."
---

최근 ASUS Tinker Board 2S를 이용해서 개발을 진행하고 있다. 그 과정에서 SPI 통신 파형이 이상하게 나오는 문제가 발생해서 이 부분을 기록으로 남겨두려 한다.

## 개발 환경

Tinker Board 2S에서는 SPI1과 SPI5, 두 개의 SPI 버스를 사용할 수 있다.

<!-- 이미지: Tinker Board 2S GPIO Pin Map -->
![Tinker Board 2S GPIO Pin Map](/images/tinkerboard/tinkerboard2s-gpio-pinmap.png)
*Tinker Board 2S GPIO Pin Map*

개발 언어는 Android Studio에서 Java를 사용하고 있으며, GPIO 제어는 **MRAA 라이브러리**를 사용했다.

<!-- 이미지: MRAA Library SPI Index 설정 -->
![MRAA Library SPI Index](/images/tinkerboard/mraa-spi-index.png)
*MRAA 라이브러리에서 SPI Index 설정*

MRAA에서는 위 그림처럼 index를 설정해주면 SPI1과 SPI5를 각각 사용할 수 있다.

## 문제 상황

AD5420과 MAX1032 클래스를 이용해 SPI를 초기화하고 디버깅 목적으로 `SPI.write()`를 호출해 오실로스코프로 파형을 확인해봤다.

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

정상적인 사각파가 나오는 것을 확인했다.

다만 **SPI5(MAX1032)** 쪽은 1MHz로는 부족했고, **50kHz**까지 낮춰야 정상 파형이 나왔다. 같은 보드에서 두 SPI 라인이 이렇게 큰 차이를 보이는 이유는 아직 명확하지 않다. 추후에 더 공부해보려고 한다.

## 정리

| 항목 | 기존 | 수정 후 |
|---|---|---|
| SPI1 Frequency | 20MHz | 1MHz |
| SPI1 파형 | 삼각파 (왜곡) | 정상 사각파 |
| SPI5 Frequency | 20MHz | 50kHz |
| SPI5 파형 | 오실레이션 | 정상 사각파 |

Digital Isolator를 사용할 때는 반드시 **해당 소자의 Maximum pulse width(최대 동작 주파수)를 확인**해야 한다는 걸 이번에 직접 경험으로 배웠다. 하드웨어를 먼저 의심하다가 시간을 꽤 날렸는데, 데이터시트를 먼저 꼼꼼히 읽는 습관의 중요성을 다시 한번 느꼈다.
