import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_documents"))
os.makedirs(DATA_DIR, exist_ok=True)

def create_sample_permit_application(path: str):
    doc = SimpleDocTemplate(path, pagesize=letter, margin=36)
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#0F172A'))
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#1E293B'))
    body = ParagraphStyle('B', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#334155'))

    story = [
        Paragraph("DEPARTMENT OF BUILDING AND SAFETY — CITY OF SPRINGFIELD", h2),
        Paragraph("RESIDENTIAL BUILDING PERMIT APPLICATION", h1),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=6, spaceAfter=10),
        Paragraph("<b>1. PROJECT SITE LOCATION</b>", h2),
        Paragraph("Job Address: <b>124 Elm Street, Springfield, CA 90210</b>", body),
        Paragraph("Parcel Number (APN): <b>452-890-1234</b>", body),
        Paragraph("Zoning District: <b>R-1 Single Family Residential</b>", body),
        Spacer(1, 8),
        Paragraph("<b>2. APPLICANT & OWNER IDENTIFICATION</b>", h2),
        Paragraph("Property Owner Name: <b>Alex Builder</b>", body),
        Paragraph("Owner Phone: <b>(555) 234-5678</b> | Email: <b>alex.builder@example.com</b>", body),
        Paragraph("Contractor License Number: <b>CSLB-987654-B</b>", body),
        Spacer(1, 8),
        Paragraph("<b>3. SCOPE OF PROPOSED WORK</b>", h2),
        Paragraph("Scope of Work: <b>One-story master bedroom and bathroom addition to existing single-family residence.</b>", body),
        Paragraph("Existing Building Area: <b>1,400 sq ft</b>", body),
        Paragraph("Proposed Addition Area: <b>450 sq ft</b>", body),
        Paragraph("Total Floor Area: <b>1,850 sq ft</b>", body),
        Paragraph("Number of Stories: <b>1 Story</b> | Construction Type: <b>Type V-B Wood Frame</b>", body),
        Spacer(1, 10),
        Paragraph("<b>4. OWNER-BUILDER DECLARATION & SIGNATURE</b>", h2),
        Paragraph("I hereby certify that I have read this application and state that the above information is correct. I agree to comply with all city ordinances and state laws relating to building construction.", body),
        Spacer(1, 12),
        Paragraph("Applicant Signature: <i>Alex Builder</i> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Date: <b>2024-10-15</b>", body),
    ]
    doc.build(story)

def create_sample_site_plan(path: str):
    doc = SimpleDocTemplate(path, pagesize=letter, margin=36)
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#0F172A'))
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#1E293B'))
    body = ParagraphStyle('B', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#334155'))

    story = [
        Paragraph("ARCHITECTURAL SITE PLAN & PLOT PLAN", h1),
        Paragraph("Sheet A-101 | Project Address: <b>124 Elm Street, Springfield, CA 90210</b>", body),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=6, spaceAfter=10),
        Paragraph("<b>SITE & ZONING COMPLIANCE SUMMARY</b>", h2),
        Paragraph("Lot Dimensions: <b>60.0' Wide x 120.0' Deep</b> (Total Lot Area: 7,200 SF)", body),
        Paragraph("Front Yard Setback: <b>25'-0\"</b> (Minimum required: 20'-0\")", body),
        Paragraph("Rear Yard Setback: <b>35'-0\"</b> (Minimum required: 15'-0\")", body),
        Paragraph("Side Yard Setback (North): <b>6'-0\"</b> (Minimum required: 5'-0\")", body),
        Paragraph("Side Yard Setback (South): <b>8'-6\"</b> (Minimum required: 5'-0\")", body),
        Paragraph("Lot Coverage: <b>25.7%</b> (Maximum permitted: 40%)", body),
        Spacer(1, 10),
        Paragraph("<b>DRAWING ANNOTATIONS & ORIENTATION</b>", h2),
        Paragraph("Drawing Scale: <b>1/8\" = 1'-0\"</b>", body),
        Paragraph("Orientation: <b>True North Arrow</b> indicated at upper right quadrant.", body),
        Paragraph("Easements: 5.0' public utility easement along rear property line.", body),
        Paragraph("Proposed Addition: 450 SF footprint located at rear south quadrant.", body),
        Spacer(1, 20),
        Paragraph("[BLUEPRINT VECTOR DRAWING - PLOT BOUNDARY & PROPOSED ADDITION FOOTPRINT]", body),
    ]
    doc.build(story)

