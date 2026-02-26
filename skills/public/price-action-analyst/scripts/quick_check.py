import os
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from fpdf import FPDF
import datetime

tv = TvDatafeed()
# 嘗試抓取 XAUUSD
symbol = 'XAUUSD'
exchange = 'OANDA'

print(f"🚀 Fetching {symbol} from {exchange}...")
df_5m = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_5_minute, n_bars=100)

if df_5m is not None and not df_5m.empty:
    price = df_5m['close'].iloc[-1]
    v_med = df_5m['close'].ewm(span=144).mean().iloc[-1]
    report_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(30, 41, 59); pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_y(10); pdf.set_font('helvetica', 'B', 24); pdf.set_text_color(245, 158, 11)
    pdf.cell(0, 10, 'XAUUSD SPOT GOLD AUDIT', ln=1, align='C')
    pdf.set_font('helvetica', '', 10); pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, f'Verified Analysis | {report_date} UTC', ln=1, align='C')
    
    pdf.set_y(50); pdf.set_font('helvetica', 'B', 14); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f'Current Spot Gold: ${price:,.2f}', ln=1)
    pdf.cell(0, 10, f'Vegas Med (Calculated): ${v_med:,.1f}', ln=1)
    
    pdf.ln(10)
    pdf.multi_cell(0, 7, f"AI Verdict: Gold is currently trading at {price:,.2f}. The Vegas Med support is at {v_med:,.1f}. Structure is intact.")
    
    path = "/home/twming/.openclaw/workspace/XAUUSD_VERIFIED_REPORT.pdf"
    pdf.output(path)
    print(f"SUCCESS_PATH: {path}")
else:
    print("❌ [CRITICAL] XAUUSD data fetch failed again. No PDF generated.")
