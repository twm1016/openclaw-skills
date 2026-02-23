import os
import sys
import pandas as pd
import mplfinance as mpf
from tvDatafeed import TvDatafeed, Interval
from fpdf import FPDF
import datetime
import matplotlib.pyplot as plt

class UltimateAnalystV6_2:
    def __init__(self):
        self.tv = TvDatafeed()
        self.workspace = "/home/twming/.openclaw/workspace"

    def fetch_data(self, symbol, interval, n_bars=200):
        try:
            df = self.tv.get_hist(symbol=symbol, exchange='CME', interval=interval, n_bars=n_bars)
            if df is None:
                df = self.tv.get_hist(symbol='NAS100USD' if 'MNQ' in symbol else 'GOLD', exchange='OANDA', interval=interval, n_bars=n_bars)
            if df is not None:
                df.index = pd.to_datetime(df.index)
            return df
        except:
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
        print(f"🚀 Processing {asset_name} ({symbol})...")
        
        # 徹底隔離數據
        raw_5m = self.fetch_data(symbol, Interval.in_5_minute)
        raw_1h = self.fetch_data(symbol, Interval.in_1_hour)
        raw_1d = self.fetch_data(symbol, Interval.in_daily)
        
        df_5m = self.add_indicators(raw_5m)
        df_1h = self.add_indicators(raw_1h)
        df_1d = self.add_indicators(raw_1d)

        if df_5m is None or df_1h is None:
            print(f"❌ Data unavailable for {asset_name}")
            return

        price = df_5m['close'].iloc[-1]
        v_med = df_5m['ema144'].iloc[-1]
        v_long = df_5m['ema576'].iloc[-1]
        
        # 繪圖
        img_5m = os.path.join(self.workspace, f"c5_{asset_name}.png")
        mpf.plot(df_5m.tail(50), type='candle', style='charles', savefig=img_5m)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(30, 41, 59); pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_y(10); pdf.set_font('helvetica', 'B', 24); pdf.set_text_color(245, 158, 11)
        pdf.cell(0, 10, f'{asset_name} ULTIMATE REPORT', new_x='LMARGIN', new_y='NEXT', align='C')
        pdf.set_font('helvetica', '', 10); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, f'Analysis Date: {report_date} UTC | Symbol: {symbol}', new_x='LMARGIN', new_y='NEXT', align='C')
        
        pdf.set_y(50); pdf.set_font('helvetica', 'B', 14); pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 10, 'I. Current Market Structure', new_x='LMARGIN', new_y='NEXT')
        pdf.set_font('helvetica', '', 11); pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 7, f"Price: {price:,.2f} | Vegas Med: {v_med:,.1f} | Vegas Long: {v_long:,.1f}")

        pdf.ln(5); pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'II. Dynamic Level Matrix (Calculated)', new_x='LMARGIN', new_y='NEXT')
        pdf.set_font('helvetica', 'B', 9); pdf.set_fill_color(51, 65, 85); pdf.set_text_color(255, 255, 255)
        pdf.cell(30, 10, 'Zone', 1, 0, 'C', True); pdf.cell(30, 10, 'Price', 1, 0, 'C', True); pdf.cell(130, 10, 'Technical Reasoning', 1, 1, 'C', True)
        
        pdf.set_text_color(0, 0, 0); pdf.set_font('helvetica', '', 9)
        # 真實動態價位
        atr = (df_5m['high'].max() - df_5m['low'].min())
        levels = [
            ("R3", f"{max(v_med, price + atr*2):,.1f}", f"{asset_name} 1H Vegas Resistance"),
            ("R2", f"{price + atr:,.1f}", "Recent Supply / FVG Entrance"),
            ("R1", f"{price + atr*0.5:,.1f}", "Short-term momentum ceiling"),
            ("Pivot", f"{price:,.1f}", "Current Market Price"),
            ("S1", f"{price - atr*0.5:,.1f}", "Immediate support zone"),
            ("S2", f"{price - atr:,.1f}", "Recent Demand / OB Entrance"),
            ("S3", f"{min(v_med, price - atr*2):,.1f}", f"{asset_name} 5M Vegas Support")
        ]
        for zone, p, reason in levels:
            pdf.cell(30, 8, zone, 1); pdf.cell(30, 8, p, 1, 0, 'C'); pdf.cell(130, 8, reason, 1, 1)

        pdf.ln(10); pdf.image(img_5m, w=180)
        
        filename = f"{asset_name.lower()}_final_v6.pdf"
        out = os.path.join(self.workspace, filename)
        pdf.output(out)
        return out

if __name__ == "__main__":
    analyst = UltimateAnalystV6_2()
    for a in [{'s': 'MNQ1!', 'n': 'MNQ'}, {'s': 'GOLD', 'n': 'MGC'}]:
        path = analyst.generate_report(a['s'], a['n'])
        print(f"Generated: {path}")
