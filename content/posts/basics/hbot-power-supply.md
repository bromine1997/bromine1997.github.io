---
title: "HBOT 챔버 PCB 전원부 설계: 24V→5V→3.3V와 절연"
date: 2026-06-13T12:00:00+09:00
tags: ["power supply", "VR10S05", "MIC5233", "ADUM1400", "ISO7421", "isolation", "hardware", "HBOT"]
categories: ["Embedded Basic"]
description: "HBOT 챔버 제어 PCB에서 24V→5V(스위칭)→3.3V(LDO) 전원 설계와 ADUM1400/1200, ISO7421, VO1400AEFTR를 이용한 절연 설계를 정리했다."
ShowToc: true
TocOpen: false
draft: false
math: true
---

## 들어가며

고압산소챔버(HBOT) 제어 PCB를 설계하면서 전원 구조를 먼저 정리했다. 시스템에는 여러 전압 레벨이 사용된다.

- **24V**: 솔레노이드 밸브, 비례제어 밸브, 센서류
- **5V**: ADC 아날로그 전원(AVDD), OP-AMP
- **3.3V**: 디지털 아이솔레이터(ADUM VCC), ADC 디지털 전원(DVDD)

여기에 Tinkerboard(SBC)가 상용 전원 어댑터로 독립 동작하고, 밸브·센서 측은 챔버 제조사의 의료용 SMPS에서 24V를 공급받는다. 두 측의 GND가 달라 신호 연결 시 절연이 필요하다. 모든 회로는 하나의 PCB에 올라간다.

![전원부 구조 개요](/images/hardware/power-supply-overview.png)

---

## 24V → 5V: VR10S05

