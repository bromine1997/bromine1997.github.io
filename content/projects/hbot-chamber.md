---
title: "IoT 고압산소챔버 시스템"
date: 2024-01-01
hidemeta: false
showtoc: true
tocopen: true
comments: false
tags:
  - Android
  - NestJS
  - IoT
  - 석사논문
summary: "Tinker Board 2S 기반 고압산소챔버 원격 제어 및 모니터링 시스템. Android 앱 + NestJS 서버 + Vue3 대시보드로 구성된 풀스택 IoT 플랫폼. 석사 학위논문 프로젝트."
cover:
  image: /images/projects/hbot-chamber.png
  alt: IoT 고압산소챔버 시스템
---

## 개요

기존 고압산소치료(HBOT) 시스템은 높은 도입 비용, 전문 설치 환경의 필요성, **실시간 원격 관리 기능의 부재**로 인해 병원 외 환경에서의 활용이 어려웠다. 의료진이 항상 상주해야 하고, 원격 제어·모니터링이 불가능했으며, 자동화된 프로세스가 부족해 운영 효율성이 낮았다.

본 연구는 **IoT 기술과 Android OS를 결합해 고압산소챔버를 헬스케어 기기로 확장**하는 것을 목표로 개발되었다.

| 항목 | 내용 |
|------|------|
| 기간 | 2024 |
| 소속 | 연세대학교 의공학과 석사 학위논문 |
| 역할 | 전체 시스템 설계 및 개발 (단독) |
| 최대 운용 압력 | 3기압 |
| GitHub | [App](https://github.com/bromine1997/HBOTChamber) · [Server](https://github.com/bromine1997/tinkerboard-test) |

---

## 시스템 아키텍처

```
[고압산소챔버]
  ├─ 압력 센서
  ├─ 온도 · 습도 센서
  ├─ O₂ / CO₂ 센서
  └─ 유량계
       │
       │ GPIO · SPI · I2C (MRAA)
       ▼
[Tinker Board 2S]  ← Android 앱이 SBC에서 직접 실행
  ├─ 센서 데이터 수집 (1초 주기)
  ├─ PID 자동 압력 제어 (2채널 비례밸브)
  └─ Profile-based automated operation
       │
       │ WebSocket
       ▼
[NestJS 서버]  ←→  [MongoDB]
  ├─ 모듈화 구조 (auth / user / chamber)
  ├─ JWT 기반 인증 및 Role-Based Access Control (RBAC)
  └─ Swagger API 문서 자동 생성
       │
       │ REST API · WebSocket
       ▼
[Vue 3 대시보드]
  ├─ 실시간 라이브 차트
  ├─ 압력 프로파일 편집기
  └─ 역할별 차등 접근 제어 (User / Operator / Admin)
```

<!-- 📌 이미지 추가: 전체 시스템 블록다이어그램 → PPT 15페이지 캡처 -->
<!-- 저장 경로: /images/projects/hbot/system-block-diagram.png -->
![전체 시스템 블록다이어그램](/images/projects/hbot/system-block-diagram.png)

일반적인 Android 앱은 스마트폰에서 실행되는 UI다. 이 프로젝트에서는 챔버에 부착된 Tinker Board 2S(소형 컴퓨터) 위에서 Android 앱이 직접 실행되며, 앱 자체가 **챔버를 제어하는 컨트롤러** 역할을 한다. MRAA 라이브러리를 통해 앱 코드에서 하드웨어 핀(GPIO·SPI·I2C)을 직접 읽고 쓸 수 있어, 센서 수집 → PID 제어 → 서버 전송까지 단일 앱 안에서 모두 처리한다.

<!-- 📌 이미지 추가: 하드웨어 시스템 블록다이어그램 → PPT 16페이지 캡처 -->
<!-- 저장 경로: /images/projects/hbot/hardware-block-diagram.png -->
![하드웨어 시스템 블록다이어그램](/images/projects/hbot/hardware-block-diagram.png)

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| 실시간 센서 모니터링 | 압력·온도·습도·O₂·CO₂·유량을 1초 주기로 수집 |
| PID 자동 압력 제어 | 2채널 PID로 가압/감압 비례밸브 정밀 제어 |
| 압력 프로파일 편집 | 구간별 시작압력·종료압력·지속시간 설정 |
| 라이브 차트 | 목표 프로파일(검정)과 실측 압력(빨강) 실시간 비교 |
| JWT 인증 | User / Operator / Administrator 역할 기반 접근 제어 |
| 원격 모니터링 | WebSocket으로 외부에서 실시간 데이터 확인 및 제어 |

<!-- 📌 이미지 추가: Android 앱 주요 화면 → PPT 19-20페이지 캡처 (앱 스크린샷 2장) -->
<!-- 저장 경로: /images/projects/hbot/app-screens.png -->
![Android 앱 화면](/images/projects/hbot/app-screens.png)

<!-- 📌 이미지 추가: 웹 원격 제어 및 모니터링 화면 → PPT 30페이지 캡처 -->
<!-- 저장 경로: /images/projects/hbot/web-dashboard.png -->
![웹 대시보드](/images/projects/hbot/web-dashboard.png)

---

## 기술 스택

**Android App (On-device Controller)**
- Language: Java
- Architecture: MVVM (ViewModel · LiveData)
- Hardware Control: MRAA (GPIO, SPI, I2C)
- Target: Tinker Board 2S (Rockchip RK3399, Android 11)

**Server & Dashboard**
- Backend: NestJS (Node.js) — Modular architecture, Swagger integration
- Frontend: Vue 3
- Database: MongoDB
- Protocol: WebSocket · REST API
- Auth: JWT + Role-Based Access Control (RBAC)

---

## 검증 결과

식품의약품안전처 인증 1인용 의료용 고압산소챔버 규격과 비교 검증을 진행했다.

| 항목 | 측정값 | 비고 |
|------|--------|------|
| 최대 운용 압력 | 3기압 | |
| 가압 속도 | 0.028 MPa/min | 기준 대비 현저히 낮음 (안전) |
| 감압 속도 | 0.00446 MPa/min | |
| Step Function Overshoot | **0.67%** | 3기압 기준 |
| 30분 프로파일 overshoot | 최대 0.02기압 | 2기압 유지 구간 |
| 35분 프로파일 overshoot | 최대 0.03기압 | 응급 배기 상황 포함 |
| 3시간 장기 프로파일 | 최대 2.03기압 | 응급 배기 상황 포함 |

<!-- 📌 이미지 추가: Step Function 그래프 → PPT 35페이지 캡처 -->
<!-- 저장 경로: /images/projects/hbot/step-function-result.png -->
![Step Function 검증 결과](/images/projects/hbot/step-function-result.png)

<!-- 📌 이미지 추가: 장기 프로파일 검증 그래프 → PPT 37~39페이지 중 택1 (30분 or 3시간) -->
<!-- 저장 경로: /images/projects/hbot/profile-result.png -->
![프로파일 운용 검증 결과](/images/projects/hbot/profile-result.png)

Step-Function 실험에서의 미미한 Overshoot와 응급 배기밸브 테스트 결과는 **PID 제어 시스템의 안정성**을 보여준다.

---

## Design Rationale

**Android 앱을 SBC 컨트롤러로 사용한 이유**

일반적인 임베디드 제어 시스템은 Linux + Python/C로 하드웨어를 제어한다. 이 프로젝트는 Tinker Board 2S가 Android OS를 지원한다는 점을 활용해 Android 앱 자체를 컨트롤러로 운용했다. MRAA 라이브러리를 통해 Java 코드에서 GPIO 핀을 직접 제어하는 구조로, 제어 로직과 UI·통신을 단일 개발 환경에서 통합 관리할 수 있다는 장점이 있다.

**2채널 독립 PID 구성**

고압산소챔버는 압력 오버슈트가 안전 문제로 직결된다. 가압과 감압을 단일 PID로 처리하면 응답 특성이 달라 제어가 불안정해진다. 가압/감압 각각 독립적인 PID 채널을 구성하고, setpoint tracking algorithm을 적용해 3기압 Step Function 기준 0.67% overshoot를 달성했다.

---

## Discussion

본 연구는 IoT 기술을 통해 고압산소치료 시스템의 근본적인 한계를 극복하고, **병원 중심에서 개인 맞춤형 헬스케어로의 전환 가능성**을 제시했다.

검증 결과 식약처 인증 기기 대비 현저히 낮은 가압·감압 속도와 0.67%의 낮은 overshoot를 달성해 의료기기 수준의 안전성 기준을 충족했다. 응급 배기밸브 테스트에서도 예상치 못한 압력 변화에 안정적으로 대응함을 확인했다.

**한계 및 향후 과제**

- 비교 대상 기기 수가 제한적이어서 절대적 성능 평가에는 제약이 있음
- 실험이 통제된 환경에서 이루어져 다양한 실사용 환경에 대한 검증 필요
- 장기간 운용에 따른 시스템 안정성 및 신뢰성 평가 미실시
- 향후 실제 의료 프로토콜 적용 및 임상 검증으로 확장 가능
