---
title: "ATmega4809 Peripheral Driver"
date: 2024-01-01
hidemeta: false
showtoc: true
tocopen: true
comments: false
tags:
  - ATmega4809
  - C
  - 임베디드
summary: "연세대학교 마이크로컴퓨터시스템 수업 실습 프로젝트. 커스텀 PCB 직접 납땜 후 ATmega4809 주변장치 드라이버를 외부 라이브러리 없이 레지스터 수준에서 구현."
---

## 개요

연세대학교 의공학부 **마이크로컴퓨터시스템** 수업에서 진행한 실습 프로젝트. 회로도를 직접 해석하고 **납땜부터 펌웨어까지** 전 과정을 수행했다.

| 항목 | 내용 |
|------|------|
| 기간 | 학부 재학 중 |
| 소속 | 연세대학교 의공학부 수업 |
| 역할 | PCB 납땜 + 펌웨어 전체 구현 |
| GitHub | [atmega4809-project](https://github.com/bromine1997/atmega4809-project) |

---

## 주요 구현 내용

모든 드라이버를 **외부 라이브러리 없이 레지스터 직접 제어**로 구현했다.

| 모듈 | 구현 내용 |
|------|------|
| GPIO | 포트 방향 설정, 핀 입출력 제어 |
| UART | Baud rate 계산, 송수신 인터럽트 |
| SPI | Master mode, clock polarity/phase 설정 |
| I2C (TWI) | Start/stop condition, ACK/NACK 처리 |
| ADC | 기준 전압 설정, 변환 트리거, 결과 읽기 |
| Timer | CTC 모드, 인터럽트 |

---

## 기술 스택

- MCU: ATmega4809 (AVR, 8-bit, 48MHz)
- 보드: 커스텀 PCB (직접 납땜)
- 개발 환경: Microchip Studio
- 언어: C (Bare-metal)
- 제어 방식: 레지스터 직접 접근 (HAL 없음)