![POWER#1 — 24V to 5V converter](/images/hardware/circuit-power-supply.png)

24V에서 5V를 만드는 데 스위칭 레귤레이터(VR10S05, XP Power)를 선택했다. 이유는 두 가지다.

**전압 강하가 크다.** 24V → 5V는 19V를 낮춰야 한다. LDO로 이 구간을 처리하면 손실 전력이 $P_{loss} = (V_{IN} - V_{OUT}) \times I$로 계산된다. 500mA 부하 기준으로도 9.5W가 열로 버려진다. 히트싱크 없이는 소자 온도를 유지하기 어렵다.

| 항목 | 값 |
|------|-----|
| 입력 전압 | 24V (SMPS 출력) |
| 출력 전압 | 5V |
| 최대 출력 전류 | 2A (10W) |
| 효율 | 약 85%+ |

외부 부품은 최소화되어 있어 별도 인덕터 없이 사용할 수 있다. 입출력 디커플링 커패시터만 달면 된다.

---

## 5V → 3.3V: MIC5233

5V에서 3.3V로의 변환은 LDO(MIC5233-3.3YM5-TR, Microchip)를 썼다.

**전압 강하가 작다.** 5V → 3.3V는 1.7V 강하다. 3.3V 라인의 최대 부하(ADUM VCC + MAX1032 DVDD + 여유분)는 약 100mA 수준이다. 이 조건에서 LDO 손실은 $P_{loss} = 1.7 \times 0.1 = 0.17\text{W}$로 허용 가능하다.

**노이즈가 중요하다.** 3.3V는 ADUM1400/1200(디지털 아이솔레이터)과 MAX1032 DVDD에 공급된다. 스위칭 레귤레이터는 스위칭 주파수에 의한 리플 노이즈를 가지고 있어 디지털 아이솔레이터에 유리하지 않다. LDO는 출력 노이즈가 낮아 이 용도에 적합하다.

| 항목 | 값 |
|------|-----|
| 입력 전압 | 2.5~12V |
| 출력 전압 | 3.3V (고정) |
| 최대 출력 전류 | 150mA |
| 패키지 | SOT-23-5 |

---

## 절연 설계

Tinkerboard는 상용 전원 어댑터로 동작하고 PCB 밸브·센서 측은 의료용 SMPS에서 전력을 받는다. 두 GND를 직접 연결하면 접지 루프가 형성되고, 한쪽의 전기적 이상이 다른 쪽으로 전파될 수 있다. 의료기기 환경에서는 환자 보호를 위해서도 절연이 필요하다.

절연 경계는 다음과 같다.

- **Tinkerboard 측**: DVCC_3.3V, DVCC_5V (SBC 어댑터 GND)
- **밸브·센서 측**: AVCC_3.3V, AVCC_5V, AVCC_24V (의료용 SMPS GND)

이 경계를 통과하는 신호 경로가 세 가지다.

### SPI 절연 — ADUM1400 + ADUM1200

![MAX1032 ADC + ADUM1400/ADUM1200 절연 회로](/images/hardware/circuit-isolation-adc.png)

MAX1032 ADC와 Tinkerboard 사이의 SPI 통신을 절연한다.

- **ADUM1400**: 단방향 4채널 디지털 아이솔레이터. CS, CLK, MOSI 등 Tinkerboard→ADC 방향 신호를 담당한다.
- **ADUM1200**: 단방향 2채널 디지털 아이솔레이터. MISO(ADC→Tinkerboard) 및 추가 신호를 담당한다.

VCC1(DVCC_3.3V)과 VCC2(AVCC_3.3V)가 독립적으로 공급되어 두 GND 간 전위 차가 발생해도 신호가 안전하게 전달된다.

MAX1032는 DVDD(3.3V, 디지털 측)와 AVDD(5V, 아날로그 측)를 분리해서 공급받는다. DVDD는 AVCC_3.3V, AVDD는 AVCC_5V에서 공급된다.

### UART 절연 — ISO7421

![ISO7421 UART 절연 회로](/images/hardware/circuit-uart-iso7421.png)

UART 시리얼 통신도 절연했다. ISO7421은 2채널 디지털 아이솔레이터로 VCC1/VCC2 듀얼 전원을 지원한다. Tinkerboard의 UART0_TX/RX 신호가 절연 경계를 넘어 외부 장치로 연결된다.

### DRV110 EN 절연 — VO1400AEFTR

![VO1400AEFTR 포토커플러 EN 제어 회로](/images/hardware/circuit-photocoupler-en.png)

DRV110은 AVCC_24V 측에서 동작한다. Tinkerboard의 3.3V 디지털 출력 신호로 솔레노이드/비례밸브의 ON/OFF를 제어하려면 EN 핀 신호도 절연이 필요하다.

VO1400AEFTR는 포토커플러다. Tinkerboard 측 신호(DVCC_5V 레벨)가 NPN 트랜지스터를 거쳐 포토커플러 LED를 구동하고, 광 신호로 절연 경계를 넘어 DRV110의 EN 핀을 제어한다.

이 구조에서 Tinkerboard 측과 DRV110(24V 구동) 측은 전기적으로 완전히 분리된다.

---

## 정리

| 구간 | 소자 | 방식 | 선택 이유 |
|------|------|------|----------|
| 24V → 5V | VR10S05 | 스위칭 | 큰 전압 강하, 효율 우선 |
| 5V → 3.3V | MIC5233 | LDO | 작은 전압 강하, 저노이즈 필요 |
| SPI 절연 | ADUM1400/1200 | 디지털 아이솔레이터 | 고속 SPI 신호 |
| UART 절연 | ISO7421 | 디지털 아이솔레이터 | 시리얼 통신 |
| EN 신호 절연 | VO1400AEFTR | 포토커플러 | ON/OFF 제어 |

전원 설계에서 스위칭과 LDO를 조합한 이유는 단순하다. 전압 강하가 큰 구간에서는 효율이 중요하고, 전압 강하가 작고 노이즈에 민감한 구간에서는 LDO가 낫다. 절연은 서로 다른 전원에서 동작하는 두 시스템을 연결할 때 GND 분리를 유지하기 위한 필수 조건이었다.

---

*회로도 출처: 자체 설계 (CHAMBER_SBC REV 0.2, 2024.07.25)*
