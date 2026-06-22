import csv
import json
from io import StringIO, BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

def export_to_csv(result_data):
    """Export analysis result to CSV format"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["Sequence ID", "Length", "GC Content", "Nucleotide Composition"])
    
    # Write sequence data
    for seq in result_data.get("sequences", []):
        composition = seq.get("composition", {})
        comp_str = f"A:{composition.get('A', 0)} T:{composition.get('T', 0)} G:{composition.get('G', 0)} C:{composition.get('C', 0)}"
        
        writer.writerow([
            seq.get("id", ""),
            seq.get("length", ""),
            seq.get("gc_content", ""),
            comp_str if composition else ""
        ])
    
    # Write summary
    writer.writerow([])
    writer.writerow(["Summary"])
    summary = result_data.get("summary", {})
    for key, value in summary.items():
        writer.writerow([key, value])
    
    return output.getvalue()

def export_to_json(result_data):
    """Export analysis result to JSON format"""
    return json.dumps(result_data, indent=2, default=str)

def export_to_pdf(result_data):
    """Export analysis result to PDF format"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.5*inch, leftMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=12,
    )
    
    # Title
    elements.append(Paragraph("Bioinformatics Analysis Report", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Summary section
    elements.append(Paragraph("Analysis Summary", styles['Heading2']))
    summary = result_data.get("summary", {})
    summary_data = [["Metric", "Value"]]
    for key, value in summary.items():
        summary_data.append([str(key).replace("_", " ").title(), str(value)])
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Sequences section
    elements.append(Paragraph("Sequence Details", styles['Heading2']))
    seq_data = [["Sequence ID", "Length", "GC Content"]]
    for seq in result_data.get("sequences", [])[:10]:  # Limit to first 10 for readability
        seq_data.append([
            seq.get("id", ""),
            str(seq.get("length", "")),
            f"{seq.get('gc_content', ''):.2f}%" if seq.get('gc_content') else ""
        ])
    
    seq_table = Table(seq_data)
    seq_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    elements.append(seq_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
