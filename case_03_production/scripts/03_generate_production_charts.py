"""
03_generate_production_charts.py
Case 03: Defense Production Analytics: Manufacturing Throughput, Capacity Scaling & Assembly Bottlenecks (2022-2025)

Generates 4 publication-grade 300 DPI charts in strict Light Theme:
- chart1_production_throughput_scaling.png
- chart2_assembly_cycle_and_rhythmicity.png
- chart3_manufacturer_capacity_tiers.png
- chart4_production_bottlenecks_and_delays.png
"""

import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import json
from pathlib import Path

# Paths
CASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = CASE_DIR / "data" / "processed"
ARTIFACTS_DIR = CASE_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

JSON_IN = DATA_DIR / "production_analysis_summary.json"

# Visual Theme Tokens (CASE_DESIGN_GUIDELINES.md)
COLOR_BG = "#F8FAFC"
COLOR_CARD = "#FFFFFF"
COLOR_BORDER = "#E2E8F0"
COLOR_TEXT = "#0F172A"
COLOR_MUTED = "#64748B"
COLOR_PRIMARY = "#0284C7"    # Sky-600
COLOR_CYAN = "#0891B2"       # Cyan-600
COLOR_SUCCESS = "#16A34A"    # Emerald-600
COLOR_ALERT = "#E11D48"      # Rose-600
COLOR_AMBER = "#D97706"      # Amber-600
COLOR_PURPLE = "#7C3AED"     # Violet-600

def setup_plot_style():
    plt.rcParams.update({
        'font.sans-serif': ['Segoe UI', 'DejaVu Sans', 'Arial', 'sans-serif'],
        'font.family': 'sans-serif',
        'figure.facecolor': COLOR_BG,
        'axes.facecolor': COLOR_CARD,
        'axes.edgecolor': COLOR_BORDER,
        'axes.linewidth': 1.0,
        'axes.labelcolor': COLOR_TEXT,
        'axes.titlesize': 12,
        'axes.titleweight': 'bold',
        'axes.titlepad': 12,
        'xtick.color': COLOR_MUTED,
        'ytick.color': COLOR_MUTED,
        'xtick.labelsize': 9.5,
        'ytick.labelsize': 9.5,
        'grid.color': COLOR_BORDER,
        'grid.linestyle': '--',
        'grid.alpha': 0.7,
        'text.color': COLOR_TEXT
    })

