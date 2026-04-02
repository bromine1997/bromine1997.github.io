---
title: "[Paper Review] Risk Factors Associated with Middle Ear Barotrauma in Patients Undergoing Monoplace Hyperbaric Oxygen Therapy"
date: 2025-04-02
categories: ["Paper Review"]
tags: ["HBOT", "MEB", "barotrauma", "monoplace chamber", "logistic regression"]
description: "1인용 HBOT(monoplace chamber)을 받은 296명 환자를 대상으로 MEB의 독립적 위험 인자를 multivariable logistic regression으로 분석한 연구"
ShowToc: true
TocOpen: false
draft: false
---

> **한 줄 요약**: 1인용 HBOT 환자에서 MEB 발생의 독립적 위험 인자는 altered mental status(OR 2.50)와 응급 치료군 분류(OR 6.75)였다.

---

## 📌 논문 정보

| 항목 | 내용 |
|------|------|
| 제목 | Risk Factors Associated with Middle Ear Barotrauma in Patients Undergoing Monoplace Hyperbaric Oxygen Therapy |
| 저자 | Yoon Sung Lee, Sang Won Ko, Hyoung Youn Lee, Kyung Hoon Sun, Tag Heo, Sung Min Lee |
| 저널 / 학회 | Yonsei Medical Journal |
| 연도 | 2025 |
| DOI / 링크 | https://doi.org/10.3349/ymj.2024.0068 |
| 분야 | `biomedical` `clinical` |

---

## 🎯 문제 정의

MEB(Middle Ear Barotrauma)는 HBOT에서 가장 흔한 합병증 중 하나로 알려져 있다. 그러나 기존 연구 대부분은 multiplace chamber 환자를 대상으로 하고 있어, monoplace chamber에서의 MEB 위험 인자에 대한 데이터가 부족하다.

Monoplace chamber는 환자가 supine position으로 치료를 받는다는 점에서 multiplace와 다른 역학을 가진다. Supine position은 중심정맥압을 높여 정맥 울혈을 유발하고, 이는 중이의 pressure equalization을 더 어렵게 만든다. 이 논문은 monoplace HBOT 환자에서 MEB 발생률과 독립적 위험 인자를 규명하고, 더 안전한 운영 프로토콜 수립에 기여하는 것을 목적으로 한다.

---

## 💡 Contribution

- 단일기관 296명 규모의 monoplace HBOT 환자 데이터를 기반으로 MEB 발생률 및 위험 인자 분석
- Video otoscopy + 수정 O'Neill grading system을 적용한 객관적 MEB 평가
- Multivariable logistic regression으로 독립적 위험 인자 2개 규명: altered mental status, 응급 치료군(NHI A군)
- Restricted cubic spline graph를 통해 세션 수와 MEB 발생 확률의 비선형 관계 시각화
- 국내 건강보험 적응증 분류 체계(A/B/C군)를 위험 인자 분석에 적용한 점이 국내 임상 환경에 실질적

---

## 🔬 방법론

**연구 설계**

- 기간: 2021년 5월 ~ 2023년 12월
- 설계: 단일기관 후향적 코호트 연구
- 챔버: BARA-MED Monoplace Hyperbaric Chamber (ETC Biomedical Systems)
- 치료 프로토콜: 총 90분 (compression 15분 + 치료 + decompression 15분), 최대 2.0 ATA 또는 2.8 ATA

**MEB 평가**

Video otoscope(INSIGHT-I, MEDIANA)로 치료 전후 TM(Tympanic Membrane) 상태를 평가하고 수정 O'Neill grading system 적용:

| Grade | 기준 |
|-------|------|
| 0 | 이경 소견 없음 (증상만 존재) |
| 1 | TM 충혈, 장액성 삼출액, TM 뒤 공기 포착 중 하나 이상 |
| 2 | 명백한 출혈 또는 TM 천공 |

**적응증 분류 (국민건강보험 기준)**

| 그룹 | 내용 |
|------|------|
| A군 (응급) | CO 중독, 감압병, 공기색전증, 가스괴저, 시안화물 중독, 중심망막동맥폐색, 중증 빈혈 |
| B군 (만성) | 버거병, 피판/이식편, 지연 방사선 손상, 당뇨발, 골수염, 뇌농양 등 |
| C군 (기타) | 돌발성 난청 |

**통계 방법**

- 연속 변수: t-test 또는 Mann-Whitney U test
- 범주형 변수: chi-square test 또는 Fisher's exact test
- Univariable 분석에서 p<0.1인 변수를 multivariable logistic regression에 포함
- 세션 수에 따른 MEB 발생 확률: restricted cubic spline graph로 시각화
- 분석 도구: Stata/SE 16.1

---

## 📊 실험 및 결과

**환자 특성**

- 총 296명 (남성 68.6%, 평균 연령 49.0±17.2세)
- 주요 적응증: CO 중독 54.1%, 돌발성 난청 34.5%, CO 지연 신경정신 후유증 5.1%
- 응급 치료군(A군): 181명 (61.2%)
- 입원 시 altered mental status: 52명 (19.9%)

