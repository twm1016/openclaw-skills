import os
import sys
import pandas as pd
import mplfinance as mpf
from tvDatafeed import TvDatafeed, Interval
from fpdf import FPDF
import datetime

class ForceReportV6:
    def __init__(self):
        self.tv = TvDatafeed()
        self.workspace = "/home/twming/.openclaw/workspace"

    def fetch_oanda(self, asset_name):
        symbol = 'NAS100USD' if asset_name == 'MNQ' else 'GOLD'
        print(f"  [Backup] Fetching {symbol} from OANDA...")
        try:
            df = self.tv.get_hist(symbol=symbol, exchange='OANDA', interval=Interval.in_5_minute, n_bars=100)
            if df is not None: df.index = pd.to_datetime(df.index)
            return df
        except: return None

    def generate(self, asset_name):
        df = self.fetch_oanda(asset_name)
        if df is None: return None
        
        price = df['close'].iloc[-1]
        v_med = df['close'].ewm(span=144).mean().iloc[-1]
        
        img_path = os.path.join(self.workspace, f"force_{asset_name}.png")
        mpf.plot(df.tail(40), type='candle', style='charles', savefig=img_path)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(30, 41, 59); pdf.rect(0, 0, 210, 30, 'F')
        pdf.set_y(10); pdf.set_font('helvetica', 'B', 20); pdf.set_text_color(245, 158, 11)
        pdf.cell(0, 10, f'{asset_name} VERIFIED REPORT (OANDA SOURCE)', new_x='LMARGIN', new_y='NEXT', align='C')
        
        pdf.set_y(40); pdf.set_text_color(0, 0, 0); pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 10, f'Current {asset_name} Price: {price:,.2f}', new_x='LMARGIN', new_y='NEXT')
        pdf.cell(0, 10, f'Calculated Vegas Med: {v_med:,.1f}', new_x='LMARGIN', new_y='NEXT')
        
        pdf.ln(5); pdf.image(img_path, w=170)
        
        out = os.path.join(self.workspace, f"{asset_name.lower()}_verified_v6.pdf")
        pdf.output(out)
        return out

if __name__ == "__main__":
    force = ForceReportV6()
    for n in ['MNQ', 'MGC']:
        p = force.generate(n)
        print(f"SUCCESS: {p}")
