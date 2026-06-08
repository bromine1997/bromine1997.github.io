---
title: "[ATMEGA4809] MCU 소개 및 개발환경 설정"
date: 2026-04-29T20:35:00+09:00
draft: false
categories:
  - Embedded
tags:
  - ATmega
  - ATmega4809
  - C언어
  - Microchip Studio
  - 개발환경
  - AVR
summary: "본격적인 코드리뷰에 앞서 제가 사용한 ATmega4809 MCU와 Microchip Studio 개발환경을 간단하게 소개합니다."
---

첫 번째 글은 본격적인 코드리뷰에 들어가기 전에, 제가 사용한 MCU와 개발환경을 간단하게 정리해보려고 합니다.

개발을 할 때마다 느끼는 거지만 개발환경 설정하는 게 정말 귀찮고 어렵습니다. 처음이면 아무것도 모르는데, 하다 보면 익숙해지더라고요. 한번 같이 친해져봅시다.

## 사용한 MCU: ATmega4809

보통 펌웨어를 처음 배우면 AVR 계열 MCU로 많이 학습합니다. 그 중에서도 ATmega128이 제일 많이 사용되는 것 같습니다. 저는 그 중 **ATmega4809** 시리즈를 사용했습니다.

보통 MCU 뒤에 붙는 숫자들은 포트의 수나 메모리 크기 등 스펙을 의미합니다.

<!-- 이미지 삽입 위치: 실제 사용한 ATmega4809 개발 보드 사진 -->
![ATmega4809 개발 보드](/images/atmega4809/atmega4809-board.jpg)
*실제 사용한 ATmega4809 개발 보드*

## 개발환경: Microchip Studio

개발환경은 **Microchip Studio**를 사용했습니다.

AVR 계열 MCU를 다룰 때 가장 흔하게 쓰이는 IDE입니다. 프로젝트 생성부터 빌드, 디버깅까지 비교적 깔끔한 UI를 가지고 있습니다. 개인적으로는 꽤 만족스러운 환경이었습니다.

특히 디버깅 환경이 편해서 문제를 찾기 수월했습니다.

<!-- 이미지 삽입 위치: Microchip Studio 화면 캡처 -->
![Microchip Studio](/images/atmega4809/microchip-studio.png)
*Microchip Studio IDE 화면*

