---
name: network-sentry
description: Advanced network diagnostic tool mimicking PowerShell's Test-NetConnection. Use when the user needs to check connectivity (Ping, TCP Port, Traceroute) to an endpoint or troubleshoot connection issues with AI-driven analysis and repair suggestions.
version: 2.0
---

# Network Sentry (V2.0) 🛡️

Institutional-grade network auditing and diagnostic tool.

## Core Capabilities

1. **Service Port Audit**: Automated scanning for common critical services (SSH, HTTP, HTTPS, MSSQL, MySQL, RDP, PostgreSQL).
2. **Professional Reporting**: Generates detailed PDF audit reports with status highlighting.
3. **Deep Diagnostics**: AI-driven analysis of connectivity issues based on port status.

## Usage Guide

### Run Network Audit
- Command: `Audit [Host/IP] (e.g., 8.8.8.8, my-server.com)`
- The system executes `scripts/tnc_proxy.py` and returns a professional PDF report.

## Port Watchlist
- **22**: SSH
- **80/443**: Web Services
- **1433**: MSSQL (Institutional Database)
- **3306**: MySQL
- **3389**: RDP (Remote Desktop)
- **5432**: PostgreSQL
- **8080**: Alternative HTTP
