import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager

font_manager.fontManager.addfont(r'C:\Windows\Fonts\malgun.ttf')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

C   = '#1a2035'
PAD = 0.04  # FancyBboxPatch round,pad 값 — 실제 경계는 nominal ± PAD

OUT = r'C:\Users\bromine\Desktop\Git Projects\bromine1997.github.io\static\images\algorithm\da_push_flowchart.png'

fig, ax = plt.subplots(figsize=(12, 10))
ax.set_xlim(0, 12)
ax.set_ylim(0, 11)
ax.axis('off')

# ── 헬퍼 ──────────────────────────────────────────────────────────

def arr(x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle='->', color=C, lw=1.8,
                                mutation_scale=18), zorder=5)

def seg(x0, y0, x1, y1):
    ax.plot([x0, x1], [y0, y1], color=C, lw=1.8, zorder=4)

def txt(x, y, s, fs=9.5):
    ax.text(x, y, s, ha='center', va='center', fontsize=fs, color=C, zorder=6)

def label(x, y, s):
    ax.text(x, y, s, ha='center', va='center', fontsize=8.5, color=C, zorder=6)

def make_oval(cx, cy, w, h):
    ax.add_patch(mpatches.Ellipse(
        (cx, cy), w, h, facecolor='white', edgecolor=C, lw=1.6, zorder=3))
    # Ellipse 실제 경계 = cx±w/2, cy±h/2
    return dict(cx=cx, cy=cy, top=cy+h/2, bot=cy-h/2, left=cx-w/2, right=cx+w/2)

def make_rect(cx, cy, w, h):
    ax.add_patch(mpatches.FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle=f'round,pad={PAD}',
        facecolor='white', edgecolor=C, lw=1.5, zorder=3))
    # FancyBboxPatch(round,pad) 실제 경계 = nominal ± PAD
    return dict(cx=cx, cy=cy,
                top=cy+h/2+PAD, bot=cy-h/2-PAD,
                left=cx-w/2-PAD, right=cx+w/2+PAD)

def make_diam(cx, cy, w, h):
    hw, hh = w/2, h/2
    ax.add_patch(plt.Polygon(
        [(cx, cy+hh), (cx+hw, cy), (cx, cy-hh), (cx-hw, cy)],
        closed=True, facecolor='white', edgecolor=C, lw=1.5, zorder=3))
    # 마름모 경계 = 꼭짓점 좌표
    return dict(cx=cx, cy=cy, top=cy+hh, bot=cy-hh, left=cx-hw, right=cx+hw)

# ── 레이아웃 좌표 ──────────────────────────────────────────────────

MX  = 3.5   # 메인(왼쪽) 수직축 x
RX  = 7.6   # YES 브랜치 x
ERX = 10.6  # 에러 박스 x

Y_START = 9.20
Y_COND1 = 7.90
Y_CAP2  = 7.90   # 조건1과 같은 y — 수평 YES 화살표
Y_RALL  = 6.55
Y_COND2 = 5.20
Y_ERR   = 5.20   # 조건2와 같은 y — 수평 YES 화살표
Y_DATA  = 3.85
Y_PUSH  = 2.50
Y_END   = 1.30

# ── 도형 그리기 ────────────────────────────────────────────────────

b_start = make_oval(MX, Y_START, w=3.0, h=0.65)
txt(MX, Y_START, 'da_push() 시작', fs=10.5)

d1 = make_diam(MX, Y_COND1, w=2.6, h=0.94)
txt(MX, Y_COND1, 'size == capacity?')

b_cap2 = make_rect(RX, Y_CAP2, w=3.0, h=0.62)
txt(RX, Y_CAP2, 'capacity × 2')

b_rall = make_rect(RX, Y_RALL, w=3.6, h=0.62)
txt(RX, Y_RALL, 'temp = realloc(data, capacity)', fs=9.0)

d2 = make_diam(RX, Y_COND2, w=2.4, h=0.90)
txt(RX, Y_COND2, 'temp == NULL?')

b_err = make_rect(ERX, Y_ERR, w=2.0, h=0.70)
txt(ERX, Y_ERR+0.13, '에러 반환', fs=9.2)
txt(ERX, Y_ERR-0.18, '(data 유지)', fs=8.8)

b_data = make_rect(RX, Y_DATA, w=3.0, h=0.62)
txt(RX, Y_DATA, 'data = temp')

b_push = make_rect(MX, Y_PUSH, w=3.2, h=0.62)
txt(MX, Y_PUSH, 'data[size++] = value')

b_end = make_oval(MX, Y_END, w=2.6, h=0.60)
txt(MX, Y_END, '반환', fs=10.5)

# ── 화살표 / 선 — 모두 make_* 반환 경계값 사용 ────────────────────

# 시작 → 조건1
arr(b_start['cx'], b_start['bot'], d1['cx'], d1['top'])

# 조건1 YES → capacity×2 (수평)
arr(d1['right'], d1['cy'], b_cap2['left'], b_cap2['cy'])
label((d1['right']+b_cap2['left'])/2, d1['cy']+0.22, 'YES')

# capacity×2 → realloc
arr(b_cap2['cx'], b_cap2['bot'], b_rall['cx'], b_rall['top'])

# realloc → 조건2
arr(b_rall['cx'], b_rall['bot'], d2['cx'], d2['top'])

# 조건2 YES → 에러 반환 (수평)
arr(d2['right'], d2['cy'], b_err['left'], b_err['cy'])
label((d2['right']+b_err['left'])/2, d2['cy']+0.22, 'YES')

# 조건2 NO → data=temp
arr(d2['cx'], d2['bot'], b_data['cx'], b_data['top'])
label(d2['cx']+0.35, (d2['bot']+b_data['top'])/2, 'NO')

# data=temp → 합류 (L자: 수직 ↓ → 수평 ← → 수직 ↓ 화살표)
JY = b_data['bot'] - 0.35
seg(b_data['cx'], b_data['bot'], b_data['cx'], JY)
seg(b_data['cx'], JY, b_push['cx'], JY)
arr(b_push['cx'], JY, b_push['cx'], b_push['top'])

# 조건1 NO → 수직 하강 → 합류점 JY
seg(d1['cx'], d1['bot'], d1['cx'], JY)
label(d1['cx']-0.38, d1['bot']-0.32, 'NO')

# data[size++] → 반환
arr(b_push['cx'], b_push['bot'], b_end['cx'], b_end['top'])

# ── ylim 콘텐츠 기반 설정 ──────────────────────────────────────────
ax.set_ylim(b_end['bot'] - 0.45, b_start['top'] + 0.50)

# ── 저장 ──────────────────────────────────────────────────────────
fig.savefig(OUT, dpi=160, bbox_inches='tight', pad_inches=0.20, facecolor='white')
plt.close(fig)
print(f'saved: {OUT}')
