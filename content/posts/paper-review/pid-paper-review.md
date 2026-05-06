---
title: "[Paper Review] PID Control System Analysis, Design, and Technology"
date: 2025-04-15
categories: ["Paper Review"]
tags: ["PID", "control", "embedded", "firmware"]
description: "PID 제어기의 구조, 튜닝 방법론, 특허 및 상용 소프트웨어/하드웨어 모듈을 망라한 현대적 개요. derivative 항의 안정성 역설과 anti-windup 구현 전략을 중심으로 정리."
ShowToc: true
TocOpen: false
draft: false
math: true
---

> **한 줄 요약**: 산업 현장에서 90% 이상 사용되는 PID 제어기는 단순한 구조 덕분에 살아남았지만, ==derivative 항 하나를 잘못 튜닝하면 오히려 시스템을 불안정하게 만들 수 있다.==

---

## 📌 논문 정보

| 항목 | 내용 |
| --- | --- |
| 제목 | PID Control System Analysis, Design, and Technology |
| 저자 | Kiam Heong Ang, Gregory Chong, Yun Li |
| 저널 / 학회 | IEEE Transactions on Control Systems Technology |
| 연도 | 2005 |
| DOI / 링크 | <https://doi.org/10.1109/TCST.2005.847331> |
| 분야 | `control` `embedded` |

---

## 🎯 읽게 된 이유

석사 연구 중에 HBOT 챔버 회사에 재직 중인 선배님께 조언을 구할 기회가 있었다. 그때 선배님이 짧게 한마디 하셨다. *"미분항은 실제로 잘 안 써요."*

그 말을 듣고 당시 나는 그냥 넘겼다. 왜인지를 파고들 여유가 없었다. 솔직히 말하면, 그 시점의 나는 제어 이론보다 졸업이 더 급했다. 챔버 압력 제어 로직을 어떻게든 돌아가게 만드는 것이 목표였고, $K_D$는 노이즈가 튀어서 disabled 처리하고 넘어갔다.

그런데 졸업 이후에도 그 말이 계속 머릿속에 남았다. *현장에서 수십 년 일한 엔지니어가 왜 그렇게 말했을까.* 단순히 "노이즈 때문에"라는 설명만으로는 뭔가 부족한 느낌이었다. 이 논문을 읽고 나서야 그 이유를 수식으로 이해했다. Dead time이 있는 플랜트에서 $K_D$를 올리면 오히려 시스템이 불안정해질 수 있다는 것, 그래서 ==산업 현장의 80%가 derivative 항을 비활성화 상태로 운용한다==는 것.

선배님의 그 한마디가 이론적으로 근거가 있었다는 걸, 조금 늦게 확인한 셈이다.

---

## 🔍 핵심 개념

### PID의 세 가지 항 — 역할 분리

PID 전달 함수의 병렬(Parallel) 형태:

$$G(s) = K_P + K_I \frac{1}{s} + K_D s$$

이상(Ideal) 형태로 쓰면:

$$G(s) = K_P \left(1 + \frac{1}{T_I s} + T_D s\right)$$

각 항의 역할을 직관적으로 보면:

- **P항**: 현재 오차에 비례해서 즉각 반응한다. 빠르지만, 정상상태 오차는 남는다.
- **I항**: 오차를 시간적으로 누적해서 0으로 끌어당긴다. 정상상태 오차를 제거하지만, 위상 지연을 추가해서 시스템을 더 진동하게 만든다.
- **D항**: 오차의 변화율을 미리 예측해서 앞서 대응한다. 위상 선행(phase lead)을 주지만, 고주파 잡음을 증폭한다.

---

### Integral Windup — 왜 anti-windup이 필요한가

actuator에 포화(saturation)가 생기면 I항은 계속 오차를 누적하는데, 실제 출력은 한계에 걸려 반응을 못 한다. 포화가 풀리는 순간 누적된 I항이 한꺼번에 터져 저주파 진동과 불안정을 유발한다.

소프트웨어로 구현하는 anti-windup의 표준 방식:

$$U_I'(s) = \frac{1}{T_I s} \left[ K_P E(s) - \frac{U(s) - \tilde{U}(s)}{\gamma} \right]$$

