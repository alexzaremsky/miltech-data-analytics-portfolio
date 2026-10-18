# 🛠️ Case 02: Data Pipeline & Analysis Scripts Registry

Цей каталог містить модульні Python-скрипти аналітичного пайплайну для видобутку даних, розрахунку ринкової концентрації HHI та оцінки цінового розриву Single-Bidder для **Кейсу 02 (Defense Procurement Analytics: Prozorro 2022-2025)**.

---

## 📋 Основний аналітичний пайплайн (2022-2025 • 384,291 процедура ОВТ)

| Скрипт | Призначення та виконувана операція | Вхідні дані | Згенеровані артефакти |
| :--- | :--- | :--- | :--- |
| **`01_extract_procurement_metrics.py`** | Збагачення масиву 384,291 процедури ОВТ, об'єднання з реєстрами замовників та постачальників, функціональна класифікація замовників за 5 рівнями (Центральні агенції, Військові частини, Місцеві громади, Інфраструктура, Інші органи). | `tenders_2022_2025_drone_ew_miltech.parquet`, `buyers.csv`, `suppliers.csv` | `data/processed/procurement_enriched_miltech.parquet` |
| **`02_analyze_hhi_and_pricing.py`** | Статистичний розрахунок річної динаміки витрат (2022-2025), структури попиту, індексу Герфіндаля-Хіршмана (HHI) для ринків БпЛА та РЕБ, часток CR4/CR5 та контрфактичної економії Single-Bidder Savings Gap. | `data/processed/procurement_enriched_miltech.parquet` | `data/processed/procurement_metrics.json` |
| **`03_generate_procurement_charts.py`** | Побудова 4 аналітичних інфографік у роздільній здатності 300 DPI (динаміка бюджетів, ландшафт замовників, концентрація ринку та розрив економії торгів). | `data/processed/procurement_metrics.json` | `artifacts/chart1_market_spend_dynamics_2022_2025.png`<br>`artifacts/chart2_buyers_structure_state_vs_local.png`<br>`artifacts/chart3_hhi_market_concentration_curve.png`<br>`artifacts/chart4_single_bidder_savings_gap.png` |

---

## ⚙️ Залежності середовища (Environment Dependencies)

- Python 3.10+
- `pandas>=2.2.0`
- `pyarrow>=15.0.0`
- `numpy>=1.26.0`
- `matplotlib>=3.8.0`
