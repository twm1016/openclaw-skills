---
name: network-sentry
description: Advanced network diagnostic tool mimicking PowerShell's Test-NetConnection. Use when the user needs to check connectivity (Ping, TCP Port, Traceroute) to an endpoint or troubleshoot connection issues with AI-driven analysis and repair suggestions.
---

# Network Sentry 🛡️ (V2.0)

A professional diagnostic skill for verifying network health and service exposure between this server and external/internal endpoints.

## Core Capabilities

1. **Connectivity Test**: ICMP Ping, TCP Port verification, and fast Traceroute (-n).
2. **Common Services Audit**: One-click scan of essential ports (22, 80, 443, 1433, 3306, 3389, 5432, 8080).
3. **Professional PDF Reporting**: Generates a high-fidelity diagnostic report with color-coded status tables and AI-driven security recommendations.

## Usage Guide

### Full Audit & PDF Report
To scan a target and generate a professional PDF:
- Run: `python3 scripts/tnc_proxy.py <target> --audit`
- Result: Outputs `network_audit_report.pdf` to the workspace.

### Single Target Port Test
- Run: `python3 scripts/tnc_proxy.py <target> <port>`

## AI Recommendation Logic
- **High Latency (>150ms)**: Suggests checking regional ISP congestion.
- **Port 3389/22 Exposure**: Triggers a CRITICAL security warning in the PDF report.
- **MSSQL (1433) / MySQL (3306)**: Verified as part of the standard database integrity check.
