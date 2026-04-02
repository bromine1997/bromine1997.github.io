---
title: "[논문 리뷰] 1인용 고압산소챔버 치료 환자에서 MEB 위험 인자 분석"
date: 2025-04-02
categories: ["Paper Review"]
tags: ["HBOT", "고압산소치료", "MEB", "barotrauma", "monoplace chamber"]
draft: false
description: "1인용 HBOT(monoplace chamber)을 받은 296명 환자를 대상으로 중이 기압외상(MEB)의 독립적 위험 인자를 분석한 연구를 리뷰한다."
---

## 논문 정보

- **제목**: Risk Factors Associated with Middle Ear Barotrauma in Patients Undergoing Monoplace Hyperbaric Oxygen Therapy
- **저널**: Yonsei Medical Journal, 2025 May;66(5):302-309
- **DOI**: https://doi.org/10.3349/ymj.2024.0068
- **저자**: Yoon Sung Lee, Sang Won Ko, Hyoung Youn Lee, Kyung Hoon Sun, Tag Heo, Sung Min Lee
- **기관**: 전남대학교병원 응급의학과

---

## 배경 및 읽게 된 이유

고압산소치료(HBOT)는 석사 논문 주제였던 만큼 관련 임상 연구에 자연스럽게 눈이 간다. 챔버 시스템을 직접 설계하고 제어 펌웨어를 개발하면서 compression/decompression 속도, 치료 압력 설정이 얼마나 중요한지 체감했는데, 이 논문은 바로 그 파라미터들이 임상적으로 어떤 합병증을 유발하는지 다룬다. 특히 monoplace chamber에 집중한 연구라는 점이 흥미로웠다.

---

## 연구 목적

1인용 HBOT(monoplace chamber)를 받은 환자에서 **중이 기압외상(Middle Ear Barotrauma, MEB)** 발생의 독립적 위험 인자를 규명하는 것이다.

---

## 배경 지식

### HBOT란?

HBOT는 대기압의 2배 이상 압력 환경에서 100% 산소를 흡입시켜 혈장 내 용존 산소 농도를 높이는 치료법이다. 주요 적응증으로는 CO 중독, 감압병, 창상 치유, 괴사성 근막염, 돌발성 난청 등이 있다.

### MEB란?

HBOT 시 외부 환경과 중이(Middle Ear) 사이의 압력 차가 약 60 mmH₂O를 초과하면 귀 통증과 압박감이 발생한다. 이 상태가 지속되면 중이 내 체액 침윤, 혈관 손상, 고막(TM, Tympanic Membrane) 천공까지 이어질 수 있다.

Pressure equalization은 ET(Eustachian Tube)를 통해 이루어지는데, Valsalva법 같은 능동적 조작이 어려운 환자(소아, 치매 환자, altered mental status 환자 등)는 이 과정을 수행하기 어렵다. 또한 상기도 감염, 알레르기, 방사선 치료로 인한 연조직 손상 등이 ET 기능 부전을 유발할 수 있다.

### Monoplace chamber의 특수성

기존 MEB 연구 대부분은 multiplace chamber를 대상으로 한다. 1인용 챔버에서는 환자가 supine position으로 치료를 받는데, 이 자세는 중심정맥압을 높여 정맥 울혈을 유발하고 pressure equalization을 더 어렵게 만든다는 점에서 multiplace와 다른 역학을 가진다.

---

## 연구 방법

### 연구 설계

- **기간**: 2021년 5월 ~ 2023년 12월
- **설계**: 단일기관 후향적 코호트 연구
- **대상**: 1인용 HBOT를 받은 296명 환자
- **챔버**: BARA-MED Monoplace Hyperbaric Chamber (ETC Biomedical Systems)

### 치료 프로토콜

- 총 세션 시간: 90분 (compression 15분 + 치료 + decompression 15분)
- 최대 치료 압력: 적응증에 따라 2.0 ATA 또는 2.8 ATA
- 가압 속도: 2.2 FSW/min 또는 4 FSW/min

### MEB 평가

Video otoscope(INSIGHT-I, MEDIANA)로 치료 전후 TM 상태를 평가하고, **수정 O'Neill grading system**을 적용하였다.

| Grade | 기준 |
|-------|------|
| 0 | 이경 소견 없음 (증상만 존재) |
| 1 | TM 충혈, 장액성 삼출액, TM 뒤 공기 포착 중 하나 이상 |
| 2 | 명백한 출혈 또는 TM 천공 |

### 적응증 분류 (국민건강보험 기준)

| 그룹 | 내용 |
|------|------|
| **A군 (응급)** | CO 중독, 감압병, 공기색전증, 가스괴저, 시안화물 중독, 중심망막동맥폐색, 중증 빈혈 |
| **B군 (만성)** | 버거병, 피판/이식편, 지연 방사선 손상, 당뇨발, 골수염, 뇌농양 등 |
| **C군 (기타)** | 돌발성 난청 |

### 통계 방법

- 연속 변수: t-test 또는 Mann-Whitney U test
- 범주형 변수: chi-square test 또는 Fisher's exact test
- Univariable 분석에서 p<0.1인 변수를 multivariable logistic regression에 포함
- 세션 수에 따른 MEB 발생 확률: restricted cubic spline graph로 시각화
- 분석 도구: Stata/SE 16.1

---

## 결과

### 환자 특성

