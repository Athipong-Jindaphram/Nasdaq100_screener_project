# src/main.py
from extract import get_nasdaq_tickers, download_stock_prices
from transform import process_data
from load import load_data_to_db

def run_pipeline():
    print("🚀 เริ่มต้นรัน Data Pipeline: NASDAQ-100 Screener")
    print("-" * 50)
    
    # 1. Extract (ดึงข้อมูล)
    tickers, df_info = get_nasdaq_tickers()
    price_data = download_stock_prices(tickers)
    
    # 2. Transform (คำนวณ)
    df_result = process_data(price_data, df_info)
    
    # 3. Load (โหลดลงฐานข้อมูล)
    if not df_result.empty:
        print("\n👀 ตัวอย่างข้อมูล 3 อันดับแรก (Top 3 Daily Gainers วันนี้):")
        # โชว์ผลลัพธ์ใน Terminal ดูก่อนเอาลง DB
        print(df_result.sort_values(by='daily_change_pct', ascending=False).head(3))
        print("-" * 50)
        
        load_data_to_db(df_result)
    else:
        print("❌ ไม่มีข้อมูลสำหรับบันทึก")
        
    print("-" * 50)
    print("🎉 การประมวลผลเสร็จสมบูรณ์!")

if __name__ == "__main__":
    run_pipeline()