**MEB 발생 현황**

- 전체 MEB 발생률: <mark style="background-color: #a8f0c6;">**56.1%** (166명)</mark>
- Video otoscopy 이상 소견: 58.8% (174명) — Grade 1: 56.4%, Grade 2: 2.4%

**세션 수에 따른 MEB 발생 확률**

| 시점 | MEB 발생 확률 |
|------|--------------|
| 1회차 | 약 60% |
| 5회차 이후 | 20% 미만 |
| 18회차 이후 | 0% |

세션이 늘어날수록 MEB 발생 확률이 지속 감소하는 경향이 관찰되었다. 반복 치료를 통해 환자가 pressure equalization 기술에 적응한 결과로 해석할 수 있다. 다만 후반 세션으로 갈수록 대상 환자 수가 급격히 줄어드는 만큼(>10회: 17명), 적응 효과만으로 단순하게 해석하기보다는 신중하게 볼 필요가 있다.

**Univariable 분석 주요 결과**

| 변수 | OR (95% CI) | p값 |
|------|-------------|-----|
| 응급 치료군 A | 2.51 (1.55–4.05) | <0.001 |
| Altered mental status | 3.18 (1.51–6.67) | 0.002 |
| 증상 발생 후 7일 이내 치료 | 높은 MEB 발생 | 0.014 |
| 가압 속도 4 FSW/min (vs 2.2) | 1.95 (1.21–3.13) | 0.006 |

**Multivariable logistic regression (독립적 위험 인자)**

| 독립적 위험 인자 | OR | 95% CI | p값 |
|---|---|---|---|
| <mark style="background-color: #a8f0c6;">Altered mental status</mark> | <mark style="background-color: #a8f0c6;">**2.50**</mark> | 1.13–5.51 | 0.023 |
| <mark style="background-color: #a8f0c6;">응급 치료군 A</mark> | <mark style="background-color: #a8f0c6;">**6.75**</mark> | 1.33–34.20 | 0.021 |

> **참고**: Compression 속도(4 FSW/min)는 univariable에서 유의했지만(p=0.006), multivariable에서는 유의성을 잃었다(p=0.105). 빠른 가압이 MEB에 영향을 미치는 경향은 있었지만, 응급 여부나 altered mental status 같은 다른 변수와 교란(confounding)되어 있을 가능성이 있다. 이 연구만으로 느린 가압이 MEB를 직접 줄인다고 단정하기는 어렵다.

---

## ✅ 장점 / ⚠️ 한계

**장점**

- Video otoscopy 기반의 객관적 MEB 등급화로 주관적 평가 오류를 줄임
- 국내 건강보험 적응증 분류를 위험 인자로 활용한 실용적 접근
- Restricted cubic spline으로 세션 수와 MEB의 비선형 관계를 시각적으로 제시

**한계**

- 단일기관 후향적 연구로 일반화에 제한이 있음
- Monoplace chamber에만 해당하여 multiplace chamber에 직접 적용하기 어려움
- MEB의 장기 예후 미평가
- 사전 이과 질환 등 교란 변수를 완전히 통제하지 못함

---

## 💬 내 생각 / 인사이트

석사 논문 주제가 HBOT 챔버 제어 시스템이었기 때문에, 이 논문의 임상 데이터가 특히 와닿았다.

1. **Compression 속도와 MEB**: 펌웨어에서 압력 센서 피드백으로 compression 속도를 제어하는 로직을 짰는데, 그 파라미터가 임상적으로 이렇게 직결된다는 걸 데이터로 확인하니 흥미롭다. Multivariable에서 유의성을 잃었다는 점이 오히려 더 현실적인 메시지인 것 같다. <mark>속도보다 환자 상태가 더 중요한 변수라는 뜻이기도 하니까.</mark>

2. **Altered mental status 환자 대응**: 능동적으로 pressure equalization을 수행할 수 없는 환자라면, 시스템 레벨에서 보완이 필요하다는 생각이 든다. <mark>단순히 "몇 ATA, 몇 분"으로 고정된 프로토콜이 아니라, 환자 의식 상태에 따라 compression 속도를 자동으로 조절하거나 운영자에게 알림을 주는 방식이 임상적으로 의미 있을 것 같다.</mark>

3. **세션 반복 효과**: 18회차 이후 MEB 0%라는 결과가 인상적이지만, <mark>그 시점에서의 환자 수(전체의 5.7%)를 감안하면 그대로 받아들이기보다는 경향성 정도로 이해하는 게 맞을 것 같다.</mark>

---

## 🔗 관련 논문

- Lima MA, et al. Update on middle ear barotrauma after hyperbaric oxygen therapy. *Int Arch Otorhinolaryngol* 2014
- Karahatay S, et al. Middle ear barotrauma with hyperbaric oxygen therapy: incidence and predictive value. *Ear Nose Throat J* 2008
- Vahidova D, et al. Does the slow compression technique of HBOT decrease the incidence of MEB? *J Laryngol Otol* 2006
