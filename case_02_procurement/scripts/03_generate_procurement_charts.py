"""
03_generate_procurement_charts.py
Case 02: Defense Procurement Analytics (Prozorro 2022-2025)

Generates 4 publication-grade 300 DPI charts with generous canvas dimensions,
ample margins, and non-overlapping callout annotations:
1. chart1_market_spend_dynamics_2022_2025.png
2. chart2_buyers_structure_state_vs_local.png
3. chart3_hhi_market_concentration_curve.png
4. chart4_single_bidder_savings_gap.png
"""

import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from pathlib import Path
import json
import re
import textwrap

# Setup matplotlib styling for high-res publication light theme
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['grid.color'] = '#E2E8F0'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7
plt.rcParams['figure.facecolor'] = '#FFFFFF'
plt.rcParams['axes.facecolor'] = '#FFFFFF'
plt.rcParams['text.color'] = '#0F172A'
plt.rcParams['axes.labelcolor'] = '#0F172A'
plt.rcParams['xtick.color'] = '#334155'
plt.rcParams['ytick.color'] = '#334155'

CASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = CASE_DIR / "data" / "processed"
ARTIFACTS_DIR = CASE_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

JSON_PATH = DATA_DIR / "procurement_metrics.json"

# Palette Tokens
C_BLUE = '#0284C7'    # Sky 600
C_CYAN = '#0891B2'    # Cyan 600
C_RED = '#E11D48'     # Rose 600
C_GREEN = '#16A34A'   # Emerald 600
C_AMBER = '#D97706'   # Amber 600
C_SLATE = '#64748B'   # Slate 500

