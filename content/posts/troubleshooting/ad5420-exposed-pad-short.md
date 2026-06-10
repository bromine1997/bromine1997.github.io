---
title: "[AD5420] 만능기판 테스트에서 자꾸 발열이 생겼다"
date: 2026-06-10T12:30:00+09:00
draft: false
categories:
  - Embedded
tags:
  - AD5420
  - TSSOP
  - 노출패드
  - 납땜
  - 트러블슈팅
  - 만능기판
summary: "AD5420을 TSSOP 변환기판으로 만능기판에서 테스트하려다 전원 넣으면 발열이 심하게 생겼다. 원인은 배선이 아니라 칩 바닥 exposed pad였다."
---

AD5420을 만능기판에서 간단히 테스트해보려고 TSSOP 변환기판에 올렸다가 예상치 못한 데서 시간을 꽤 날렸다.

칩 다리 납땜하고, 전원이랑 SPI 배선 잡고 전원을 넣었는데 어딘가에서 열이 엄청 났다. 배선 다시 확인하고, 칩 다리 테스터기로 하나씩 찍어봐도 딱히 이상한 게 안 보였다. 혹시 불량 칩인가 싶어서 교체도 해봤는데 똑같이 발열이 생기는 거다.

한참 헤매다가 데이터시트를 다시 꺼내 패키지 그림을 봤더니, 칩 바닥에 뭔가가 있었다.

## 칩 바닥 Exposed Pad

AD5420은 TSSOP-24 EP 패키지다. EP가 붙은 패키지는 칩 아래쪽 가운데에 금속이 노출된 면이 있다.

![AD5420 패키지 — 아래쪽 칩에서 은색 사각형으로 보이는 게 바닥 노출 패드다](/images/troubleshooting/ad5420-exposed-pad.jpg)

데이터시트 27페이지 패키지 다이어그램을 보면 BOTTOM VIEW에 EXPOSED PAD가 명확하게 표시돼 있다.

![AD5420 데이터시트 Figure 42 — BOTTOM VIEW에 EXPOSED PAD 표기](/images/troubleshooting/ad5420-package-outline.png)

그리고 핀 설명표에는 이 paddle이 AGND, 즉 analog ground라고 나와 있다.

![AD5420 데이터시트 핀 설명표 — Paddle = AGND](/images/troubleshooting/ad5420-paddle-agnd.png)

이 exposed pad는 칩 내부에서 AGND에 연결되어 있다. 방열 목적도 겸하지만 전기적으로는 analog ground라서, 이게 PCB GND에 연결되지 않으면 아날로그 회로 전체가 불안정해진다.

TSSOP 변환기판을 쓰면 24개 다리는 pad에 딱 맞게 올라가는데, 바닥 exposed pad는 변환기판 PCB 표면 위에 그냥 올려진 상태가 된다. 기판 표면에 사용된 패턴이나 동박 잔류에 따라 exposed pad가 다른 신호선과 접촉해 의도치 않은 전류 경로가 생기거나, GND 연결 자체가 불안정해진다. 전류가 낮은 저항 경로로 몰리면 P = I²R에 의해 그 에너지가 열로 빠져나오기 때문에, 배선상 문제가 없어 보여도 발열이 심하게 나타날 수 있다.

## 해결

바닥 exposed pad를 GND에 납땜하면 된다.

만능기판에서 변환기판을 쓰는 경우에는, 칩을 변환기판에 올리기 전에 exposed pad 위치에 맞게 변환기판 뒷면에 구리 테이프나 도선을 붙여두고 GND에 연결해주는 방식으로 처리할 수 있다. 아니면 처음부터 exposed pad용 pad가 설계에 포함된 변환기판을 고르는 게 더 깔끔하다.

## PCB 아트웍 시 주의사항

만능기판 테스트를 넘어 실제 PCB를 설계할 때도 exposed pad를 빠뜨리면 같은 문제가 생긴다. footprint 작업 시 칩 다리 pad 외에 바닥 exposed pad 영역을 GND 동박과 연결되도록 별도로 잡아줘야 한다.

아래 PCB에서 U9, U14가 AD5420 소자인데, 칩 바닥 중앙에 exposed pad가 보인다.

![실제 PCB — U9, U14 (AD5420) 의 exposed pad](/images/troubleshooting/ad5420-pcb-exposed-pad.jpg)

납땜 순서도 중요하다. 칩 다리부터 납땜하면 나중에 바닥 exposed pad에 열을 가하기가 어려워진다. 열풍기로 먼저 납을 녹여 exposed pad를 GND에 붙인 다음, 칩이 자리를 잡으면 나머지 다리를 납땜하는 순서로 작업했다.

## 정리

| 항목 | 내용 |
|------|------|
| 증상 | 배선상 문제없어 보이는데 전원 인가 시 과도한 발열 발생 |
| 원인 | TSSOP-24 EP 패키지 바닥 exposed pad 미납땜 → GND 연결 불안정 |
| 해결 | Exposed pad를 PCB GND에 납땜 / EP 지원 변환기판 사용 |

만능기판에서 SMD 칩을 테스트할 때 EP 패키지 여부를 미리 확인해두는 게 좋다. 다리만 납땜하면 되는 줄 알았는데, 바닥 exposed pad 하나 빠진 게 발열로 이어질 줄은 몰랐다.
