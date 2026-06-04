---
title: "[Paper Review] Advances in Hyperbaric Oxygen Therapy: Medical Benefits and Technical Perspectives"
date: 2026-04-29
categories: ["Paper Review"]
tags: ["HBOT", "Biomedical", "Embedded", "PID", "Pressure Control"]
description: "HBOT 챔버 내 유체 거동을 수학적으로 모델링하고, 축소 실험 챔버 + MCU 기반 압력 제어 시스템으로 검증한 연구"
ShowToc: true
TocOpen: false
draft: false
---

> **한 줄 요약**: HBOT 챔버 내 유체 거동을 수학적으로 모델링하고, 축소 실험 챔버 + MCU 기반 압력 제어 시스템으로 검증한 연구

---

## 📌 논문 정보

| 항목 | 내용 |
|------|------|
| 제목 | Advances in Hyperbaric Oxygen Therapy: Medical Benefits and Technical Perspectives |
| 저자 | Antoanela Naaji, Monica Ciobanu, Marius Popescu |
| 저널 / 학회 | Annals of Biomedical Engineering |
| 연도 | 2026 |
| DOI / 링크 | https://doi.org/10.1007/s10439-026-04027-7 |
| 분야 | `biomedical` |

---

## 🎯 문제 정의

기존 HBOT 시스템은 대부분 empirical calibration에 의존하고 있으며, gas flow 및 pressure dynamics에 대한 predictive model이 부족하다. 또한 압력·산소 제어의 자동화 수준이 낮고, control loop의 feedback delay 문제가 있어 치료 재현성이 떨어진다. 이 논문은 이러한 한계를 수학적·실험적 framework으로 해결하고자 한다.

---

## 💡 Contribution

- Reynolds, Froude, Archimedes 등 dimensionless number를 활용한 HBOT 챔버 내 oxygenated air flow 수학 모델 수립
- Ruark transformation을 도입해 dimensionless coordinate로 일반화 → 유사 환경에 결과 확장 가능
- Geometric similarity condition (K=10)을 적용한 축소 실험 챔버 설계 및 제작
- ATMEL AT89C52 + solenoid valve 3개 (EV1~EV3) + pressure/vacuum pump 기반 자동 압력 제어 시스템 구현
- LabWindows GUI를 통한 real-time monitoring 및 CRC 기반 통신 프로토콜 설계

---

## 🔬 방법론

**Mathematical Modeling**
- Continuity equation, Navier-Stokes, thermal energy equation, Fick's diffusion equation을 무차원화
- Similarity condition: Re idem (self-modeling 영역), Froude idem, geometric similarity
- 실제 챔버 대비 1/10 축소 모델 → 모델 유량 D=8.5 l/min, D₁=0.45 l/min 도출

**Experimental Setup**
- Pressure transducer (MPX 5100 AP) → ADC → AT89C52 MCU → solenoid valve / pump 제어
- PC ↔ MCU 간 4-byte frame [T, X, Y, CRC] 양방향 통신
- EV1 (가압), EV2 (배기 차단), EV3 (감압) 로직으로 압력 제어

**Validation**
- 산소 농도, pressure behavior, 열적 효과 측정 후 모델 예측값과 비교
- Isothermal·단순화 boundary condition 하에서 안정성과 재현성 평가

---

## 📊 실험 및 결과

- 챔버 압력 10% 증가 시 모델 내 pO₂ 약 8~9% 향상 → 조직 산소화 관련 생리학적 반응과 일치
- 제안된 압력 제어 시스템은 안정적인 pressurization/depressurization cycle을 재현, 상업용 HBOT 챔버와 원리적으로 유사함을 확인
- Vacuum pump는 pressure pump 대비 유량 3배 → 감압 시간 ≈ 가압 시간의 절반

> **한계**: oxygen concentration mapping, flow visualization, CFD 비교는 수행하지 않았으며 향후 과제로 남김. CO₂, 습도 등 exhaled gas 조성도 미반영.

---

## ✅ 장점 / ⚠️ 한계

**장점**
- Mathematical model → 축소 실험 챔버 → 실제 제어 시스템까지 일관된 multidisciplinary pipeline
- Control architecture가 platform-independent → STM32, FPGA 등 현대 embedded platform으로 이식 가능하다고 명시
- 무차원화를 통해 결과의 generalizability 확보

**한계**
- AT89C52 + single sensor feedback loop → 임상용이 아닌 연구/교육 수준
- Isothermal 조건에서 실험 → 실제 HBOT 챔버의 thermodynamic complexity 미반영
- 개인별 호흡 패턴, 대사율 차이 등 생리적 변수 미포함
- 실험적 검증 범위가 pressure stabilization 및 flow behavior에 한정

---

## 💬 내 생각 / 인사이트

석사 논문에서 Tinker Board 2S + dual PID + AD5420 DAC 기반으로 HBOT 시스템을 구현했던 경험이 있어서, 이 논문의 방향성이 꽤 친숙하게 읽혔다.

1. **모델 접근법의 차이**: 이 논문은 Navier-Stokes + dimensionless number 기반의 fluid dynamics model에 집중한 반면, 내 연구는 PID control loop의 real-time tuning과 DAC 기반 analog output에 초점을 뒀다. 두 접근이 서로 보완적이라고 생각함.

2. **Control architecture**: EV1~EV3 solenoid + on/off 제어 방식은 단순하지만 실용적. 다만 proportional valve를 쓰지 않아서 pressure ramping의 세밀함에 한계가 있을 것 같다. 논문도 이 점을 인정하고 있음.

3. **Platform 이식 가능성 언급**: STM32, Arduino/ARM 등으로 포팅 가능하다고 명시한 게 인상적. 지금 STM32F411RE Nucleo로 공부 중인 입장에서, 이 제어 로직을 STM32로 직접 구현해보면 좋은 포트폴리오가 될 것 같다.

4. **아쉬운 점**: CFD 미수행, oxygen concentration distribution 미측정이 가장 큰 빈자리. 후속 연구로 OpenFOAM 기반 CFD와 연결하면 재밌을 것 같다.

---

## 🔗 관련 논문

- Flegg et al. (2010) - Mathematical model of HBOT for chronic diabetic wounds, *Bull. Math. Biol.*
- Kovtanyuk et al. (2023) - Mathematical modeling of cerebral oxygen transport, *Front. Appl. Math. Stat.*
- Gracia et al. (2018) - Identification and control of a multiplace hyperbaric chamber, *PLoS ONE*
