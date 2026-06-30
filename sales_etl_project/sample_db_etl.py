from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine("mysql+pymysql://root:3520@127.0.0.1:3306/sakila")

df = pd.read_sql("SELECT * FROM actor", engine)
with engine.connect() as conn:
    # conn.execute(text("""alter table actor add column film_info varchar(255)"""))
    conn.execute(text("""update actor set film_info = concat(
                      upper(left(first_name,1)),lower(substring(first_name,2)), ' ', 
                      upper(left(last_name,1)),lower(substring(last_name,2)))"""))
    conn.execute(text("""alter table actor modify column last_update date"""))
    conn.commit()
    print(df.head())