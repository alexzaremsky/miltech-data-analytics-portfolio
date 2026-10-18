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

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

def analyze_miltech():
    parquet_path = DATA_DIR / "tenders_2022_2025_drone_ew_miltech.parquet"
    print(f"Loading {parquet_path.name}...")
    df = pd.read_parquet(parquet_path)
    print(f"Total MilTech records: {len(df):,}")
    
    # Merge with buyers.csv for regional data
    buyers_path = RAW_DIR / "buyers.csv"
    if buyers_path.exists():
        print("Merging with buyers.csv for buyer_region...")
        df_buyers = pd.read_csv(buyers_path, usecols=['buyer_id', 'buyer_name', 'buyer_region'])
        df_buyers['buyer_id'] = df_buyers['buyer_id'].astype(str)
        df = df.merge(df_buyers, on='buyer_id', how='left')
    
    # 1. Overall breakdown by category
    print("\n" + "="*70)
    print("1. BREAKDOWN BY MILTECH CATEGORY (2022-2025)")
    print("="*70)
    cat_summary = df.groupby('miltech_category').agg(
        total_tenders=('tender_id', 'count'),
        total_value_uah=('award_value', lambda x: x.fillna(0).sum()),
        competitive_tenders=('is_competitive', 'sum'),
        failed_tenders=('is_failed', 'sum')
    )
    cat_summary['total_value_mln_uah'] = cat_summary['total_value_uah'] / 1e6
    cat_summary['failure_rate_pct'] = (cat_summary['failed_tenders'] / cat_summary['total_tenders']) * 100
    print(cat_summary[['total_tenders', 'total_value_mln_uah', 'competitive_tenders', 'failure_rate_pct']])

    # 2. Competitive subset (open / selective)
    comp = df[df['procurement_method'].isin(['open', 'selective'])].copy()
    valid_lead = comp[comp['lead_time_cycle_days'] > 0].copy()
    
    print("\n" + "="*70)
    print("2. YEAR-BY-YEAR EVOLUTION OF COMPETITIVE MILTECH PROCUREMENT (2022-2025)")
    print("="*70)
    yearly = valid_lead.groupby('year').agg(
        count=('tender_id', 'count'),
        p50_days=('lead_time_cycle_days', lambda x: np.percentile(x, 50)),
        p75_days=('lead_time_cycle_days', lambda x: np.percentile(x, 75)),
        p90_days=('lead_time_cycle_days', lambda x: np.percentile(x, 90)),
        mean_days=('lead_time_cycle_days', 'mean'),
        single_bidder_rate=('is_single_bidder', lambda x: x.mean() * 100),
        avg_discount_pct=('price_change_pct', lambda x: x.median())
    )
    # Failure rate across all competitive tenders per year
    comp_yearly_fail = comp.groupby('year')['is_failed'].agg(
        total_comp='count',
        failed_count='sum',
        fail_pct=lambda x: x.mean() * 100
    )
    yearly = yearly.join(comp_yearly_fail[['fail_pct']])
    print(yearly)

    # 3. DRONES & UAVs SPECIFICALLY (CPV 3471... / 3561...)
    print("\n" + "="*70)
    print("3. DRONES & UAVs SPECIFIC DEEP DIVE (2022-2025)")
    print("="*70)
    df_drones = df[df['miltech_category'] == 'БпЛА та Дрони (UAV / Drones)'].copy()
    print(f"Total Drone / UAV Tenders: {len(df_drones):,}")
    print("Procurement methods:\n", df_drones['procurement_method'].value_counts())
    
    comp_drones = df_drones[df_drones['procurement_method'].isin(['open', 'selective']) & (df_drones['lead_time_cycle_days'] > 0)]
    print(f"Competitive Drone Tenders: {len(comp_drones):,}")
    
    drones_yearly = comp_drones.groupby('year').agg(
        count=('tender_id', 'count'),
        p50=('lead_time_cycle_days', lambda x: np.percentile(x, 50)),
        p75=('lead_time_cycle_days', lambda x: np.percentile(x, 75)),
        p90=('lead_time_cycle_days', lambda x: np.percentile(x, 90)),
        bidding_p50=('bidding_window_days', lambda x: np.percentile(x.dropna(), 50)),
        eval_p50=('eval_window_days', lambda x: np.percentile(x.dropna(), 50)),
        single_bidder_rate=('is_single_bidder', lambda x: x.mean() * 100),
        discount_med=('price_change_pct', lambda x: x.median())
    )
    drone_fails = df_drones[df_drones['procurement_method'].isin(['open', 'selective'])].groupby('year')['is_failed'].agg(
        fail_rate=lambda x: x.mean() * 100
    )
    drones_yearly = drones_yearly.join(drone_fails)
    print(drones_yearly)

    # 4. EW & TACTICAL SYSTEMS (CPV 3573... / 3574...)
    print("\n" + "="*70)
    print("4. EW & TACTICAL SYSTEMS DEEP DIVE (2022-2025)")
    print("="*70)
    df_ew = df[df['miltech_category'] == 'РЕБ, РЕР та Тактичні системи (EW / Tactical)'].copy()
    comp_ew = df_ew[df_ew['procurement_method'].isin(['open', 'selective']) & (df_ew['lead_time_cycle_days'] > 0)]
    print(f"Total EW tenders: {len(df_ew):,} | Competitive: {len(comp_ew):,}")
    if len(comp_ew) > 0:
        ew_yearly = comp_ew.groupby('year').agg(
            count=('tender_id', 'count'),
            p50=('lead_time_cycle_days', lambda x: np.percentile(x, 50)),
            p90=('lead_time_cycle_days', lambda x: np.percentile(x, 90))
        )
        print(ew_yearly)

    # 5. REGIONAL LOGISTICS DISPARITIES
    print("\n" + "="*70)
    print("5. REGIONAL DISPARITIES (LEAD TIME & FAILURE RATE)")
    print("="*70)
    if 'buyer_region' in comp.columns:
        valid_comp_reg = comp[comp['lead_time_cycle_days'] > 0].copy()
        top_regions = valid_comp_reg['buyer_region'].value_counts().head(10).index
        reg_stats = valid_comp_reg[valid_comp_reg['buyer_region'].isin(top_regions)].groupby('buyer_region').agg(
            tenders=('tender_id', 'count'),
            p50_days=('lead_time_cycle_days', lambda x: np.percentile(x, 50)),
            p90_days=('lead_time_cycle_days', lambda x: np.percentile(x, 90)),
            fail_pct=('is_failed', lambda x: x.mean() * 100)
        ).sort_values(by='tenders', ascending=False)
        print(reg_stats)

    # 6. ROOT CAUSES OF PROCEDURE FAILURE
    print("\n" + "="*70)
    print("6. ROOT CAUSES OF DISRUPTED TENDERS (COMPETITIVE)")
    print("="*70)
    failed_comp = comp[comp['is_failed'] == True]
    disq_count = (failed_comp['has_unsuccessful_awards'] == 1).sum()
    canc_count = (failed_comp['has_cancelled_awards'] == 1).sum()
    zero_bid_count = (failed_comp['number_of_tenderers'] == 0).sum()
    print(f"Total Disrupted Competitive Procedures: {len(failed_comp):,}")
    print(f"  - Disqualification of bidders (has_unsuccessful_awards == 1): {disq_count:,} ({disq_count/len(failed_comp)*100:.2f}%)")
    print(f"  - Official Cancellation (has_cancelled_awards == 1): {canc_count:,} ({canc_count/len(failed_comp)*100:.2f}%)")
    print(f"  - Zero participants submitted: {zero_bid_count:,} ({zero_bid_count/len(failed_comp)*100:.2f}%)")

    # 7. THE PLANNER'S DECISION FORMULA (Передбачуваність постачання)
    print("\n" + "="*70)
    print("7. THE LOGISTICS PLANNER'S PREDICTION CARD")
    print("="*70)
    drone_p50 = float(np.percentile(comp_drones['lead_time_cycle_days'], 50))
    drone_p90 = float(np.percentile(comp_drones['lead_time_cycle_days'], 90))
    drone_tail_gap = drone_p90 - drone_p50
    
    print(f"DRONES (БпЛА):")
    print(f"  - Expected Cycle (P50): {drone_p50:.1f} days")
    print(f"  - High Confidence Cycle (P90): {drone_p90:.1f} days")
    print(f"  - Recommended Safety Stock Buffer: {drone_tail_gap:.1f} days (+{drone_tail_gap/drone_p50*100:.1f}%)")
    print(f"  - Failure probability: {df_drones[df_drones['procurement_method'].isin(['open', 'selective'])]['is_failed'].mean()*100:.2f}%")
    
    # Save master metrics JSON
    master_metrics = {
        "dataset_years": "2022-2025",
        "total_miltech_tenders": len(df),
        "total_competitive_miltech": len(comp),
        "drones_total_tenders": len(df_drones),
        "drones_competitive_tenders": len(comp_drones),
        "drone_lead_time_p50": drone_p50,
        "drone_lead_time_p90": drone_p90,
        "drone_tail_gap_days": drone_tail_gap,
        "drone_failure_rate_pct": float(df_drones[df_drones['procurement_method'].isin(['open', 'selective'])]['is_failed'].mean()*100),
        "ew_total_tenders": len(df_ew),
        "ew_competitive_tenders": len(comp_ew),
        "ew_lead_time_p50": float(np.percentile(comp_ew['lead_time_cycle_days'], 50)) if len(comp_ew) > 0 else 10.0,
        "ew_lead_time_p90": float(np.percentile(comp_ew['lead_time_cycle_days'], 90)) if len(comp_ew) > 0 else 15.0,
        "yearly_evolution": yearly.to_dict(orient='index'),
        "drones_evolution": drones_yearly.to_dict(orient='index')
    }
    
    out_json = DATA_DIR / "case_01_multiyear_metrics.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(master_metrics, f, indent=2, ensure_ascii=False)
    print(f"\nMaster metrics saved to: {out_json}")

if __name__ == "__main__":
    analyze_miltech()
