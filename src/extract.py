import pandas as pd
import yfinance as yf
import requests
import io
from config import WIKI_URL, PERIOD

def get_nasdaq_tickers():
    print("⏳ กำลังค้นหาตารางรายชื่อหุ้น NASDAQ-100 จาก Wikipedia...")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(WIKI_URL, headers=headers)
        tables = pd.read_html(io.StringIO(response.text))
        
        df_ndx = None
        # หาตารางที่มีคอลัมน์ GICS Sector หรือ Company
        for table in tables:
            cols = [str(c).lower() for c in table.columns]
            if 'gics sector' in cols or 'company' in cols:
                df_ndx = table
                break
                
        if df_ndx is None:
            raise ValueError("โครงสร้างเว็บ Wikipedia เปลี่ยนแปลง หาตารางไม่พบ")
            
        ticker_col = None
        for col in df_ndx.columns:
            if 'ticker' in str(col).lower() or 'symbol' in str(col).lower():
                ticker_col = col
                break
                
        if ticker_col is None:
            ticker_col = df_ndx.columns[1]
            
        tickers = df_ndx[ticker_col].tolist()
        tickers = [str(t).replace('.', '-') for t in tickers]
        df_ndx = df_ndx.rename(columns={ticker_col: 'Ticker'})
        
    except Exception as e:
        print(f"⚠️ ไม่สามารถดึงจาก Wikipedia ได้ ({e}) -> กำลังสลับไปใช้รายชื่อหุ้นสำรอง (Fallback)")
        # ถ้าระบบดึงเว็บไม่ได้ จะใช้รายชื่อหุ้นชุดนี้แทน (อัปเดตล่าสุด)
        tickers = [
            'AAPL', 'MSFT', 'AMZN', 'NVDA', 'META', 'TSLA', 'GOOGL', 'GOOG', 'AVGO', 'COST', 
            'PEP', 'CSCO', 'TMUS', 'ADBE', 'TXN', 'NFLX', 'AMD', 'CMCSA', 'INTU', 'QCOM', 
            'AMGN', 'HON', 'INTC', 'ISRG', 'SBUX', 'BKNG', 'MDLZ', 'GILD', 'LRCX', 'ADI', 
            'VRTX', 'REGN', 'PANW', 'ADP', 'SNPS', 'KLAC', 'CDNS', 'CSX', 'MELI', 'MU', 
            'PYPL', 'CRWD', 'ASML', 'MAR', 'CTAS', 'NXPI', 'ORLY', 'FTNT', 'MNST', 'ABNB', 
            'LULU', 'WDAY', 'PCAR', 'CHTR', 'MCHP', 'ROST', 'KDP', 'PAYX', 'AEP', 'MRVL', 
            'AZN', 'IDXX', 'EXC', 'EA', 'CTSH', 'KHC', 'BIIB', 'DASH', 'DXCM', 'TEAM', 
            'FAST', 'GEHC', 'ODFL', 'CSGP', 'TTD', 'BKR', 'DLTR', 'FANG', 'WBD', 'PDD', 
            'VRSK', 'CEG', 'WBA', 'SIRI', 'ZS', 'ILMN', 'EBAY', 'GFS', 'ALGN', 'ZM',
            'PLTR', 'ARM', 'CCEP', 'MDB', 'TTWO', 'DDOG', 'SPLK', 'ROKU', 'OKTA', 'DOCU'
        ]
        # สร้าง DataFrame จำลองให้ระบบนำไปทำงานต่อได้โดยไม่พัง
        df_ndx = pd.DataFrame({'Ticker': tickers, 'Company': tickers, 'GICS Sector': 'N/A'})
        
    return tickers, df_ndx

def download_stock_prices(tickers):
    print(f"⏳ กำลังดึงข้อมูลราคาและ Volume ของหุ้น {len(tickers)} ตัว ย้อนหลัง {PERIOD}...")
    price_data = yf.download(tickers, period=PERIOD)
    return price_data

# ==========================================
# ส่วนที่เพิ่มเข้ามาใหม่: ฟังก์ชันดึงข้อมูล Market Cap
# ==========================================
def get_market_caps(tickers):
    print("⏳ กำลังดึงข้อมูล Market Cap จาก Yahoo Finance (ใช้เวลาสักครู่)...")
    mc_data = []
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            # ใช้ fast_info เพื่อความรวดเร็วในการดึงข้อมูลโดยไม่ต้องโหลดหน้าเว็บทั้งหมด
            mc = stock.fast_info.market_cap
            mc_data.append({'Ticker': ticker, 'market_cap': mc})
        except Exception:
            # ถ้าหาข้อมูลหุ้นตัวไหนไม่เจอ ให้ใส่ค่า Market Cap เป็น 0 ไปก่อนเพื่อไม่ให้ระบบพัง
            mc_data.append({'Ticker': ticker, 'market_cap': 0})
            
    return pd.DataFrame(mc_data)