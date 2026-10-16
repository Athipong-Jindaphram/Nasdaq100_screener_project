# src/transform.py
import pandas as pd
from datetime import datetime
import yfinance as yf
from extract import get_market_caps  # ใช้ import แบบนี้ตามที่เราแก้ Error ไปก่อนหน้านี้

def process_data(price_data, df_info):
    print("⏳ กำลังคำนวณ % การเปลี่ยนแปลง พร้อมดึงข้อมูล Sector และ Volume...")
    results = []
    
    # แยก DataFrame ของ Close และ Volume ออกมาเพื่อให้เรียกใช้ง่ายขึ้น
    df_close = price_data['Close']
    df_volume = price_data['Volume']
    
    for ticker in df_close.columns:
        try:
            # ดึงข้อมูลราคาและ Volume ของหุ้นตัวนั้นๆ (ตัดค่าว่างออก)
            stock_close = df_close[ticker].dropna()
            stock_volume = df_volume[ticker].dropna()
            
            # ถ้าหุ้นใหม่เกินไป (ข้อมูลน้อยกว่า 1 เดือน) ให้ข้าม
            if len(stock_close) < 22:
                continue
                
            # ราคาปิดล่าสุด และ Volume การเทรดล่าสุด
            current_price = float(stock_close.iloc[-1])
            current_vol = int(stock_volume.iloc[-1])
            
            # คำนวณ % การเปลี่ยนแปลง
            daily_change = (current_price - float(stock_close.iloc[-2])) / float(stock_close.iloc[-2]) * 100
            monthly_change = (current_price - float(stock_close.iloc[-22])) / float(stock_close.iloc[-22]) * 100
            yearly_change = (current_price - float(stock_close.iloc[0])) / float(stock_close.iloc[0]) * 100
            
            # ดึงชื่อบริษัทและกลุ่มอุตสาหกรรม (GICS Sector) จากข้อมูล Wikipedia
            original_ticker = ticker.replace('-', '.')
            company_match = df_info.loc[df_info['Ticker'] == original_ticker]
            
            company_name = company_match['Company'].values[0] if not company_match.empty else ticker
            sector = company_match['GICS Sector'].values[0] if not company_match.empty else "N/A"
            
            # ==========================================
            # ดึงจาก Yahoo Finance หากข้อมูลวิกิพีเดียเป็น N/A
            # ==========================================
            if sector == "N/A" or company_name == ticker:
                try:
                    info = yf.Ticker(ticker).info
                    # ดึงชื่อเต็มและ Sector จาก yfinance โดยตรง
                    company_name = info.get('shortName', company_name)
                    sector = info.get('sector', sector)
                except Exception:
                    pass  # ถ้าหาไม่เจอจริงๆ ก็ปล่อยผ่านไป
            # ==========================================
            
            # ประกอบร่างข้อมูล
            results.append({
                'ticker': ticker,
                'company_name': company_name,
                'sector': sector,
                'current_price': round(current_price, 2),
                'daily_change_pct': round(daily_change, 2),
                'monthly_change_pct': round(monthly_change, 2),
                'yearly_change_pct': round(yearly_change, 2),
                'current_volume': current_vol,
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        except Exception as e:
            print(f"⚠️ ข้ามหุ้น {ticker} เนื่องจากพบปัญหา: {e}")
            
    df_result = pd.DataFrame(results)
    
    # ==========================================
    # ส่วนการดึงและเชื่อม Market Cap
    # ==========================================
    if not df_result.empty:
        # เอาเฉพาะรายชื่อหุ้นที่คำนวณผ่านแล้วส่งไปหา Market Cap
        valid_tickers = df_result['ticker'].tolist()
        df_market_cap = get_market_caps(valid_tickers)
        
        # นำตาราง Market Cap มา Merge ชนเข้าด้วยกัน
        if not df_market_cap.empty:
            df_market_cap = df_market_cap.rename(columns={'Ticker': 'ticker'})
            df_result = pd.merge(df_result, df_market_cap, on='ticker', how='left')
        else:
            df_result['market_cap'] = 0
    # ==========================================

    print(f"✅ คำนวณเสร็จสิ้น! ได้ข้อมูลสรุปหุ้นทั้งหมด {len(df_result)} ตัว")
    
    return df_result