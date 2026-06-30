import pandas as pd
print("Extracting data...")
df = pd.read_csv("raw_sales.csv")
print("Columns in file:")
print(df.columns)
print("Transforming data...")
df["Total_Price"] = df["price"] * df["quantity"] + 2
df["customer"] = df["customer"].str.upper()
print("Loading processed data...")
df.to_csv("processed_sales.csv", index=False)
print("ETL Process Completed!")