def generate_chart_1(data):
    """Chart 1: Throughput Scaling & Batch Size Evolution (2022-2025)"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    fig.patch.set_facecolor(COLOR_BG)
    
    # 1. Left: Physical Units by Year (UAV + EW)
    years = [2022, 2023, 2024, 2025]
    uav_data = {r['year']: r['units'] for r in data['rq1_throughput']['yearly_uav']}
    ew_data = {r['year']: r['units'] for r in data['rq1_throughput']['yearly_ew']}
    val_data = {r['year']: r['val_bln'] for r in data['rq1_throughput']['yearly_uav']}
    
    uav_k = [uav_data.get(y, 0) / 1000 for y in years]
    ew_k = [ew_data.get(y, 0) / 1000 for y in years]
    
    bar_width = 0.55
    bars1 = ax1.bar(years, uav_k, width=bar_width, label='БпЛА та Дрони (тис. шт)', color=COLOR_PRIMARY, edgecolor='none', zorder=3)
    bars2 = ax1.bar(years, ew_k, width=bar_width, bottom=uav_k, label='РЕБ та Тактичні системи (тис. шт)', color=COLOR_AMBER, edgecolor='none', zorder=3)
    
    ax1.set_title("Річний темп фізичного випуску ОВТ (Throughput 2022-2025)", fontsize=12, pad=12)
    ax1.set_ylabel("Фізичний обсяг випуску (тис. одиниць)", fontsize=10, color=COLOR_TEXT)
    ax1.set_xticks(years)
    ax1.set_xticklabels(['2022', '2023', '2024', '2025'], fontweight='bold')
    ax1.grid(axis='y', zorder=0)
    ax1.set_ylim(0, 1850)
    
    # Value annotations on top of bars
    for i, yr in enumerate(years):
        tot_k = uav_k[i] + ew_k[i]
        val_b = val_data.get(yr, 0)
        ax1.text(yr, tot_k + 35, f"{tot_k:,.1f} тис. шт\n({val_b:.1f} млрд грн)", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color=COLOR_TEXT)
        
    ax1.legend(loc='upper left', frameon=True, facecolor=COLOR_CARD, edgecolor=COLOR_BORDER, fontsize=9)
    
    # 2. Right: Batch Size Quantiles Evolution
    p25 = [r['batch_p25'] for r in data['rq1_throughput']['yearly_uav']]
    p50 = [r['batch_p50'] for r in data['rq1_throughput']['yearly_uav']]
    p75 = [r['batch_p75'] for r in data['rq1_throughput']['yearly_uav']]
    p90 = [r['batch_p90'] for r in data['rq1_throughput']['yearly_uav']]
    
    ax2.plot(years, p90, marker='o', linewidth=2.5, color=COLOR_ALERT, label='P90 (Хвостовий розмір серії)', zorder=4)
    ax2.plot(years, p75, marker='s', linewidth=2.0, color=COLOR_CYAN, label='P75 (Верхній квартиль партії)', zorder=4)
    ax2.plot(years, p50, marker='^', linewidth=2.5, color=COLOR_PRIMARY, label='P50 (Медіанний розмір партії)', zorder=4)
    ax2.plot(years, p25, marker='v', linewidth=1.5, color=COLOR_MUTED, label='P25 (Нижній квартиль партії)', linestyle=':', zorder=4)
    
    # Fill between P25 and P75 (IQR)
    ax2.fill_between(years, p25, p75, color=COLOR_PRIMARY, alpha=0.15, label='Міжквартильний розмах (IQR)')
    
    ax2.set_title("Еволюція розміру партії контрактів БпЛА (Batch Size 2022-2025)", fontsize=12, pad=12)
    ax2.set_ylabel("Кількість бортів у контракті (шт)", fontsize=10, color=COLOR_TEXT)
    ax2.set_xticks(years)
    ax2.set_xticklabels(['2022', '2023', '2024', '2025'], fontweight='bold')
    ax2.grid(axis='y', zorder=0)
    ax2.set_ylim(0, 650)
    
    # Text callout for P50 jump
    ax2.annotate(
        f"Зростання медіани у 34.5 раза:\nз 2 шт (2022) до 69 шт (2025)\nP90 досяг 553 шт/контракт",
        xy=(2025, p50[-1]), xytext=(2023.2, 420),
        arrowprops=dict(facecolor=COLOR_PRIMARY, shrink=0.08, width=1.5, headwidth=6),
        fontsize=9.5, fontweight='bold', color=COLOR_TEXT,
        bbox=dict(boxstyle="round,pad=0.5", facecolor=COLOR_CARD, edgecolor=COLOR_PRIMARY, lw=1.2)
    )
    
    ax2.legend(loc='upper left', frameon=True, facecolor=COLOR_CARD, edgecolor=COLOR_BORDER, fontsize=8.5)
    
    plt.tight_layout(pad=2.5)
    out_file = ARTIFACTS_DIR / "chart1_production_throughput_scaling.png"
    plt.savefig(out_file, dpi=300, facecolor=COLOR_BG)
    plt.close()
    print(f"--> [SAVE] Generated: {out_file.name}")

def generate_chart_2(data):
    """Chart 2: Manufacturing Rhythmicity & Lead Time Cycle (2022-2025)"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    fig.patch.set_facecolor(COLOR_BG)
    
    # 1. Left: Monthly Seasonality & December Rush ("Штурмівщина")
    m_data = data['rq2_rhythmicity']['monthly_seasonality']
    months = [r['month'] for r in m_data]
    vals = [r['val_bln'] for r in m_data]
    month_labels = ['Січ', 'Лют', 'Бер', 'Кві', 'Тра', 'Чер', 'Лип', 'Сер', 'Вер', 'Жов', 'Лис', 'Гру']
    
    bar_colors = [COLOR_ALERT if m == 12 else (COLOR_AMBER if m in [10, 11] else COLOR_PRIMARY) for m in months]
    bars = ax1.bar(months, vals, color=bar_colors, width=0.65, zorder=3)
    
    ax1.set_title("Аритмічність оборонного замовлення: Пік грудня проти просідання січня", fontsize=12, pad=12)
    ax1.set_ylabel("Загальна сума контрактації (млрд грн)", fontsize=10, color=COLOR_TEXT)
    ax1.set_xticks(months)
    ax1.set_xticklabels(month_labels, fontweight='bold')
    ax1.grid(axis='y', zorder=0)
    ax1.set_ylim(0, 36)
    
    # Value annotations on December and January
    ax1.text(12, vals[11] + 1.0, f"Грудень: {vals[11]:.2f} млрд грн\n(23.9% річного бюджету)", ha='center', va='bottom', fontsize=9, fontweight='bold', color=COLOR_ALERT)
    ax1.text(1, vals[0] + 1.0, f"Січень: {vals[0]:.2f} млрд грн\n(Провал ліній)", ha='center', va='bottom', fontsize=9, fontweight='bold', color=COLOR_PRIMARY)
    
    # Ratio callout box
    ax1.text(
        0.05, 0.88,
        f"Коефіцієнт аритмічності: 4.04x\n(Грудень перевищує Січень у 4 рази)",
        transform=ax1.transAxes, fontsize=9.5, fontweight='bold', color=COLOR_TEXT,
        bbox=dict(boxstyle="round,pad=0.4", facecolor=COLOR_CARD, edgecolor=COLOR_ALERT, lw=1.2)
    )
    
    # 2. Right: Lead Time Cycle Quantiles (P50 vs P90)
    cats = ['БпЛА та Дрони', 'РЕБ та Тактичні', 'FPV Комплектуючі', 'Оборонне спорядження']
    p50_vals = [6.0, 10.1, 9.1, 12.0]
    p90_vals = [13.9, 16.0, 17.0, 21.1]
    deltas = [round(p90 - p50, 1) for p50, p90 in zip(p50_vals, p90_vals)]
    
    y_pos = np.arange(len(cats))
    h = 0.35
    
    ax2.barh(y_pos - h/2, p50_vals, height=h, label='P50 (Медіанний строк виконання)', color=COLOR_PRIMARY, zorder=3)
    ax2.barh(y_pos + h/2, p90_vals, height=h, label='P90 (Хвостовий ризик виконання)', color=COLOR_ALERT, zorder=3)
    
    ax2.set_title("Виробничий цикл Contract-to-Delivery: Необхідний буфер P90", fontsize=12, pad=12)
    ax2.set_xlabel("Тривалість виробничо-закупівельного циклу (днів)", fontsize=10, color=COLOR_TEXT)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(cats, fontweight='bold')
    ax2.grid(axis='x', zorder=0)
    ax2.set_xlim(0, 26)
    
    for i in range(len(cats)):
        ax2.text(p50_vals[i] + 0.4, y_pos[i] - h/2, f"{p50_vals[i]} дн", va='center', fontsize=9, fontweight='bold', color=COLOR_PRIMARY)
        ax2.text(p90_vals[i] + 0.4, y_pos[i] + h/2, f"{p90_vals[i]} дн (+{deltas[i]} дн)", va='center', fontsize=9, fontweight='bold', color=COLOR_ALERT)
        
    ax2.legend(loc='lower right', frameon=True, facecolor=COLOR_CARD, edgecolor=COLOR_BORDER, fontsize=9)
    
    plt.tight_layout(pad=2.5)
    out_file = ARTIFACTS_DIR / "chart2_assembly_cycle_and_rhythmicity.png"
    plt.savefig(out_file, dpi=300, facecolor=COLOR_BG)
    plt.close()
    print(f"--> [SAVE] Generated: {out_file.name}")

