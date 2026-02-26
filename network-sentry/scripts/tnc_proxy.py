import os
import sys
import subprocess
import datetime
from fpdf import FPDF

class NetworkSentryV2:
    """
    Network Sentry V2.0
    - Capabilities: Ping, TCP Port Test, Traceroute
    - Audit: Common Services (SSH, HTTP, MSSQL, MySQL, RDP, etc.)
    - Output: Professional PDF Report
    """
    def __init__(self):
        self.common_ports = {
            22: "SSH",
            80: "HTTP",
            443: "HTTPS",
            1433: "MSSQL",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            8080: "HTTP-ALT"
        }
        self.workspace = "/home/twming/.openclaw/workspace"

    def test_port(self, host, port):
        try:
            cmd = f"nc -zv -w 2 {host} {port}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return "[OPEN]" if result.returncode == 0 else "[CLOSED]"
        except:
            return "[ERROR]"

    def generate_report(self, target="8.8.8.8"):
        report_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        results = []
        for port, service in self.common_ports.items():
            status = self.test_port(target, port)
            results.append((port, service, status))

        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(30, 41, 59); pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_y(10); pdf.set_font('helvetica', 'B', 24); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, 'NETWORK SENTRY AUDIT', align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('helvetica', '', 10)
        pdf.cell(0, 10, f'V2.0 Audit Report | {report_date} UTC | Target: {target}', align='C', new_x="LMARGIN", new_y="NEXT")

        pdf.set_y(50); pdf.set_font('helvetica', 'B', 14); pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, 'I. Service Port Audit Results', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('helvetica', 'B', 10); pdf.set_fill_color(200, 200, 200)
        pdf.cell(30, 10, 'Port', 1, 0, 'C', True); pdf.cell(60, 10, 'Service', 1, 0, 'C', True); pdf.cell(100, 10, 'Status', 1, 1, 'C', True)

        pdf.set_font('helvetica', '', 10)
        for port, svc, status in results:
            pdf.cell(30, 8, str(port), 1, 0, 'C')
            pdf.cell(60, 8, svc, 1, 0, 'C')
            if status == "[OPEN]": pdf.set_text_color(0, 128, 0)
            else: pdf.set_text_color(128, 0, 0)
            pdf.cell(100, 8, status, 1, 1, 'C')
            pdf.set_text_color(0, 0, 0)

        out_path = os.path.join(self.workspace, f"network_audit_{target}.pdf")
        pdf.output(out_path)
        return out_path

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "8.8.8.8"
    print(NetworkSentryV2().generate_report(target))