$\tilde{U}(s)$는 포화된 실제 출력, $\gamma \in [0.1, 1.0]$는 보정 계수다.

직관적으로 보면, **"integrator가 포화된 만큼만 역방향으로 빼줘서 누적이 계속 쌓이지 않도록 억제하는 음수 피드백"**이다. 펌웨어에서는 단순히 아래 한 줄로 구현한다.

```c
if (output > MAX) integral -= (output - MAX) / gamma;
```

---

### Derivative 항이 오히려 불안정을 만드는 조건

이 논문의 핵심 반전이다. 일반적으로 D항을 올리면 안정성이 좋아진다고 알려져 있지만, **transport delay(dead time)가 있는 1차 플랜트**에서는 다르다.

1차 지연 + 순수 지연 플랜트:

$$G(s) = \frac{K}{1+Ts}e^{-Ls}$$

여기에 PD 제어기를 붙이면 개루프 게인은:

$$\left|G(j\omega)G_{PD}(j\omega)\right| = KK_P\sqrt{\frac{1 + T_D^2 \omega^2}{1 + T^2 \omega^2}} \geq KK_P \min\left(1, \frac{T_D}{T}\right)$$

$T_D \geq T$ 이거나 $KK_P \leq 1$ 이면, 위 식은 **모든 주파수에서 게인이 0 dB 이상**임을 뜻한다. 이 경우 게인 교차 주파수 $\omega_c$ 가 무한대이고, 거기서의 위상은:

$$\angle G = \frac{\pi}{2} - \frac{\pi}{2} - \infty < -\pi$$

Bode/Nyquist 기준으로 안정 마진이 사라져 **시스템이 불안정**해진다.

---

### Derivative 필터링 — 실제 구현

순수 미분기 $T_D s$ 는 고주파에서 게인이 무한대다. 실제 구현에서는 low-pass filter를 직렬 연결한다.

$$G_D'(s) = \frac{T_D s}{1 + \frac{T_D}{\beta} s}$$

산업용 하드웨어에서 $\beta$ 설정 범위는 1–33이고, 대부분 8–16 사이에서 사용한다. 임베디드에서는 이를 discretize해서 difference equation으로 구현한다.

---

### Tuning 방법 5가지 분류

| 방법 | 원리 | 특징 |
| --- | --- | --- |
| Analytical (IMC/Lambda) | 모델 → 수식 직접 계산 | 정확하지만 모델 정확도에 의존 |
| Heuristic (Ziegler-Nichols) | 경험 기반 공식 | 빠르지만 최적과 거리 있음 |
| Frequency Response | 루프 셰이핑 | 안정성에 강인하나 offline 위주 |
| Optimization | 수치 최적화 | 다목적 가능하나 느림 |
| Adaptive | 실시간 식별 + 위 방법 혼합 | 자동화 가능하나 복잡 |

---

## 📊 파라미터/변수의 의미

아래 표는 $K_P$, $K_I$, $K_D$ 각각이 독립적으로 closed-loop 응답에 미치는 영향이다 (논문 Table I 기준, 안정적인 open-loop 플랜트 한정).

| 파라미터 | Rise Time | Overshoot | Settling Time | SS Error | Stability |
| --- | --- | --- | --- | --- | --- |
| **Kp 증가** | 감소 ↓ | 증가 ↑ | 약간 증가 | 감소 ↓ | 저하 |
| **Ki 증가** | 약간 감소 | 증가 ↑ | 증가 ↑ | → 0 (제거) | 저하 |
| **Kd 증가** | 약간 감소 | 감소 ↓ | 감소 ↓ | 미세 변화 | 개선 (without dead time) |

> ⚠️ 위 표는 각 항을 **독립적으로** 조정했을 때의 경향이다. 실제로는 $K_P$, $T_I$, $T_D$ 가 상호의존적으로 동작한다. 특히 $K_D$ 의 "stability 개선"은 **dead time이 없는 경우에만** 유효하다.

---

## 💡 직관적 유도 & 인사이트

### "D항이 안정을 해친다"는 게 맞는 말인가?