def clean_company_name(name):
    import re
    if not name or not isinstance(name, str):
        return 'Невідомий виробник'
    s = name.strip()
    s = re.sub(r'(?i)товариство\s+з\s+обмеженою\s+відповідальністю', 'ТОВ', s)
    s = re.sub(r'(?i)приватне\s+підприємство', 'ПП', s)
    s = re.sub(r'(?i)акціонерне\s+товариство', 'АТ', s)
    s = re.sub(r'(?i)публічне\s+акціонерне\s+товариство', 'ПАТ', s)
    s = re.sub(r'(?i)державне\s+підприємство', 'ДП', s)
    s = re.sub(r'(?i)фізична\s+особа[\s-]+підприємець', 'ФОП', s)
    s = re.sub(r'\bТзОВ\b', 'ТОВ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    if len(s) > 30:
        s = s[:28] + '..'
    return s

def generate_chart_3(data):
    """Chart 3: Manufacturer Capacity Tiers & Stratification"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300, gridspec_kw={'width_ratios': [1, 1.25]})
    fig.patch.set_facecolor(COLOR_BG)
    
    # 1. Left: Stratification Pyramid (Suppliers % vs Physical Output %)
    tier_info = data['rq3_tiering']['tier_summary']
    tier_names = ['Tier 1 (>10k шт)', 'Tier 2 (1k-10k шт)', 'Tier 3 (<1k шт)']
    sup_counts = [r['suppliers'] for r in tier_info]
    units_pct = [r['units_pct'] for r in tier_info]
    val_pct = [r['val_pct'] for r in tier_info]
    
    x = np.arange(len(tier_names))
    width = 0.35
    
    b1 = ax1.bar(x - width/2, units_pct, width=width, label='Частка у фізичному випуску (%)', color=COLOR_PRIMARY, zorder=3)
    b2 = ax1.bar(x + width/2, val_pct, width=width, label='Частка у вартості контрактів (%)', color=COLOR_CYAN, zorder=3)
    
    ax1.set_title("Стратифікація виробників ОВТ: Внесок ешелонів Tier 1-3", fontsize=12, pad=12)
    ax1.set_ylabel("Частка у загальному обсязі (%)", fontsize=10, color=COLOR_TEXT)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"Tier 1 (>10k)\n{sup_counts[0]} заводів (1.8%)", f"Tier 2 (1k-10k)\n{sup_counts[1]} виробників (5.2%)", f"Tier 3 (<1k)\n{sup_counts[2]} SME (93.0%)"], fontweight='bold')
    ax1.grid(axis='y', zorder=0)
    ax1.set_ylim(0, 90)
    
    # Bar labels
    for bar in b1:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, h + 1.5, f"{h:.1f}%", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color=COLOR_PRIMARY)
    for bar in b2:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, h + 1.5, f"{h:.1f}%", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color=COLOR_CYAN)
        
    ax1.legend(loc='upper right', frameon=True, facecolor=COLOR_CARD, edgecolor=COLOR_BORDER, fontsize=9)
    
    # 2. Right: Top 10 Manufacturers Leaderboard by Output
    top_m = data['rq3_tiering']['top_manufacturers'][:10]
    names = [clean_company_name(r['supplier_name']) for r in top_m][::-1]
    units_k = [r['total_units'] / 1000 for r in top_m][::-1]
    vals_b = [r['total_val_bln'] for r in top_m][::-1]
    
    y_pos = np.arange(len(names))
    b_top = ax2.barh(y_pos, units_k, color=COLOR_PRIMARY, height=0.6, zorder=3)
    
    ax2.set_title("Топ-10 виробників за фізичним обсягом випуску (2022-2025)", fontsize=12, pad=12)
    ax2.set_xlabel("Фізичний випуск (тис. одиниць)", fontsize=10, color=COLOR_TEXT)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(names, fontsize=8.5, fontweight='bold')
    ax2.grid(axis='x', zorder=0)
    ax2.set_xlim(0, max(units_k) * 1.35)
    
    for i, bar in enumerate(b_top):
        w = bar.get_width()
        vb = vals_b[i]
        ax2.text(w + max(units_k)*0.02, bar.get_y() + bar.get_height()/2, f"{w:.1f} тис. ({vb:.2f} млрд грн)", va='center', fontsize=8, fontweight='bold', color=COLOR_TEXT)
        
    plt.tight_layout(pad=2.5, w_pad=3.2)
    out_file = ARTIFACTS_DIR / "chart3_manufacturer_capacity_tiers.png"
    plt.savefig(out_file, dpi=300, facecolor=COLOR_BG)
    plt.close()
    print(f"--> [SAVE] Generated: {out_file.name}")

def generate_chart_4(data):
    """Chart 4: Production Bottlenecks & Assembly Failure Points"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    fig.patch.set_facecolor(COLOR_BG)
    
    # 1. Left: Contract Failure Rate across MilTech Categories
    fail_data = data['rq4_bottlenecks']['fail_by_cat']
    # Filter and sort
    cats_plot = []
    fail_pcts = []
    colors = []
    
    for r in fail_data:
        c_short = r['miltech_category'].split('(')[0].strip()
        cats_plot.append(c_short)
        fail_pcts.append(r['fail_rate_pct'])
        if 'БпЛА' in c_short or 'РЕБ' in c_short:
            colors.append(COLOR_ALERT)
        else:
            colors.append(COLOR_MUTED)
            
    # Sort descending
    sorted_idx = np.argsort(fail_pcts)[::-1]
    cats_plot = [cats_plot[i] for i in sorted_idx]
    fail_pcts = [fail_pcts[i] for i in sorted_idx]
    colors = [colors[i] for i in sorted_idx]
    
    y_pos = np.arange(len(cats_plot))
    ax1.barh(y_pos[::-1], fail_pcts[::-1], color=colors[::-1], height=0.55, zorder=3)
    
    ax1.set_title("Частка зірваних процедур закупівлі за категоріями ОВТ (%)", fontsize=12, pad=12)
    ax1.set_xlabel("Відсоток неуспішних / скасованих торгів (%)", fontsize=10, color=COLOR_TEXT)
    ax1.set_yticks(y_pos[::-1])
    ax1.set_yticklabels(cats_plot[::-1], fontweight='bold', fontsize=9)
    ax1.grid(axis='x', zorder=0)
    ax1.set_xlim(0, 12.5)
    
    for i, p in enumerate(fail_pcts[::-1]):
        ax1.text(p + 0.3, y_pos[::-1][i], f"{p:.2f}%", va='center', fontsize=9, fontweight='bold', color=COLOR_ALERT if p > 5 else COLOR_TEXT)
        
    # Annotation on Drones
    ax1.text(
        0.05, 0.88,
        "БпЛА та Дрони: найвищий рівень зривів (9.78%)\nчерез жорсткі ТЗ та дефіцит компонентів",
        transform=ax1.transAxes, fontsize=9.5, fontweight='bold', color=COLOR_ALERT,
        bbox=dict(boxstyle="round,pad=0.4", facecolor=COLOR_CARD, edgecolor=COLOR_ALERT, lw=1.2)
    )
    
    # 2. Right: Bottleneck Stage Weight Waterfall
    taxonomy = data['rq4_bottlenecks']['taxonomy']
    stages = [r['stage'].split('(')[0].strip() for r in taxonomy][::-1]
    weights = [r['delay_weight_pct'] for r in taxonomy][::-1]
    impacts = [r['impact_days'] for r in taxonomy][::-1]
    
    y_pos2 = np.arange(len(stages))
    b2 = ax2.barh(y_pos2, weights, color=[COLOR_AMBER, COLOR_PRIMARY, COLOR_CYAN, COLOR_ALERT], height=0.55, zorder=3)
    
    ax2.set_title("Анатомія виробничих вузьких місць: Внесок етапів у затримки", fontsize=12, pad=12)
    ax2.set_xlabel("Частка у сукупній дисперсії строків постачання (%)", fontsize=10, color=COLOR_TEXT)
    ax2.set_yticks(y_pos2)
    ax2.set_yticklabels(stages, fontweight='bold', fontsize=8.5)
    ax2.grid(axis='x', zorder=0)
    ax2.set_xlim(0, 52)
    
    for i, bar in enumerate(b2):
        w = bar.get_width()
        imp = impacts[i]
        ax2.text(w + 1.0, bar.get_y() + bar.get_height()/2, f"{w:.0f}% ({imp})", va='center', fontsize=8.5, fontweight='bold', color=COLOR_TEXT)
        
    plt.tight_layout(pad=2.5)
    out_file = ARTIFACTS_DIR / "chart4_production_bottlenecks_and_delays.png"
    plt.savefig(out_file, dpi=300, facecolor=COLOR_BG)
    plt.close()
    print(f"--> [SAVE] Generated: {out_file.name}")

def main():
    setup_plot_style()
    print("=" * 75)
    print("STEP 03: GENERATING 4 PUBLICATION CHARTS (300 DPI, LIGHT THEME)")
    print("=" * 75)
    with open(JSON_IN, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    generate_chart_1(data)
    generate_chart_2(data)
    generate_chart_3(data)
    generate_chart_4(data)
    print("--> [DONE] All 4 publication charts successfully created in artifacts/")

if __name__ == '__main__':
    main()
