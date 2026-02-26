---
name: price-action-analyst
description: Comprehensive financial analysis tool for Stocks, Crypto, and Futures (MNQ, MGC). Supports dual-data sourcing (Tradovate API for institutional data or standard sources with 10-15m latency). Generates professional multi-timeframe PDF reports with Vegas Tunnel, SMC logic (FVG, Order Blocks), and AI tactical forecasts.
version: 7.5
spec: Ultimate Institutional Pro
---

# Price Action Analyst (V7.5 Ultimate) 🕶️

Professional-grade market intelligence tool for high-precision technical analysis.

## Core Capabilities (V7.5 Spec)

1. **Dual-Data Sourcing**:
   - **Institutional Mode**: Priority connection via Tradovate API for real-time CME/NYMEX futures.
   - **Standard Mode**: Fallback to public data (OANDA/Binance) for general asset analysis.
2. **Standardized Analysis Framework**:
   - **Timeframes**: Mandatory 15M, 1H, and 1D correlation.
   - **Indicators**: Vegas Tunnel (144/169/576/676) + EMA 12/24 trend filters.
   - **SMC Detection**: Automated detection and visualization of Fair Value Gaps (FVG) and Order Blocks (OB).
3. **High-Precision Output**:
   - **Strict 10-Level Matrix**: Forced output of R5 to S5 levels with technical confluence reasoning.
   - **Visual Annotations**: Transparent geometric overlays on charts for detected FVG/OB zones.
   - **AI Tactical Verdict**: Automated scenarios for Bullish/Bearish price paths based on key level interaction.

## Usage Guide

### Generate Ultimate Report
To trigger a V7.5 PDF analysis:
- Command: `Analyze [Asset Symbol] (e.g., MNQ!, BTC!, GC!)`
- The system executes `scripts/analyze.py` using the Ultimate V7.5 logic.

### Technical Spec
- **Color Key**: 
  - Green/Red Rectangles: Bullish/Bearish FVG & Demand/Supply OB.
  - Orange Lines: Vegas Med Tunnel (144/169).
  - Blue Lines: Vegas Long Tunnel (576/676).
  - Cyan/Magenta Lines: EMA 12/24.

## AI Tactical Logic
- **Precision**: Levels are calculated with confluence (e.g., FVG overlapping with Vegas Tunnel).
- **Bias**: Bullish/Bearish ratings are strictly relative to the Vegas Med Tunnel.
