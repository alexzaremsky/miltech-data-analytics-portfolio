import pandas as pd
import numpy as np
from pathlib import Path
import time

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

USECOLS = [
    'tender_id', 'ocid', 'published_date', 
    'tender_start_date', 'tender_end_date', 'award_date',
    'year', 'month', 'quarter', 'day_of_week', 'is_q4', 'is_december',
    'buyer_id', 'procuring_entity_id', 'locality', 'supplier_id',
    'procurement_method', 'main_procurement_category', 'award_criteria',
    'main_cpv_code', 'main_cpv_2_digit', 'main_cpv_4_digit',
    'tender_value', 'award_value', 'price_change_amount', 'price_change_pct',
    'currency', 'number_of_items', 'number_of_tenderers', 'number_of_bids',
    'number_of_awards', 'number_of_contracts', 'number_of_documents',
    'is_single_bidder', 'is_competitive', 'is_cross_region', 'has_enquiries',
    'is_buyer_masked', 'is_supplier_masked', 'has_multiple_awards',
    'award_value_total', 'award_value_max', 'award_value_min',
    'discount_percentage_avg', 'discount_percentage_max',
    'has_unsuccessful_awards', 'has_cancelled_awards', 'active_awards_count'
]

# Exact CPV classification for UAVs, EW, Comms, Tactical Components:
def classify_miltech_category(cpv_code, is_masked):
    if not isinstance(cpv_code, str):
        cpv_code = ""
        
    if cpv_code.startswith(('3471', '3561')):
        return 'БпЛА та Дрони (UAV / Drones)'
    elif cpv_code.startswith(('3573', '3574', '3570', '3571', '3572')):
        return 'РЕБ, РЕР та Тактичні системи (EW / Tactical)'
    elif cpv_code.startswith(('325', '323')):
        return 'Тактичний звʼязок та Антени (Comms / Antennas)'
    elif cpv_code.startswith(('3023', '316', '317')):
        return 'Електроніка та Комплектуючі FPV (Components / Avionics)'
    elif cpv_code.startswith(('358', '351', '352', '353', '354', '355')):
        return 'Оборонне спорядження та Захист (Defense Gear)'
    elif is_masked:
        return 'Засекречені закупівлі ОВТ (Masked Military)'
    else:
        return 'Other'

def run_extraction():
    start_time = time.time()
    years = [2022, 2023, 2024, 2025]
    all_records = []
    
    print("="*70)
    print("STARTING FULL 4-YEAR EXTRACTION (Prozorro 2022-2025)")
    print("="*70)
    
    for yr in years:
        file_path = RAW_DIR / f"tenders_{yr}.csv"
        if not file_path.exists():
            print(f"WARNING: {file_path.name} not found! Skipping...")
            continue
            
        print(f"\nProcessing {file_path.name} ({file_path.stat().st_size / (1024*1024):.1f} MB)...")
        chunksize = 250000
        yr_count = 0
        yr_captured = 0
        
        for chunk in pd.read_csv(file_path, usecols=USECOLS, chunksize=chunksize, low_memory=False):
            yr_count += len(chunk)
            
            # Mask for MilTech target items
            # 1. UAVs / Aircraft: CPV starts with 3471 or 3561
            # 2. EW / Radar / Tactical electronics: CPV starts with 357
            # 3. Comms / Radio: CPV starts with 325
            # 4. Components / Electronics: CPV starts with 3023, 316, 317
            # 5. Defense gear / weaponry: CPV starts with 351, 352, 353, 354, 355, 358
            # 6. Masked military tenders: is_buyer_masked == 1 or is_supplier_masked == 1
            
            cpv_str = chunk['main_cpv_code'].astype(str)
            mask = (
                cpv_str.str.startswith(('3471', '3561', '357', '325', '3023', '316', '317', '351', '352', '353', '354', '355', '358')) |
                (chunk['is_buyer_masked'] == 1) |
                (chunk['is_supplier_masked'] == 1)
            )
            
            filtered = chunk[mask].copy()
            yr_captured += len(filtered)
            all_records.append(filtered)
            
        print(f"  Year {yr}: Scanned {yr_count:,} rows | Captured {yr_captured:,} MilTech/UAV/EW tenders")
        
    df = pd.concat(all_records, ignore_index=True)
    print("\n" + "="*70)
    print(f"TOTAL 2022-2025 MILTECH TENDERS CAPTURED: {len(df):,}")
    print("="*70)
    
    # Dates parsing
    print("Parsing timestamps to UTC...")
    df['pub_dt'] = pd.to_datetime(df['published_date'], errors='coerce', utc=True)
    df['t_start_dt'] = pd.to_datetime(df['tender_start_date'], errors='coerce', utc=True)
    df['t_end_dt'] = pd.to_datetime(df['tender_end_date'], errors='coerce', utc=True)
    df['awd_dt'] = pd.to_datetime(df['award_date'], errors='coerce', utc=True)
    
    # Calculate durations (days)
    # Total cycle for competitive (open / selective): t_start_dt -> awd_dt
    df['lead_time_cycle_days'] = (df['awd_dt'] - df['t_start_dt']).dt.total_seconds() / 86400.0
    df['bidding_window_days'] = (df['t_end_dt'] - df['t_start_dt']).dt.total_seconds() / 86400.0
    df['eval_window_days'] = (df['awd_dt'] - df['t_end_dt']).dt.total_seconds() / 86400.0
    
    # Direct contract lead time (for limited: published to award)
    df['pub_to_awd_days'] = (df['awd_dt'] - df['pub_dt']).dt.total_seconds() / 86400.0
    
    # Categorization
    print("Assigning MilTech taxonomy...")
    df['miltech_category'] = [
        classify_miltech_category(c, m) for c, m in zip(df['main_cpv_code'], (df['is_buyer_masked'] == 1) | (df['is_supplier_masked'] == 1))
    ]
    
    # Failure flag
    df['is_failed'] = (
        (df['active_awards_count'] == 0) | 
        (df['has_cancelled_awards'] == 1) | 
        (df['has_unsuccessful_awards'] == 1) | 
        (df['award_value'].isna())
    )
    
    # Sanitize string and object columns for PyArrow
    print("Sanitizing object columns for PyArrow...")
    str_cols = ['tender_id', 'ocid', 'buyer_id', 'procuring_entity_id', 'locality', 'supplier_id', 'procurement_method', 'main_procurement_category', 'award_criteria', 'main_cpv_code', 'currency', 'miltech_category']
    for c in str_cols:
        if c in df.columns:
            df[c] = df[c].fillna('').astype(str)

    # Save output parquet
    out_parquet = PROCESSED_DIR / "tenders_2022_2025_drone_ew_miltech.parquet"
    df.to_parquet(out_parquet, index=False)
    print(f"\nSaved consolidated 4-year parquet to: {out_parquet}")
    print(f"File size: {out_parquet.stat().st_size / (1024*1024):.2f} MB")
    print(f"Extraction completed in {time.time() - start_time:.1f} seconds")

if __name__ == "__main__":
    run_extraction()
