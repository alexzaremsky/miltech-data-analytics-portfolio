import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import json

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

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "artifacts"
PROOFS_DIR = ARTIFACTS_DIR / "code_proofs"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
PROOFS_DIR.mkdir(parents=True, exist_ok=True)

def generate_multiyear_charts():
    parquet_path = DATA_DIR / "tenders_2022_2025_drone_ew_miltech.parquet"
    print(f"Loading {parquet_path.name}...")
    df = pd.read_parquet(parquet_path)
    
    # -------------------------------------------------------------
    # CHART 1: Drones Scaling & Lead Time Evolution (2022-2025)
    # -------------------------------------------------------------
    print("Generating Chart 1: Drone Procurement Scaling & Lead Time (Spacious Light Theme)...")
    df_drones = df[df['miltech_category'] == 'БпЛА та Дрони (UAV / Drones)'].copy()
    comp_drones = df_drones[df_drones['procurement_method'].isin(['open', 'selective']) & (df_drones['lead_time_cycle_days'] > 0)]
    
    yearly_drones = comp_drones.groupby('year').agg(
        volume=('tender_id', 'count'),
        p50=('lead_time_cycle_days', lambda x: np.percentile(x, 50)),
        p90=('lead_time_cycle_days', lambda x: np.percentile(x, 90))
    ).reset_index()
    
    # Figsize with ample room top and bottom
    fig, ax1 = plt.subplots(figsize=(11, 6.4), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax1.set_facecolor('#FFFFFF')
    
    x = np.arange(len(yearly_drones))
    width = 0.38
    
    bars = ax1.bar(x - 0.05, yearly_drones['volume'], width=width, color='#0284C7', alpha=0.85, label='Кількість торгів БпЛА (од.)')
    ax1.set_xlabel('Рік закупівлі', fontsize=10.5, fontweight='bold', labelpad=8)
    ax1.set_ylabel('Кількість конкурентних торгів БпЛА', color='#0369A1', fontsize=10.5, fontweight='bold', labelpad=8)
    ax1.tick_params(axis='y', labelcolor='#0369A1')
    ax1.set_xticks(x)
    ax1.set_xticklabels([str(y) for y in yearly_drones['year']], fontsize=10, fontweight='bold')
    ax1.set_ylim(0, 4800)
    
    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., h + 90, f"{h:,}", ha='center', va='bottom', fontsize=9.5, color='#0369A1', fontweight='bold')
        
    ax2 = ax1.twinx()
    l1 = ax2.plot(x + 0.05, yearly_drones['p50'], color='#10B981', linewidth=3.0, marker='s', markersize=8, label='P50 (Медіана циклу, дн)')
    l2 = ax2.plot(x + 0.05, yearly_drones['p90'], color='#E11D48', linewidth=3.0, marker='o', markersize=8, label='P90 (Хвостовий ризик, дн)')
    ax2.set_ylabel('Тривалість циклу закупівлі (днів)', color='#991B1B', fontsize=10.5, fontweight='bold', labelpad=8)
    ax2.tick_params(axis='y', labelcolor='#991B1B')
    ax2.set_ylim(0, 24)
    
    for i in range(len(x)):
        ax2.text(x[i] + 0.05, yearly_drones['p50'].iloc[i] - 1.2, f"P50: {yearly_drones['p50'].iloc[i]:.1f}д", ha='center', fontsize=9, color='#047857', fontweight='bold')
        ax2.text(x[i] + 0.05, yearly_drones['p90'].iloc[i] + 0.7, f"P90: {yearly_drones['p90'].iloc[i]:.1f}д", ha='center', fontsize=9, color='#BE123C', fontweight='bold')
        
    ax1.annotate('Масштабування FPV-ринку:\nвід 17 торгів (2022) до 3,399 (2025)\nЗростання у 200 разів!',
                 xy=(3 - 0.05, 3400), xytext=(1.05, 3750),
                 arrowprops=dict(facecolor='#0284C7', shrink=0.08, width=1.5, headwidth=6),
                 fontsize=9.5, fontweight='bold', color='#0F172A',
                 bbox=dict(boxstyle="round,pad=0.5", fc="#F0F9FF", ec="#0284C7", lw=1.2))
                 
    plt.title('Еволюція ринку та строків постачання БпЛА в Україні (Prozorro 2022-2025)\nХоча медіанний строк скоротився до 5.1 дн, хвостовий P90 тримається на рівні 12-14 дн (+135%)', 
              fontsize=11.0, fontweight='bold', pad=14)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Legend placed strictly at the BOTTOM below the X-axis
    lines = [bars, l1[0], l2[0]]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper center', bbox_to_anchor=(0.5, -0.16), ncol=3, 
               frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=9.5)
    
    chart1_path = ARTIFACTS_DIR / "chart1_drones_lead_time_evolution_2022_2025.png"
    fig.savefig(chart1_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved Chart 1 to: {chart1_path}")

    # -------------------------------------------------------------
    # CHART 2: Planner's Prediction Card (Spacious Canvas)
    # -------------------------------------------------------------
    print("Generating Chart 2: Planner Prediction Card (Spacious Canvas)...")
    fig, ax = plt.subplots(figsize=(11, 6.4), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    
    categories = [
        ("БпЛА та FPV-дрони (CPV 3471)", 6.0, 13.9, 7.9, "#0284C7", "#E11D48"),
        ("РЕБ, РЕР та Тактичні системи (CPV 3573)", 10.0, 17.0, 7.0, "#4F46E5", "#DC2626"),
        ("Тактичний зв'язок та антени (CPV 325)", 7.9, 14.1, 6.2, "#0891B2", "#EA580C"),
        ("Комплектуючі FPV та авіоніка (CPV 3023/316)", 6.8, 13.0, 6.2, "#059669", "#D97706"),
        ("Оборонне спорядження та захист (CPV 358)", 9.2, 16.8, 7.6, "#7C3AED", "#BE123C")
    ]
    
    labels = [c[0] for c in categories]
    p50_vals = [c[1] for c in categories]
    tail_buffers = [c[3] for c in categories]
    p90_vals = [c[2] for c in categories]
    
    y = np.arange(len(labels))
    b1 = ax.barh(y, p50_vals, height=0.42, color='#0284C7', label='P50 (Очікуваний медіанний цикл)')
    b2 = ax.barh(y, tail_buffers, left=p50_vals, height=0.42, color='#E11D48', alpha=0.88, label='Хвостовий буфер безпеки (P90 - P50)')
    
    for i in range(len(labels)):
        ax.text(p50_vals[i] / 2., y[i], f"{p50_vals[i]:.1f} дн", ha='center', va='center', color='#FFFFFF', fontweight='bold', fontsize=9.5)
        ax.text(p50_vals[i] + tail_buffers[i] / 2., y[i], f"+{tail_buffers[i]:.1f} дн", ha='center', va='center', color='#FFFFFF', fontweight='bold', fontsize=9.5)
        ax.text(p90_vals[i] + 0.45, y[i], f"P90: {p90_vals[i]:.1f} дн", va='center', color='#991B1B', fontweight='bold', fontsize=10)
        
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10, fontweight='bold')
    ax.invert_yaxis()
    ax.set_xlim(0, 24)
    ax.set_xlabel('Строк закупівлі від оголошення до акцепту (днів)', fontsize=10.5, fontweight='bold', labelpad=8)
    ax.set_title('КАРТКА ПЛАНУВАЛЬНИКА: Скільки часу реально йде на поставку і чого чекати?\nДля БпЛА медіана 6 днів, але для гарантії 90% без дефіциту необхідно закладати 14 днів (+7.9 дн буфера)', 
                 fontsize=11.0, fontweight='bold', pad=14)
    
    # Legend placed strictly at the BOTTOM below the X-axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.16), ncol=2, 
              frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=9.5)
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    
    chart2_path = ARTIFACTS_DIR / "chart2_prediction_card_safety_stock.png"
    fig.savefig(chart2_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved Chart 2 to: {chart2_path}")

    # -------------------------------------------------------------
    # CHART 3: Regional Disparities & Failure Rates
    # -------------------------------------------------------------
    print("Generating Chart 3: Regional Disparities (Spacious Canvas)...")
    fig, (ax_days, ax_fails) = plt.subplots(1, 2, figsize=(12, 6.4), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax_days.set_facecolor('#FFFFFF')
    ax_fails.set_facecolor('#FFFFFF')
    
    regions = [
        ("Київська обл.", 12.0, 22.1, 14.3),
        ("м. Київ", 10.0, 19.0, 14.9),
        ("Хмельницька обл.", 11.1, 21.2, 13.2),
        ("Дніпропетровська обл. (Хаб)", 9.2, 15.0, 12.9),
        ("Львівська обл. (Захід)", 9.0, 17.0, 14.7),
        ("Харківська обл. (Фронт)", 9.2, 17.0, 13.4),
        ("Запорізька обл. (Фронт)", 9.0, 16.3, 15.8),
        ("Одеська обл. (Південь)", 9.9, 16.0, 13.1)
    ]
    
    r_names = [r[0] for r in regions]
    r_p50 = [r[1] for r in regions]
    r_p90 = [r[2] for r in regions]
    r_fail = [r[3] for r in regions]
    
    y_r = np.arange(len(r_names))
    b_p50 = ax_days.barh(y_r - 0.16, r_p50, height=0.3, color='#0284C7', label='P50 Медіана (днів)')
    b_p90 = ax_days.barh(y_r + 0.16, r_p90, height=0.3, color='#E11D48', label='P90 Хвостовий строк (днів)')
    ax_days.set_yticks(y_r)
    ax_days.set_yticklabels(r_names, fontsize=9.5, fontweight='bold')
    ax_days.invert_yaxis()
    ax_days.set_xlim(0, 26)
    ax_days.set_xlabel('Строк циклу (днів)', fontsize=10, fontweight='bold', labelpad=8)
    ax_days.set_title('Розкид Lead Time за регіонами:\nКиїв та Центр мають більший розкид (P90: 22д)', fontsize=10.5, fontweight='bold', pad=12)
    ax_days.grid(axis='x', linestyle='--', alpha=0.5)
    
    # Failure rate plot
    bars_f = ax_fails.barh(y_r, r_fail, height=0.45, color='#F59E0B', alpha=0.9, label='Рівень зривів торгів (Failure Rate %)')
    ax_fails.set_yticks(y_r)
    ax_fails.set_yticklabels([])
    ax_fails.invert_yaxis()
    ax_fails.set_xlabel('Частка зірваних торгів (%)', fontsize=10, fontweight='bold', labelpad=8)
    ax_fails.set_title('Рівень зривів торгів (Failure Rate):\nФронтове Запоріжжя має найвищий ризик (15.8%)', fontsize=10.5, fontweight='bold', pad=12)
    ax_fails.grid(axis='x', linestyle='--', alpha=0.5)
    ax_fails.set_xlim(0, 21)
    
    for bar in bars_f:
        w = bar.get_width()
        ax_fails.text(w + 0.45, bar.get_y() + bar.get_height()/2., f"{w:.1f}%", va='center', fontsize=9, fontweight='bold', color='#B45309')
        
    plt.suptitle('Регіональні відмінності оборонних закупівель ОВТ (Prozorro 2022-2025)', fontsize=12.0, fontweight='bold', y=0.98)
    
    # Unified Legend placed strictly at the BOTTOM across both subplots
    handles = [b_p50, b_p90, bars_f]
    labels = ['P50 Медіана (днів)', 'P90 Хвостовий строк (днів)', 'Частка зірваних торгів (%)']
    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, -0.06), ncol=3,
               frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=9.5)
    
    chart3_path = ARTIFACTS_DIR / "chart3_regional_disparities_map.png"
    fig.savefig(chart3_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved Chart 3 to: {chart3_path}")

    # -------------------------------------------------------------
    # CHART 4: Failure Anatomy (Spacious Canvas)
    # -------------------------------------------------------------
    print("Generating Chart 4: Failure Root Causes (Spacious Canvas)...")
    fig, ax = plt.subplots(figsize=(10, 5.8), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    
    causes = [
        ("Дискваліфікація поданих пропозицій\n(Відхилення комісіями через ТЗ / помилки)", 96.40, "#E11D48"),
        ("Офіційне скасування процедури\n(Неможливість усунення порушень)", 40.94, "#F59E0B"),
        ("Участь лише 1 постачальника\n(Single-bidder ризик відсутності вибору)", 25.10, "#4F46E5"),
        ("Нульова кількість заявок ринку\n(Повний дефіцит пропозицій на ринку)", 0.00, "#64748B")
    ]
    
    c_names = [c[0] for c in causes]
    c_shares = [c[1] for c in causes]
    c_colors = [c[2] for c in causes]
    
    y_c = np.arange(len(c_names))
    b_c = ax.barh(y_c, c_shares, height=0.42, color=c_colors, alpha=0.9)
    ax.set_yticks(y_c)
    ax.set_yticklabels(c_names, fontsize=9.5, fontweight='bold')
    ax.invert_yaxis()
    ax.set_xlim(0, 118)
    ax.set_xlabel('Частка серед 5,911 зірваних конкурентних процедур ОВТ (%)', fontsize=10.5, fontweight='bold', labelpad=10)
    
    # Wrapped title so it never clips on the right or top
    ax.set_title('Анатомія зриву 5,911 оборонних закупівель БпЛА та ОВТ (2022-2025):\n96.4% зривів - це дискваліфікація учасників за формальні невідповідності документації!', 
                 fontsize=10.5, fontweight='bold', pad=14)
    
    for bar in b_c:
        w = bar.get_width()
        ax.text(w + 1.5, bar.get_y() + bar.get_height()/2., f"{w:.1f}%", va='center', fontsize=9.5, fontweight='bold', color='#0F172A')
        
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    chart4_path = ARTIFACTS_DIR / "chart4_failure_anatomy_disqualification.png"
    fig.savefig(chart4_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved Chart 4 to: {chart4_path}")

    # -------------------------------------------------------------
    # PROOF OF WORK CODE CARD (Python Syntax Highlighting + Comments)
    # -------------------------------------------------------------
    print("Generating Multi-Year Code Proof Card (Python Syntax Highlighted)...")
    # Spacious canvas: 11.8 x 8.0 inches for comfortable margins
    fig, ax = plt.subplots(figsize=(11.8, 8.0), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FAFAFA')
    ax.axis('off')

    # Card border
    border_rect = plt.Rectangle((0, 0), 1, 1, facecolor='#FAFAFA', edgecolor='#E2E8F0', linewidth=1.5, transform=ax.transAxes)
    ax.add_patch(border_rect)

    # Mac-style / IDE-style Top Header Bar
    header_rect = plt.Rectangle((0, 0.935), 1, 0.065, facecolor='#F1F5F9', edgecolor='#E2E8F0', linewidth=1.0, transform=ax.transAxes)
    ax.add_patch(header_rect)
    
    # macOS window action dots
    circle_red = plt.Circle((0.025, 0.967), 0.009, facecolor='#EF4444', edgecolor='none', transform=ax.transAxes)
    circle_yellow = plt.Circle((0.042, 0.967), 0.009, facecolor='#F59E0B', edgecolor='none', transform=ax.transAxes)
    circle_green = plt.Circle((0.059, 0.967), 0.009, facecolor='#10B981', edgecolor='none', transform=ax.transAxes)
    ax.add_patch(circle_red)
    ax.add_patch(circle_yellow)
    ax.add_patch(circle_green)

    ax.text(0.08, 0.967, "02_analyze_2022_2025_miltech.py  -  Python 3.12 (Pandas / PyArrow / NumPy)", 
            color='#475569', fontsize=9.2, fontfamily='monospace', transform=ax.transAxes, va='center', fontweight='bold')

    lines_data = [
        # (indent, tokens) -> token: (text, color, weight, style)
        (0.03, [("# 1. ФІЛЬТРАЦІЯ: відсікаємо неконкурентні прямі договори (limited), де строк = 0", "#64748B", "normal", "italic")]),
        (0.03, [
            ("comp_drones", "#0284C7", "bold", "normal"),
            (" = ", "#475569", "normal", "normal"),
            ("df_drones", "#0F172A", "normal", "normal"),
            ("[", "#475569", "normal", "normal"),
            ("df_drones", "#0F172A", "normal", "normal"),
            ("[", "#475569", "normal", "normal"),
            ("'procurement_method'", "#059669", "normal", "normal"),
            ("].", "#475569", "normal", "normal"),
            ("isin", "#2563EB", "bold", "normal"),
            ("([", "#475569", "normal", "normal"),
            ("'open'", "#059669", "normal", "normal"),
            (", ", "#475569", "normal", "normal"),
            ("'selective'", "#059669", "normal", "normal"),
            ("]) & (", "#475569", "normal", "normal"),
            ("df", "#0F172A", "normal", "normal"),
            ("[", "#475569", "normal", "normal"),
            ("'lead_time_days'", "#059669", "normal", "normal"),
            ("] > ", "#475569", "normal", "normal"),
            ("0", "#D97706", "bold", "normal"),
            (")]", "#475569", "normal", "normal")
        ]),
        (0.03, [("#    -> Залишаємо лише відкриті торги ОВТ із валідним позитивним циклом", "#64748B", "normal", "italic")]),
        (0.03, []), # Empty spacer
        (0.03, [("# 2. АГРЕГАЦІЯ: розрахунок річних квантилів та надійності ринку БпЛА / FPV", "#64748B", "normal", "italic")]),
        (0.03, [
            ("drone_stats", "#0284C7", "bold", "normal"),
            (" = ", "#475569", "normal", "normal"),
            ("comp_drones", "#0F172A", "normal", "normal"),
            (".", "#475569", "normal", "normal"),
            ("groupby", "#2563EB", "bold", "normal"),
            ("(", "#475569", "normal", "normal"),
            ("'year'", "#059669", "normal", "normal"),
            (").", "#475569", "normal", "normal"),
            ("agg", "#2563EB", "bold", "normal"),
            ("(", "#475569", "normal", "normal")
        ]),
        (0.05, [
            ("tenders", "#7C3AED", "bold", "normal"),
            ("=(", "#475569", "normal", "normal"),
            ("'tender_id'", "#059669", "normal", "normal"),
            (", ", "#475569", "normal", "normal"),
            ("'count'", "#059669", "normal", "normal"),
            ("),", "#475569", "normal", "normal"),
            ("  # Кількість процедур (масштаб ринку)", "#64748B", "normal", "italic")
        ]),
        (0.05, [
            ("p50_days", "#7C3AED", "bold", "normal"),
            ("=(", "#475569", "normal", "normal"),
            ("'lead_time_cycle_days'", "#059669", "normal", "normal"),
            (", ", "#475569", "normal", "normal"),
            ("lambda", "#7C3AED", "bold", "normal"),
            (" x: np.", "#0F172A", "normal", "normal"),
            ("percentile", "#2563EB", "bold", "normal"),
            ("(x, ", "#475569", "normal", "normal"),
            ("50", "#D97706", "bold", "normal"),
            (")),", "#475569", "normal", "normal"),
            ("  # P50 Медіана (типовий строк закупівлі)", "#64748B", "normal", "italic")
        ]),
        (0.05, [
            ("p90_days", "#7C3AED", "bold", "normal"),
            ("=(", "#475569", "normal", "normal"),
            ("'lead_time_cycle_days'", "#059669", "normal", "normal"),
            (", ", "#475569", "normal", "normal"),
            ("lambda", "#7C3AED", "bold", "normal"),
            (" x: np.", "#0F172A", "normal", "normal"),
            ("percentile", "#2563EB", "bold", "normal"),
            ("(x, ", "#475569", "normal", "normal"),
            ("90", "#D97706", "bold", "normal"),
            (")),", "#475569", "normal", "normal"),
            ("  # P90 Хвіст (гарантія 90% без запізнень)", "#64748B", "normal", "italic")
        ]),
        (0.05, [
            ("single_bidder_rate", "#7C3AED", "bold", "normal"),
            ("=(", "#475569", "normal", "normal"),
            ("'is_single_bidder'", "#059669", "normal", "normal"),
            (", ", "#475569", "normal", "normal"),
            ("lambda", "#7C3AED", "bold", "normal"),
            (" x: x.", "#0F172A", "normal", "normal"),
            ("mean", "#2563EB", "bold", "normal"),
            ("() * ", "#475569", "normal", "normal"),
            ("100", "#D97706", "bold", "normal"),
            ("),", "#475569", "normal", "normal"),
            ("  # Частка торгів з 1 учасником (монополія)", "#64748B", "normal", "italic")
        ]),
        (0.05, [
            ("failure_rate", "#7C3AED", "bold", "normal"),
            ("=(", "#475569", "normal", "normal"),
            ("'is_failed'", "#059669", "normal", "normal"),
            (", ", "#475569", "normal", "normal"),
            ("lambda", "#7C3AED", "bold", "normal"),
            (" x: x.", "#0F172A", "normal", "normal"),
            ("mean", "#2563EB", "bold", "normal"),
            ("() * ", "#475569", "normal", "normal"),
            ("100", "#D97706", "bold", "normal"),
            (")", "#475569", "normal", "normal"),
            ("   # Відсоток зривів торгів (Failure Rate)", "#64748B", "normal", "italic")
        ]),
        (0.03, [(")", "#475569", "normal", "normal")]),
        (0.03, []), # Empty spacer
        (0.03, [("# >>> ЕМПІРИЧНІ РЕЗУЛЬТАТИ ВЕРИФІКАЦІЇ (PROZORRO 2022-2025):", "#0369A1", "bold", "normal")]),
        (0.03, [("# 2022:      17 торгів | P50: 11.1 дн | P90: 16.8 дн | Single-bidder: 58.8% | Failure:  7.5%", "#334155", "normal", "normal")]),
        (0.03, [("# 2023:     836 торгів | P50: 10.0 дн | P90: 18.0 дн | Single-bidder: 37.3% | Failure: 13.4%", "#334155", "normal", "normal")]),
        (0.03, [("# 2024:   3,236 торгів | P50:  6.9 дн | P90: 15.2 дн | Single-bidder: 18.3% | Failure: 16.5%", "#334155", "normal", "normal")]),
        (0.03, [("# 2025:   3,399 торгів | P50:  5.1 дн | P90: 12.0 дн | Single-bidder: 19.5% | Failure: 14.5%", "#334155", "normal", "normal")]),
        (0.03, []), # Empty spacer
        (0.03, [
            ("# >>> ВИСНОВОК ДЛЯ ПЛАНУВАЛЬНИКА: ", "#BE123C", "bold", "normal"),
            ("P50 = 6.0 дн, P90 = 13.9 дн -> Необхідний буфер безпеки = +7.9 діб!", "#BE123C", "bold", "normal")
        ])
    ]

    # Draw code line by line with fine font size
    y_start = 0.89
    line_height = 0.035
    for idx, (x_indent, tokens) in enumerate(lines_data):
        curr_y = y_start - (idx * line_height)
        curr_x = x_indent
        for token_text, color, weight, style in tokens:
            t = ax.text(curr_x, curr_y, token_text, color=color, fontsize=8.4, 
                        fontfamily='monospace', fontweight=weight, fontstyle=style,
                        transform=ax.transAxes, va='center')
            fig.canvas.draw()
            bbox = t.get_window_extent(fig.canvas.get_renderer())
            ax_bbox = ax.get_window_extent(fig.canvas.get_renderer())
            token_width = bbox.width / ax_bbox.width
            curr_x += token_width

    # Bottom summary footer bar
    footer_rect = plt.Rectangle((0, 0), 1, 0.11, facecolor='#F1F5F9', edgecolor='#E2E8F0', linewidth=1.0, transform=ax.transAxes)
    ax.add_patch(footer_rect)
    
    meta_text = (
        "Стек: Python 3.12 (Pandas / PyArrow / NumPy)  |  Об'єм: 384k процедур ОВТ із 12.88 млн рядків 2022-2025\n"
        "Мета: Точний розрахунок буфера Safety Stock  |  Результат: Хвостовий ризик P90 перевищує медіану в 2.3 рази"
    )
    ax.text(0.025, 0.055, meta_text, color='#0F172A', fontsize=8.5, fontfamily='sans-serif', fontweight='bold',
            transform=ax.transAxes, va='center')

    proof_path = PROOFS_DIR / "proof_of_work_multiyear.png"
    fig.savefig(proof_path, dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"Saved Multi-Year Proof to: {proof_path}")

if __name__ == "__main__":
    generate_multiyear_charts()
