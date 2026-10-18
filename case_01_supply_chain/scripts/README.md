# 🛠️ Case 01: Data Pipeline & Analysis Scripts Registry

Цей каталог містить модульні Python-скрипти аналітичного пайплайну для видобутку, квантильного моделювання та візуалізації даних для **Кейсу 1 (Supply Chain & Lead Time Analytics: Prozorro 2022-2025)**.

---

## 📋 Основний аналітичний пайплайн (2022-2025 • 5.44 GB • 12.88M процедур)

| Скрипт | Призначення та виконувана операція | Вхідні дані | Згенеровані артефакти |
| :--- | :--- | :--- | :--- |
| **`01_extract_2022_2025_miltech.py`** | Пакетне сканування 12,877,960 рядків за 4 роки (2022-2025). Векторизована фільтрація 384,291 процедури ОВТ за профільними CPV-кодами та ключовими словами (БпЛА, FPV, РЕБ, антени, зв'язок, масковані закупівлі ВЧ). | `data/raw/tenders_202*.csv` (з [Kaggle](https://www.kaggle.com/datasets/romankachmar/prozorro-ukraine-procurement-2022-2025)) | `data/processed/tenders_2022_2025_drone_ew_miltech.parquet` |
| **`02_analyze_2022_2025_miltech.py`** | Векторизований розрахунок квантилів P50, P75, P90 Lead Time, двоетапної декомпозиції циклу, річної еволюції ринку БпЛА, анатомії причин зривів (5,911 торгів) та регіонального зрізу. | Parquet DWH | `data/processed/case_01_multiyear_metrics.json` |
| **`03_generate_multiyear_charts.py`** | Побудова 4 аналітичних інфографік у роздільній здатності 300 DPI у світлій темі та картки верифікації коду (Proof of Work). | Parquet DWH, JSON-метрики | `artifacts/chart1..4_*.png` |

---

## ⚙️ Залежності середовища (Environment Dependencies)
- Python 3.12+
- `pandas>=2.2.0`
- `pyarrow>=15.0.0`
- `numpy>=1.26.0`
- `matplotlib>=3.8.0`
- `seaborn>=0.13.0`

