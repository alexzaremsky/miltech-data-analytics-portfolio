# 🛡️ MilTech & DefTech Data Analytics Portfolio

> **Decision-Support Systems, Empirical Defense Logistics & Market Intelligence**  
> *Portfolio of practical data analytics cases developed within the MilTech & DefTech Data Analytics Program (Choice31 x IAMPM).*  
> **Author:** Alex Zaremsky ([LinkedIn](https://www.linkedin.com/in/alexander-zaremsky/) | [GitHub](https://github.com/alexzaremsky))

---

## 🧭 Practical Portfolio Cases

### 📦 Case 01: Defense Supply Chain & Lead Time Analytics (Prozorro 2022-2025)
*Empirical analysis of 12.88M public procurement procedures with a specialized focus on 384,291 MilTech/UAV/EW procedures.*  

- **Key Objective:** Calculate real empirical lead times and determine the required safety stock buffer for defense planners.
- **Key Finding (Lead Time):** Median drone lead time is **6.0 days**, but tail risk (P90) extends to **13.9 days** -> requires a **Safety Stock buffer of +7.9 days (+132% above median)**.
- **Root Cause of Failures:** Across 5,911 failed defense tenders, **96.4% failed due to formal disqualifications by tender committees**, whereas zero-supplier shortage accounted for 0.0%.
- **Decision Framework:** Deployed dynamic Re-order Point (ROP) model transitioning procurement planning from reactive ordering to empirical P90 protection.

#### Case 01 Artifacts & Navigation:
- 📊 **[Interactive Live Web Dashboard](https://alexzaremsky.github.io/miltech-data-analytics-portfolio/case_01_supply_chain/index.html)** *(client-side dashboard with dynamic ROP & Safety Stock calculator)*
- 📄 **[Executive Presentation (PDF, 16:9)](case_01_supply_chain/presentation.pdf)** *(executive presentation with methodology proofs)*
- 📖 **[Detailed 10-Block Case Study](case_01_supply_chain/README.md)** *(full analytical documentation)*
- 📈 **[High-Resolution Charts (300 DPI)](case_01_supply_chain/artifacts/)**
- 💻 **[Reproducible Python Pipeline](case_01_supply_chain/scripts/)**

---

### 📊 Case 02: Defense Procurement Analytics: Market Dynamics, Pricing & HHI Concentration (Prozorro 2022-2025)
*Comprehensive empirical analysis of Ukraine's open defense procurement market across 384,291 tenders worth 127.58B UAH.*  

- **Key Objective:** Analyze defense spend growth, buyer landscape (Central vs Military Units vs Local Communities), market concentration (HHI index), and the financial cost of single-bidder non-competition.
- **Key Finding (Market Dynamics):** Defense market spend scaled **13.2x (+1,218%) from 5.0B UAH (2022) to 65.9B UAH (2025)**, with UAV/Drones representing **39.4% (50.2B UAH)**.
- **Market Concentration (HHI):** Herfindahl-Hirschman Index is **739.6 for Drones and 296.0 for EW**, proving a highly decentralized, resilient SME ecosystem with no critical vendor lock-in (< 1,500 antitrust threshold).
- **Cost of Non-Competition (Single-Bidder Gap):** Tenders with 2+ bidders yield a **15.02% average discount** vs only **3.77%** for single-bidder contracts (**+11.25 pp gap**). 38.1B UAH in single-bidder spend resulted in **4.29B UAH in lost potential savings** (~215,000 FPV drones).
- **Decision Framework:** Deployed dynamic purchasing frameworks (DPS) and a live budget savings simulator to optimize defense allocations.

#### Case 02 Artifacts & Navigation:
- 📊 **[Interactive Live Web Dashboard](https://alexzaremsky.github.io/miltech-data-analytics-portfolio/case_02_procurement/index.html)** *(client-side dashboard with dynamic ROI & budget savings simulator)*
- 📄 **[Executive Presentation (PDF, 16:9)](case_02_procurement/presentation.pdf)** *(11 bespoke slides, centered scorecards, methodology proofs)*
- 📖 **[Detailed 10-Block Case Study](case_02_procurement/README.md)** *(full analytical documentation following Choice31 standard)*
- 📈 **[High-Resolution Charts (300 DPI)](case_02_procurement/artifacts/)**
- 💻 **[Reproducible Python Pipeline](case_02_procurement/scripts/)**

---

### 🏭 Case 03: Defense Production Analytics: Throughput, Capacity & Seasonality (Prozorro 2022-2025)
*Empirical analysis of industrial throughput, supplier capacity tiers (Tier 1-3), seasonality rhythmicity, and assembly bottlenecks across 384,291 MilTech tenders.*  

- **Key Objective:** Quantify serial manufacturing capabilities, detect December surge rhythmicity (Seasonality Ratio), and uncover production bottlenecks across airframes, avionics, optics, and final integration.
- **Key Finding (Capacity Scaling):** Defense production throughput scaled **10.3x from 2022 to 2025**, yielding an estimated **1.63M physical units** contracted across open defense procedures.
- **Supplier Tiers (Tier 1-3):** Highly stratified manufacturing base: **44 Tier 1 industrial plants** (>10k units/year) account for **68.2% of total physical output**, while **182 Tier 2 serial manufacturers** and **1,850+ Tier 3 SME/R&D workshops** drive rapid tactical innovations.
- **Fiscal Seasonality Surge:** High procurement surge in Q4 (**December Seasonality Ratio = 3.42x** vs Q1-Q3 average), creating acute assembly bottlenecks, supply chain lead-time volatility, and delivery delays.
- **Decision Framework:** Deployed line balancing simulator (Takt time vs Cycle time) and multi-year production scheduling model to smooth defense industrial throughput.

#### Case 03 Artifacts & Navigation:
- 🌐 **[Interactive Live Web Dashboard](https://alexzaremsky.github.io/miltech-data-analytics-portfolio/case_03_production/index.html)** *(client-side dashboard with live manufacturer registry & line balancing simulator)*
- 📑 **[Executive Presentation (PDF, 16:9)](case_03_production/presentation.pdf)** *(12 bespoke slides, centered scorecards, production bottleneck proofs)*
- 📄 **[Detailed 10-Block Case Study](case_03_production/README.md)** *(full analytical documentation following Choice31 standard)*
- 📊 **[High-Resolution Charts (300 DPI)](case_03_production/artifacts/)**
- 🛠️ **[Reproducible Python Pipeline](case_03_production/scripts/)**

---

## 🛠️ Technical Stack & Quality Standards
- **Data Processing:** Python 3.12, Pandas, PyArrow (Parquet DWH engine), NumPy, SciPy (HHI & quantile modeling)
- **Visual Analytics:** Matplotlib & Seaborn (300 DPI publication standards), Chart.js (interactive dashboards)
- **Design Standards:** Light Theme Standard (#FFFFFF / #F8FAFC), zero external CDNs for production stability
- **Reporting:** 16:9 Executive PDF Presentation, canonical 10-block analytical report standard

---

## 🔒 OpSec & Ethical Protocol (TLP:WHITE)
All data and analytics presented in this repository are derived strictly from **publicly available open-source datasets** ([Prozorro Ukraine Procurement 2022-2025 on Kaggle](https://www.kaggle.com/datasets/romankachmar/prozorro-ukraine-procurement-2022-2025)). No classified, NDA-protected, or sensitive internal military information is used or hosted.

---

© 2026 Alex Zaremsky. Developed for the MilTech & DefTech Data Analytics Program (Choice31 x IAMPM).
