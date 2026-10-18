"""
01_extract_procurement_metrics.py
Case 02: Defense Procurement Analytics (Prozorro 2022-2025)

Loads the 384,291 MilTech tenders dataset, merges with buyers and suppliers master registries,
classifies buyers into functional defense tiers, cleans pricing and discount fields,
and exports the enriched procurement dataset.
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

# Paths
CASE_DIR = Path(__file__).resolve().parent.parent
PORTFOLIO_ROOT = CASE_DIR.parent.parent
DATA_DIR = CASE_DIR / "data" / "processed"
DATA_DIR.mkdir(parents=True, exist_ok=True)

C1_DATA_DIR = PORTFOLIO_ROOT / "cases" / "case_01_supply_chain" / "data"
PARQUET_IN = C1_DATA_DIR / "processed" / "tenders_2022_2025_drone_ew_miltech.parquet"
BUYERS_CSV = C1_DATA_DIR / "raw" / "buyers.csv"
SUPPLIERS_CSV = C1_DATA_DIR / "raw" / "suppliers.csv"

PARQUET_OUT = DATA_DIR / "procurement_enriched_miltech.parquet"

def classify_buyer(row):
    name = str(row.get('buyer_name', '')).lower()
    
    # 1. Military Units (frontline tactical units)
    if any(k in name for k in ['військова частина', 'в/ч', 'полк', 'батальйон', 'бригада']):
        return 'Військові частини (Military Units)'
    
    # 2. Central State Defense Agencies
    if any(k in name for k in [
        'державний оператор тилу', 'агенція оборонних закупівель', 'міністерство оборони',
        'департамент забезпечення державної служби спеціального зв', 'прикордонної служби',
        'національної гвардії', 'національної поліції', 'служби безпеки', 'головний центр',
        'центр авіаційного забезпечення', 'оперативно-рятувальної служби цивільного захисту',
        'фонд розвитку інновацій'
    ]):
        return 'Державні оборонні агенції (State Agencies / MO / AOZ / DOT)'
        
    # 3. Local Municipalities & Regional Administrations (Communities)
    if any(k in name for k in [
        'рада', 'адміністрація', 'ода', 'ова', 'виконавчий комітет', 'міськрада',
        'селищна', 'сільська', 'департамент цивільного захисту', 'управління оборонної роботи',
        'комунальне підприємство', 'департамент муніципальної'
    ]):
        return 'Місцеві громади (Local Municipalities & Regional Admin)'
        
    # 4. Critical Infrastructure SOEs
    if any(k in name for k in ['укргідроенерго', 'енергоатом', 'укренерго', 'залізниця', 'газ', 'нафтогаз']):
        return 'Критична інфраструктура (Critical Infrastructure SOEs)'
        
    # 5. Other Public Entities
    return 'Інші державні органи (Other Public Entities)'

def run_extraction():
    print(f"--> [ETL] Reading source parquet: {PARQUET_IN}")
    cols_to_load = [
        'tender_id', 'ocid', 'year', 'month', 'quarter', 'is_q4',
        'buyer_id', 'procuring_entity_id', 'locality', 'supplier_id',
        'procurement_method', 'award_criteria', 'main_cpv_code',
        'tender_value', 'award_value', 'price_change_amount', 'price_change_pct',
        'number_of_items', 'number_of_tenderers', 'number_of_bids',
        'is_single_bidder', 'is_competitive', 'is_failed',
        'discount_percentage_avg', 'discount_percentage_max',
        'lead_time_cycle_days', 'miltech_category'
    ]
    df = pd.read_parquet(PARQUET_IN, columns=cols_to_load)
    print(f"    Loaded {len(df):,} records.")

    # Merge buyers
    if BUYERS_CSV.exists():
        print(f"--> [ETL] Merging with buyers registry: {BUYERS_CSV.name}")
        df_buyers = pd.read_csv(BUYERS_CSV, usecols=['buyer_id', 'buyer_name', 'buyer_region'], low_memory=False)
        df_buyers['buyer_id'] = df_buyers['buyer_id'].astype(str)
        df['buyer_id'] = df['buyer_id'].astype(str)
        df = df.merge(df_buyers, on='buyer_id', how='left')
    else:
        print("    [WARNING] buyers.csv not found, creating placeholders")
        df['buyer_name'] = 'Невідомий замовник'
        df['buyer_region'] = df['locality']

    # Merge suppliers
    if SUPPLIERS_CSV.exists():
        print(f"--> [ETL] Merging with suppliers registry: {SUPPLIERS_CSV.name}")
        df_supp = pd.read_csv(SUPPLIERS_CSV, usecols=['supplier_id', 'supplier_name', 'supplier_region'], low_memory=False)
        df_supp['supplier_id'] = df_supp['supplier_id'].astype(str)
        df['supplier_id'] = df['supplier_id'].astype(str)
        df = df.merge(df_supp, on='supplier_id', how='left')
    else:
        print("    [WARNING] suppliers.csv not found, creating placeholders")
        df['supplier_name'] = 'Невідомий постачальник'
        df['supplier_region'] = 'Невідомо'

    # Fill missing names
    df['buyer_name'] = df['buyer_name'].fillna('Невідомий замовник')
    df['supplier_name'] = df['supplier_name'].fillna('Приховано / Не вказано')
    df['buyer_region'] = df['buyer_region'].fillna('Невідомо')
    df['supplier_region'] = df['supplier_region'].fillna('Невідомо')

    # Buyer Grouping
    print("--> [ETL] Classifying buyers into functional defense tiers...")
    df['buyer_group'] = df.apply(classify_buyer, axis=1)

    # Clean discount fields
    # discount_percentage_avg in dataset: clip at sensible bounds [0, 95] to remove corrupted negative or 1000% anomalies
    df['clean_discount_pct'] = df['discount_percentage_avg'].clip(lower=0.0, upper=95.0).fillna(0.0)

    # Save output
    print(f"--> [ETL] Writing enriched dataset to: {PARQUET_OUT}")
    df.to_parquet(PARQUET_OUT, index=False, compression='snappy')
    print(f"    Successfully exported {len(df):,} rows ({PARQUET_OUT.stat().st_size / (1024*1024):.2f} MB)")

if __name__ == '__main__':
    run_extraction()