def create_sample_floor_plan(path: str):
    doc = SimpleDocTemplate(path, pagesize=letter, margin=36)
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#0F172A'))
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#1E293B'))
    body = ParagraphStyle('B', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#334155'))

    story = [
        Paragraph("PROPOSED ARCHITECTURAL FLOOR PLAN", h1),
        Paragraph("Sheet A-102 | Project Address: <b>124 Elm Street, Springfield, CA 90210</b>", body),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=6, spaceAfter=10),
        Paragraph("<b>ROOM DIMENSIONS & PROGRAM</b>", h2),
        Paragraph("Living Room: <b>18'-0\" x 16'-0\"</b>", body),
        Paragraph("Kitchen & Dining Room: <b>14'-0\" x 20'-0\"</b>", body),
        Paragraph("Master Bedroom (Proposed Addition): <b>16'-0\" x 18'-0\"</b>", body),
        Paragraph("Bath 1: <b>8'-0\" x 10'-0\"</b>", body),
        Paragraph("Bath 2 (Proposed Addition): <b>9'-0\" x 12'-0\"</b>", body),
        Paragraph("Bedroom 2: <b>12'-0\" x 14'-0\"</b>", body),
        Paragraph("Bedroom 3: <b>11'-0\" x 13'-0\"</b>", body),
        Spacer(1, 10),
        Paragraph("<b>TOTAL BUILDING AREA</b>", h2),
        Paragraph("Stated Total Floor Area: <b>1,850 sq ft</b>", body),
        Paragraph("Drawing Scale: <b>1/4\" = 1'-0\"</b>", body),
        Paragraph("Ceiling Height: <b>9'-0\" throughout habitable spaces</b>", body),
        Paragraph("Door and Window Schedule: Refer to Sheet A-501.", body),
    ]
    doc.build(story)

def create_sample_inconsistent_document(path: str):
    """Document with intentional address mismatch and area conflict for testing pre-check engine!"""
    doc = SimpleDocTemplate(path, pagesize=letter, margin=36)
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#991B1B'))
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#1E293B'))
    body = ParagraphStyle('B', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#334155'))

    story = [
        Paragraph("STRUCTURAL GENERAL NOTES & FRAMING SPECIFICATIONS", h1),
        Paragraph("Sheet S-1 | Project Address: <b>142 Elm Street, Springfield, CA 90210</b>", body), # Typo 142 instead of 124
        HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=6, spaceAfter=10),
        Paragraph("<b>DESIGN CRITERIA & LOADS</b>", h2),
        Paragraph("Stated Total Floor Area: <b>2,400 sq ft</b>", body), # Conflicting 2,400 instead of 1,850
        Paragraph("Roof Live Load: 20 PSF | Floor Live Load: 40 PSF", body),
        Paragraph("Basic Wind Speed: 110 MPH | Exposure Category C", body),
        Paragraph("Seismic Design Category: D2", body),
        Paragraph("Concrete Compressive Strength: f'c = 2,500 PSI at 28 days", body),
        Paragraph("Anchor Bolts: 1/2\" dia embedded 7\" min into concrete foundation at 4'-0\" O.C. max.", body),
        Spacer(1, 15),
        Paragraph("Professional Engineer Stamp: <i>CA PE License #C98231</i>", body),
    ]
    doc.build(story)

if __name__ == "__main__":
    app_pdf = os.path.join(DATA_DIR, "Sample_Permit_Application.pdf")
    site_pdf = os.path.join(DATA_DIR, "Sample_Site_Plan.pdf")
    floor_pdf = os.path.join(DATA_DIR, "Sample_Floor_Plan.pdf")
    inconsistent_pdf = os.path.join(DATA_DIR, "Sample_Inconsistent_Document.pdf")

    create_sample_permit_application(app_pdf)
    create_sample_site_plan(site_pdf)
    create_sample_floor_plan(floor_pdf)
    create_sample_inconsistent_document(inconsistent_pdf)
    print(f"Generated 4 sample test documents in {DATA_DIR}")
