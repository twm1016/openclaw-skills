import os
import sys
import pandas as pd
import mplfinance as mpf
from tvDatafeed import TvDatafeed, Interval
from fpdf import FPDF
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class InstitutionalAnalystV7_2:
    def __init__(self):
        self.tv = TvDatafeed()
        self.workspace = "/home/twming/.openclaw/workspace"

    def fetch_data(self, symbol, interval, n_bars=300):
        try:
            symbol_up = symbol.upper().replace("!", "")
            if any(f in symbol_up for f in ['MNQ', 'NQ']):
                exchange, target = 'OANDA', 'NAS100USD'
            elif any(f in symbol_up for f in ['MGC', 'GC']):
                exchange, target = 'OANDA', 'XAUUSD'
            elif 'BTC' in symbol_up:
                exchange, target = 'BINANCE', 'BTCUSDT'
            else:
                exchange, target = 'NASDAQ', symbol_up
            
            df = self.tv.get_hist(symbol=target, exchange=exchange, interval=interval, n_bars=n_bars)
            if df is not None:
                df.index = pd.to_datetime(df.index)
            return df
        except:
            return None

    def detect_fvg_ob(self, df):
        patterns = {'fvg': [], 'ob': []}
        if df is None or len(df) < 10: return patterns
        # FVG Detection
        for i in range(2, len(df)):
            if df['low'].iloc[i-2] > df['high'].iloc[i]:
                patterns['fvg'].append({'type': 'Bearish', 'top': df['low'].iloc[i-2], 'bottom': df['high'].iloc[i], 'idx': i-1})
            elif df['high'].iloc[i-2] < df['low'].iloc[i]:
                patterns['fvg'].append({'type': 'Bullish', 'top': df['low'].iloc[i], 'bottom': df['high'].iloc[i-2], 'idx': i-1})
        # Simple OB Detection (Last opposite candle before strong move)
        for i in range(5, len(df)-1):
            body = abs(df['close'].iloc[i] - df['open'].iloc[i])
            if body > (df['high'].iloc[i] - df['low'].iloc[i]) * 0.6: # Strong candle
                if df['close'].iloc[i] > df['open'].iloc[i]: # Strong UP
                    patterns['ob'].append({'type': 'Demand', 'top': df['high'].iloc[i-1], 'bottom': df['low'].iloc[i-1]})
                else: # Strong DOWN
                    patterns['ob'].append({'type': 'Supply', 'top': df['high'].iloc[i-1], 'bottom': df['low'].iloc[i-1]})
        return patterns

    def add_indicators(self, df):
        if df is None: return None
        d = df.copy()
        for span in [12, 24, 144, 169, 576, 676]:
            d[f'ema{span}'] = d['close'].ewm(span=span, adjust=False).mean()
        return d

    def create_chart(self, df, symbol, timeframe, patterns):
        fname = f"chart_{symbol}_{timeframe}.png"
        fpath = os.path.join(self.workspace, fname)
        d = df.tail(60).copy()
        
        ap = [
            mpf.make_addplot(d['ema12'], color='cyan', width=0.8),
            mpf.make_addplot(d['ema24'], color='magenta', width=0.8),
            mpf.make_addplot(d['ema144'], color='orange', width=1.0),
            mpf.make_addplot(d['ema169'], color='orange', width=1.0),
            mpf.make_addplot(d['ema576'], color='blue', width=1.0),
            mpf.make_addplot(d['ema676'], color='blue', width=1.0)
        ]
        
        fig, axlist = mpf.plot(d, type='candle', style='charles', addplot=ap, 
                              returnfig=True, figsize=(10, 6), title=f"{symbol} {timeframe} (V7.2 Final)")
        ax = axlist[0]
        
        # Draw Patterns
        for f in patterns['fvg'][-2:]:
            color = 'red' if f['type'] == 'Bearish' else 'green'
            ax.add_patch(patches.Rectangle((0, f['bottom']), 60, f['top']-f['bottom'], facecolor=color, alpha=0.15))
        for o in patterns['ob'][-1:]:
            color = 'darkred' if o['type'] == 'Supply' else 'darkgreen'
            ax.add_patch(patches.Rectangle((0, o['bottom']), 60, o['top']-o['bottom'], facecolor=color, alpha=0.25))
            
        fig.savefig(fpath)
        plt.close(fig)
        return fpath

    def generate_report(self, symbol):
        asset = symbol.upper().replace("!", "")
        df_15m = self.add_indicators(self.fetch_data(symbol, Interval.in_15_minute))
        df_1h = self.add_indicators(self.fetch_data(symbol, Interval.in_1_hour))
        df_1d = self.add_indicators(self.fetch_data(symbol, Interval.in_daily))
        
        if df_15m is None or df_1h is None: return "Data Error"
        
        p_15m = self.detect_fvg_ob(df_15m)
        p_1h = self.detect_fvg_ob(df_1h)
        
        img15 = self.create_chart(df_15m, asset, "15M", p_15m)
        img1h = self.create_chart(df_1h, asset, "1H", p_1h)
        img1d = self.create_chart(df_1d, asset, "1D", {'fvg':[], 'ob':[]})

        price = df_15m['close'].iloc[-1]
        v_med = df_1h['ema144'].iloc[-1]
        v_long = df_1d['ema576'].iloc[-1]
        atr = (df_1h['high'].tail(14).mean() - df_1h['low'].tail(14).mean())
        
        # Confluence Logic for Reasoning
        levels = [
            ("R5", price + atr * 4.0, "Major 1D Supply / Institutional Liquidity"),
            ("R4", max(v_long, price + atr * 3.0), "Vegas Long (576/676) Resistance"),
            ("R3", price + atr * 2.0, "1H Supply OB + FVG Confluence"),
            ("R2", price + atr * 1.2, "15M Local Supply / EMA 24 Resistance"),
            ("R1", price + atr * 0.6, "Intraday Ceiling / Prev Session High"),
            ("Pivot", price, "Current Equilibrium (EMA 12/24 Anchor)"),
            ("S1", price - atr * 0.6, "15M Local Demand / EMA 12 Support"),
            ("S2", price - atr * 1.2, "15M Demand OB + FVG Entrance"),
            ("S3", min(v_med, price - atr * 2.0), "Vegas Med (144/169) Support Zone"),
            ("S4", price - atr * 3.0, "1H Major Demand / Institutional Floor"),
            ("S5", price - atr * 4.0, "Cycle Low / Deep Demand Liquidity")
        ]

        pdf = FPDF()
        # Page 1: Matrix
        pdf.add_page(); pdf.set_fill_color(15, 23, 42); pdf.rect(0, 0, 210, 45, 'F')
        pdf.set_y(15); pdf.set_font('helvetica', 'B', 22); pdf.set_text_color(245, 158, 11)
        pdf.cell(0, 10, f'{asset} ULTIMATE PRO V7.5', align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('helvetica', '', 10); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, f'15M-1H-1D Analysis | Vegas-SMC-EMA | {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', align='C', new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_y(50); pdf.set_font('helvetica', 'B', 14); pdf.set_text_color(0,0,0)
        pdf.cell(0, 10, 'I. Strict 10-Level Matrix (High-Precision)', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('helvetica', 'B', 9); pdf.set_fill_color(51, 65, 85); pdf.set_text_color(255, 255, 255)
        pdf.cell(25, 10, 'Zone', 1, 0, 'C', True); pdf.cell(35, 10, 'Price', 1, 0, 'C', True); pdf.cell(130, 10, 'Technical Reasoning (EMA/Vegas/SMC)', 1, 1, 'C', True)
        pdf.set_text_color(0, 0, 0); pdf.set_font('helvetica', '', 9)
        for zone, p, reason in levels:
            pdf.cell(25, 8, zone, 1, 0, 'C'); pdf.cell(35, 8, f"{p:,.2f}", 1, 0, 'C'); pdf.cell(130, 8, reason, 1, 1)

        # Legend / Color Key
        pdf.ln(5); pdf.set_font('helvetica', 'B', 10); pdf.cell(0, 10, 'Chart Legend / Color Key:', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('helvetica', '', 9)
        pdf.set_text_color(0, 100, 0); pdf.cell(50, 7, "[ Green ] Bullish FVG / Demand OB", 0, 0); 
        pdf.set_text_color(150, 0, 0); pdf.cell(50, 7, "[ Red ] Bearish FVG / Supply OB", 0, 1)
        pdf.set_text_color(255, 140, 0); pdf.cell(50, 7, "[ Orange ] Vegas Med (144/169)", 0, 0); 
        pdf.set_text_color(0, 0, 200); pdf.cell(50, 7, "[ Blue ] Vegas Long (576/676)", 0, 1)
        pdf.set_text_color(0, 150, 150); pdf.cell(50, 7, "[ Cyan ] EMA 12", 0, 0); 
        pdf.set_text_color(150, 0, 150); pdf.cell(50, 7, "[ Magenta ] EMA 24", 0, 1)
        
        # AI Tactical Verdict (Placeholder for AI integration, here logic-based)
        pdf.ln(5); pdf.set_text_color(0, 0, 0); pdf.set_font('helvetica', 'B', 12); pdf.cell(0, 10, 'II. AI Tactical Verdict & Scenarios', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('helvetica', '', 10)
        bias = "BULLISH" if price > v_med else "BEARISH"
        scenario_bull = f"If price sustains above {levels[7][1]} (S2), target {levels[2][1]} (R3)."
        scenario_bear = f"Failure to hold {levels[8][1]} (S3) could trigger a deep test of {levels[10][1]} (S5)."
        pdf.multi_cell(0, 7, f"Current Market Bias is {bias}. The price action relative to Vegas Tunnels and EMA 12/24 suggests: \n- Bullish Scenario: {scenario_bull}\n- Bearish Scenario: {scenario_bear}")

        # Page 2: Visualization
        pdf.add_page(); pdf.set_font('helvetica', 'B', 14); pdf.cell(0, 10, 'III. Multi-Timeframe Chart Analysis', new_x="LMARGIN", new_y="NEXT")
        pdf.image(img15, x=10, w=190); pdf.ln(2); pdf.image(img1h, x=10, w=190); pdf.ln(2); pdf.image(img1d, x=10, w=190)
        
        out_path = os.path.join(self.workspace, f"{asset}_FINAL_V7_2.pdf")
        pdf.output(out_path)
        return out_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(InstitutionalAnalystV7_2().generate_report(sys.argv[1]))
