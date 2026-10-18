"""
02_analyze_hhi_and_pricing.py
Case 02: Defense Procurement Analytics (Prozorro 2022-2025)

Performs comprehensive empirical and statistical analysis:
1. Multiyear spend dynamics and category breakdown (2022-2025).
2. Defense buyer landscape: Central State Agencies vs Military Units vs Local Municipalities.
3. Supplier market concentration: Herfindahl-Hirschman Index (HHI), CR4, CR5, top vendors.
4. Single-bidder pricing gap: Competitive auction discount vs uncontested single-bidder rate,
   and counterfactual budget savings calculation.

Exports results to: data/processed/procurement_metrics.json
"""

import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import pandas as pd
import numpy as np
from pathlib import Path
import json
import re

CASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = CASE_DIR / "data" / "processed"
PARQUET_IN = DATA_DIR / "procurement_enriched_miltech.parquet"
JSON_OUT = DATA_DIR / "procurement_metrics.json"

def clean_org_name(name):
    n = str(name).strip()
    n = re.sub(r'(?i)товариство з обмеженою відповідальністю\s*', 'ТОВ ', n)
    n = re.sub(r'(?i)приватне акціонерне товариство\s*', 'ПрАТ ', n)
    n = re.sub(r'(?i)публічне акціонерне товариство\s*', 'ПАТ ', n)
    n = re.sub(r'(?i)акціонерне товариство\s*', 'АТ ', n)
    n = re.sub(r'(?i)приватне підприємство\s*', 'ПП ', n)
    return re.sub(r'\s+', ' ', n).strip()

def calculate_hhi(series_val):
    total = series_val.sum()
    if total <= 0:
        return 0.0
    shares = (series_val / total) * 100.0
    return float((shares ** 2).sum())

