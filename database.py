import pandas as pd
from config import config
from sqlalchemy import create_engine

# load data from CSV and write to DB
engine = create_engine(config.db_url)
df = pd.read_csv("./data/buildings.csv", encoding="windows-1251")
df.to_sql("buildings", engine, if_exists="replace")
