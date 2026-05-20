---
title: "[Paper Review] Understanding the Basis of the Kalman Filter Via a Simple and Intuitive Derivation"
date: 2025-05-19
categories: ["Paper Review"]
tags: ["Kalman Filter", "State Estimation", "Sensor Fusion", "Embedded Systems", "Signal Processing"]
description: "가우시안 곱셈 성질만으로 칼만 필터 측정 업데이트 방정식을 유도하는 직관적 접근법 — 펌웨어 구현 관점에서 분석"
ShowToc: true
TocOpen: false
draft: false
math: true
---

> **한 줄 요약**: <mark>두 가우시안 PDF의 곱이 또 다른 가우시안이라는 단 하나의 성질만으로 칼만 필터의 측정 업데이트 방정식 전체를 유도할 수 있다.</mark>

---

## 📌 논문 정보

| 항목 | 내용 |
| --- | --- |
| 제목 | Understanding the Basis of the Kalman Filter Via a Simple and Intuitive Derivation |
| 저자 | Ramsey Faragher |
| 저널 / 학회 | IEEE Signal Processing Magazine |
| 연도 | 2012 |
| DOI / 링크 | <https://doi.org/10.1109/MSP.2012.2203621> |
| 분야 | `Kalman Filter` `State Estimation` `Bayesian Filtering` `Sensor Fusion` |

---

## 🎯 읽게 된 이유

마이크로컴퓨터 수업에서 칼만 필터를 처음 접할 때, 교과서의 접근 방식은 대부분 벡터 대수와 최소 평균 제곱 추정(MMSE) 관점에서 시작한다. 수식은 나열되지만 "왜 이 형태인가"에 대한 물리적·직관적 답변은 부재한다.

임베디드 시스템에서 칼만 필터는 더 이상 이론의 영역이 아니다. IMU 센서 퓨전, 모터 속도 추정, 배터리 SOC(State of Charge) 추정 등 실무에서 직접 구현해야 하는 알고리즘이다. 구현자가 수식의 의미를 이해하지 못하면 Q, R 행렬 튜닝 하나도 근거 없이 시행착오에 의존하게 된다.

이 논문은 가우시안 분포의 곱 연산이라는 단순한 수학만으로 칼만 필터의 핵심 방정식을 유도하며, 그 과정이 펌웨어 엔지니어에게 실질적인 직관을 제공한다.

---

## 🔍 핵심 개념

### 시스템 모델

칼만 필터는 두 개의 선형 모델을 전제로 한다.

**상태 전이 방정식 (Process Model):**

$$x_t = F_t x_{t-1} + B_t u_t + w_t$$

**측정 방정식 (Measurement Model):**

$$z_t = H_t x_t + v_t$$

프로세스 노이즈 $w_t$는 공분산 $Q_t$인 제로-평균 가우시안, 측정 노이즈 $v_t$는 공분산 $R_t$인 제로-평균 가우시안으로 가정한다.

---

### 핵심 유도: 두 가우시안의 곱

예측 단계에서 생성되는 사전 추정 PDF와 측정 PDF를 각각 다음과 같이 정의한다.

$$y_1(r) = \frac{1}{\sqrt{2\pi}\sigma_1} \exp\!\left(-\frac{(r - \mu_1)^2}{2\sigma_1^2}\right)$$

$$y_2(r) = \frac{1}{\sqrt{2\pi}\sigma_2} \exp\!\left(-\frac{(r - \mu_2)^2}{2\sigma_2^2}\right)$$

이 두 PDF를 곱하면 결과 역시 가우시안이며, 융합된 평균과 분산은 다음과 같이 결정된다.

$$\mu_{\text{fused}} = \mu_1 + \frac{\sigma_1^2}{\sigma_1^2 + \sigma_2^2}(\mu_2 - \mu_1)$$

