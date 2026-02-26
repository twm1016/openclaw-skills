import os
import sys
import pandas as pd
import mplfinance as mpf
from tvDatafeed import TvDatafeed, Interval
from fpdf import FPDF
import datetime
import matplotlib.pyplot as plt

class XauusdUltimateV6:
    def __init__(self):
        self.tv = TvDatafeed()
        self.report_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.workspace = "/home/twming/.openclaw/workspace"

    def fetch_data(self, symbol, interval, n_bars=200):
        # 強制使用 OANDA 作為 XAUUSD 的穩定數據源
        try:
            df = self.tv.get_hist(symbol=symbol, exchange='OANDA', interval=interval, n_bars=n_bars)
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

    def save_chart(self, df, timeframe_name, filename):
        apds = [
            mpf.make_addplot(df['ema12'], color='orange', width=0.7),
            mpf.make_addplot(df['ema144'], color='cyan', width=0.8),
            mpf.make_addplot(df['ema169'], color='cyan', width=0.8),
            mpf.make_addplot(df['ema576'], color='magenta', width=1.0),
            mpf.make_addplot(df['ema676'], color='magenta', width=1.0)
        ]
        path = os.path.join(self.workspace, filename)
        mpf.plot(df, type='candle', style='charles', addplot=apds, 
                 savefig=dict(fname=path, dpi=100, bbox_inches='tight'),
                 title=f"XAUUSD {timeframe_name} Analysis", tight_layout=True)
        return path

    def calculate_levels(self, df_5m, df_1h):
        price = df_5m['close'].iloc[-1]
        v_med_5m = df_5m['ema144'].iloc[-1]
        v_med_1h = df_1h['ema144'].iloc[-1]
        v_long_1h = df_1h['ema576'].iloc[-1]
        atr = (df_5m['high'].max() - df_5m['low'].min()) / 12

        return [
            ("R5 (Major)", f"{max(v_long_1h * 1.01, price + atr*5):,.1f}", "Major Daily Supply / Vegas Long 1H"),
            ("R4", f"{price + atr*4:,.1f}", "1H Resistance Zone"),
            ("R3", f"{v_med_1h * 1.005:,.1f}", "1H Vegas Med Ceiling"),
            ("R2", f"{price + atr*2:,.1f}", "Local Liquidity Gap"),
            ("R1 (Minor)", f"{max(v_med_5m, price + atr):,.1f}", "5M Vegas Med Resistance"),
            ("S1 (Minor)", f"{min(v_med_5m, price - atr):,.1f}", "5M Vegas Med Support"),
            ("S2", f"{v_med_1h:,.1f}", "1H Vegas Med Base (144/169)"),
            ("S3", f"{price - atr*2:,.1f}", "SMC Demand Zone"),
            ("S4", f"{v_long_1h:,.1f}", "Vegas Long 1H Floor (576/676)"),
            ("S5 (Major)", f"{v_long_1h * 0.99:,.1f}", "Deep Trend Support / Institutional Pivot")
        ]

    def generate(self):
        symbol = 'XAUUSD'
        print(f"🚀 Generating XAUUSD V6 Ultimate Report...")
        
        df_5m = self.add_indicators(self.fetch_data(symbol, Interval.in_5_minute))
        df_1h = self.add_indicators(self.fetch_data(symbol, Interval.in_1_hour))
        df_1d = self.add_indicators(self.fetch_data(symbol, Interval.in_daily))

        if df_5m is None or df_1h is None:
            print("❌ Data fetch failed.")
            return

        img_5m = self.save_chart(df_5m.tail(50), "5M", "xau_5m.png")
        img_1h = self.save_chart(df_1h.tail(50), "1H", "xau_1h.png")
        img_1d = self.save_chart(df_1d.tail(50), "1D", "xau_1d.png")

        pdf = FPDF()
        pdf.add_page()
        
        # Header Box (V6 Spec)
        pdf.set_fill_color(30, 41, 59)
        pdf.rect(0, 0, 210, 45, 'F')
        pdf.set_y(15); pdf.set_font('helvetica', 'B', 26); pdf.set_text_color(245, 158, 11)
        pdf.cell(0, 10, 'GOLD MARKET INTELLIGENCE V6', new_x='LMARGIN', new_y='NEXT', align='C')
        pdf.set_font('helvetica', 'I', 11); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, f'XAUUSD Professional Audit | {self.report_date} UTC', new_x='LMARGIN', new_y='NEXT', align='C')
        
        # Bias
        pdf.set_y(55); pdf.set_font('helvetica', 'B', 16); pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 10, 'I. Bias & Multi-Timeframe Alignment', new_x='LMARGIN', new_y='NEXT')
        price = df_5m['close'].iloc[-1]
        v_med = df_5m['ema144'].iloc[-1]
        pdf.set_font('helvetica', '', 11); pdf.set_text_color(0, 0, 0)
        bias = "BULLISH" if price > v_med else "NEUTRAL/BEARISH"
        pdf.multi_cell(0, 7, f"Price: ${price:,.2f} | 5M Bias: {bias}\nVegas Med (144/169): ${v_med:,.1f}")

        # Matrix (10 Levels)
        pdf.ln(5); pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'II. Strategic 10-Level Matrix', new_x='LMARGIN', new_y='NEXT')
        pdf.set_font('helvetica', 'B', 9); pdf.set_fill_color(51, 65, 85); pdf.set_text_color(255, 255, 255)
        pdf.cell(30, 10, 'Zone', 1, 0, 'C', True); pdf.cell(30, 10, 'Price', 1, 0, 'C', True); pdf.cell(130, 10, 'Technical Reasoning', 1, 1, 'C', True)
        
        pdf.set_text_color(0, 0, 0); pdf.set_font('helvetica', '', 9)
        for zone, p, reason in self.calculate_levels(df_5m, df_1h):
            pdf.cell(30, 8, zone, 1); pdf.cell(30, 8, p, 1, 0, 'C'); pdf.cell(130, 8, reason, 1, 1)

        # Charts
        pdf.add_page(); pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'III. Visual Execution Charts', new_x='LMARGIN', new_y='NEXT')
        pdf.image(img_5m, x=10, y=30, w=90); pdf.image(img_1h, x=110, y=30, w=90)
        pdf.set_y(100); pdf.image(img_1d, x=55, y=105, w=100)

        out = os.path.join(self.workspace, "XAUUSD_ULTIMATE_V6.pdf")
        pdf.output(out)
        print(f"✅ SUCCESS: {out}")
        return out

if __name__ == "__main__":
    XauusdUltimateV6().generate()
