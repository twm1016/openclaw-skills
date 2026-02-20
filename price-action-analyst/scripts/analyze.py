import os
import sys
import pandas as pd
import mplfinance as mpf
from tvDatafeed import TvDatafeed, Interval
from fpdf import FPDF
import datetime

# --- 配置區 ---
TRADOVATE_ENABLED = False # 待填入 API 後改為 True
DEFAULT_SYMBOL = 'MNQ1!'
PROXY_SYMBOL = 'NAS100USD' # 免費源備用 Ticker

class PriceActionAnalyst:
    def __init__(self):
        self.tv = TvDatafeed()
        self.report_date = datetime.date.today().strftime("%Y-%m-%d")

    def fetch_data(self, symbol, interval, n_bars=300):
        """雙軌制數據抓取"""
        if TRADOVATE_ENABLED:
            print(f"Connecting to Tradovate for institutional data: {symbol}...")
            # 這裡預留 Tradovate API 調用邏輯
            return None 
        else:
            print(f"Using standard data source for: {symbol} (Latency: 10-15m)...")
            try:
                # 優先嘗試期貨 Ticker
                df = self.tv.get_hist(symbol=symbol, exchange='CME', interval=interval, n_bars=n_bars)
                if df is None:
                    # 備用：使用 OANDA 代理
                    df = self.tv.get_hist(symbol=PROXY_SYMBOL, exchange='OANDA', interval=interval, n_bars=n_bars)
                if df is not None:
                    df.index = pd.to_datetime(df.index)
                return df
            except:
                return None

    def calculate_indicators(self, df):
        """對齊 MNQ V2.0 策略邏輯"""
        df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema144'] = df['close'].ewm(span=144, adjust=False).mean()
        df['ema169'] = df['close'].ewm(span=169, adjust=False).mean()
        df['ema576'] = df['close'].ewm(span=576, adjust=False).mean()
        df['ema676'] = df['close'].ewm(span=676, adjust=False).mean()
        # ATR 14
        hl = df['high'] - df['low']
        hcp = (df['high'] - df['close'].shift()).abs()
        lcp = (df['low'] - df['close'].shift()).abs()
        df['atr'] = pd.concat([hl, hcp, lcp], axis=1).max(axis=1).rolling(14).mean()
        return df

    def generate_pdf(self, symbol, df_5m, df_1h, df_1d):
        price = df_5m['close'].iloc[-1]
        ema576 = df_5m['ema576'].iloc[-1]
        atr = df_5m['atr'].iloc[-1]
        bias = "BULLISH" if price > ema576 else "BEARISH"

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('helvetica', 'B', 20)
        pdf.set_text_color(245, 158, 11)
        pdf.cell(0, 15, f'MNQ Analysis Report - {symbol}', new_x='LMARGIN', new_y='NEXT', align='C')
        pdf.ln(5)

        # I. Technical Setup
        pdf.set_font('helvetica', 'B', 14); pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, 'I. Technical Setup (Current Values)', new_x='LMARGIN', new_y='NEXT')
        pdf.set_font('helvetica', '', 10)
        pdf.multi_cell(0, 7, f"Price: {price:,.1f} | Bias: {bias} | ATR: {atr:.2f}\nVegas Med (144/169): {df_5m['ema144'].iloc[-1]:,.1f} / {df_5m['ema169'].iloc[-1]:,.1f}\nVegas Long (576/676): {df_5m['ema576'].iloc[-1]:,.1f} / {df_5m['ema676'].iloc[-1]:,.1f}")
        
        # II. Level Matrix
        pdf.ln(5); pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'II. Strategic Level Matrix', new_x='LMARGIN', new_y='NEXT')
        pdf.set_font('helvetica', 'B', 10); pdf.set_fill_color(30, 41, 59); pdf.set_text_color(255, 255, 255)
        pdf.cell(35, 10, 'Type', 1, 0, 'C', True); pdf.cell(30, 10, 'Price', 1, 0, 'C', True); pdf.cell(125, 10, 'Technical Reasoning', 1, 1, 'C', True)
        
        pdf.set_text_color(0, 0, 0); pdf.set_font('helvetica', '', 9)
        # 示範位
        pdf.cell(35, 8, 'RESISTANCE', 1); pdf.cell(30, 8, f'{price*1.01:,.1f}', 1); pdf.cell(125, 8, 'Vegas Tunnel rejection / FVG entrance.', 1, 1)
        pdf.cell(35, 8, 'SUPPORT', 1); pdf.cell(30, 8, f'{price*0.99:,.1f}', 1); pdf.cell(125, 8, 'Bullish Order Block / Long-term trend anchor.', 1, 1)

        # III. AI Forecast
        pdf.ln(5); pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'III. AI Tactical Forecast', new_x='LMARGIN', new_y='NEXT')
        pdf.set_font('helvetica', '', 10)
        pdf.multi_cell(0, 7, f"If price stays above {price*0.99:,.1f}, the {bias} bias remains strong. A breach of {price*1.01:,.1f} confirms a new breakout cycle.")

        # 保存並導出
        pdf.output(f'{symbol.lower()}_final_report.pdf')
        print(f"Report generated: {symbol.lower()}_final_report.pdf")

if __name__ == "__main__":
    analyst = PriceActionAnalyst()
    data_5m = analyst.fetch_data(DEFAULT_SYMBOL, Interval.in_5_minute)
    if data_5m is not None:
        data_5m = analyst.calculate_indicators(data_5m)
        analyst.generate_pdf(DEFAULT_SYMBOL, data_5m, None, None)