$$\sigma_{\text{fused}}^2 = \sigma_1^2 - \frac{\sigma_1^2}{\sigma_1^2 + \sigma_2^2} \cdot \sigma_1^2$$

여기서 칼만 이득 $K$가 자연스럽게 등장한다.

$$K = \frac{\sigma_1^2}{\sigma_1^2 + \sigma_2^2}$$

측정 좌표계 변환 행렬 $H$를 일반화하면:

$$K_t = P_{t|t-1} H_t^T \left(H_t P_{t|t-1} H_t^T + R_t\right)^{-1}$$

---

### 필터 전체 알고리즘

**예측 단계 (Predict):**

$$\hat{x}_{t|t-1} = F_t \hat{x}_{t-1|t-1} + B_t u_t$$

$$P_{t|t-1} = F_t P_{t-1|t-1} F_t^T + Q_t$$

**측정 업데이트 단계 (Update):**

$$K_t = P_{t|t-1} H_t^T \left(H_t P_{t|t-1} H_t^T + R_t\right)^{-1}$$

$$\hat{x}_{t|t} = \hat{x}_{t|t-1} + K_t\left(z_t - H_t \hat{x}_{t|t-1}\right)$$

$$P_{t|t} = P_{t|t-1} - K_t H_t P_{t|t-1}$$

---

### 펌웨어(C언어) 구현 예시 — 1D 스칼라 칼만 필터

아래는 1차원 상태(예: 온도 센서 노이즈 제거)에 대한 최소 구현이다.

```c
#include <stdint.h>

typedef struct {
    float x;    /* 상태 추정값 (State estimate)       */
    float p;    /* 추정 오차 분산 (Error covariance)  */
    float q;    /* 프로세스 노이즈 분산 (Process noise) */
    float r;    /* 측정 노이즈 분산 (Measurement noise) */
} KalmanFilter1D;

/**
 * @brief 칼만 필터 초기화
 * @param kf    필터 구조체 포인터
 * @param init_x 초기 상태값
 * @param init_p 초기 오차 분산 (불확실성이 클수록 크게 설정)
 * @param q      프로세스 노이즈: 상태 변화가 빠를수록 크게
 * @param r      측정 노이즈: 센서 데이터시트의 noise density 참조
 */
void kalman1d_init(KalmanFilter1D *kf,
                   float init_x, float init_p,
                   float q, float r)
{
    kf->x = init_x;
    kf->p = init_p;
    kf->q = q;
    kf->r = r;
}

/**
 * @brief 칼만 필터 업데이트 (예측 + 측정 업데이트 통합, F=1 가정)
 * @param kf      필터 구조체 포인터
 * @param measurement 현재 센서 측정값
 * @return float  필터링된 상태 추정값
 */
float kalman1d_update(KalmanFilter1D *kf, float measurement)
{
    /* --- Predict --- */
    /* F = 1 (상수 모델): x_pred = x,  p_pred = p + q */
    kf->p = kf->p + kf->q;

    /* --- Update --- */
    /* 칼만 이득: K = p / (p + R) */
    float K = kf->p / (kf->p + kf->r);

    /* 상태 업데이트: x = x + K * (z - H*x),  H = 1 */
    kf->x = kf->x + K * (measurement - kf->x);

    /* 공분산 업데이트: p = (1 - K) * p */
    kf->p = (1.0f - K) * kf->p;

    return kf->x;
}

/* ---- 사용 예시 ---- */
/*
KalmanFilter1D kf;
kalman1d_init(&kf, 0.0f, 1.0f, 0.01f, 0.1f);

while (1) {
    float raw = read_adc_temperature();
    float filtered = kalman1d_update(&kf, raw);
    report_temperature(filtered);
    delay_ms(10);
}
*/
```

> **구현 주의**: 부동소수점 나눗셈 연산이 매 루프마다 수행된다. Cortex-M0/M0+ 계열처럼 FPU가 없는 MCU에서는 fixed-point 연산으로 포팅하거나, 루프 주기를 늘려 연산 부하를 조절해야 한다.

