---
name: network-sentry
description: Advanced network diagnostic tool mimicking PowerShell's Test-NetConnection. Use when the user needs to check connectivity (Ping, TCP Port, Traceroute) to an endpoint or troubleshoot connection issues with AI-driven analysis and repair suggestions.
---

# Network Sentry 🛡️

A professional diagnostic skill for verifying network health between this server and external/internal endpoints.

## Core Capabilities

1. **Connectivity Test**: Ping, TCP Port verification, and Traceroute.
2. **AI Analysis**: Translates raw RTT and hop data into human-readable insights.
3. **Watchlist Management**: One-click check for all critical services.

## Usage Guide

### Single Target Test
To test a specific address:
- Run: `python3 scripts/tnc_proxy.py <target> [port]`

### Full Health Check
1. Read `references/watchlist.md` to identify all targets.
2. Loop through each target using the script.
3. Provide a summary table of results.

## AI Recommendation Logic
- **High Latency (>150ms)**: Suggest checking regional ISP congestion or using a different tunnel endpoint.
- **TCP Failure but Ping OK**: Suggest that the service is down or the firewall is blocking that specific port.
- **Traceroute Timeout at Hop 1-2**: Suggest local network interface or router issues.
- **Traceroute Timeout mid-way**: Suggest backbone provider issues.
