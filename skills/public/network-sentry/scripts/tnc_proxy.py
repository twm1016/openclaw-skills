import subprocess
import socket
import time
import sys
import json
import os
from reporter import NetworkSentryReporter

def ping(target):
    try:
        output = subprocess.check_output(["ping", "-c", "4", target], stderr=subprocess.STDOUT, timeout=10).decode()
        lines = output.split('\n')
        avg_line = [line for line in lines if 'avg' in line]
        if avg_line:
            rtt = avg_line[0].split('/')[4]
            return True, f"{rtt} ms"
        return True, "Success"
    except Exception:
        return False, "Timed out"

def tcp_test(target, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    start = time.time()
    try:
        s.connect((target, int(port)))
        end = time.time()
        s.close()
        return True, f"{(end - start) * 1000:.2f} ms"
    except Exception as e:
        return False, "Closed/Refused"

def trace(target):
    try:
        output = subprocess.check_output(["traceroute", "-n", "-m", "15", target], stderr=subprocess.STDOUT, timeout=30).decode()
        return output
    except Exception as e:
        return f"Traceroute failed: {str(e)}"

def audit_services(target):
    common_ports = {
        22: "SSH (Remote Access)",
        80: "HTTP (Web Service)",
        443: "HTTPS (Secure Web)",
        1433: "MSSQL (Database)",
        3306: "MySQL (Database)",
        3389: "RDP (Remote Desktop)",
        5432: "PostgreSQL (Database)",
        8080: "Web-Proxy/Custom"
    }
    results = []
    print(f"\n--- [Audit] Common Services for {target} ---")
    for port, name in common_ports.items():
        ok, rtt = tcp_test(target, port)
        status = "[OPEN]" if ok else "[CLOSED]"
        results.append({"port": port, "service": name, "status": status, "rtt": rtt})
        print(f"{port:<6} | {name:<20} | {status:<10} | {rtt}")
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tnc_proxy.py <target> [port/--audit]")
        sys.exit(1)

    target = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "--audit"

    print(f"--- [AI Sentry] Diagnostic for {target} ---")
    
    ping_ok, ping_rtt = ping(target)
    print(f"Ping Succeeded: {ping_ok} ({ping_rtt})")

    audit_results = []
    if mode == "--audit":
        audit_results = audit_services(target)
    elif mode.isdigit():
        ok, rtt = tcp_test(target, mode)
        status = "[OPEN]" if ok else "[CLOSED]"
        audit_results = [{"port": int(mode), "service": "Custom Port", "status": status, "rtt": rtt}]
        print(f"TcpTest (Port {mode}): {status} ({rtt})")
    else:
        audit_results = audit_services(target)
    
    print("\n--- [Trace] Routing path ---")
    trace_output = trace(target)
    print(trace_output)

    print("\n--- [PDF] Generating Report ---")
    try:
        reporter = NetworkSentryReporter(target)
        filename = f"network_audit_report.pdf"
        save_path = f"/home/twming/.openclaw/workspace/{filename}"
        reporter.generate(
            ping_data={"ok": ping_ok, "rtt": ping_rtt},
            audit_data=audit_results,
            trace_data=trace_output,
            filename=save_path
        )
        print(f"REPORT_PATH: {save_path}")
    except Exception as e:
        print(f"Failed to generate PDF: {str(e)}")
