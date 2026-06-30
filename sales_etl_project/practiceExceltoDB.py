import pandas as pd
import mysql.connector as conn

print("Extracting data from processed_sales.csv...")
df = pd.read_csv("processed_sales.csv")

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="3520",
    database="sakila"
)
corser = conn.cursor()
print("Loading data into MySQL database...")
print(df.head())
