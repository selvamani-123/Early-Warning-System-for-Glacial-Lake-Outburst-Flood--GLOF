import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np
import os

os.makedirs('d:/GLOF Sentinel/Backend/report_assets', exist_ok=True)

# ---- DATA (actual run results) ----
classes = ['CRITICAL', 'HIGH', 'LOW', 'MODERATE']
cm = np.array([
    [1, 0, 0, 0],
    [0, 5, 0, 1],
    [0, 0, 1193, 0],
    [0, 0, 0, 335]
])

feat_imp = {
    'rainfall_intensity': 0.2525,
    'rainfall': 0.2488,
    'water_accumulation_score': 0.2159,
    'seasonal_index': 0.0957,
    'temperature': 0.0696,
    'melt_rate_index': 0.0676,
    'elevation': 0.0178,
    'glacier_area': 0.0156,
    'lake_area': 0.0124,
    'humidity': 0.0041
}

class_dist_full = {'LOW': 5965, 'MODERATE': 1672, 'HIGH': 32, 'CRITICAL': 3}
train_dist = {'LOW': 4772, 'MODERATE': 1337, 'HIGH': 116, 'CRITICAL': 52}
test_dist = {'LOW': 1193, 'MODERATE': 335, 'HIGH': 6, 'CRITICAL': 1}

cv_scores = [0.9968, 1.0000, 0.9992, 0.9984, 0.9992]

COLORS = {
    'CRITICAL': '#FF2D55',
    'HIGH': '#FF9500',
    'MODERATE': '#FFD60A',
    'LOW': '#30D158'
}

BG = '#0A0E1A'
CARD_BG = '#111827'
TEXT = '#E2E8F0'
ACCENT = '#6366F1'
GRID = '#1E2A3A'

# ===================== FIGURE 1: Confusion Matrix =====================
fig, ax = plt.subplots(figsize=(8, 6.5), facecolor=BG)
ax.set_facecolor(BG)

norm_cm = cm.astype(float)
for i in range(len(classes)):
    row_sum = cm[i].sum()
    if row_sum > 0:
        norm_cm[i] = cm[i] / row_sum

im = ax.imshow(norm_cm, cmap='Blues', vmin=0, vmax=1)

for i in range(len(classes)):
    for j in range(len(classes)):
        val = cm[i][j]
        pct = norm_cm[i][j]
        color = 'white' if pct > 0.5 else '#CBD5E1'
        ax.text(j, i, f'{val}\n({pct:.0%})', ha='center', va='center',
                fontsize=11, color=color, fontweight='bold')

ax.set_xticks(range(len(classes)))
ax.set_yticks(range(len(classes)))
ax.set_xticklabels(classes, color=TEXT, fontsize=11)
ax.set_yticklabels(classes, color=TEXT, fontsize=11)
ax.set_xlabel('Predicted Label', color=TEXT, fontsize=12, labelpad=10)
ax.set_ylabel('True Label', color=TEXT, fontsize=12, labelpad=10)
ax.set_title('Confusion Matrix — Test Set (n=1,535)', color=TEXT, fontsize=14, fontweight='bold', pad=15)
ax.tick_params(colors=TEXT)
for spine in ax.spines.values():
    spine.set_edgecolor(GRID)
cbar = plt.colorbar(im, ax=ax)
cbar.ax.yaxis.set_tick_params(color=TEXT)
plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TEXT)
cbar.set_label('Normalized Rate', color=TEXT, fontsize=10)

