# 🚴 Bike Sales Data Lakehouse

An end-to-end data engineering project built on **Databricks** using the **Medallion Architecture** (Bronze → Silver → Gold), transforming raw CRM and ERP CSV files into a star-schema data model ready for analytics.

---

## 📐 Architecture Overview

```
Source CSVs  →  Bronze (Raw)  →  Silver (Cleansed)  →  Gold (Star Schema)  →  Dashboard
```

| Layer  | Description |
|--------|-------------|
| **Bronze** | Raw CSV files ingested as Delta tables — no transformations |
| **Silver** | Cleaned, normalised, and renamed tables using PySpark |
| **Gold**   | Star schema: `dim_customer`, `dim_product`, `fact_sales` |

---

## 📁 Project Structure

```
bike-lakehouse/
│
├── bronze/
│   ├── ingest_crm_cust_info.py
│   ├── ingest_crm_prd_info.py
│   ├── ingest_crm_sales_detail.py
│   ├── ingest_erp_cust_az12.py
│   ├── ingest_erp_loc_a101.py
│   └── ingest_erp_px_cat_g1v2.py
│
├── silver/
│   ├── silver_crm_cust_info.py
│   ├── silver_crm_prd_info.py
│   ├── silver_crm_sales_detail.py
│   ├── silver_erp_cust_az12.py
│   ├── silver_erp_loc_a101.py
│   └── silver_erp_px_cat_g1v2.py
│
├── gold/
│   ├── gold_dim_customer.py
│   ├── gold_dim_product.py
│   └── gold_fact_sales.py
│
├── data/
│   └── source/                  # Raw CSV source files
│
└── README.md
```

---

## 🗂️ Source Data

Six CSV files across two source systems:

**CRM System**
- `crm_cust_info` — Customer demographics and segments
- `crm_prd_info` — Product catalogue with pricing
- `crm_sales_detail` — Order-level transaction records

**ERP System**
- `prd_cust_az12` — Additional customer attributes
- `erp_loc_a101` — Location and region mappings
- `erp_px_cat_g1v2` — Product category hierarchy

---

## 🥉 Bronze Layer — Raw Ingestion

- CSV files loaded directly into Delta tables using `spark.read.csv()`
- Schema inferred or defined explicitly
- No transformations applied — data preserved as-is
- Acts as the immutable source-of-truth layer

---

## 🥈 Silver Layer — Transformations

Applied consistently across all tables:

- **String trimming** — `trim()` on all string columns to remove leading/trailing whitespace
- **Normalisation** — Standardised date formats, corrected data types, null handling
- **Column renaming** — Consistent snake_case naming convention across all tables
- **Deduplication** — Removed duplicate rows using `dropDuplicates()`

---

## 🥇 Gold Layer — Star Schema

Business-ready Delta tables modelled using **star schema** for optimal analytics performance.

### `dim_customer`
| Column | Description |
|--------|-------------|
| `customer_id` | Primary key |
| `customer_name` | Full name |
| `country`, `city` | Location |
| `segment` | Customer segment |

### `dim_product`
| Column | Description |
|--------|-------------|
| `product_id` | Primary key |
| `product_name` | Name |
| `category`, `subcategory` | Hierarchy |
| `cost`, `price` | Financials |

### `fact_sales`
| Column | Description |
|--------|-------------|
| `order_id` | Primary key |
| `customer_id` | FK → dim_customer |
| `product_id` | FK → dim_product |
| `order_date` | Transaction date |
| `quantity`, `revenue` | Measures |

---

## ⚙️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Databricks** | Notebook execution, Delta Lake storage |
| **PySpark** | Distributed data transformations |
| **Delta Lake** | ACID-compliant table format |
| **GitHub** | Version control (connected via Databricks Repos) |

---

## 🔗 GitHub Integration

This project is connected to GitHub via **Databricks Repos**, enabling:
- Notebook version control directly from Databricks UI
- Branch-based development workflow
- Commit and push without leaving Databricks

To sync changes:
1. Open **Repos** in the Databricks sidebar
2. Pull latest changes or commit new notebooks
3. Push to GitHub from the Repos panel

---

## 🚀 How to Run

1. Clone this repo into Databricks via **Repos → Add Repo**
2. Attach notebooks to a cluster with Delta Lake enabled
3. Run in order: `bronze/` → `silver/` → `gold/`
4. Query Gold tables from the SQL editor or connect the Streamlit dashboard

---

## 📊 Dashboard

A separate Streamlit dashboard (`/dashboard`) connects to the Gold layer and visualises:
- Total revenue and order KPIs
- Sales by product category
- Customer segment breakdown
- Monthly trend analysis

See [`dashboard/README.md`](./dashboard/README.md) for setup instructions.

---

## 👤 Author

Built as a portfolio project to demonstrate end-to-end data engineering skills using modern lakehouse architecture.