P항만 쓰다가 D항을 추가하면 두 가지가 동시에 일어난다.

- 위상 앞당김(phase lead) → 위상 마진 증가 → 안정성 ↑
- 게인 증가 → 게인 마진 감소 → 안정성 ↓

이 두 효과가 서로 충돌하는데, ==dead time이 클수록 게인 증가의 부정적 영향이 압도==한다. 비유하자면, 자동차 핸들을 1초 뒤에야 반응하는 파워스티어링으로 바꿨는데, 거기다가 핸들 감도까지 올린 것과 같다. 반응이 빨라지는 게 아니라 오버슈트가 폭발한다.

### Anti-windup을 적용하지 않으면 어떻게 되나

직관적으로: **"목표 지점 근처에 도착했는데도 브레이크가 걸리지 않는 차"**다. I항이 계속 누적되어 있으면, 오차가 0이 되어도 출력이 계속 올라간다. 결국 반대 방향 오차가 크게 생겨야 I항이 줄기 시작한다. 이 lag가 저주파 진동의 원인이다.

### 왜 IMC/Lambda tuning이 소프트웨어에서 지배적인가

IMC는 플랜트를 $\frac{K}{1+Ts}e^{-Ls}$ 로 근사하고, 원하는 closed-loop 응답 시정수 $\lambda$ 를 설정하면 $K_P$, $T_I$, $T_D$ 가 수식으로 바로 나온다. "모델 → 파라미터"가 closed form이라 실시간 계산이 가능하고, $\lambda$ 하나로 빠름/느림 트레이드오프를 조절할 수 있어서 현장에서 쓰기 편하다.

---

## ✅ 정리

- **D항 비활성화는 충분히 합리적인 선택이다.** 산업 현장의 80%가 이미 그렇게 운용하고 있고, dead time이 있는 플랜트에서는 $K_D$ 를 올리는 것이 오히려 불안정을 유발할 수 있다는 수학적 증명이 논문에 명확히 나와 있다. HBOT 챔버에서 D항을 비활성화한 것은 맞는 판단이었다.

- **Anti-windup은 선택이 아니라 필수다.** 4–20mA 비례 밸브처럼 actuator saturation이 발생하는 시스템에서 anti-windup 없이 PID를 운용하면 저주파 진동이 반드시 나타난다. 소프트웨어 구현에서 $\gamma \in [0.1, 1.0]$ 범위면 대부분 잘 동작한다.

- **튜닝 방법론은 상황에 따라 선택해야 한다.** Ziegler-Nichols는 초기 파라미터 추정에 적합하고, IMC/Lambda는 closed-form 공식이라 온라인 튜닝에 유리하다. 최적 성능이 필요하면 optimization 기반을 써야 하지만, 그만큼 계산 비용과 모델 정확도를 요구한다.

- **표준화 부재가 현장의 가장 큰 문제다.** ABB, Foxboro, Honeywell, Yokogawa 각각의 PID 구조와 튜닝 규칙이 달라서, 학계에서 제안한 튜닝 공식이 특정 하드웨어에서 동작하지 않는 이유가 여기 있다. 논문은 이를 해결하기 위해 표준 PID 구조 위에서 "plug-and-play" 방식의 자동 튜닝을 지향하는 PIDeasy를 제안하는 것으로 마무리된다.

---

## 💬 내 생각 / 인사이트

> 🔖 **개인적 메모**: 다음에 STM32에서 PID 루프를 다시 구현한다면, (1) anti-windup을 반드시 포함하고, (2) D항은 low-pass filter를 직렬 연결해서 $\beta = 10$ 정도로 고주파 차단, (3) 초기 $K_P$ 는 Z-N으로 추정하고 IMC 공식으로 전환하는 순서로 접근할 것이다.

---

## 🔗 관련 논문

- Ziegler JG, Nichols NB. Optimum settings for automatic controllers. *Trans ASME* 1942
- Åström KJ, Hägglund T. PID Controllers: Theory, Design, and Tuning. *ISA* 1995
- Shinskey FG. Feedback Controllers for the Process Industries. *McGraw-Hill* 1994