plt.tight_layout()
plt.savefig('d:/GLOF Sentinel/Backend/report_assets/confusion_matrix.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print('Saved confusion_matrix.png')

# ===================== FIGURE 2: Feature Importance =====================
fig, ax = plt.subplots(figsize=(10, 6.5), facecolor=BG)
ax.set_facecolor(BG)

features = list(feat_imp.keys())
values = list(feat_imp.values())

feature_labels = {
    'rainfall_intensity': 'Rainfall Intensity (derived)',
    'rainfall': 'Rainfall — mm (real)',
    'water_accumulation_score': 'Water Accumulation Score (derived)',
    'seasonal_index': 'Seasonal Index (derived)',
    'temperature': 'Temperature — °C (real)',
    'melt_rate_index': 'Melt Rate Index (derived)',
    'elevation': 'Elevation — m (real)',
    'glacier_area': 'Glacier Area — km² (real)',
    'lake_area': 'Lake Area — km² (real)',
    'humidity': 'Humidity — % (semi-synthetic)'
}

bar_colors = ['#6366F1' if v > 0.15 else '#818CF8' if v > 0.05 else '#A5B4FC' for v in values]
bars = ax.barh([feature_labels.get(f, f) for f in features], values, color=bar_colors, height=0.65, edgecolor='none')

for bar, val in zip(bars, values):
    ax.text(val + 0.004, bar.get_y() + bar.get_height()/2, f'{val:.4f}',
            va='center', ha='left', color=TEXT, fontsize=9.5)

ax.set_xlabel('Feature Importance Score (Gini)', color=TEXT, fontsize=11)
ax.set_title('Feature Importance — Random Forest Classifier', color=TEXT, fontsize=14, fontweight='bold')
ax.tick_params(colors=TEXT, labelsize=9.5)
ax.set_xlim(0, max(values) * 1.25)
ax.invert_yaxis()
ax.xaxis.grid(True, color=GRID, linestyle='--', alpha=0.5)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_edgecolor(GRID)

plt.tight_layout()
plt.savefig('d:/GLOF Sentinel/Backend/report_assets/feature_importance.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print('Saved feature_importance.png')

# ===================== FIGURE 3: Class Distribution =====================
fig, axes = plt.subplots(1, 3, figsize=(16, 5.5), facecolor=BG)
fig.suptitle('Class Distribution — GLOF Risk Labels', color=TEXT, fontsize=15, fontweight='bold', y=1.02)

datasets = [
    ('Full Dataset\n(7,672 records)', class_dist_full),
    ('Training Set\n(6,277 augmented)', train_dist),
    ('Test Set\n(1,535 records)', test_dist)
]

for ax, (title, dist) in zip(axes, datasets):
    ax.set_facecolor(BG)
    labels = list(dist.keys())
    sizes = list(dist.values())
    colors_pie = [COLORS[l] for l in labels]
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct='%1.1f%%', colors=colors_pie,
        startangle=90, wedgeprops={'edgecolor': BG, 'linewidth': 3}, pctdistance=0.78
    )
    for text in texts:
        text.set_color(TEXT); text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_color('white'); autotext.set_fontsize(9); autotext.set_fontweight('bold')
    ax.set_title(title, color=TEXT, fontsize=11, fontweight='bold', pad=12)
    ax.text(0, -1.35, f'n = {sum(sizes):,}', ha='center', color='#94A3B8', fontsize=9)

plt.tight_layout()
plt.savefig('d:/GLOF Sentinel/Backend/report_assets/class_distribution.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print('Saved class_distribution.png')

# ===================== FIGURE 4: Accuracy + CV Dashboard =====================
fig = plt.figure(figsize=(14, 5), facecolor=BG)
gs = gridspec.GridSpec(1, 2, figure=fig, width_ratios=[1.3, 1], wspace=0.3)

# Left: metric cards
ax_left = fig.add_subplot(gs[0])
ax_left.set_facecolor(BG)
ax_left.axis('off')
ax_left.set_title('Model Performance Summary', color=TEXT, fontsize=13, fontweight='bold', pad=10)

metrics = [
    ('Train Accuracy', '100.00%', '#30D158', 1.0000),
    ('Test Accuracy', '99.93%', '#6366F1', 0.9993),
    ('CV Mean (5-fold)', '99.87%', '#0EA5E9', 0.9987),
]
for i, (label, value, color, score) in enumerate(metrics):
    y_pos = 0.78 - i * 0.33
    card = mpatches.FancyBboxPatch((0.02, y_pos - 0.13), 0.95, 0.28,
        boxstyle='round,pad=0.015', facecolor=CARD_BG, edgecolor=color,
        linewidth=1.5, transform=ax_left.transAxes)
    ax_left.add_patch(card)
    ax_left.text(0.25, y_pos + 0.05, value, ha='center', va='center',
        transform=ax_left.transAxes, fontsize=18, color=color, fontweight='bold')
    ax_left.text(0.25, y_pos - 0.06, label, ha='center', va='center',
        transform=ax_left.transAxes, fontsize=9, color='#94A3B8')
    bg_r = mpatches.FancyBboxPatch((0.5, y_pos - 0.04), 0.44, 0.07,
        boxstyle='round,pad=0.005', facecolor='#1E2A3A', edgecolor='none',
        transform=ax_left.transAxes)
    ax_left.add_patch(bg_r)
    fill_r = mpatches.FancyBboxPatch((0.5, y_pos - 0.04), 0.44 * score, 0.07,
        boxstyle='round,pad=0.005', facecolor=color, edgecolor='none',
        transform=ax_left.transAxes, alpha=0.85)
    ax_left.add_patch(fill_r)
    ax_left.text(0.95, y_pos - 0.005, f'{score*100:.2f}%', ha='right', va='center',
        transform=ax_left.transAxes, fontsize=8, color=color)

# Right: CV fold scores bar
ax_right = fig.add_subplot(gs[1])
ax_right.set_facecolor(BG)
fold_labels = [f'Fold {i+1}' for i in range(5)]
fold_colors = ['#6366F1', '#818CF8', '#6366F1', '#818CF8', '#6366F1']
bars = ax_right.bar(fold_labels, [s * 100 for s in cv_scores], color=fold_colors, edgecolor='none', width=0.6)
ax_right.axhline(y=99.87, color='#30D158', linestyle='--', linewidth=1.5, label='Mean: 99.87%')
ax_right.set_ylim(99.5, 100.1)
ax_right.set_ylabel('Accuracy (%)', color=TEXT, fontsize=10)
ax_right.set_title('5-Fold Cross-Validation Scores', color=TEXT, fontsize=12, fontweight='bold')
ax_right.tick_params(colors=TEXT, labelsize=9)
for spine in ax_right.spines.values():
    spine.set_edgecolor(GRID)
ax_right.yaxis.grid(True, color=GRID, linestyle='--', alpha=0.5)
ax_right.set_axisbelow(True)
ax_right.legend(fontsize=9, facecolor=CARD_BG, labelcolor=TEXT, edgecolor=GRID)
for bar, score in zip(bars, cv_scores):
    ax_right.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
        f'{score*100:.2f}%', ha='center', va='bottom', color=TEXT, fontsize=8, fontweight='bold')

plt.tight_layout()
plt.savefig('d:/GLOF Sentinel/Backend/report_assets/accuracy_dashboard.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print('Saved accuracy_dashboard.png')

print('\nAll 4 charts generated successfully!')
