# src/load.py
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# โหลดค่าตัวแปรจากไฟล์ .env
load_dotenv()

def load_data_to_db(df, table_name="nasdaq100_summary"):
    print(f"⏳ กำลังบันทึกข้อมูล {len(df)} แถว ลงใน PostgreSQL...")
    
    # ดึงค่าจาก .env มาต่อกันเป็น Connection String
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    
    # URL สำหรับเชื่อมต่อ PostgreSQL
    engine_url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(engine_url)
    
    try:
        # if_exists='replace' คือหัวใจสำคัญ ที่ทำให้ Database ไม่บวม!
        # index=False คือไม่ต้องเอาเลข Index ของ Pandas ใส่ลงไปใน DB
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
        print(f"✅ บันทึกข้อมูลลงตาราง '{table_name}' สำเร็จแล้ว!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการบันทึกข้อมูล: {e}")