import subprocess
import socket
import time
import sys
import json

def ping(target):
    try:
        output = subprocess.check_output(["ping", "-c", "4", target], stderr=subprocess.STDOUT, timeout=10).decode()
        # 提取平均延遲
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
    s.settimeout(3)
    start = time.time()
    try:
        s.connect((target, int(port)))
        end = time.time()
        s.close()
        return True, f"{(end - start) * 1000:.2f} ms"
    except Exception as e:
        return False, str(e)

def trace(target):
    try:
        output = subprocess.check_output(["traceroute", "-m", "15", target], stderr=subprocess.STDOUT, timeout=30).decode()
        return output
    except Exception as e:
        return f"Traceroute failed: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tnc_proxy.py <target> [port]")
        sys.exit(1)

    target = sys.argv[1]
    port = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"--- 📡 AI Sentry Diagnostic for {target} ---")
    
    ping_ok, ping_rtt = ping(target)
    print(f"Ping Succeeded: {ping_ok} ({ping_rtt})")

    if port:
        tcp_ok, tcp_rtt = tcp_test(target, port)
        print(f"TcpTestSucceeded (Port {port}): {tcp_ok} ({tcp_rtt})")
    
    print("\n--- 🔍 Traceroute (Max 15 hops) ---")
    print(trace(target))
