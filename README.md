# 🍬 Nassau Candy Distributor — Shipping Route Efficiency Analysis

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ram-patel2112-nassau--nassau-route-efficiency-projectapp-8ref96.streamlit.app/)

## 📌 Project Overview

This project delivers a comprehensive **Factory-to-Customer Shipping Route Efficiency Analysis** for Nassau Candy Distributor — a national confectionery distributor operating across all major US regions. The analysis transforms raw order and shipment data into actionable logistics intelligence through exploratory data analysis, route benchmarking, geographic bottleneck detection, and an interactive real-time dashboard.

---

## 🔍 Key Features

✔️ **Data Cleaning & Validation** — Date parsing, field validation, zero missing values confirmed  
✔️ **Feature Engineering** — Lead time calculation, factory mapping, route definition, delay flagging  
✔️ **Route Efficiency Benchmarking** — Top 10 fastest & slowest routes ranked by avg lead time  
✔️ **Geographic Heatmap** — US state-level choropleth for delay rates, lead times, and volumes  
✔️ **Ship Mode Analysis** — Counter-intuitive finding: Standard Class outperforms First Class & Same Day  
✔️ **Factory Performance** — The Other Factory leads efficiency; Sugar Shack is the highest-risk supplier  
✔️ **Interactive Dashboard** — Streamlit app with filters, drill-downs, and Plotly visualizations  
✔️ **Full Research Report** — PDF covering EDA, benchmarking, geographic analysis, and KPIs  
✔️ **Executive Summary** — Stakeholder-ready PDF with critical findings and strategic recommendations  

---

## 📊 Key Findings

| Finding | Detail |
|---------|--------|
| **Overall Delay Rate** | 33.1% of 10,194 shipments exceed the delay threshold |
| **Best Factory** | The Other Factory — avg 1,280 days lead time |
| **Worst Factory** | Sugar Shack — avg 1,340 days, 48.5% delay rate |
| **Best Ship Mode** | Standard Class — 1,314 days avg (fastest!) |
| **Worst Ship Mode** | First Class — 1,338 days (slower than Standard) |
| **Most Delayed Region** | Pacific — 34.2% delay rate |
| **Total Revenue** | $141,783.63 | Gross Profit: $93,442.80 |
| **Unique Routes** | 196 factory-to-state routes analyzed |

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly Express, Plotly Graph Objects |
| Dashboard | Streamlit |
| Notebook EDA | Jupyter, Matplotlib, Seaborn |
| PDF Reports | ReportLab |

---

## 📁 Project Structure

```
Nassau-Candy-Shipping-Analysis/
│
├── app.py                                      # Streamlit dashboard (5 tabs)
├── Shipping_Route_Efficiency_Analysis.ipynb    # Full EDA & analysis notebook
├── Nassau_Candy_Distributor.csv                # Source dataset (10,194 records)
├── Shipping_Route_Efficiency_Report.pdf        # Detailed research report (9 sections)
├── Executive_Summary.pdf                       # Stakeholder executive summary
├── requirements.txt                            # Python dependencies
└── README.md                                   # This file
```

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/ram-patel2112/nassau-candy-shipping-analysis.git
cd nassau-candy-shipping-analysis
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the dashboard
```bash
streamlit run app.py
```

### 4. Open the notebook (optional)
```bash
jupyter notebook Shipping_Route_Efficiency_Analysis.ipynb
```

---

## 📊 Dashboard Modules

| Tab | Description |
|-----|-------------|
| 📊 **Overview** | KPI cards, Top/Bottom 10 route leaderboards, factory bubble chart |
| 🗺️ **Geographic Map** | US choropleth heatmap, factory locations, regional bottleneck chart |
| 🚚 **Ship Mode** | Box plots, cost-time tradeoff scatter, Ship Mode × Region heatmap |
| 📦 **Route Drill-Down** | Select any Factory → State for order timeline and product breakdown |
| 📈 **Trends** | Monthly volume/lead time/delay/revenue trends, per-factory trends |

### Sidebar Filters
- 📅 Date range selector
- 🗺️ Region multi-select
- 🚚 Ship mode multi-select
- 🏭 Factory multi-select
- ⚠️ Delay threshold slider

---

## 📈 Business Impact

- Identifies **196 unique routes** across **59 US states** with performance benchmarks
- Quantifies **$0 delay visibility** before this analysis — now fully instrumented
- Enables **proactive customer communication** for 3,379 flagged delayed orders
- Provides executive-ready insights for **carrier renegotiation** and **hub placement** decisions

---

## 👤 Author

**Ram Patel**  
BCA Final Year | Batch 2023–2026  
Unified Mentor — Data Analyst Internship  

---

## 📄 License

This project was developed as part of the Unified Mentor Data Analyst Internship program.