def run_analysis():
    print(f"--> [ANALYTICS] Loading {PARQUET_IN.name}...")
    df = pd.read_parquet(PARQUET_IN)
    total_records = len(df)
    total_award_b = float(df['award_value'].sum() / 1e9)
    total_tender_b = float(df['tender_value'].sum() / 1e9)
    print(f"    Loaded {total_records:,} tenders | Total Award Value: {total_award_b:.2f} B UAH")

    results = {
        "metadata": {
            "total_records": total_records,
            "total_award_b_uah": round(total_award_b, 2),
            "total_tender_b_uah": round(total_tender_b, 2),
            "timeframe": "2022-2025",
            "currency": "UAH"
        }
    }

    # =========================================================================
    # 1. YEARLY SPEND DYNAMICS
    # =========================================================================
    print("\n--> [ANALYTICS] 1. Calculating Yearly Dynamics (2022-2025)...")
    yearly_dict = {}
    for yr in [2022, 2023, 2024, 2025]:
        df_y = df[df['year'] == yr]
        award_b = float(df_y['award_value'].sum() / 1e9)
        tender_b = float(df_y['tender_value'].sum() / 1e9)
        count = int(len(df_y))
        comp_count = int(df_y['is_competitive'].sum())
        comp_share = round((comp_count / count) * 100, 1) if count > 0 else 0
        yearly_dict[str(yr)] = {
            "tenders": count,
            "award_b_uah": round(award_b, 3),
            "tender_b_uah": round(tender_b, 3),
            "competitive_tenders": comp_count,
            "competitive_share_pct": comp_share
        }
        print(f"    {yr}: {count:,} tenders | {award_b:.2f} B UAH (Comp: {comp_share}%)")
    results["yearly_dynamics"] = yearly_dict

    # =========================================================================
    # 2. CATEGORY BREAKDOWN
    # =========================================================================
    print("\n--> [ANALYTICS] 2. Calculating MilTech Category Breakdown...")
    cat_dict = {}
    for cat_name, group in df.groupby('miltech_category'):
        count = int(len(group))
        award_b = float(group['award_value'].sum() / 1e9)
        share_spend = round((award_b / total_award_b) * 100, 2)
        comp_count = int(group['is_competitive'].sum())
        single_count = int(group['is_single_bidder'].sum())
        cat_dict[cat_name] = {
            "tenders": count,
            "award_b_uah": round(award_b, 3),
            "share_spend_pct": share_spend,
            "competitive_tenders": comp_count,
            "competitive_share_pct": round((comp_count / count) * 100, 1) if count > 0 else 0,
            "single_bidder_tenders": single_count,
            "single_bidder_pct": round((single_count / count) * 100, 1) if count > 0 else 0
        }
        print(f"    {cat_name}: {count:,} tenders | {award_b:.2f} B UAH ({share_spend}%)")
    results["category_breakdown"] = cat_dict

    # =========================================================================
    # 3. BUYER LANDSCAPE
    # =========================================================================
    print("\n--> [ANALYTICS] 3. Calculating Defense Buyer Landscape...")
    buyer_groups_dict = {}
    for bg_name, group in df.groupby('buyer_group'):
        award_b = float(group['award_value'].sum() / 1e9)
        share_spend = round((award_b / total_award_b) * 100, 2)
        count = int(len(group))
        buyer_groups_dict[bg_name] = {
            "tenders": count,
            "award_b_uah": round(award_b, 3),
            "share_spend_pct": share_spend
        }
        print(f"    {bg_name}: {award_b:.2f} B UAH ({share_spend}%) | {count:,} tenders")
    results["buyer_groups"] = buyer_groups_dict

    # Buyer landscape yearly evolution
    bg_yearly = df.pivot_table(index='buyer_group', columns='year', values='award_value', aggfunc=lambda x: x.sum() / 1e9, fill_value=0)
    bg_yearly_dict = {}
    for bg_name in bg_yearly.index:
        bg_yearly_dict[bg_name] = {str(yr): round(float(bg_yearly.loc[bg_name, yr]), 3) for yr in [2022, 2023, 2024, 2025]}
    results["buyer_groups_yearly"] = bg_yearly_dict

    # Drones buyer landscape specifically
    df_drones = df[df['miltech_category'] == 'БпЛА та Дрони (UAV / Drones)'].copy()
    drone_total_b = float(df_drones['award_value'].sum() / 1e9)
    drone_buyer_dict = {}
    for bg_name, group in df_drones.groupby('buyer_group'):
        award_b = float(group['award_value'].sum() / 1e9)
        drone_buyer_dict[bg_name] = {
            "tenders": int(len(group)),
            "award_b_uah": round(award_b, 3),
            "share_pct": round((award_b / drone_total_b) * 100, 2)
        }
    results["drones_buyer_groups"] = drone_buyer_dict

    # Top 100 Buyers Overall
    top_buyers_100 = df.groupby(['buyer_id', 'buyer_name', 'buyer_region', 'buyer_group']).agg(
        tenders=('tender_id', 'count'),
        award_b=('award_value', lambda x: x.sum() / 1e9)
    ).reset_index().sort_values('award_b', ascending=False).head(100)
    top_100_list = [
        {
            "buyer_id": str(r['buyer_id']),
            "buyer_name": clean_org_name(r['buyer_name']),
            "region": str(r['buyer_region']).strip(),
            "buyer_group": str(r['buyer_group']).strip(),
            "tenders": int(r['tenders']),
            "award_b_uah": round(float(r['award_b']), 3),
            "share_pct": round((float(r['award_b']) / total_award_b) * 100, 2)
        }
        for _, r in top_buyers_100.iterrows()
    ]
    results["top_100_buyers"] = top_100_list
    results["top_10_buyers"] = top_100_list[:10]

    # =========================================================================
    # 4. SUPPLIER CONCENTRATION & HHI
    # =========================================================================
    print("\n--> [ANALYTICS] 4. Calculating Market Concentration & HHI...")
    
    # Drones concentration
    drone_supp = df_drones.groupby(['supplier_id', 'supplier_name', 'supplier_region']).agg(
        awards=('tender_id', 'count'),
        award_val_uah=('award_value', 'sum')
    ).reset_index().sort_values('award_val_uah', ascending=False)
    
    drone_total_uah = df_drones['award_value'].sum()
    drone_supp['share_pct'] = (drone_supp['award_val_uah'] / drone_total_uah) * 100.0
    drone_hhi = calculate_hhi(drone_supp['award_val_uah'])
    drone_cr4 = float(drone_supp.head(4)['share_pct'].sum())
    drone_cr5 = float(drone_supp.head(5)['share_pct'].sum())
    drone_cr10 = float(drone_supp.head(10)['share_pct'].sum())

    # Open / Non-masked drones concentration
    drone_open_supp = drone_supp[drone_supp['supplier_name'] != 'Приховано / Не вказано'].copy()
    drone_open_hhi = calculate_hhi(drone_open_supp['award_val_uah'])

    results["drones_concentration"] = {
        "total_award_b_uah": round(drone_total_b, 3),
        "total_suppliers": int(len(drone_supp)),
        "hhi_total": round(drone_hhi, 1),
        "hhi_open_market": round(drone_open_hhi, 1),
        "cr4_pct": round(drone_cr4, 2),
        "cr5_pct": round(drone_cr5, 2),
        "cr10_pct": round(drone_cr10, 2),
        "top_10_suppliers": [
            {
                "supplier_id": r['supplier_id'],
                "supplier_name": str(r['supplier_name']).strip(),
                "region": str(r['supplier_region']).strip(),
                "awards": int(r['awards']),
                "award_m_uah": round(float(r['award_val_uah'] / 1e6), 2),
                "share_pct": round(float(r['share_pct']), 2)
            }
            for _, r in drone_supp.head(10).iterrows()
        ]
    }
    print(f"    Drones Total HHI: {drone_hhi:.1f} | Open Market HHI: {drone_open_hhi:.1f} | CR5: {drone_cr5:.1f}%")

    # EW Concentration
    df_ew = df[df['miltech_category'] == 'РЕБ, РЕР та Тактичні системи (EW / Tactical)'].copy()
    ew_total_b = float(df_ew['award_value'].sum() / 1e9)
    ew_supp = df_ew.groupby(['supplier_id', 'supplier_name', 'supplier_region']).agg(
        awards=('tender_id', 'count'),
        award_val_uah=('award_value', 'sum')
    ).reset_index().sort_values('award_val_uah', ascending=False)
    
    ew_total_uah = df_ew['award_value'].sum()
    ew_supp['share_pct'] = (ew_supp['award_val_uah'] / ew_total_uah) * 100.0
    ew_hhi = calculate_hhi(ew_supp['award_val_uah'])
    ew_cr4 = float(ew_supp.head(4)['share_pct'].sum())
    ew_cr5 = float(ew_supp.head(5)['share_pct'].sum())
    ew_cr10 = float(ew_supp.head(10)['share_pct'].sum())

    results["ew_concentration"] = {
        "total_award_b_uah": round(ew_total_b, 3),
        "total_suppliers": int(len(ew_supp)),
        "hhi_total": round(ew_hhi, 1),
        "cr4_pct": round(ew_cr4, 2),
        "cr5_pct": round(ew_cr5, 2),
        "cr10_pct": round(ew_cr10, 2),
        "top_10_suppliers": [
            {
                "supplier_id": r['supplier_id'],
                "supplier_name": str(r['supplier_name']).strip(),
                "region": str(r['supplier_region']).strip(),
                "awards": int(r['awards']),
                "award_m_uah": round(float(r['award_val_uah'] / 1e6), 2),
                "share_pct": round(float(r['share_pct']), 2)
            }
            for _, r in ew_supp.head(10).iterrows()
        ]
    }
    print(f"    EW HHI: {ew_hhi:.1f} | CR5: {ew_cr5:.1f}% | Top: {ew_supp.iloc[0]['supplier_name']} ({ew_supp.iloc[0]['share_pct']:.1f}%)")

    # =========================================================================
    # 5. SINGLE-BIDDER PRICING GAP & SAVINGS
    # =========================================================================
    print("\n--> [ANALYTICS] 5. Calculating Single-Bidder Savings Gap...")
    comp = df[df['procurement_method'].isin(['open', 'selective'])].copy()
    
    sb0 = comp[comp['is_single_bidder'] == 0]
    sb1 = comp[comp['is_single_bidder'] == 1]
    
    disc0_mean = float(sb0['clean_discount_pct'].mean())
    disc0_med = float(sb0['clean_discount_pct'].median())
    disc1_mean = float(sb1['clean_discount_pct'].mean())
    disc1_med = float(sb1['clean_discount_pct'].median())
    
    gap_pp = round(disc0_mean - disc1_mean, 2)
    sb1_spend_b = float(sb1['award_value'].sum() / 1e9)
    sb0_spend_b = float(sb0['award_value'].sum() / 1e9)
    potential_savings_b = round(sb1_spend_b * (gap_pp / 100.0), 3)

    results["single_bidder_gap"] = {
        "competitive_tenders_total": int(len(comp)),
        "multi_bidder_tenders": int(len(sb0)),
        "single_bidder_tenders": int(len(sb1)),
        "single_bidder_share_pct": round((len(sb1) / len(comp)) * 100, 1),
        "multi_bidder_spend_b_uah": round(sb0_spend_b, 3),
        "single_bidder_spend_b_uah": round(sb1_spend_b, 3),
        "multi_bidder_mean_discount_pct": round(disc0_mean, 2),
        "multi_bidder_median_discount_pct": round(disc0_med, 2),
        "single_bidder_mean_discount_pct": round(disc1_mean, 2),
        "single_bidder_median_discount_pct": round(disc1_med, 2),
        "savings_gap_pp": gap_pp,
        "potential_savings_b_uah": potential_savings_b,
        "potential_savings_m_uah": round(potential_savings_b * 1000, 1)
    }
    print(f"    Multi-Bidder Discount: {disc0_mean:.2f}% vs Single-Bidder: {disc1_mean:.2f}%")
    print(f"    Net Savings Gap: {gap_pp:.2f} percentage points!")
    print(f"    Single-Bidder Spend: {sb1_spend_b:.2f} B UAH -> Potential Savings: {potential_savings_b:.3f} B UAH ({potential_savings_b*1000:.1f} M UAH)")

    # Category-specific Single Bidder Gap
    cat_gap_dict = {}
    for cat_name, group in comp.groupby('miltech_category'):
        c_sb0 = group[group['is_single_bidder'] == 0]
        c_sb1 = group[group['is_single_bidder'] == 1]
        c_disc0 = float(c_sb0['clean_discount_pct'].mean()) if len(c_sb0) > 0 else 0
        c_disc1 = float(c_sb1['clean_discount_pct'].mean()) if len(c_sb1) > 0 else 0
        c_gap = round(c_disc0 - c_disc1, 2)
        c_sb1_spend = float(c_sb1['award_value'].sum() / 1e9)
        c_pot = round(c_sb1_spend * (c_gap / 100.0) * 1000, 1) # in M UAH
        cat_gap_dict[cat_name] = {
            "comp_tenders": int(len(group)),
            "single_bidder_count": int(len(c_sb1)),
            "single_bidder_share_pct": round((len(c_sb1) / len(group)) * 100, 1) if len(group) > 0 else 0,
            "multi_bidder_discount_pct": round(c_disc0, 2),
            "single_bidder_discount_pct": round(c_disc1, 2),
            "savings_gap_pp": c_gap,
            "single_bidder_spend_b_uah": round(c_sb1_spend, 3),
            "potential_savings_m_uah": c_pot
        }
    results["category_single_bidder_gap"] = cat_gap_dict

    # Yearly Single Bidder Evolution
    yearly_gap_dict = {}
    for yr in [2022, 2023, 2024, 2025]:
        y_comp = comp[comp['year'] == yr]
        y_sb0 = y_comp[y_comp['is_single_bidder'] == 0]
        y_sb1 = y_comp[y_comp['is_single_bidder'] == 1]
        y_disc0 = float(y_sb0['clean_discount_pct'].mean()) if len(y_sb0) > 0 else 0
        y_disc1 = float(y_sb1['clean_discount_pct'].mean()) if len(y_sb1) > 0 else 0
        y_gap = round(y_disc0 - y_disc1, 2)
        yearly_gap_dict[str(yr)] = {
            "comp_tenders": int(len(y_comp)),
            "single_bidder_count": int(len(y_sb1)),
            "single_bidder_pct": round((len(y_sb1) / len(y_comp)) * 100, 1) if len(y_comp) > 0 else 0,
            "multi_bidder_discount_pct": round(y_disc0, 2),
            "single_bidder_discount_pct": round(y_disc1, 2),
            "savings_gap_pp": y_gap,
            "single_bidder_spend_b_uah": round(float(y_sb1['award_value'].sum() / 1e9), 3)
        }
    results["yearly_single_bidder_evolution"] = yearly_gap_dict

    # Top 50 Suppliers Overall
    print("--> [ANALYTICS] Computing Top 50 Suppliers Overall...")
    top_supp_50 = df.groupby(['supplier_id', 'supplier_name', 'supplier_region']).agg(
        awards=('tender_id', 'count'),
        award_val=('award_value', 'sum')
    ).reset_index().sort_values('award_val', ascending=False).head(50)
    results["top_50_suppliers"] = [
        {
            "supplier_id": str(r['supplier_id']),
            "supplier_name": clean_org_name(r['supplier_name']),
            "region": str(r['supplier_region']).strip(),
            "awards": int(r['awards']),
            "award_m_uah": round(float(r['award_val'] / 1e6), 2),
            "share_pct": round((float(r['award_val']) / (total_award_b * 1e9)) * 100, 2)
        }
        for _, r in top_supp_50.iterrows()
    ]

    # 6. Interactive Category Bundles for Dynamic Dashboard Filtering
    print("--> [ANALYTICS] Building Interactive Category & Yearly Bundles for Dashboard...")
    cat_keys = {
        'ALL': 'Всі категорії ОВТ',
        'DRONES': 'БпЛА та Дрони (UAV / Drones)',
        'EW': 'РЕБ, РЕР та Тактичні системи (EW / Tactical)',
        'COMMS': 'Тактичний звʼязок та Антени (Comms / Antennas)',
        'COMPONENTS': 'Електроніка та Комплектуючі FPV (Components / Avionics)',
        'GEAR': 'Оборонне спорядження та Захист (Defense Gear)'
    }
    
    cat_bundle = {}
    for code, cat_label in cat_keys.items():
        if code == 'ALL':
            sub = df
            sub_comp = comp
        elif code == 'COMMS':
            sub = df[df['miltech_category'].str.contains('Тактичний зв', na=False)]
            sub_comp = comp[comp['miltech_category'].str.contains('Тактичний зв', na=False)]
        else:
            sub = df[df['miltech_category'] == cat_label]
            sub_comp = comp[comp['miltech_category'] == cat_label]
        
        tot_spend = float(sub['award_value'].sum() / 1e9)
        tot_tenders = int(len(sub))
        
        # HHI
        supp_grp = sub.groupby('supplier_id')['award_value'].sum()
        hhi_val = calculate_hhi(supp_grp)
        
        # Pricing Gap
        sb0 = sub_comp[sub_comp['is_single_bidder'] == 0]
        sb1 = sub_comp[sub_comp['is_single_bidder'] == 1]
        disc0 = float(sb0['clean_discount_pct'].mean()) if len(sb0) > 0 else 0.0
        disc1 = float(sb1['clean_discount_pct'].mean()) if len(sb1) > 0 else 0.0
        c_gap = round(disc0 - disc1, 2)
        sb1_spend = float(sb1['award_value'].sum() / 1e9)
        c_loss_b = round(sb1_spend * (c_gap / 100.0), 3)
        c_loss_m = round(c_loss_b * 1000, 1)
        
        # Yearly dynamics
        yr_spend = [round(float(sub[sub['year'] == y]['award_value'].sum() / 1e9), 2) for y in [2022, 2023, 2024, 2025]]
        yr_tenders = [round(float(len(sub[sub['year'] == y]) / 1000.0), 1) for y in [2022, 2023, 2024, 2025]]
        
        # Buyer groups
        bg_order = [
            'Державні оборонні агенції (State Agencies / MO / AOZ / DOT)',
            'Військові частини (Military Units)',
            'Місцеві громади (Local Municipalities & Regional Admin)',
            'Інші державні органи (Other Public Entities)'
        ]
        bg_vals = [round(float(sub[sub['buyer_group'] == bg]['award_value'].sum() / 1e9), 2) for bg in bg_order]
        
        # Top 7 Suppliers
        top_supp = sub.groupby(['supplier_id', 'supplier_name', 'supplier_region']).agg(
            awards=('tender_id', 'count'),
            val=('award_value', 'sum')
        ).reset_index().sort_values('val', ascending=False).head(7)
        
        supp_list = [
            {
                'name': clean_org_name(r['supplier_name']),
                'id': str(r['supplier_id']),
                'award_m': round(float(r['val'] / 1e6), 1),
                'share_pct': round((float(r['val']) / (tot_spend * 1e9)) * 100, 2) if tot_spend > 0 else 0
            }
            for _, r in top_supp.iterrows()
        ]
        
        # Category top 100 buyers
        top_cat_buyers = sub.groupby(['buyer_id', 'buyer_name', 'buyer_region', 'buyer_group']).agg(
            tenders=('tender_id', 'count'),
            award_b=('award_value', lambda x: x.sum() / 1e9)
        ).reset_index().sort_values('award_b', ascending=False).head(100)
        
        cat_buyers_list = [
            {
                "buyer_id": str(r['buyer_id']),
                "buyer_name": clean_org_name(r['buyer_name']),
                "region": str(r['buyer_region']).strip(),
                "buyer_group": str(r['buyer_group']).strip(),
                "tenders": int(r['tenders']),
                "award_b_uah": round(float(r['award_b']), 3),
                "share_pct": round((float(r['award_b']) / tot_spend) * 100, 2) if tot_spend > 0 else 0
            }
            for _, r in top_cat_buyers.iterrows()
        ]
        
        # By Year breakdown for this category
        by_year_dict = {}
        for y in [2022, 2023, 2024, 2025]:
            y_sub = sub[sub['year'] == y]
            y_comp = sub_comp[sub_comp['year'] == y]
            y_sb0 = y_comp[y_comp['is_single_bidder'] == 0]
            y_sb1 = y_comp[y_comp['is_single_bidder'] == 1]
            y_d0 = float(y_sb0['clean_discount_pct'].mean()) if len(y_sb0) > 0 else 0.0
            y_d1 = float(y_sb1['clean_discount_pct'].mean()) if len(y_sb1) > 0 else 0.0
            y_gap = round(y_d0 - y_d1, 2)
            y_sb1_spend = float(y_sb1['award_value'].sum() / 1e9)
            y_loss = round(y_sb1_spend * (y_gap / 100.0), 3)
            by_year_dict[str(y)] = {
                'spend_b': round(float(y_sub['award_value'].sum() / 1e9), 2),
                'tenders': int(len(y_sub)),
                'comp_disc': round(y_d0, 2),
                'single_disc': round(y_d1, 2),
                'gap_pp': y_gap,
                'loss_b': y_loss,
                'loss_m': round(y_loss * 1000, 1),
                'buyer_groups': [round(float(y_sub[y_sub['buyer_group'] == bg]['award_value'].sum() / 1e9), 2) for bg in bg_order]
            }
        
        cat_bundle[code] = {
            'name': cat_label,
            'kpi': {
                'spend_b': round(tot_spend, 2),
                'tenders': tot_tenders,
                'hhi': round(hhi_val, 1),
                'gap_pp': c_gap,
                'loss_b': c_loss_b,
                'loss_m': c_loss_m,
                'comp_disc': round(disc0, 2),
                'single_disc': round(disc1, 2)
            },
            'yearly': {
                'spend_b': yr_spend,
                'tenders_k': yr_tenders
            },
            'buyer_groups': {
                'labels': ['Державні агенції (АОЗ/ДОТ)', 'Військові частини', 'Місцеві громади', 'Інші органи'],
                'values_b': bg_vals
            },
            'top_suppliers': supp_list,
            'top_buyers': cat_buyers_list,
            'by_year': by_year_dict
        }
    
    results["interactive_categories"] = cat_bundle

    # Save metrics.json
    print(f"\n--> [ANALYTICS] Saving compiled metrics to: {JSON_OUT}")
    with open(JSON_OUT, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("    Done. Metrics successfully exported.")

if __name__ == '__main__':
    run_analysis()
