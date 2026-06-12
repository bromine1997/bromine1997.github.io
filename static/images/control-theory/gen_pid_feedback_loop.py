import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Ellipse
import numpy as np
from matplotlib import font_manager
import os, shutil

font_manager.fontManager.addfont(r'C:\Windows\Fonts\malgun.ttf')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

C   = '#1a2035'
PAD = 0.04

TMP   = r'C:\Users\bromine\AppData\Local\Temp\diagram_preview.png'
FINAL = r'C:\Users\bromine\Desktop\Git Projects\bromine1997.github.io\static\images\control-theory\pid-feedback-loop.png'

# ── 캔버스 ──────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 5))
ax.set_xlim(0, 13)
ax.set_ylim(0.5, 4.5)
ax.axis('off')

# ── 상수 ────────────────────────────────────────────────────────────
Y_MAIN  = 2.8        # 메인 라인 y
SJ_X    = 1.8        # 합산 접합점 center x
SJ_Y    = Y_MAIN

PID_CX, PID_CY = 4.5,  Y_MAIN
PID_W,  PID_H  = 2.4,  1.0

PLANT_CX, PLANT_CY = 8.2,  Y_MAIN
PLANT_W,  PLANT_H  = 2.8,  1.2

OUT_X = 11.2   # 출력 분기점 x

# ── 헬퍼 ────────────────────────────────────────────────────────────
def make_rect(cx, cy, w, h, lw=1.5):
    ax.add_patch(mpatches.FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle=f'round,pad={PAD}',
        facecolor='white', edgecolor=C, lw=lw, zorder=3))
    return dict(cx=cx, cy=cy,
                top=cy + h/2 + PAD, bot=cy - h/2 - PAD,
                left=cx - w/2 - PAD, right=cx + w/2 + PAD)

def arr(x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle='->', color=C, lw=1.8,
                                mutation_scale=18), zorder=5)

def seg(x0, y0, x1, y1):
    ax.plot([x0, x1], [y0, y1], color=C, lw=1.8, zorder=4)

def dot(x, y, r=0.06):
    ax.add_patch(plt.Circle((x, y), r, color=C, zorder=6))

# ── 블록 박스 ────────────────────────────────────────────────────────
pid   = make_rect(PID_CX,   PID_CY,   PID_W,   PID_H)
plant = make_rect(PLANT_CX, PLANT_CY, PLANT_W, PLANT_H)

# ── 박스 내부 텍스트 ──────────────────────────────────────────────────
ax.text(PID_CX, PID_CY, 'PID 제어기',
        ha='center', va='center', fontsize=15, color=C, zorder=4)

ax.text(PLANT_CX, PLANT_CY + 0.18, '밸브 → 유량',
        ha='center', va='center', fontsize=14, color=C, zorder=4)
ax.text(PLANT_CX, PLANT_CY - 0.18, '→ 챔버 압력',
        ha='center', va='center', fontsize=14, color=C, zorder=4)

# ── 합산 접합점 (진원 — Ellipse + 종횡비 보정) ──────────────────────
# 1. canvas draw로 레이아웃 확정 (Ellipse 추가 전)
fig.canvas.draw()

# 2. 실제 픽셀 비율 계산
ax_bbox   = ax.get_window_extent()
x_range   = ax.get_xlim()[1] - ax.get_xlim()[0]
y_range   = ax.get_ylim()[1] - ax.get_ylim()[0]
px_per_xu = ax_bbox.width  / x_range
px_per_yu = ax_bbox.height / y_range

# 3. 화면에서 원형으로 보이는 반지름 (픽셀 기준)
R_px = 36

# 4. data 좌표계 반지름으로 역산
r_x = R_px / px_per_xu
r_y = R_px / px_per_yu

# 5. Ellipse로 그리기 — 화면에서는 정원으로 보임
sj = Ellipse((SJ_X, SJ_Y), width=2*r_x, height=2*r_y,
             fc='white', ec=C, lw=1.8, zorder=3)
ax.add_patch(sj)

# 6. +/- 기호 (진원 기준으로 내부에 배치)
# "+" : 위에서 들어오는 forward path → 원 상단 내부 (12시 방향)
ax.text(SJ_X, SJ_Y + r_y * 0.52, '+',
        ha='center', va='center', fontsize=17, color=C, zorder=4)

# "-" : 아래에서 들어오는 feedback → 원 하단 내부 (6시 방향)
ax.text(SJ_X, SJ_Y - r_y * 0.52, '-',
        ha='center', va='center', fontsize=19, color=C, zorder=4,
        fontweight='bold')

# ── 메인 신호선 ──────────────────────────────────────────────────────
# r(t) → 합산 접합점 (왼쪽에서 진입)
arr(0.2, Y_MAIN, SJ_X - r_x - 0.05, Y_MAIN)

# 합산 접합점 → PID (e(t), 오른쪽으로 나감)
arr(SJ_X + r_x + 0.05, Y_MAIN, pid['left'], Y_MAIN)

# PID → Plant (u(t))
arr(pid['right'], Y_MAIN, plant['left'], Y_MAIN)

# Plant → 출력 분기점
seg(plant['right'], Y_MAIN, OUT_X, Y_MAIN)
arr(OUT_X, Y_MAIN, OUT_X + 0.9, Y_MAIN)

# 분기점 dot
dot(OUT_X, Y_MAIN)

# ── 피드백 경로 ──────────────────────────────────────────────────────
FB_Y_BOT = 1.2   # 피드백 하단 라인 y

# 출력 분기점 → 아래
seg(OUT_X, Y_MAIN, OUT_X, FB_Y_BOT)

# 아래 → 합산 접합점 하단 (수평)
seg(OUT_X, FB_Y_BOT, SJ_X, FB_Y_BOT)

# 합산 접합점 하단으로 화살표 (수직 — r_y 기준 끝점)
arr(SJ_X, FB_Y_BOT, SJ_X, SJ_Y - r_y - 0.05)

# ── 레이블 ──────────────────────────────────────────────────────────
ax.text(0.15, Y_MAIN + 0.35, '목표압력', ha='center', va='bottom', fontsize=15, color=C)
ax.text(0.15, Y_MAIN + 0.05, 'r(t)',    ha='center', va='bottom', fontsize=15, color=C)

ax.text(12.0, Y_MAIN + 0.35, '실제압력', ha='center', va='bottom', fontsize=15, color=C)
ax.text(12.0, Y_MAIN + 0.05, 'y(t)',    ha='center', va='bottom', fontsize=15, color=C)

ax.text((SJ_X + r_x + pid['left']) / 2, Y_MAIN + 0.15, 'e(t)',
        ha='center', va='bottom', fontsize=13, color=C)
ax.text((pid['right'] + plant['left']) / 2, Y_MAIN + 0.15, 'u(t)',
        ha='center', va='bottom', fontsize=13, color=C)

ax.text((SJ_X + OUT_X) / 2, FB_Y_BOT - 0.22, '압력 센서 피드백',
        ha='center', va='top', fontsize=14, color=C)

# ── 저장 ────────────────────────────────────────────────────────────
fig.savefig(TMP, dpi=160, bbox_inches='tight', pad_inches=0.25, facecolor='white')
plt.close(fig)
print('saved TMP:', TMP)
