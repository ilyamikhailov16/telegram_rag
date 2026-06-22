import pandas as pd
from config import config
from sqlalchemy import create_engine

# load data from CSV and write to DB
engine = create_engine(config.db_url)
df = pd.read_csv("./data/buildings.csv", encoding="windows-1251")

# Ensure date-like columns are parsed to proper datetimes so SQL functions work
for col in ["create_date", "zpo_n", "zpo_k", "ird_n", "ird_k", "pir_st", "pir_fn", "smr_st", "smr_fn", "plan_vvod"]:
    df[col] = pd.to_datetime(df[col], errors="coerce")

# Numeric columns
numeric_cols = ["latit_oks", "longit_oks"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Write to SQL (replace existing table)
df.to_sql("buildings", engine, if_exists="replace", index=False)
