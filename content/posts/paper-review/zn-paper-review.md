---
title: "[Paper Review] Optimum Settings for Automatic Controllers"
date: 2025-04-21
categories: ["Paper Review"]
tags: ["PID", "Ziegler-Nichols", "tuning", "control"]
description: "PID 제어기의 최적 파라미터를 실험적으로 결정하는 Z-N 튜닝 방법을 제안한 1942년 고전 논문. Ultimate sensitivity와 process reaction curve 두 가지 방법을 통해 현장에서 빠르게 최적 설정을 도출하는 절차를 제시한다."
ShowToc: true
TocOpen: false
draft: false
math: true
---

> **한 줄 요약**: <mark>수학 없이도 현장에서 PID 파라미터를 빠르게 결정할 수 있는 두 가지 실험적 튜닝 절차</mark>를 제시한, 제어 공학의 출발점이 된 논문.

---

## 📌 논문 정보

| 항목 | 내용 |
| --- | --- |
| 제목 | Optimum Settings for Automatic Controllers |
| 저자 | J. G. Ziegler, N. B. Nichols |
| 저널 / 학회 | Transactions of the ASME |
| 연도 | 1942 |
| DOI / 링크 | <https://doi.org/10.1115/1.2899060> |
| 분야 | `control` `embedded` |

---

## 🎯 읽게 된 이유

고압산소챔버(HBOT) 제어 시스템을 구현하면서 압력을 목표값까지 안정적으로 올리는 것이 핵심 과제였다. 4–20mA 비례 밸브로 압력을 제어하는 구조였는데, PID를 쓰려면 $K_P$, $T_I$, $T_D$ 를 어떻게든 정해야 했다.

그때 가장 먼저 등장하는 이름이 Ziegler-Nichols였다. 인터넷 어디서든 "PID 튜닝 = Z-N"이라고 나올 정도로 기본 중의 기본이지만, 실제로 원본 논문을 읽어본 적은 없었다. 공식만 외워서 쓰다 보니 <mark>왜 $K_P = 0.6S_u$ 인지, 왜 $T_I = P_u/2$ 인지 근거를 제대로 몰랐다.</mark> 이 논문은 그 공식들이 어디서 나왔는지를 직접 확인하기 위해 찾았다.

---

## 🔍 핵심 개념

### 세 가지 제어 효과

Z-N 논문은 PID의 세 항을 당시 현장 용어로 부른다.

| 현재 용어 | Z-N 논문 용어 | 측정 단위 |
| --- | --- | --- |
| P (비례) | Proportional response | Sensitivity (psi/in) |
| I (적분) | Automatic reset | Reset rate (1/min) |
| D (미분) | Pre-act | Pre-act time (min) |

"sensitivity"는 펜 1인치 움직임당 밸브 출력 압력 변화량으로 정의한다. 현재의 $K_P$ 와 같은 개념이다.

---

### 방법 1 — Ultimate Sensitivity (폐루프 실험)

현장에서 가장 많이 쓰이는 방법이다. 절차는 단순하다.

1. I, D 항을 비활성화하고 P만 남긴다.
2. $K_P$ 를 서서히 올리면서 출력이 **등진폭 진동(sustained oscillation)**을 시작하는 지점을 찾는다.
3. 그 시점의 gain을 $S_u$ (ultimate sensitivity), 진동 주기를 $P_u$ (ultimate period)로 기록한다.

이 두 값으로 아래 공식에 대입하면 최적 파라미터가 나온다.

**P only:**

$$K_P = 0.5\, S_u$$

**PI:**

$$K_P = 0.45\, S_u, \qquad \text{Reset rate} = \frac{1.2}{P_u}$$

**PID:**

$$K_P = 0.6\, S_u, \qquad \text{Reset rate} = \frac{2.0}{P_u}, \qquad \text{Pre-act time} = \frac{P_u}{8}$$

현대 표기로 변환하면:

$$K_P = 0.6\, S_u, \qquad T_I = \frac{P_u}{2}, \qquad T_D = \frac{P_u}{8}$$

---

### 방법 2 — Process Reaction Curve (개루프 실험)

컨트롤러를 루프에서 분리하고 밸브에 step 입력 $\Delta F$ (psi)를 가해 플랜트의 응답 곡선(S자 곡선)을 측정한다.

이 곡선의 변곡점에서 접선을 그으면 두 가지 값을 읽을 수 있다.

- **R** (reaction rate): 변곡점에서의 최대 기울기 (in/min)
- **L** (lag): 접선이 초기 출력값과 만나는 시간 (min)

단위 반응률로 정규화하면:

$$R_1 = \frac{R}{\Delta F}$$

이 두 값으로 최적 파라미터:

**P only:**

$$\text{Sensitivity} = \frac{1}{R_1 L}$$

**PI:**

$$\text{Sensitivity} = \frac{0.9}{R_1 L}, \qquad \text{Reset rate} = \frac{0.3}{L}$$

**PID:**

$$\text{Sensitivity} = \frac{1.2}{R_1 L}, \qquad \text{Reset rate} = \frac{0.5}{L}, \qquad \text{Pre-act time} = 0.5L$$

