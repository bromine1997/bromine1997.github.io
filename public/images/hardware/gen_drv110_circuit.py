"""
DRV110 소레노이드 드라이버 응용 회로도
figsize=(15, 11), xlim=0~15, ylim=-1~11.2
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib import font_manager
import os, shutil

font_manager.fontManager.addfont(r'C:\Windows\Fonts\malgun.ttf')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

C   = '#1a2035'
PAD = 0.08

TMP   = r'C:\Users\bromine\AppData\Local\Temp\diagram_preview.png'
FINAL = r'C:\Users\bromine\Desktop\Git Projects\bromine1997.github.io\static\images\hardware\drv110-circuit.png'

fig, ax = plt.subplots(figsize=(15, 11))
ax.set_xlim(0, 15)
ax.set_ylim(-1.0, 11.2)
ax.axis('off')


# ── 헬퍼 ───────────────────────────────────────────────────────────────
def make_rect(cx, cy, w, h, fc='white', ec=C, lw=1.5):
    ax.add_patch(mpatches.FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle=f'round,pad={PAD}',
        facecolor=fc, edgecolor=ec, lw=lw, zorder=3))
    return dict(cx=cx, cy=cy,
                top=cy + h/2 + PAD, bot=cy - h/2 - PAD,
                left=cx - w/2 - PAD, right=cx + w/2 + PAD)

def seg(x0, y0, x1, y1, lw=1.6):
    ax.plot([x0, x1], [y0, y1], color=C, lw=lw, zorder=4)

def txt(x, y, s, fs=9, bold=False, ha='center', va='center', color=C):
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs,
            color=color, fontweight='bold' if bold else 'normal', zorder=6)

def gnd_sym(cx, y, lw=1.6):
    ax.plot([cx - 0.55, cx + 0.55], [y,        y       ], color=C, lw=lw+0.2, zorder=6)
    ax.plot([cx - 0.38, cx + 0.38], [y - 0.15, y - 0.15], color=C, lw=lw,     zorder=6)
    ax.plot([cx - 0.20, cx + 0.20], [y - 0.30, y - 0.30], color=C, lw=lw,     zorder=6)


# ══════════════════════════════════════════════════════════════════════
# 좌표 (xlim=15로 공간 확보)
# 오른쪽 소자를 x=10.5 중심으로 배치 (IC_X2=7.5에서 충분한 간격)
# 수직 연결선은 IC_X2+PIN_LEN+0.5=8.6 이후로 배치
# ══════════════════════════════════════════════════════════════════════

# DRV110 IC
IC_X1, IC_X2 = 3.8, 7.5
IC_Y1, IC_Y2 = 2.8, 9.8
IC_CX = (IC_X1 + IC_X2) / 2   # 5.65
IC_CY = (IC_Y1 + IC_Y2) / 2   # 6.3

ax.add_patch(mpatches.FancyBboxPatch(
    (IC_X1, IC_Y1), IC_X2 - IC_X1, IC_Y2 - IC_Y1,
    boxstyle=f'round,pad={PAD}',
    facecolor='#f0f4f8', edgecolor=C, lw=2.2, zorder=2))
txt(IC_CX, IC_CY, 'DRV110', fs=22, bold=True)

# 핀
VIN_Y   = 9.0
EN_Y    = 7.8
GND_PY  = 6.5
OUT_Y   = 9.0
SENSE_Y = 7.5

PEAK_X = 4.3
HOLD_X = 5.1
KEEP_X = 5.9
OSC_X  = 6.7

PIN_LEN = 0.6

for y, label in [(VIN_Y, 'VIN'), (EN_Y, 'EN'), (GND_PY, 'GND')]:
    seg(IC_X1 - PIN_LEN, y, IC_X1, y)
    txt(IC_X1 - PIN_LEN - 0.12, y, label, fs=9, ha='right')

for y, label in [(OUT_Y, 'OUT'), (SENSE_Y, 'SENSE')]:
    seg(IC_X2, y, IC_X2 + PIN_LEN, y)
    txt(IC_X2 + PIN_LEN + 0.12, y, label, fs=9, ha='left')

for x, label in [(PEAK_X, 'PEAK'), (HOLD_X, 'HOLD'), (KEEP_X, 'KEEP'), (OSC_X, 'OSC')]:
    seg(x, IC_Y1, x, IC_Y1 - PIN_LEN)
    txt(x, IC_Y1 - PIN_LEN - 0.18, label, fs=8, va='top')


# ══════════════════════════════════════════════════════════════════════
# 전원부
# ══════════════════════════════════════════════════════════════════════
VS_Y  = 10.8
RS_CX = 1.5
RS_CY = 9.0
RS_W  = 1.8
RS_H  = 0.7

txt(RS_CX, VS_Y, 'VS (24V)', fs=11, bold=True)
rs_box = make_rect(RS_CX, RS_CY, RS_W, RS_H)
txt(RS_CX, RS_CY, 'RS (9.1kΩ)', fs=9)
txt(RS_CX + RS_W/2 + 0.5, RS_CY + 0.45, 'C1', fs=9)
seg(RS_CX, VS_Y - 0.18, RS_CX, rs_box['top'])


# ══════════════════════════════════════════════════════════════════════
# 오른쪽 소자 (x=10.5 중심)
# ── 중요 설계 ──
#   Ls  : cx=10.5, cy=9.3, w=2.2, h=1.0  → left=9.38, right=11.62
#   M1  : cx=10.5, cy=6.5, w=2.2, h=1.6  → left=9.38, right=11.62, top=7.38, bot=5.62
#   R2  : cx=10.5, cy=3.8, w=2.2, h=1.0  → left=9.38, right=11.62
#   D1  : cx=13.0, cy=7.9, w=0.7, h=2.4
#
#   수직 버스 x=M1_CX=10.5 (Ls bot~M1 top, M1 bot~R2 top)
#   OUT→Gate 경로 x=8.8 (IC_X2+PIN_LEN=8.1 이후, M1 left=9.38 이전)
#   SENSE→R2 경로: SENSE(8.1, 7.5) → x=9.6 → y=R2_CY 로 R2 left 연결
# ══════════════════════════════════════════════════════════════════════
LS_CX, LS_CY, LS_W, LS_H = 10.5, 9.3, 2.2, 1.0
M1_CX, M1_CY, M1_W, M1_H = 10.5, 6.5, 2.2, 1.6
R2_CX, R2_CY, R2_W, R2_H = 10.5, 3.8, 2.2, 1.0
D1_CX, D1_CY, D1_W, D1_H = 13.0, 7.9, 0.7, 2.4

ls = make_rect(LS_CX, LS_CY, LS_W, LS_H)
m1 = make_rect(M1_CX, M1_CY, M1_W, M1_H)
r2 = make_rect(R2_CX, R2_CY, R2_W, R2_H)
d1 = make_rect(D1_CX, D1_CY, D1_W, D1_H)

txt(LS_CX, LS_CY, 'Ls\n(솔레노이드)', fs=9)
txt(M1_CX, M1_CY, 'M1\n(MOSFET)',    fs=9)
txt(R2_CX, R2_CY, 'RSENSE\n(1Ω)',    fs=9)
txt(D1_CX, D1_CY, 'D1',              fs=9)

# 계산값:
# ls['bot'] = 9.3 - 0.5 - 0.08 = 8.72
# m1['top'] = 6.5 + 0.8 + 0.08 = 7.38
# m1['bot'] = 6.5 - 0.8 - 0.08 = 5.62
# r2['top'] = 3.8 + 0.5 + 0.08 = 4.38
# m1['left'] = 10.5 - 1.1 - 0.08 = 9.32
# r2['left'] = 10.5 - 1.1 - 0.08 = 9.32


# ══════════════════════════════════════════════════════════════════════
# 아래쪽 소자
# ══════════════════════════════════════════════════════════════════════
BOT_CY = 1.0
BOT_H  = 0.72
BOT_W  = 0.70

rpeak = make_rect(PEAK_X, BOT_CY, BOT_W, BOT_H)
rhold = make_rect(HOLD_X, BOT_CY, BOT_W, BOT_H)
ckeep = make_rect(KEEP_X, BOT_CY, BOT_W, BOT_H)
rosc  = make_rect(OSC_X,  BOT_CY, BOT_W, BOT_H)

for cx_v, l1, l2 in [
    (PEAK_X, 'RPEAK', '200kΩ'),
    (HOLD_X, 'RHOLD', '100kΩ'),
    (KEEP_X, 'CKEEP', '220nF'),
    (OSC_X,  'ROSC',  '160kΩ'),
]:
    txt(cx_v, BOT_CY + 0.12, l1, fs=7.5)
    txt(cx_v, BOT_CY - 0.12, l2, fs=7.5)


# ══════════════════════════════════════════════════════════════════════
# 연결선
# ══════════════════════════════════════════════════════════════════════
out_pin_end = IC_X2 + PIN_LEN   # 8.1

# (A) RS → VIN (수평)
seg(rs_box['right'], VIN_Y, IC_X1 - PIN_LEN, VIN_Y)

# (B) OUT → M1 Gate (왼쪽 측면)
# 경로: OUT(8.1, 9.0) → 수평(8.8, 9.0) → 수직(8.8, 6.5=M1_CY) → m1['left'](9.32)
# x=8.8은 ls['left']=9.32보다 왼쪽 → Ls 박스 밖으로 통과 OK
GATE_X = 8.8
seg(out_pin_end, OUT_Y, GATE_X, OUT_Y)
seg(GATE_X, OUT_Y, GATE_X, M1_CY)
seg(GATE_X, M1_CY, m1['left'], M1_CY)

# (C) Ls 하단 ↔ M1 Drain(top) 수직
seg(M1_CX, ls['bot'], M1_CX, m1['top'])

# (D) M1 Source(bot) ↔ RSENSE(top) 수직
seg(M1_CX, m1['bot'], M1_CX, r2['top'])

# (E) SENSE → RSENSE 노드 (T형)
# SENSE(8.1, 7.5) → 수평(9.32=r2['left'] 이전) → 꺾어 → R2 상단 노드 합류
# R2_CY=3.8 에서 M1_CX=10.5 수직선(m1['bot']~r2['top'])에 합류
# 경로: (8.1, 7.5) → (9.0, 7.5) → (9.0, 5.0) → (M1_CX, 5.0)
# M1_CX에서 5.0→r2['top']=4.38 으로 수직 연장
# 5.0은 m1['bot']=5.62보다 아래이고 r2['top']=4.38보다 위 → T형 합류 O
SENSE_DROP_X = 9.0    # ls['left']=9.32보다 왼쪽 → 박스 외부
SENSE_JY     = 4.9    # m1['bot']=5.62보다 아래, r2['top']=4.38보다 위
seg(out_pin_end, SENSE_Y, SENSE_DROP_X, SENSE_Y)
seg(SENSE_DROP_X, SENSE_Y, SENSE_DROP_X, SENSE_JY)
seg(SENSE_DROP_X, SENSE_JY, M1_CX, SENSE_JY)
# SENSE_JY에서 r2['top']까지 수직 (M1 bot~SENSE_JY 는 (D)에서 처리)
# 실제로 (D)는 m1['bot']~r2['top']이므로 SENSE_JY=4.9가 그 사이에 들어감
# (D) 수직선을 분할: m1['bot']~SENSE_JY 와 SENSE_JY~r2['top']
# 이미 연속으로 그어진 선에 T형으로 합류하므로 별도 선 추가 불필요

# (F) Ls 상단 → VS 전원 레일
seg(LS_CX, ls['top'], LS_CX, VS_Y)
seg(RS_CX, VS_Y, LS_CX, VS_Y)

# (G) D1 플라이백
seg(ls['right'], LS_CY, D1_CX, LS_CY)
seg(D1_CX, LS_CY, D1_CX, d1['top'])
seg(m1['right'], M1_CY, D1_CX, M1_CY)
seg(D1_CX, M1_CY, D1_CX, d1['bot'])

# (H) 하단 핀 → 박스 상단
for px, box in [(PEAK_X, rpeak), (HOLD_X, rhold), (KEEP_X, ckeep), (OSC_X, rosc)]:
    seg(px, IC_Y1 - PIN_LEN, px, box['top'])

# (I) GND 공통선
GND_LY = 0.22
for bx, box in [(PEAK_X, rpeak), (HOLD_X, rhold), (KEEP_X, ckeep), (OSC_X, rosc)]:
    seg(bx, box['bot'], bx, GND_LY)
seg(PEAK_X, GND_LY, OSC_X, GND_LY)

seg(R2_CX, r2['bot'], R2_CX, GND_LY)
seg(OSC_X, GND_LY, R2_CX, GND_LY)

gnd_lx = IC_X1 - PIN_LEN - 0.15
seg(IC_X1 - PIN_LEN, GND_PY, gnd_lx, GND_PY)
seg(gnd_lx, GND_PY, gnd_lx, GND_LY)
seg(gnd_lx, GND_LY, PEAK_X, GND_LY)

gnd_sym_x = (PEAK_X + R2_CX) / 2
gnd_sym(gnd_sym_x, GND_LY)
txt(gnd_sym_x, GND_LY - 0.55, 'GND', fs=9.5, bold=True)

txt(IC_X1 - PIN_LEN - 0.45, EN_Y, 'EN\n(제어)', fs=8.5, ha='right')


# ══════════════════════════════════════════════════════════════════════
# 저장
# ══════════════════════════════════════════════════════════════════════
fig.savefig(TMP, dpi=160, bbox_inches='tight', pad_inches=0.20, facecolor='white')
plt.close(fig)
print(f'TMP saved: {TMP}')
