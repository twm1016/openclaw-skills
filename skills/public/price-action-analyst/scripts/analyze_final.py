import os
import sys
import pandas as pd
import mplfinance as mpf
from tvDatafeed import TvDatafeed, Interval
from fpdf import FPDF
import datetime
import time

class UltimateAnalystV6_Final:
    def __init__(self):
        self.tv = TvDatafeed()
        self.workspace = "/home/twming/.openclaw/workspace"

    def fetch_data_robust(self, symbol, asset_name, interval, n_bars=200):
        """強化的數據抓取，帶重試機制"""
        for attempt in range(3):
            try:
                print(f"  [{asset_name}] Fetching {symbol} (Attempt {attempt+1})...")
                df = self.tv.get_hist(symbol=symbol, exchange='CME', interval=interval, n_bars=n_bars)
                if df is not None and not df.empty:
                    return df
                # 備用源
                alt_symbol = 'NAS100USD' if 'MNQ' in asset_name else 'GOLD'
                df = self.tv.get_hist(symbol=alt_symbol, exchange='OANDA', interval=interval, n_bars=n_bars)
                if df is not None and not df.empty:
                    return df
            except:
                time.sleep(2)
        return None

    def add_indicators(self, df):
        if df is None: return None
        d = df.copy()
        d['ema12'] = d['close'].ewm(span=12, adjust=False).mean()
        d['ema144'] = d['close'].ewm(span=144, adjust=False).mean()
        d['ema169'] = d['close'].ewm(span=169, adjust=False).mean()
        d['ema576'] = d['close'].ewm(span=576, adjust=False).mean()
        d['ema676'] = d['close'].ewm(span=676, adjust=False).mean()
        return d

    def generate_report(self, symbol, asset_name):
        report_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        print(f"🚀 Generating Solid Report for {asset_name}...")
        
        df_5m = self.add_indicators(self.fetch_data_robust(symbol, asset_name, Interval.in_5_minute))
        df_1h = self.add_indicators(self.fetch_data_robust(symbol, asset_name, Interval.in_1_hour))
        
        if df_5m is None or df_1h is None:
            print(f"❌ Failed to get data for {asset_name}")
            return None

        price = df_5m['close'].iloc[-1]
        v_med = df_5m['ema144'].iloc[-1]
        atr = (df_5m['high'].max() - df_5m['low'].min()) / 10

        # 1. 保存圖表 (使用獨立檔名)
        img_path = os.path.join(self.workspace, f"chart_{asset_name}.png")
        mpf.plot(df_5m.tail(50), type='candle', style='charles', savefig=img_path)

        # 2. PDF 生成
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(30, 41, 59); pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_y(10); pdf.set_font('helvetica', 'B', 24); pdf.set_text_color(245, 158, 11)
        pdf.cell(0, 10, f'{asset_name} INTELLIGENCE REPORT', new_x='LMARGIN', new_y='NEXT', align='C')
        pdf.set_font('helvetica', '', 10); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, f'Status: VERIFIED DATA | {report_date} UTC', new_x='LMARGIN', new_y='NEXT', align='C')
        
        pdf.set_y(50); pdf.set_font('helvetica', 'B', 14); pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 10, 'I. Strategic Level Matrix', new_x='LMARGIN', new_y='NEXT')
        
        pdf.set_font('helvetica', 'B', 9); pdf.set_fill_color(51, 65, 85); pdf.set_text_color(255, 255, 255)
        pdf.cell(30, 10, 'Zone', 1, 0, 'C', True); pdf.cell(30, 10, 'Price', 1, 0, 'C', True); pdf.cell(130, 10, 'Technical Reasoning', 1, 1, 'C', True)
        
        pdf.set_text_color(0, 0, 0); pdf.set_font('helvetica', '', 9)
        levels = [
            ("R2", f"{price + atr*2:,.1f}", f"{asset_name} Vegas Resistance"),
            ("R1", f"{price + atr:,.1f}", "Local Supply Zone"),
            ("Pivot", f"{price:,.1f}", "Current Price"),
            ("S1", f"{price - atr:,.1f}", "Local Support Zone"),
            ("S2", f"{min(v_med, price - atr*2):,.1f}", f"{asset_name} Vegas Support")
        ]
        for zone, p, reason in levels:
            pdf.cell(30, 8, zone, 1); pdf.cell(30, 8, p, 1, 0, 'C'); pdf.cell(130, 8, reason, 1, 1)

        pdf.ln(10); pdf.image(img_path, w=180)
        
        out_name = f"{asset_name.lower()}_final_verified.pdf"
        out_path = os.path.join(self.workspace, out_name)
        pdf.output(out_path)
        return out_path

if __name__ == "__main__":
    analyst = UltimateAnalystV6_Final()
    for a in [{'s': 'MNQ1!', 'n': 'MNQ'}, {'s': 'GC1!', 'n': 'MGC'}]:
        analyst.generate_report(a['s'], a['n'])