---

## 📊 파라미터/변수의 의미

### 핵심 행렬/변수 대응표

| 기호 | 역할 | 스칼라 대응 | 실무 의미 |
| --- | --- | --- | --- |
| $\hat{x}_{t\|t-1}$ | 사전 상태 추정 | $\mu_1$ | 모델 기반 예측값 |
| $\hat{x}_{t\|t}$ | 사후 상태 추정 | $\mu_{\text{fused}}$ | 센서 퓨전 후 최적 추정값 |
| $P_{t\|t-1}$ | 사전 공분산 | $\sigma_1^2$ | 예측 불확실성 |
| $P_{t\|t}$ | 사후 공분산 | $\sigma_{\text{fused}}^2$ | 업데이트 후 불확실성 |
| $Q_t$ | 프로세스 노이즈 공분산 | $q$ | 모델 오차 크기 |
| $R_t$ | 측정 노이즈 공분산 | $r$ | 센서 노이즈 크기 |
| $K_t$ | 칼만 이득 | $K$ | 예측 vs 측정 신뢰 비율 |
| $H_t$ | 측정 변환 행렬 | $c^{-1}$ (단위 변환) | 상태 → 측정 도메인 매핑 |
| $F_t$ | 상태 전이 행렬 | $1$ (상수 모델) | 시간에 따른 상태 변화 |

---

### Q, R 튜닝 트레이드오프

| 설정 | 칼만 이득 $K$ | 동작 특성 | 적합한 상황 |
| --- | --- | --- | --- |
| $Q \gg R$ | $K \to 1$ | 측정값을 거의 그대로 사용 | 센서 신뢰도 높음, 모델 불확실 |
| $Q \ll R$ | $K \to 0$ | 예측값 위주로 동작 | 모델 신뢰도 높음, 센서 노이즈 큼 |
| $Q = R$ | $K = 0.5$ | 예측·측정 균등 반영 | 초기 튜닝 시작점 |
| $Q = 0$ | $K \to 0$ (시간 경과 후) | 순수 예측 (필터 발산 위험) | 사용 금지 |

---

## 💡 직관적 유도 & 인사이트

### 왜 가우시안의 곱인가

두 정보 소스(예측, 측정)가 각각 불확실성을 가진 가우시안으로 표현될 때, 두 정보를 **동시에 만족하는** 상태를 찾는 것은 두 PDF의 곱에서 최대값(MAP 추정)을 구하는 것과 동일하다.

핵심은 가우시안의 곱이 **여전히 가우시안**이라는 점이다. 이 성질이 없다면 시간이 지남에 따라 PDF의 형태가 점점 복잡해져 재귀적 계산이 불가능하다. 칼만 필터의 재귀적 우아함은 전적으로 이 수학적 성질에 기반한다.

### 이노베이션(Innovation)의 의미

측정 업데이트 방정식에서 $z_t - H_t \hat{x}_{t|t-1}$ 항을 **이노베이션(Innovation)** 또는 잔차(Residual)라 부른다. 이 값이 0에 가깝다면 예측이 정확했다는 의미이고, 크다면 모델과 현실 사이의 괴리가 크다는 신호다.

실무에서 이노베이션을 모니터링하면 센서 고장(innovation이 갑자기 폭증) 또는 모델 열화를 조기에 탐지할 수 있다.

### 공분산 행렬 $P$의 물리적 의미

$P$의 대각 원소는 각 상태 변수의 **추정 분산**이다. 이 값이 작을수록 추정에 대한 확신이 높다. 업데이트 직후 $P$는 반드시 감소하며(불확실성 감소), 예측 단계에서는 $Q$가 더해지면서 증가한다(불확실성 증가). 이 증감 사이클이 필터의 동적 균형을 만들어낸다.

---

## ✅ 정리

