import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager

font_manager.fontManager.addfont(r'C:\Windows\Fonts\malgun.ttf')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

C = '#1a2035'
GRAY = '#888'
PAD = 0.10   # FancyBboxPatch pad=0.08 + 약간의 gap: 화살표가 박스 안에 묻히지 않도록
OUT = r'C:\Users\bromine\Desktop\Git Projects\bromine1997.github.io\static\images\hardware\power-supply-overview.png'

fig, ax = plt.subplots(figsize=(18, 5.5))
ax.set_xlim(0, 18)
ax.set_ylim(0.2, 5.5)
ax.axis('off')

BW = 1.1
BH = 0.65
ISO_BW = 2.8
BOUNDARY_X = 4.8


def box_right(cx, bw=None):
    return cx + (bw or BW) / 2 + PAD

def box_left(cx, bw=None):
    return cx - (bw or BW) / 2 - PAD


def box(cx, cy, label, sublabel=None, bw=None, ec=C, fc='white', lw=1.4):
    bw = bw or BW
    rect = mpatches.FancyBboxPatch(
        (cx - bw / 2, cy - BH / 2), bw, BH,
        boxstyle="round,pad=0.08",
        linewidth=lw, edgecolor=ec, facecolor=fc, zorder=3,
    )
    ax.add_patch(rect)
    dy = 0.10 if sublabel else 0
    ax.text(cx, cy + dy, label, ha='center', va='center',
            fontsize=9.5, color=C, zorder=4)
    if sublabel:
        ax.text(cx, cy - 0.18, sublabel, ha='center', va='center',
                fontsize=8, color=GRAY, zorder=4)


def arr(x0, y0, x1, y1, color=C, lw=1.8, ms=18):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw,
                                mutation_scale=ms),
                zorder=5)


# ── LEFT: TINKERBOARD 측 ──────────────────────────────────────────────
box(1.1, 4.0, '상용전원')
arr(box_right(1.1), 4.0, box_left(2.8), 4.0)
box(2.8, 4.0, 'TINKERBOARD', sublabel='(SBC)')

ax.text(2.8, 3.15, '5V  /  3.3V',
        ha='center', va='center', fontsize=9, color=C,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#f0f0f0', edgecolor=GRAY, lw=1))

# bus: TINKERBOARD 박스 아래 중심 → 마지막 절연 소자 y까지만
iso_ys = [2.9, 2.0, 1.1]
bus_x  = 2.8
bus_top = 4.0 - BH / 2 - PAD   # TINKERBOARD 박스 아래쪽 끝 + gap
bus_bot = iso_ys[-1]            # 마지막 분기점에서 딱 끊음
ax.plot([bus_x, bus_x], [bus_top, bus_bot], color=GRAY, lw=1.5, zorder=4)

# T분기 접합점 dot
for cy in iso_ys:
    ax.plot(bus_x, cy, 'o', color=GRAY, markersize=6,
            markerfacecolor=GRAY, zorder=6)

# ── BOUNDARY ─────────────────────────────────────────────────────────
ax.plot([BOUNDARY_X, BOUNDARY_X], [0.4, 5.1], color=GRAY, lw=1.5, ls='--', zorder=2)
ax.text(BOUNDARY_X, 5.2, '절연 경계', ha='center', va='bottom', fontsize=9, color=C,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=C, lw=1.2))

# ── RIGHT: PCB 전원 체인 ──────────────────────────────────────────────
chain_y = 4.0
rx      = [6.0, 7.6, 9.2, 10.9, 12.5, 14.1, 15.8]
rlabels = ['220V AC', '의료용 SMPS', '24V', 'VR10S05', '5V', 'MIC5233', '3.3V']
rsubs   = [None,      None,          None,  '(스위칭)', None, '(LDO)',   None]

for x, lbl, sub in zip(rx, rlabels, rsubs):
    box(x, chain_y, lbl, sub)

for i in range(len(rx) - 1):
    arr(box_right(rx[i]), chain_y, box_left(rx[i + 1]), chain_y)

ax.text(10.9, 4.85, 'PCB 전원 체인 (센서·밸브 측)',
        ha='center', va='center', fontsize=9, color=C)

# ── ISOLATORS + 목적지 ────────────────────────────────────────────────
iso_labels = ['ADUM1400 / ADUM1200', 'ISO7421', 'VO1400AEFTR']
iso_subs   = ['SPI 신호 절연', 'UART 신호 절연', 'DRV110 EN 절연 (포토커플러)']
dst_labels = ['AD5420 / MAX1032', 'UART RX / TX', '솔레노이드 밸브']
DST_BW = 2.4
DST_X  = 9.8

for cy, lbl, sub, dst in zip(iso_ys, iso_labels, iso_subs, dst_labels):
    # 절연 소자 박스
    rect = mpatches.FancyBboxPatch(
        (BOUNDARY_X - ISO_BW / 2, cy - BH / 2), ISO_BW, BH,
        boxstyle="round,pad=0.08",
        linewidth=1.4, edgecolor=C, facecolor='white', zorder=3,
    )
    ax.add_patch(rect)
    ax.text(BOUNDARY_X, cy + 0.10, lbl, ha='center', va='center',
            fontsize=9.5, color=C, fontweight='bold', zorder=4)
    ax.text(BOUNDARY_X, cy - 0.17, sub, ha='center', va='center',
            fontsize=8, color=GRAY, zorder=4)

    # 왼쪽: bus dot → 절연 소자 왼쪽 끝 바깥
    iso_left  = BOUNDARY_X - ISO_BW / 2 - PAD
    arr(bus_x, cy, iso_left, cy, color=GRAY, lw=1.5, ms=16)

    # 오른쪽: 절연 소자 오른쪽 끝 바깥 → 목적지 박스 왼쪽 끝 바깥
    iso_right = BOUNDARY_X + ISO_BW / 2 + PAD
    dst_left  = DST_X - DST_BW / 2 - PAD
    arr(iso_right, cy, dst_left, cy)

    # 목적지 박스
    dst_rect = mpatches.FancyBboxPatch(
        (DST_X - DST_BW / 2, cy - BH / 2), DST_BW, BH,
        boxstyle="round,pad=0.08",
        linewidth=1.2, edgecolor=GRAY, facecolor='#f5f5f5', zorder=3,
    )
    ax.add_patch(dst_rect)
    ax.text(DST_X, cy, dst, ha='center', va='center',
            fontsize=9, color=C, zorder=4)

# ── 도메인 레이블 ─────────────────────────────────────────────────────
ax.text(2.2, 0.55, 'TINKERBOARD 측',
        ha='center', va='center', fontsize=8.5, color=C,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#f5f5f5', edgecolor=GRAY, lw=1))
ax.text(11.0, 0.55, '센서 · 밸브 측 (PCB)',
        ha='center', va='center', fontsize=8.5, color=C,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#f5f5f5', edgecolor=GRAY, lw=1))

fig.savefig(OUT, dpi=160, bbox_inches='tight', pad_inches=0.20, facecolor='white')
plt.close(fig)
print('saved:', OUT)
