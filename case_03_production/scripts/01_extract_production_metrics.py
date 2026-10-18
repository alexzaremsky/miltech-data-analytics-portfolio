"""
01_extract_production_metrics.py
Case 03: Defense Production Analytics: Manufacturing Throughput, Capacity Scaling & Assembly Bottlenecks (2022-2025)

Processes 384,291 MilTech tenders, merges supplier registries, calculates calibrated physical production
units (UAVs, EW, Avionics), segments batch sizes, classifies manufacturer capacity tiers (Tier 1, Tier 2, Tier 3),
and exports the enriched production dataset.
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
import time

# Paths
CASE_DIR = Path(__file__).resolve().parent.parent
PORTFOLIO_ROOT = CASE_DIR.parent.parent
DATA_DIR = CASE_DIR / "data" / "processed"
DATA_DIR.mkdir(parents=True, exist_ok=True)

C1_DATA_DIR = PORTFOLIO_ROOT / "cases" / "case_01_supply_chain" / "data"
PARQUET_IN = C1_DATA_DIR / "processed" / "tenders_2022_2025_drone_ew_miltech.parquet"
SUPPLIERS_CSV = C1_DATA_DIR / "raw" / "suppliers.csv"
BUYERS_CSV = C1_DATA_DIR / "raw" / "buyers.csv"

PARQUET_OUT = DATA_DIR / "production_enriched_miltech.parquet"

# Calibrated unit cost benchmarks (UAH) reflecting component deflation and economies of scale (2022-2025)
UAV_COST_MAP = {
    2022: 85000,   # Initial market: predominantly commercial recon quadcopters (Mavic/Matrice)
    2023: 35000,   # Emerging FPV sector alongside tactical recon platforms
    2024: 22000,   # Mass-scale FPV standardisation and localized frame production
    2025: 18000    # Industrial volume scaling, direct component supply chains
}

EW_COST_MAP = {
    2022: 250000,  # Specialized initial tactical systems
    2023: 200000,  # Proliferation of modular anti-drone systems
    2024: 160000,  # Trench EW (окопний РЕБ) mass adoption
    2025: 130000   # Multi-band serial jammer dome systems
}

def calculate_physical_units(row):
    """
    Estimates physical output units (бортів/комплексів) based on awarded contract value,
    calibrated benchmark costs per category and year, and raw lot items.
    """
    val = row['award_value']
    cat = row['miltech_category']
    yr = int(row['year'])
    lot_items = int(row.get('number_of_items', 1))
    
    if val <= 0 or pd.isna(val):
        return 0
        
    if cat == 'БпЛА та Дрони (UAV / Drones)':
        bench = UAV_COST_MAP.get(yr, 20000)
        units = int(round(val / bench))
        return max(lot_items, max(1, units))
        
    elif cat == 'РЕБ, РЕР та Тактичні системи (EW / Tactical)':
        bench = EW_COST_MAP.get(yr, 150000)
        units = int(round(val / bench))
        return max(lot_items, max(1, units))
        
    elif cat == 'Електроніка та Комплектуючі FPV (Components / Avionics)':
        # Avionics, motors, ESCs, antennas, cameras (~2,500 UAH per component unit)
        units = int(round(val / 2500))
        return max(lot_items, max(1, units))
        
    else:
        # Defense gear, tactical comms, masked tenders: use lot item count
        return max(1, lot_items)

def classify_batch_size(units):
    """Classifies physical lot into production batch size bands."""
    if units <= 10:
        return 'Micro (1-10 шт)'
    elif units <= 50:
        return 'Tactical (11-50 шт)'
    elif units <= 250:
        return 'Serial (51-250 шт)'
    elif units <= 1000:
        return 'Large Serial (251-1,000 шт)'
    else:
        return 'Industrial Mega (>1,000 шт)'

def run_extraction():
    start_time = time.time()
    print("=" * 75)
    print("STEP 01: EXTRACTING & ENRICHING DEFENSE PRODUCTION DATASET (2022-2025)")
    print("=" * 75)
    
    print(f"--> [ETL] Reading source parquet: {PARQUET_IN}")
    cols_to_load = [
        'tender_id', 'ocid', 'year', 'month', 'quarter', 'is_q4', 'is_december',
        'buyer_id', 'procuring_entity_id', 'locality', 'supplier_id',
        'procurement_method', 'award_criteria', 'main_cpv_code',
        'tender_value', 'award_value', 'price_change_amount', 'price_change_pct',
        'number_of_items', 'number_of_tenderers', 'number_of_bids',
        'is_single_bidder', 'is_competitive', 'is_failed',
        'lead_time_cycle_days', 'pub_to_awd_days', 'miltech_category'
    ]
    df = pd.read_parquet(PARQUET_IN, columns=cols_to_load)
    print(f"--> [ETL] Loaded {len(df):,} raw records.")
    
    # 1. Join Suppliers Master Registry
    print(f"--> [ETL] Merging supplier registry: {SUPPLIERS_CSV}")
    if SUPPLIERS_CSV.exists():
        sup_df = pd.read_csv(SUPPLIERS_CSV, usecols=['supplier_id', 'supplier_name', 'supplier_region'])
        sup_df['supplier_id'] = sup_df['supplier_id'].astype(str)
        df['supplier_id'] = df['supplier_id'].astype(str)
        df = df.merge(sup_df, on='supplier_id', how='left')
        df['supplier_name'] = df['supplier_name'].fillna('Невідомий постачальник / FOP')
        df['supplier_region'] = df['supplier_region'].fillna('Не вказано')
    else:
        df['supplier_name'] = 'Постачальник ' + df['supplier_id'].astype(str)
        df['supplier_region'] = 'Не вказано'
        
    # 2. Join Buyers Master Registry
    print(f"--> [ETL] Merging buyer registry: {BUYERS_CSV}")
    if BUYERS_CSV.exists():
        buyer_df = pd.read_csv(BUYERS_CSV, usecols=['buyer_id', 'buyer_name', 'buyer_region'])
        buyer_df['buyer_id'] = buyer_df['buyer_id'].astype(str)
        df['buyer_id'] = df['buyer_id'].astype(str)
        df = df.merge(buyer_df, on='buyer_id', how='left')
        df['buyer_name'] = df['buyer_name'].fillna('Державний замовник')
        df['buyer_region'] = df['buyer_region'].fillna('Не вказано')
    else:
        df['buyer_name'] = 'Замовник ' + df['buyer_id'].astype(str)
        df['buyer_region'] = 'Не вказано'
        
    # 3. Model Physical Output Units & Unit Price
    print("--> [CALC] Modeling physical output units (Throughput) & Unit Prices...")
    df['est_physical_units'] = df.apply(calculate_physical_units, axis=1)
    df['effective_unit_price'] = np.where(
        df['est_physical_units'] > 0,
        df['award_value'] / df['est_physical_units'],
        df['award_value']
    )
    df['batch_tier'] = df['est_physical_units'].apply(classify_batch_size)
    
    # 4. Supplier Annual Run-Rate & Capacity Tiering
    print("--> [CALC] Stratifying manufacturer capacity tiers (Tier 1 / Tier 2 / Tier 3)...")
    # Calculate total physical units per supplier across UAVs, EW, and MilTech equipment
    miltech_equip_mask = df['miltech_category'].isin([
        'БпЛА та Дрони (UAV / Drones)',
        'РЕБ, РЕР та Тактичні системи (EW / Tactical)'
    ])
    sup_totals = df[miltech_equip_mask].groupby('supplier_id')['est_physical_units'].sum().to_dict()
    
    def assign_tier(sup_id):
        tot = sup_totals.get(str(sup_id), 0)
        if tot >= 10000:
            return 'Tier 1 (High-Scale: >10k шт)'
        elif tot >= 1000:
            return 'Tier 2 (Mid-Scale: 1k-10k шт)'
        elif tot > 0:
            return 'Tier 3 (SME / Garage: <1k шт)'
        else:
            return 'Non-Equipment / Ancillary'
            
    df['manufacturer_tier'] = df['supplier_id'].apply(assign_tier)
    
    # 5. Production Rhythmicity Metrics
    # Month name & Quarter string
    month_names = {
        1: 'Січ', 2: 'Лют', 3: 'Бер', 4: 'Кві', 5: 'Тра', 6: 'Чер',
        7: 'Лип', 8: 'Сер', 9: 'Вер', 10: 'Жов', 11: 'Лис', 12: 'Гру'
    }
    df['month_name'] = df['month'].map(month_names)
    df['period_ym'] = df['year'].astype(str) + '-' + df['month'].astype(str).str.zfill(2)
    
    # 6. Cycle Metrics
    df['clean_cycle_days'] = df['lead_time_cycle_days'].clip(lower=1, upper=120)
    
    # Save enriched parquet
    print(f"--> [SAVE] Exporting enriched production dataset to: {PARQUET_OUT}")
    df.to_parquet(PARQUET_OUT, index=False, engine='pyarrow')
    file_size_mb = PARQUET_OUT.stat().st_size / (1024 * 1024)
    print(f"--> [DONE] Successfully exported {len(df):,} rows ({file_size_mb:.2f} MB) in {time.time() - start_time:.1f}s.")
    
    # Quick Validation Report
    print("\n--- VALIDATION SUMMARY ---")
    uav_df = df[df['miltech_category'] == 'БпЛА та Дрони (UAV / Drones)']
    ew_df = df[df['miltech_category'] == 'РЕБ, РЕР та Тактичні системи (EW / Tactical)']
    print(f"Total UAV Contracts: {len(uav_df):,} | Estimated Drones: {uav_df['est_physical_units'].sum():,} шт | Total Value: {uav_df['award_value'].sum()/1e9:.2f} млрд грн")
    print(f"Total EW Contracts: {len(ew_df):,} | Estimated EW Systems: {ew_df['est_physical_units'].sum():,} шт | Total Value: {ew_df['award_value'].sum()/1e9:.2f} млрд грн")
    
    print("\nManufacturer Tier Distribution (UAV & EW suppliers):")
    tier_counts = df[miltech_equip_mask].groupby('manufacturer_tier').agg(
        suppliers=('supplier_id', 'nunique'),
        units=('est_physical_units', 'sum'),
        value_bln=('award_value', lambda x: x.sum() / 1e9)
    ).loc[['Tier 1 (High-Scale: >10k шт)', 'Tier 2 (Mid-Scale: 1k-10k шт)', 'Tier 3 (SME / Garage: <1k шт)']]
    print(tier_counts)

if __name__ == '__main__':
    run_extraction()
