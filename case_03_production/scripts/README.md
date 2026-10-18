# 🛠️ Case 03: Data Pipeline & Analysis Scripts Registry

Цей каталог містить модульні Python-скрипти аналітичного пайплайну для видобутку даних, моделювання виробничої спроможності (Throughput), оцінки аритмічності постачань, стратифікації ешелонів Tier 1-3 та аналізу складальних вузьких місць для **Кейсу 03 (Defense Production Analytics: 2022-2025)**.

---

## 📋 Основний аналітичний пайплайн (2022-2025 • 384,291 процедура ОВТ)

| Скрипт | Призначення та виконувана операція | Вхідні дані | Згенеровані артефакти |
| :--- | :--- | :--- | :--- |
| **`01_extract_production_metrics.py`** | Збагачення масиву 384,291 процедури ОВТ, об'єднання з реєстрами постачальників та замовників, розрахунок каліброваного фізичного випуску бортів (Unit Price Benchmark model), класифікація партій (Batch Size) та первинне ешелонування виробників. | `tenders_2022_2025_drone_ew_miltech.parquet`, `suppliers.csv`, `buyers.csv` | `data/processed/production_enriched_miltech.parquet` |
| **`02_analyze_throughput_and_capacity.py`** | Статистичне моделювання темпу випуску (Throughput), розрахунок квантилів розміру партій (P25..P90), коефіцієнта грудневої аритмічності (Seasonality Ratio), стратифікація потужностей Tier 1/2/3, аналіз зривів та декомпозиція затримок. | `data/processed/production_enriched_miltech.parquet` | `data/processed/production_analysis_summary.json` |
| **`03_generate_production_charts.py`** | Побудова 4 публікаційних інфографік у роздільній здатності 300 DPI у строгій світлій темі (темп випуску та партії, аритмічність та цикл виконання, ешелони Tier 1-3, вузькі місця виробництва). | `data/processed/production_analysis_summary.json` | `artifacts/chart1_production_throughput_scaling.png`<br>`artifacts/chart2_assembly_cycle_and_rhythmicity.png`<br>`artifacts/chart3_manufacturer_capacity_tiers.png`<br>`artifacts/chart4_production_bottlenecks_and_delays.png` |

---

## ⚙️ Залежності середовища (Environment Dependencies)

- Python 3.10+
- `pandas>=2.2.0`
- `pyarrow>=15.0.0`
- `numpy>=1.26.0`
- `matplotlib>=3.8.0`