def generate_all_charts():
    print(f"--> [CHARTS] Loading metrics from: {JSON_PATH}")
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        m = json.load(f)

    years = ['2022', '2023', '2024', '2025']

    # =========================================================================
    # CHART 1: Market Spend Dynamics (2022-2025)
    # Increased canvas height, generous headroom (ylim 0..100), no overlapping
    # =========================================================================
    print("--> [CHARTS] 1. Generating chart1_market_spend_dynamics_2022_2025.png...")
    fig, ax1 = plt.subplots(figsize=(12.5, 7.8), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax1.set_facecolor('#FFFFFF')

    spends = [m['yearly_dynamics'][y]['award_b_uah'] for y in years]
    tenders = [m['yearly_dynamics'][y]['tenders'] for y in years]

    x = np.arange(len(years))
    width = 0.40

    bars = ax1.bar(x - 0.05, spends, width=width, color=C_BLUE, alpha=0.9, edgecolor='#0369A1', linewidth=1.2, label='Бюджет укладених угод (млрд грн)')
    ax1.set_xlabel('Рік закупівлі', fontsize=11, fontweight='bold', labelpad=10)
    ax1.set_ylabel('Обсяг фінансування (млрд грн)', color='#0369A1', fontsize=11, fontweight='bold', labelpad=10)
    ax1.tick_params(axis='y', labelcolor='#0369A1', labelsize=10)
    ax1.set_xticks(x)
    ax1.set_xticklabels(years, fontsize=11, fontweight='bold')
    ax1.set_ylim(0, 100)
    ax1.yaxis.grid(True)

    # Bar labels
    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2., h + 1.8, f"{h:.2f} млрд", ha='center', va='bottom', fontsize=10, fontweight='bold', color='#0369A1')

    # Line on twin axis for number of procedures
    ax2 = ax1.twinx()
    line = ax2.plot(x + 0.05, [t / 1000 for t in tenders], color=C_AMBER, linewidth=3.2, marker='o', markersize=9, label='Кількість торгів (тис. процедур)')
    ax2.set_ylabel('Кількість торгів (тис. процедур)', color='#B45309', fontsize=11, fontweight='bold', labelpad=10)
    ax2.tick_params(axis='y', labelcolor='#B45309', labelsize=10)
    ax2.set_ylim(0, 160)
    ax2.grid(False)

    for i in range(len(x)):
        ax2.text(x[i] + 0.05, (tenders[i] / 1000) + 4.2, f"{tenders[i]:,} торгів", ha='center', fontsize=9.5, fontweight='bold', color='#92400E')

    # Repositioned callout badge: placed in upper-left open area with ample clearance above bars
    ax1.annotate('Масштабування ринку: у 13.2 рази (+1,218%)\nвід 5.0 млрд грн (2022) до 65.9 млрд грн (2025)\nЗагальний пул ОВТ: 127.58 млрд грн у 384,291 торгах\nЧастка сегменту БпЛА та FPV: 39.4% (50.2 млрд грн)',
                 xy=(3 - 0.05, 66.0), xytext=(0.15, 76.0),
                 arrowprops=dict(facecolor=C_BLUE, shrink=0.08, width=1.5, headwidth=6),
                 fontsize=10, fontweight='bold', color='#0F172A',
                 bbox=dict(boxstyle="round,pad=0.6", fc="#F0F9FF", ec="#0284C7", lw=1.3))

    # Unified Title with plenty of padding
    plt.title('Динаміка оборонних закупівель ОВТ у системі Prozorro (2022-2025)\nМасштабування фінансування у 13.2 рази та зростання кількості процедур до 111.7 тис.',
              fontsize=13.5, fontweight='bold', pad=22, color='#0F172A', loc='left')

    out_p1 = ARTIFACTS_DIR / "chart1_market_spend_dynamics_2022_2025.png"
    plt.tight_layout()
    plt.savefig(out_p1, dpi=300)
    plt.close()
    print(f"    Saved: {out_p1.name} ({out_p1.stat().st_size / 1024:.1f} KB)")

    # =========================================================================
    # CHART 2: Buyers Structure - State vs Military vs Local (2022-2025)
    # Increased canvas, higher headroom, non-overlapping annotations
    # =========================================================================
    print("--> [CHARTS] 2. Generating chart2_buyers_structure_state_vs_local.png...")
    fig, (ax_bar, ax_pie) = plt.subplots(1, 2, figsize=(15.0, 8.0), dpi=300, gridspec_kw={'width_ratios': [1.35, 1.0]})
    fig.patch.set_facecolor('#FFFFFF')

    bg_yearly = m['buyer_groups_yearly']
    bg_names = [
        'Державні оборонні агенції (State Agencies / MO / AOZ / DOT)',
        'Військові частини (Military Units)',
        'Місцеві громади (Local Municipalities & Regional Admin)',
        'Інші державні органи (Other Public Entities)'
    ]
    labels_short = [
        'Центральні агенції (АОЗ/ДОТ/МОУ)',
        'Військові частини (ЗСУ/НГУ)',
        'Місцеві громади (ОДА/міськради)',
        'Інші держоргани'
    ]
    colors_bg = [C_BLUE, C_GREEN, C_AMBER, C_SLATE]

    bottom = np.zeros(len(years))
    for i, bg_key in enumerate(bg_names):
        vals = [bg_yearly.get(bg_key, {}).get(y, 0) for y in years]
        ax_bar.bar(years, vals, bottom=bottom, label=labels_short[i], color=colors_bg[i], width=0.50, edgecolor='#FFFFFF', linewidth=1.2)
        bottom += np.array(vals)

    ax_bar.set_ylabel('Обсяг фінансування (млрд грн)', fontsize=11, fontweight='bold', labelpad=8)
    ax_bar.set_title('Еволюція фінансування замовників (2022-2025)', fontsize=12.5, fontweight='bold', pad=14, loc='left')
    ax_bar.set_ylim(0, 90)
    ax_bar.yaxis.grid(True)
    ax_bar.legend(loc='upper left', frameon=True, framealpha=0.95, fontsize=9.2)

    # Stack total numbers
    for idx, yr in enumerate(years):
        tot = bottom[idx]
        ax_bar.text(idx, tot + 1.6, f"{tot:.1f} млрд", ha='center', fontsize=10, fontweight='bold', color='#0F172A')

    # Annotations placed with clean margins so they don't collide with bars
    ax_bar.annotate('2022: 52% витрат тримали\nгромади (міськради/ОДА)',
                    xy=(0, 3.2), xytext=(0.15, 26.0),
                    arrowprops=dict(facecolor=C_AMBER, shrink=0.08, width=1.2, headwidth=5),
                    fontsize=8.8, fontweight='bold', color='#92400E',
                    bbox=dict(boxstyle="round,pad=0.4", fc="#FEF3C7", ec="#D97706", lw=1))

    ax_bar.annotate('2024-2025: Стрибок прямих закупівель\nВійськових частин: з 0.1 до 15.4 млрд грн\nта централізація АОЗ: 30.3 млрд грн',
                    xy=(3, 52.0), xytext=(1.45, 74.0),
                    arrowprops=dict(facecolor=C_BLUE, shrink=0.08, width=1.2, headwidth=5),
                    fontsize=8.8, fontweight='bold', color='#0F172A',
                    bbox=dict(boxstyle="round,pad=0.4", fc="#F0F9FF", ec="#0284C7", lw=1))

    # Pie chart for Drones specifically
    drone_bg = m['drones_buyer_groups']
    drone_labels = [
        "Центр (АОЗ/ДОТ):\n29.4% (14.8 млрд)",
        "Військові частини:\n27.9% (14.0 млрд)",
        "Громади (ОДА/міськради):\n22.7% (11.4 млрд)",
        "Інші замовники:\n20.0% (10.0 млрд)"
    ]
    drone_vals = [
        drone_bg.get('Державні оборонні агенції (State Agencies / MO / AOZ / DOT)', {}).get('award_b_uah', 0),
        drone_bg.get('Військові частини (Military Units)', {}).get('award_b_uah', 0),
        drone_bg.get('Місцеві громади (Local Municipalities & Regional Admin)', {}).get('award_b_uah', 0),
        drone_bg.get('Інші державні органи (Other Public Entities)', {}).get('award_b_uah', 0)
    ]
    wedges, texts = ax_pie.pie(drone_vals, labels=drone_labels, colors=[C_BLUE, C_GREEN, C_AMBER, C_SLATE],
                               startangle=140, textprops=dict(fontsize=9.2, fontweight='bold'),
                               wedgeprops=dict(width=0.45, edgecolor='#FFFFFF', linewidth=2.5))

    ax_pie.set_title('Розподіл попиту на БпЛА та FPV (50.2 млрд грн)\nТри опори оборонного забезпечення', fontsize=12.5, fontweight='bold', pad=14)

    plt.suptitle('Ландшафт замовників: Хто купує для фронту у 2022-2025 роках\nТрансформація від екстрених закупівель громад до прямого контрактування бригад ЗСУ та АОЗ',
                 fontsize=14, fontweight='bold', y=0.97, color='#0F172A')

    out_p2 = ARTIFACTS_DIR / "chart2_buyers_structure_state_vs_local.png"
    plt.subplots_adjust(top=0.85, bottom=0.10, wspace=0.30)
    plt.savefig(out_p2, dpi=300)
    plt.close()
    print(f"    Saved: {out_p2.name} ({out_p2.stat().st_size / 1024:.1f} KB)")

    # =========================================================================
    # CHART 3: HHI Market Concentration & Supplier Structure
    # Wider canvas, distinct subplots, clear non-overlapping titles & margins
    # =========================================================================
    print("--> [CHARTS] 3. Generating chart3_hhi_market_concentration_curve.png...")
    fig, (ax_ew, ax_gauge) = plt.subplots(1, 2, figsize=(16.0, 8.2), dpi=300, gridspec_kw={'width_ratios': [1.35, 1.0]})
    fig.patch.set_facecolor('#FFFFFF')

    def clean_and_wrap(name: str, width: int = 24) -> str:
        n = name.strip()
        n = re.sub(r'(?i)товариство з обмеженою відповідальністю\s*', 'ТОВ ', n)
        n = re.sub(r'(?i)приватне акціонерне товариство\s*', 'ПрАТ ', n)
        n = re.sub(r'(?i)публічне акціонерне товариство\s*', 'ПАТ ', n)
        n = re.sub(r'(?i)акціонерне товариство\s*', 'АТ ', n)
        n = re.sub(r'(?i)приватне підприємство\s*', 'ПП ', n)
        n = re.sub(r'\s+', ' ', n).strip()
        lines = textwrap.wrap(n, width=width)
        if len(lines) > 3:
            lines = lines[:2] + [textwrap.shorten(" ".join(lines[2:]), width=width, placeholder="...")]
        return "\n".join(lines)

    ew_top = m['ew_concentration']['top_10_suppliers']
    supp_names = [clean_and_wrap(r['supplier_name'], width=24) for r in ew_top][::-1]
    supp_shares = [r['share_pct'] for r in ew_top][::-1]
    supp_vals = [r['award_m_uah'] for r in ew_top][::-1]

    y_pos = np.arange(len(supp_names))
    ew_bars = ax_ew.barh(y_pos, supp_shares, color=C_CYAN, alpha=0.9, edgecolor='#0E7490', height=0.62)
    ax_ew.set_yticks(y_pos)
    ax_ew.set_yticklabels(supp_names, fontsize=7.8, fontweight='bold', linespacing=0.9)
    ax_ew.tick_params(axis='y', pad=6)
    ax_ew.set_xlabel('Частка ринку РЕБ / РЕР (%)', fontsize=11, fontweight='bold', labelpad=8)
    ax_ew.set_title('Топ-10 постачальників систем РЕБ та тактичних засобів (5.82 млрд грн)', fontsize=12, fontweight='bold', pad=16, loc='left')
    ax_ew.set_xlim(0, 15.5)
    ax_ew.xaxis.grid(True)

    for bar, val in zip(ew_bars, supp_vals):
        w = bar.get_width()
        ax_ew.text(w + 0.25, bar.get_y() + bar.get_height() / 2., f"{w:.1f}% ({val:.1f} млн грн)", va='center', fontsize=8.8, fontweight='bold', color='#0E7490')

    # Benchmarks
    benchmarks = ['БпЛА та Дрони\n(HHI = 739.6)', 'РЕБ та РЕР\n(HHI = 296.0)', 'Поріг безпечної\nконкуренції\n(< 1,500)', 'Помірна\nконцентрація\n(1,500 - 2,500)', 'Висока\nмонополізація\n(> 2,500)']
    hhi_vals = [739.6, 296.0, 1500, 2500, 3500]
    colors_hhi = [C_BLUE, C_CYAN, C_GREEN, C_AMBER, C_RED]

    y_bench = np.arange(len(benchmarks))
    ax_gauge.barh(y_bench, hhi_vals, color=colors_hhi, alpha=0.85, height=0.58, edgecolor='#334155', linewidth=1)
    ax_gauge.set_yticks(y_bench)
    ax_gauge.set_yticklabels(benchmarks, fontsize=9.0, fontweight='bold')
    ax_gauge.set_xlabel('Індекс Герфіндаля-Хіршмана (HHI)', fontsize=11, fontweight='bold', labelpad=8)
    ax_gauge.set_title('Міжнародна антимонопольна шкала HHI (DOJ / FTC)', fontsize=12, fontweight='bold', pad=16, loc='left')
    ax_gauge.axvline(1500, color=C_GREEN, linestyle='--', linewidth=1.8, label='Межа неконцентрованого ринку')
    ax_gauge.xaxis.grid(True)
    ax_gauge.set_xlim(0, 4800)
    ax_gauge.set_ylim(-0.6, 4.6)

    for i, v in enumerate(hhi_vals):
        ax_gauge.text(v + 90, i, f"{v:.1f}" if v < 1000 else f"{v}", va='center', fontsize=9.2, fontweight='bold', color=colors_hhi[i])

    # Summary callout shifted to the right into the empty quadrant so it doesn't overlap the bars
    callout_txt = (
        "ВИСНОВОК:\n"
        "Ринок ОВТ є повністю\n"
        "децентралізованим (HHI < 1,000).\n"
        "Жоден вендор не має монополії,\n"
        "ринок захищений від шантажу."
    )
    ax_gauge.text(2100, 0.40, callout_txt,
                  fontsize=8.0, fontweight='bold', color='#0F172A',
                  bbox=dict(boxstyle="round,pad=0.45", fc="#F0FDF4", ec="#16A34A", lw=1.2))

    plt.suptitle('Концентрація ринку постачальників ОВТ: Індекс HHI та відсутність монополії\nРинки БпЛА (HHI = 739.6) та РЕБ (HHI = 296.0) знаходяться глибоко в безпечній зоні конкуренції',
                 fontsize=14, fontweight='bold', y=0.97, color='#0F172A')

    out_p3 = ARTIFACTS_DIR / "chart3_hhi_market_concentration_curve.png"
    plt.subplots_adjust(left=0.18, right=0.96, top=0.85, bottom=0.10, wspace=0.36)
    plt.savefig(out_p3, dpi=300)
    plt.close()
    print(f"    Saved: {out_p3.name} ({out_p3.stat().st_size / 1024:.1f} KB)")

    # =========================================================================
    # CHART 4: Single-Bidder Savings Gap & Non-Competition Cost
    # Wider canvas, ample top clearance, clear distinction between subplots
    # =========================================================================
    print("--> [CHARTS] 4. Generating chart4_single_bidder_savings_gap.png...")
    fig, (ax_gap, ax_loss) = plt.subplots(1, 2, figsize=(15.5, 8.0), dpi=300, gridspec_kw={'width_ratios': [1.15, 1.0]})
    fig.patch.set_facecolor('#FFFFFF')

    cats = ['Всі торги ОВТ', 'БпЛА та Дрони', 'РЕБ та РЕР', 'Тактичний звʼязок']
    multi_disc = [15.02, 10.06, 16.37, 12.82]
    single_disc = [3.77, 2.93, 2.15, 3.14]

    y_cats = np.arange(len(cats))
    h = 0.34

    b_multi = ax_gap.barh(y_cats - h/2, multi_disc, height=h, color=C_GREEN, label='Конкурентні торги (2+ учасники)', edgecolor='#15803D')
    b_single = ax_gap.barh(y_cats + h/2, single_disc, height=h, color=C_RED, label='Торги з 1 учасником (Single Bidder)', edgecolor='#B91C1C')

    ax_gap.set_yticks(y_cats)
    ax_gap.set_yticklabels(cats, fontsize=10.5, fontweight='bold')
    ax_gap.set_xlabel('Середня економія від очікуваної вартості (%)', fontsize=11, fontweight='bold', labelpad=8)
    ax_gap.set_title('Середня знижка: Конкуренція проти Single Bidder', fontsize=12, fontweight='bold', pad=16, loc='left')
    ax_gap.set_xlim(0, 24)
    ax_gap.xaxis.grid(True)
    ax_gap.legend(loc='lower right', frameon=True, framealpha=0.95, fontsize=9.5)

    for bar in b_multi:
        w = bar.get_width()
        ax_gap.text(w + 0.35, bar.get_y() + bar.get_height()/2., f"{w:.2f}%", va='center', fontsize=9.2, fontweight='bold', color='#15803D')

    for bar in b_single:
        w = bar.get_width()
        ax_gap.text(w + 0.35, bar.get_y() + bar.get_height()/2., f"{w:.2f}%", va='center', fontsize=9.2, fontweight='bold', color='#B91C1C')

    # Annotate gap cleanly
    ax_gap.annotate('Розрив економії (Savings Gap):\n11.25 відсоткових пунктів!',
                    xy=(9.5, -0.2), xytext=(12.2, 0.45),
                    arrowprops=dict(facecolor=C_BLUE, shrink=0.08, width=1.2, headwidth=5),
                    fontsize=9.2, fontweight='bold', color='#0F172A',
                    bbox=dict(boxstyle="round,pad=0.4", fc="#EFF6FF", ec="#3B82F6", lw=1))

    # Second Subplot: Unrealized Savings Waterfall
    loss_cats = ['Всі торги ОВТ', 'БпЛА та Дрони', 'РЕБ та РЕР', 'Інші позиції']
    loss_vals = [4287.0, 606.0, 376.3, 3304.7]
    loss_colors = [C_RED, C_BLUE, C_CYAN, C_SLATE]

    b_loss = ax_loss.bar(loss_cats, [v / 1000 for v in loss_vals], color=loss_colors, width=0.50, edgecolor='#334155', linewidth=1)
    ax_loss.set_ylabel('Втрачена потенційна економія (млрд грн)', fontsize=11, fontweight='bold', labelpad=8)
    ax_loss.set_title('Ціна відсутності конкуренції (втрачений бюджет)', fontsize=12, fontweight='bold', pad=16, loc='left')
    ax_loss.set_ylim(0, 6.2)
    ax_loss.yaxis.grid(True)

    for bar, val in zip(b_loss, loss_vals):
        h_val = bar.get_height()
        ax_loss.text(bar.get_x() + bar.get_width()/2., h_val + 0.15, f"{val:.0f} млн грн\n({h_val:.2f} млрд)", ha='center', va='bottom', fontsize=9.2, fontweight='bold', color='#0F172A')

    # Equivalence callout box placed in open top right area
    ax_loss.text(0.60, 3.8, '4.29 МЛРД ГРН ВТРАЧЕНОЇ ЕКОНОМІЇ\nЦе еквівалент:\n• ~215,000 FPV-дронів (по 20 тис. грн)\n• або ~2,800 мобільних комплексів РЕБ\n\nЗниження частки Single Bidder на 10%\nвивільняє понад 420 млн грн на рік!',
                 fontsize=9.2, fontweight='bold', color='#0F172A',
                 bbox=dict(boxstyle="round,pad=0.55", fc="#FFF1F2", ec="#E11D48", lw=1.3))

    plt.suptitle('Ціна відсутності конкуренції: Single-Bidder Gap та втрачений бюджет (4.29 млрд грн)\nЗалучення другого учасника збільшує економію бюджету з 3.77% до 15.02%',
                 fontsize=14, fontweight='bold', y=0.97, color='#0F172A')

    out_p4 = ARTIFACTS_DIR / "chart4_single_bidder_savings_gap.png"
    plt.subplots_adjust(top=0.85, bottom=0.10, wspace=0.32)
    plt.savefig(out_p4, dpi=300)
    plt.close()
    print(f"    Saved: {out_p4.name} ({out_p4.stat().st_size / 1024:.1f} KB)")

if __name__ == '__main__':
    generate_all_charts()