| 구분 | 내용 |
| --- | --- |
| 핵심 수학 | 두 가우시안 PDF의 곱 → 가우시안 (재귀성의 근거) |
| 예측 단계 | 상태 전이 모델로 사전 추정값과 공분산 전파 |
| 업데이트 단계 | 칼만 이득으로 예측과 측정을 가중 평균 |
| 칼만 이득 | $K = P_{t\|t-1}H^T(HP_{t\|t-1}H^T + R)^{-1}$ |
| 최적성 조건 | 선형 시스템 + 가우시안 노이즈 → MMSE 의미에서 최적 |
| 변형 | 비선형 시스템: EKF(Extended), UKF(Unscented) |

---

## 💬 내 생각 / 인사이트

### 실무 적용 가능성

이 논문의 유도 방식은 단순하지만, 펌웨어 엔지니어에게 가장 중요한 질문인 "Q와 R을 어떻게 설정하는가"에 직접적인 답을 제공한다. 공분산 행렬이 PDF의 분산이라는 사실을 이해하면, Q는 모델이 얼마나 부정확한지, R은 센서가 얼마나 노이즈한지를 반영한다는 것이 자명해진다.

실제 IMU(MPU-6050 등)를 이용한 자세 추정 펌웨어를 작성할 때, 자이로스코프의 드리프트를 Q, 가속도계의 노이즈를 R로 모델링하면 튜닝의 출발점을 잡을 수 있다. 이는 감(感)이 아니라 물리적 근거다.

### 한계와 주의점

**선형성 가정**: 실제 시스템(예: 쿼드콥터 자세, 차량 조향)은 비선형이다. 이 경우 EKF(야코비안 선형화) 또는 UKF(시그마 포인트)로 확장이 필요하며, 선형 칼만 필터의 최적성 보장은 사라진다.

**가우시안 노이즈 가정**: 현실의 센서 노이즈는 충격, 전자기 간섭 등으로 인해 가우시안이 아닐 수 있다. 이 경우 필터 성능이 저하되며, 파티클 필터(Particle Filter) 등을 검토해야 한다.

**수치 안정성**: 부동소수점 연산에서 공분산 행렬 $P$의 양의 정치(Positive Definite) 성질이 누적 오차로 깨질 수 있다. 실무에서는 Joseph 형태의 공분산 업데이트나 Square Root Kalman Filter 사용을 권장한다.

**정적 Q, R의 한계**: 이 논문은 Q와 R을 상수로 가정한다. 실제로는 온도·진동 등 환경에 따라 노이즈 특성이 변한다. 적응형 칼만 필터(Adaptive KF)나 Noise Covariance Estimation 기법이 필요한 이유다.

학부 수업에서 칼만 필터를 처음 배울 때 이 논문의 접근 방식은 수식 암기가 아닌 개념 이해를 가능하게 한다는 점에서 교육적 가치가 높다. 다만 이것을 실제 임베디드 시스템에 적용하려면, 이 논문이 출발점일 뿐 비선형 확장, 수치 안정성, 파라미터 추정 등의 후속 학습이 반드시 필요하다.

---

## 🔗 관련 논문

- R. E. Kalman, "A new approach to linear filtering and prediction problems," *J. Basic Eng.*, vol. 82, no. 1, pp. 35–45, 1960. — 칼만 필터 원본 논문
- S. J. Julier and J. K. Uhlmann, "Unscented filtering and nonlinear estimation," *Proc. IEEE*, vol. 92, no. 3, pp. 401–422, 2004. — UKF: 비선형 확장
- P. D. Groves, *Principles of GNSS, Inertial, and Multisensor Integrated Navigation Systems*, Artech House, 2008. — EKF 및 센서 퓨전 실무 레퍼런스
- B. D. O. Anderson and J. B. Moore, *Optimal Filtering*, Dover, 2005. — 칼만 필터 최적성 증명 포함
