import datetime
from fpdf import FPDF
import os

class NetworkSentryReporter:
    def __init__(self, target):
        self.target = target
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)

    def generate(self, ping_data, audit_data, trace_data, filename):
        self.pdf.add_page()
        
        # --- Header ---
        self.pdf.set_fill_color(30, 41, 59)
        self.pdf.rect(0, 0, 210, 40, 'F')
        
        self.pdf.set_y(12)
        self.pdf.set_font('helvetica', 'B', 22)
        self.pdf.set_text_color(245, 158, 11)
        self.pdf.cell(0, 10, 'NETWORK SENTRY DIAGNOSTIC', new_x='LMARGIN', new_y='NEXT', align='C')
        
        self.pdf.set_font('helvetica', 'I', 10)
        self.pdf.set_text_color(255, 255, 255)
        self.pdf.cell(0, 10, f'Target: {self.target} | Generated: {self.timestamp} UTC', new_x='LMARGIN', new_y='NEXT', align='C')
        self.pdf.ln(15)

        # --- I. Summary Section ---
        self.pdf.set_font('helvetica', 'B', 14); self.pdf.set_text_color(30, 41, 59)
        self.pdf.cell(0, 10, 'I. Connectivity Summary', new_x='LMARGIN', new_y='NEXT')
        self.pdf.set_font('helvetica', '', 11); self.pdf.set_text_color(0, 0, 0)
        
        ping_status = "PASS" if ping_data['ok'] else "FAIL"
        self.pdf.multi_cell(0, 8, f"Status: {ping_status}\nAvg Latency (ICMP): {ping_data['rtt']}\nDiagnostic Result: Network layer is responsive.")
        self.pdf.ln(5)

        # --- II. Common Services Audit ---
        self.pdf.set_font('helvetica', 'B', 14); self.pdf.set_text_color(30, 41, 59)
        self.pdf.cell(0, 10, 'II. Common Services Audit', new_x='LMARGIN', new_y='NEXT')
        
        self.pdf.set_font('helvetica', 'B', 10); self.pdf.set_fill_color(51, 65, 85); self.pdf.set_text_color(255, 255, 255)
        self.pdf.cell(25, 10, 'Port', 1, 0, 'C', True)
        self.pdf.cell(50, 10, 'Service', 1, 0, 'C', True)
        self.pdf.cell(35, 10, 'Status', 1, 0, 'C', True)
        self.pdf.cell(80, 10, 'Latency / Error', 1, 1, 'C', True)
        
        self.pdf.set_font('helvetica', '', 10); self.pdf.set_text_color(0, 0, 0)
        for row in audit_data:
            self.pdf.cell(25, 8, str(row['port']), 1, 0, 'C')
            self.pdf.cell(50, 8, row['service'], 1, 0, 'L')
            
            if "OPEN" in row['status']:
                self.pdf.set_text_color(22, 163, 74)
            else:
                self.pdf.set_text_color(220, 38, 38)
            
            self.pdf.cell(35, 8, row['status'], 1, 0, 'C')
            self.pdf.set_text_color(0, 0, 0)
            self.pdf.cell(80, 8, str(row['rtt']), 1, 1, 'L')

        # --- III. Routing Intelligence ---
        self.pdf.ln(10)
        self.pdf.set_font('helvetica', 'B', 14); self.pdf.set_text_color(30, 41, 59)
        self.pdf.cell(0, 10, 'III. Routing Intelligence (Traceroute)', new_x='LMARGIN', new_y='NEXT')
        self.pdf.set_font('courier', '', 8); self.pdf.set_fill_color(248, 250, 252)
        # 清洗 trace_data 確保無非法字符
        clean_trace = trace_data.encode('ascii', 'ignore').decode('ascii')
        self.pdf.multi_cell(0, 5, clean_trace, border=1, fill=True)

        self.pdf.output(filename)
        return filename