- 총 296명 (남성 68.6%, 평균 연령 49.0±17.2세)
- 주요 적응증: CO 중독 54.1%, 돌발성 난청 34.5%, CO 지연 신경정신 후유증 5.1%
- 응급 치료군(A군): 181명 (61.2%)
- 입원 시 altered mental status: 52명 (19.9%)

### MEB 발생 현황

- **전체 MEB 발생률: 56.1%** (166명)
- Video otoscopy 이상 소견: 58.8% (174명)
  - Grade 1: 56.4%
  - Grade 2: 2.4%

### 세션 수에 따른 MEB 발생 확률

세션이 늘어날수록 MEB 발생 확률은 지속적으로 감소하였다.

- 1회차: 약 60%
- 5회차 이후: 20% 미만
- **18회차 이후: 0%**

반복 치료를 통해 환자가 Valsalva법 등 pressure equalization 기술에 적응하기 때문으로 해석된다.

### Univariable 분석 주요 결과

| 변수 | OR (95% CI) | p값 |
|------|-------------|-----|
| 응급 치료군 A | 2.51 (1.55–4.05) | <0.001 |
| Altered mental status | 3.18 (1.51–6.67) | 0.002 |
| 증상 발생 후 7일 이내 치료 | 높은 MEB 발생 | 0.014 |
| 가압 속도 4 FSW/min (vs 2.2) | 1.95 (1.21–3.13) | 0.006 |

### Multivariable logistic regression (독립적 위험 인자)

| 독립적 위험 인자 | OR | 95% CI | p값 |
|---|---|---|---|
| **Altered mental status** | **2.50** | 1.13–5.51 | 0.023 |
| **응급 치료군 A** | **6.75** | 1.33–34.20 | 0.021 |

---

## 고찰

### 응급 치료군에서 MEB가 높은 이유

응급 치료군 환자(CO 중독 등)는 상태가 불안정하여 빠른 compression이 필요한 경우가 많다. 이때 pressure equalization이 능동적으로 이루어지지 못하면 ET 기능 부전으로 이어진다. CO 중독 환자의 MEB 발생률이 62.6%로 가장 높았다는 점도 이를 뒷받침한다.

### Altered mental status가 MEB를 높이는 이유

Valsalva법, Toynbee법 등 능동적 pressure equalization 기술은 의식이 명료한 환자에게만 기대할 수 있다. Altered mental status 환자는 이를 수행할 수 없어 MEB 위험이 높아진다.

### Compression 속도의 영향

4 FSW/min 가압 시 2.2 FSW/min 대비 MEB가 약 2배 증가하였다(univariable). Multivariable 분석에서는 통계적 유의성을 잃었지만, 느린 compression이 중이 적응에 유리하다는 근거는 타 연구에서도 확인된다.

다만 빠른 가압에서 MEB가 더 많이 나타나는 경향은 있었지만, 다른 변수들을 함께 고려한 분석에서는 그 영향이 뚜렷하게 유지되지 않았다. 따라서 compression 속도가 중요한 요소일 가능성은 있지만, 이 연구만으로 느린 가압이 MEB를 직접 줄인다고 단정하기는 어렵다.

### 초기 세션에서의 높은 MEB 발생

증상 발생 7일 이내에 치료를 시작한 환자에서 MEB가 더 많이 발생하였다. 이는 상태의 급성도와 관련이 있으며, 반복 세션을 통해 적응이 이루어지면 발생률이 감소하는 패턴과 일치한다.

세션 수가 늘어날수록 MEB 발생이 감소하는 경향이 관찰되었는데, 이는 환자가 반복 치료를 통해 압력 변화에 점차 적응한 결과로 해석할 수 있다. 다만 후반 세션으로 갈수록 대상 환자 수가 줄어들 수 있으므로, 이 결과 역시 적응 효과만으로 단순하게 해석하기보다는 신중하게 볼 필요가 있다.

### 연구 한계

- 단일기관 후향적 연구로 일반화에 제한이 있다
- Monoplace chamber에만 해당하여 multiplace chamber에 적용하기 어렵다
- MEB의 장기 예후에 대한 평가가 없다
- 사전 이과 질환 등 교란 변수를 완전히 통제하지 못하였다

---

## 개인적 소감

내가 직접 설계했던 HBOT 시스템에서도 compression/decompression 속도 설정은 중요한 파라미터였다. 펌웨어 레벨에서 압력 센서 피드백으로 가압 속도를 제어하는 로직을 짜면서 "이 값이 왜 중요한가"를 막연히 알고 있었는데, 이 논문이 그 이유를 임상 데이터로 보여준다는 점에서 의미 있다.

특히 altered mental status 환자에서 MEB 위험이 높다는 결과는, 시스템 설계 관점에서도 흥미롭다. 환자가 능동적으로 pressure equalization을 수행할 수 없다면, 챔버 시스템이 더 세밀한 compression 프로토콜을 자동 적용하거나 운영자에게 경고를 줄 수 있어야 한다는 방향으로 이어질 수 있기 때문이다. 단순히 "몇 ATA, 몇 분"으로 고정된 프로토콜이 아니라, 환자 상태에 따라 적응적으로 compression 속도를 조절하는 시스템을 구현한다면 임상적으로도 의미 있을 것이다.

---

## 핵심 요약

> 1인용 HBOT(monoplace chamber)에서 MEB 발생률은 56.1%로 높으며, **altered mental status(OR 2.50)**와 **응급 치료군 분류(OR 6.75)**가 독립적인 위험 인자이다. 세션이 반복될수록 MEB 발생률은 감소하며, 느린 compression 속도가 MEB 예방에 유리하다.