두 방법의 관계: $L = P_u/4$, $R_1 = 8/(S_u P_u)$ 로 서로 변환 가능하다.

---

## 📊 파라미터/변수의 의미

| 변수 | 의미 | 결정 방법 |
| --- | --- | --- |
| $S_u$ | 등진폭 진동을 만드는 최소 gain | 폐루프 실험에서 직접 측정 |
| $P_u$ | $S_u$ 에서의 진동 주기 | 폐루프 실험에서 직접 측정 |
| $R_1$ | 단위 밸브 압력당 반응률 | 개루프 step 실험에서 측정 |
| $L$ | 공정의 등가 지연 시간 | 반응 곡선 접선에서 측정 |

<mark>L이 작을수록 $K_P$ 높게, reset rate 높게, pre-act time 짧게 설정 가능하다.</mark> 즉 **응답이 빠른 플랜트일수록 더 aggressive하게 튜닝할 수 있다.**

---

## 💡 직관적 유도 & 인사이트

### 왜 $K_P = 0.5\, S_u$ 인가

$S_u$ 에서 시스템은 amplitude ratio = 1, 즉 진동이 줄지도 늘지도 않는 경계다. 논문은 대부분의 응용에서 **amplitude ratio 25%가 안정성과 응답속도 사이의 좋은 타협점**임을 실험적으로 보였고, 이 25%가 대략 $0.5\, S_u$ 에서 얻어진다는 것을 확인했다. 수식 유도가 아니라 **실험 관찰에서 나온 경험칙**이다.

### 왜 I항을 추가하면 $K_P$ 를 0.5에서 0.45로 낮추는가

I항(automatic reset)은 위상 지연을 추가해 amplitude ratio를 높인다. $K_P$ 를 그대로 두면 I항 추가만으로 진동이 커지기 때문에 $K_P$ 를 10% 낮춰서 안정성 마진을 보상한다.

### Reaction Curve의 L이 "lag"인 이유

접선이 초기값과 만나는 시간 L은 플랜트 내의 모든 시간 지연(밸브 지연, 센서 지연, 공정 지연)의 합산 효과를 하나의 숫자로 표현한 것이다. 수학적으로 엄밀한 dead time은 아니지만, 현장에서 측정 가능한 근사값으로서 실용적으로 충분하다.

---

## ✅ 정리

- **Z-N 공식은 수학적 유도가 아니라 실험 관찰의 산물이다.** $K_P = 0.6\, S_u$, $T_I = P_u/2$ 같은 공식은 다양한 공정에서 반복 실험한 결과 경험적으로 도출된 값이다. 이 사실을 알면 "왜 이 공식이 내 플랜트에서 안 맞지?"라는 질문에 답할 수 있다. Z-N은 범용 출발점이지 보편적 최적해가 아니다.

- **두 방법은 상황에 따라 선택한다.** Ultimate sensitivity 방법은 폐루프에서 진행하므로 실제 운용 중인 시스템에 적합하지만, 진동을 의도적으로 유발해야 한다. Reaction curve 방법은 개루프라 안전하지만 시스템을 잠시 수동 제어해야 한다. <mark>HBOT 챔버처럼 환자가 탑승한 상황에서는 reaction curve 방법이 더 현실적이다.</mark>

- **Z-N은 초기 파라미터 추정에 적합하다.** 논문 자체가 "optimum"이라는 표현을 쓰지만, 실제로는 quarter-decay ratio(amplitude ratio 25%) 기준의 설정이라 overshoot이 크다. 현장에서는 Z-N으로 시작점을 잡고 IMC나 수동 fine-tuning으로 마무리하는 것이 일반적이다.

- **80년이 지나도 기본이 되는 이유가 있다.** 이 논문이 제시한 개념, 즉 플랜트 응답에서 두 가지 숫자($S_u$, $P_u$ 또는 $R_1$, $L$)만 뽑아내면 세 개의 파라미터를 결정할 수 있다는 아이디어는, 이후 IMC, Lambda tuning, relay feedback 등 거의 모든 자동 튜닝 방법론의 출발점이 되었다.

---

## 💬 내 생각 / 인사이트

> 🔖 **개인적 메모**: HBOT 챔버 압력 제어에서는 compression 초기 구간이 사실상 1차 플랜트에 가깝기 때문에 reaction curve 방법으로 $R_1$ 과 $L$ 을 측정하고 PI 설정을 시작점으로 쓰는 것이 합리적이다. 챔버 내부 압력은 환자 안전과 직결되므로 overshoot을 줄이는 방향, 즉 Z-N 기본값보다 $K_P$ 를 낮게, $T_I$ 를 길게 잡는 보수적 조정이 필요하다.

---

## 🔗 관련 논문

- Ang KH, Chong G, Li Y. PID control system analysis, design, and technology. *IEEE Trans Control Syst Technol* 2005
- Åström KJ, Hägglund T. Revisiting the Ziegler-Nichols step response method for PID control. *J Process Control* 2004
- O'Dwyer A. Handbook of PI and PID Controller Tuning Rules. *Imperial College Press* 2003
