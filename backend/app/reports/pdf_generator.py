import os
from datetime import datetime, timezone
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
from app.core.logging import log_info, log_error

def generate_pdf_report(
    output_path: str,
    project_data: Dict[str, Any],
    documents_data: List[Dict[str, Any]],
    findings_data: List[Dict[str, Any]],
    checklist_data: List[Dict[str, Any]],
    report_number: str
) -> bool:
    """
    Generates an official AI Pre-Submission Review Report PDF using ReportLab.
    Labels the report clearly as 'AI Pre-Submission Review Report — Not an Official Permit Approval'.
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()
        
        # Custom Typography
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#0F172A')
        )
        subtitle_style = ParagraphStyle(
            'DocSub',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#64748B')
        )
        section_style = ParagraphStyle(
            'SectionHead',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=17,
            textColor=colors.HexColor('#1E293B'),
            spaceBefore=14,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#334155')
        )
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#B91C1C')
        )
        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#1E293B')
        )
        table_head_style = ParagraphStyle(
            'TableHead',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#FFFFFF')
        )

        elements = []

        # 1. Header Banner
        elements.append(Paragraph("BUILDPERMIT AI — RESIDENTIAL PERMIT PRE-CHECK PLATFORM", subtitle_style))
        elements.append(Paragraph("AI Pre-Submission Review Report", title_style))
        elements.append(Paragraph("<b>LEGAL NOTICE:</b> AI Pre-Submission Review Report — Not an Official Permit Approval. This report assists with preparation and does not guarantee approval by any building department.", disclaimer_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=4, spaceAfter=12))

        # 2. Project & Jurisdiction Summary Table
        proj_rows = [
            [
                Paragraph("<b>Project Name:</b>", body_style),
                Paragraph(str(project_data.get("name", "Untitled")), body_style),
                Paragraph("<b>Report ID:</b>", body_style),
                Paragraph(report_number, body_style)
            ],
            [
                Paragraph("<b>Property Address:</b>", body_style),
                Paragraph(str(project_data.get("address", "N/A")), body_style),
                Paragraph("<b>Date Generated:</b>", body_style),
                Paragraph(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), body_style)
            ],
            [
                Paragraph("<b>Jurisdiction:</b>", body_style),
                Paragraph(f"{project_data.get('city', '')}, {project_data.get('state_region', '')} ({project_data.get('jurisdiction_id', 'US-CA-GENERIC')})", body_style),
                Paragraph("<b>Project Type:</b>", body_style),
                Paragraph(f"{project_data.get('project_type', 'Residential')} ({project_data.get('num_floors', 1)} Fl)", body_style)
            ]
        ]
        proj_table = Table(proj_rows, colWidths=[90, 180, 85, 175])
        proj_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('PADDING', (0,0), (-1,-1), 5),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(proj_table)
        elements.append(Spacer(1, 12))

        # 3. Pre-Check Metrics Cards
        open_findings = [f for f in findings_data if f.get("status") in ("open", "in_review")]
        critical_count = sum(1 for f in open_findings if f.get("severity") == "critical")
        warning_count = sum(1 for f in open_findings if f.get("severity") == "warning")
        complete_checklist = sum(1 for c in checklist_data if c.get("status") == "complete")
        total_checklist = len(checklist_data) or 1
        checklist_pct = int((complete_checklist / total_checklist) * 100)

        metrics_data = [
            [
                Paragraph(f"<font size=16 color='#026FC7'><b>{len(documents_data)}</b></font><br/>Documents Analyzed", body_style),
                Paragraph(f"<font size=16 color='{'#DC2626' if critical_count > 0 else '#16A34A'}'><b>{critical_count}</b></font><br/>Critical Issues", body_style),
                Paragraph(f"<font size=16 color='#D97706'><b>{warning_count}</b></font><br/>Warnings / Inconsistencies", body_style),
                Paragraph(f"<font size=16 color='#16A34A'><b>{checklist_pct}%</b></font><br/>Checklist Completion", body_style),
            ]
        ]
        metrics_table = Table(metrics_data, colWidths=[130, 130, 135, 135])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 14))

        # 4. Uploaded Documents Inventory
        elements.append(Paragraph("1. Document Submittal Inventory", section_style))
        doc_rows = [[
            Paragraph("Document Name", table_head_style),
            Paragraph("Assigned Category", table_head_style),
            Paragraph("Pages", table_head_style),
            Paragraph("Classification Status", table_head_style)
        ]]
        for d in documents_data:
            doc_rows.append([
                Paragraph(d.get("filename", "Unknown"), table_cell_style),
                Paragraph(d.get("category", "General"), table_cell_style),
                Paragraph(str(d.get("page_count", 1)), table_cell_style),
                Paragraph(f"Confidence: {int((d.get('category_confidence') or 0.8)*100)}%", table_cell_style)
            ])
        doc_table = Table(doc_rows, colWidths=[180, 160, 50, 140])
        doc_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
            ('PADDING', (0,0), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ]))
        elements.append(doc_table)
        elements.append(Spacer(1, 14))

        # 5. Pre-Check Findings & Evidence
        elements.append(Paragraph("2. Pre-Check Findings & Evidence References", section_style))
        if not open_findings:
            elements.append(Paragraph("<i>No open issues or discrepancies detected in submitted documents.</i>", body_style))
        else:
            finding_rows = [[
                Paragraph("Severity", table_head_style),
                Paragraph("Finding & Explanation", table_head_style),
                Paragraph("Document & Evidence", table_head_style),
                Paragraph("Recommended Action", table_head_style)
            ]]
            for f in open_findings:
                sev = f.get("severity", "warning").upper()
                sev_color = "#DC2626" if sev == "CRITICAL" else ("#D97706" if sev == "WARNING" else "#2563EB")
                
                finding_desc = f"<b>{f.get('title')}</b><br/>{f.get('explanation')}"
                if f.get("rule_reference"):
                    finding_desc += f"<br/><font color='#64748B'>Rule: {f.get('rule_reference')}</font>"

                doc_ref = f.get("document_name") or "Cross-Document Check"
                if f.get("page_number"):
                    doc_ref += f" (Page {f.get('page_number')})"
                if f.get("evidence_text"):
                    doc_ref += f"<br/><font color='#475569'><i>\"{f.get('evidence_text')[:120]}\"</i></font>"

                finding_rows.append([
                    Paragraph(f"<font color='{sev_color}'><b>{sev}</b></font>", table_cell_style),
                    Paragraph(finding_desc, table_cell_style),
                    Paragraph(doc_ref, table_cell_style),
                    Paragraph(f.get("recommended_action") or "Review and update sheet.", table_cell_style)
                ])

            finding_table = Table(finding_rows, colWidths=[65, 185, 140, 140])
            finding_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
                ('PADDING', (0,0), (-1,-1), 5),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
            ]))
            elements.append(finding_table)

        elements.append(Spacer(1, 14))

        # 6. Pre-Submission Checklist Status
        elements.append(Paragraph("3. Pre-Submission Municipal Requirements Checklist", section_style))
        chk_rows = [[
            Paragraph("Category", table_head_style),
            Paragraph("Requirement", table_head_style),
            Paragraph("Status", table_head_style),
            Paragraph("Verification Notes", table_head_style)
        ]]
        for item in checklist_data:
            st = item.get("status", "missing").upper()
            st_color = "#16A34A" if st == "COMPLETE" else ("#DC2626" if st == "MISSING" else "#D97706")
            chk_rows.append([
                Paragraph(item.get("category", ""), table_cell_style),
                Paragraph(f"<b>{item.get('title')}</b><br/>{item.get('description')[:110]}", table_cell_style),
                Paragraph(f"<font color='{st_color}'><b>{st}</b></font>", table_cell_style),
                Paragraph(item.get("notes") or "N/A", table_cell_style)
            ])
        chk_table = Table(chk_rows, colWidths=[100, 180, 80, 170])
        chk_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
            ('PADDING', (0,0), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ]))
        elements.append(chk_table)
        elements.append(Spacer(1, 16))

        # 7. Final Footer & Legal Verification Note
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=8, spaceAfter=8))
        elements.append(Paragraph("<b>DISCLAIMER:</b> BuildPermit AI is a pre-submission preparation tool. Local building codes, zoning bylaws, utility easements, and geotechnical conditions vary widely. Homeowners and applicants must confirm all final submittals with licensed design professionals and the local building authority.", disclaimer_style))

        doc.build(elements)
        log_info(f"Generated PDF report successfully at {output_path}")
        return True
    except Exception as e:
        log_error(f"Failed to generate PDF report: {e}")
        return False
