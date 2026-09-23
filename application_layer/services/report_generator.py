"""
PDF report generator.
Converts an AnalysisResult and its Recommendations into a formatted PDF.
"""

import os
import json
from fpdf import FPDF
from datetime import datetime

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Startup Analysis & Recommendation Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(analysis, startup, recommendations) -> str:
    """
    Generates a PDF report and returns the file path.
    """
    pdf = PDFReport()
    pdf.add_page()
    
    # ── Startup Profile ──
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Company: {startup.company_name}", 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f"Industry: {startup.industry} | Stage: {startup.funding_stage}", 0, 1)
    pdf.cell(0, 8, f"Peer Group: {analysis.peer_group_label}", 0, 1)
    pdf.cell(0, 8, f"Efficiency Score: {analysis.efficiency_score:.1f} / 100", 0, 1)
    pdf.ln(5)
    
    # ── Top Deviations ──
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Top Metric Deviations vs Peers", 0, 1)
    pdf.set_font('Arial', '', 10)
    
    deviations = json.loads(analysis.deviations_json)
    for dev in deviations[:5]:
        direction = "above" if dev["direction"] == "above" else "below"
        pdf.multi_cell(0, 8, f"- {dev['label']}: {dev['your_value']:.2f} (Peer Avg: {dev['benchmark_mean']:.2f}). {abs(dev['z_score']):.1f} std devs {direction} peers.")
    pdf.ln(5)
    
    # ── Recommendations ──
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Prioritized Recommendations", 0, 1)
    pdf.ln(2)
    
    for rec in recommendations:
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, f"{rec.rank}. {rec.title}", 0, 1)
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 6, f"Category: {rec.category} | Impact: {rec.impact_level}", 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 6, rec.explanation)
        pdf.ln(5)
        
    output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data_layer", "processed")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"report_{analysis.id}.pdf")
    pdf.output(file_path)
    
    return file_path
