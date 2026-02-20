---
name: price-action-analyst
description: Comprehensive financial analysis tool for Stocks, Crypto, and Futures (MNQ, MGC). Supports dual-data sourcing (Tradovate API for institutional data or standard sources with 10-15m latency). Generates professional multi-timeframe PDF reports with Vegas Tunnel, SMC logic (FVG, Order Blocks), and AI tactical forecasts.
---

# Price Action Analyst 🕶️

A professional-grade market intelligence skill designed for high-precision technical analysis.

## Core Capabilities

1. **Dual-Data Sourcing**: 
   - **Institutional Mode**: Connects via Tradovate API for real-time CME futures data.
   - **Standard Mode**: Fallback to public data sources (10-15m latency) for general analysis.
2. **Strategy Alignment (V2.0)**: Built-in logic for Vegas Tunnel System (144/169/576/676), ATR filters, and EMA 12 trend confirmation.
3. **Multi-Timeframe Intelligence**: Correlates 5M, 1H, and 1D data to provide a unified market bias.
4. **SMC Detection**: Identifies Fair Value Gaps (FVG) and Order Blocks (OB).

## Usage Guide

### Generate Full Report
To trigger a comprehensive PDF analysis:
- Command: "Analyze [Asset Name] (e.g., MNQ, BTC, Gold)"
- The agent will run `scripts/analyze.py` and output a multi-page PDF.

### Switch Data Source
- To enable Tradovate: "Set my Tradovate API credentials"
- To use free source: "Run analysis using standard data"

## AI Tactical Logic
- **Resistance Detection**: Prioritizes FVG entrances and Vegas Med tunnel rejections.
- **Support Detection**: Focuses on Vegas Long (576/676) and institutional demand zones.
- **Scenario Analysis**: Provides specific price targets for "Bounce" and "Breakout" cases.
