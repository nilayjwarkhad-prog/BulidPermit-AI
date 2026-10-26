from typing import List, Dict, Any, Optional
from app.document_processing.evidence_locator import locate_evidence_in_pages

# Standard residential building permit checklist template
# Designed with plain-language descriptions and practical advice for homeowners and builders.
STANDARD_CHECKLIST_TEMPLATE = [
    {
        "category": "Application & Property Info",
        "requirement_code": "CHK-APP-FORM",
        "title": "Completed Permit Application Form",
        "description": "The official municipal building permit application form with property owner details, contractor info (or owner-builder declaration), and clear project scope.",
        "why_it_matters": "Building departments cannot open or process your permit application without a signed application form establishing legal ownership and scope of work.",
        "how_to_fix": "Download the standard residential permit application from your city or county building department website, fill in the applicant and contractor information, sign it, and upload it here.",
        "required_category": "Permit Application",
        "required_field": "applicant_name",
        "applicable_project_types": None  # Applies to all project types
    },
    {
        "category": "Application & Property Info",
        "requirement_code": "CHK-ADDR-MATCH",
        "title": "Matching Property Address on All Sheets",
        "description": "Verification that the street address and parcel number (APN) are identical across the permit application, site plan, floor plans, and title blocks.",
        "why_it_matters": "Discrepancies in project addresses (such as '124 Elm St' vs '142 Elm St') may need to be reconciled before submission to ensure consistent records across documents.",
        "how_to_fix": "Review the title block in the bottom-right corner of every drawing sheet. Ensure the street address, unit number, city, and zip code match your permit application word-for-word.",
        "required_category": None,
        "required_field": "property_address",
        "applicable_project_types": None
    },
    {
        "category": "Site & Zoning Plans",
        "requirement_code": "CHK-SITE-PLAN",
        "title": "Site Plan / Property Plot Plan",
        "description": "An overhead map of your entire property showing property boundary lines, existing house footprint, proposed new construction, driveways, and easements.",
        "why_it_matters": "City zoning examiners need to verify how your project sits on your lot and ensure it does not encroach onto neighboring parcels, sidewalks, or utility easements.",
        "how_to_fix": "Ask your drafter or surveyor for a scaled Site Plan (Plot Plan) that shows your entire lot with dimension lines from the house to all 4 property lines.",
        "required_category": "Site Plan",
        "required_field": "setback_front",
        "applicable_project_types": ["Residential Addition", "New Construction", "ADU (Accessory Dwelling Unit)", "Garage Conversion"]
    },
    {
        "category": "Site & Zoning Plans",
        "requirement_code": "CHK-NORTH-ARROW",
        "title": "North Orientation Arrow on Site Plan",
        "description": "A clear compass arrow indicating True North or Project North on the property plot plan.",
        "why_it_matters": "Plan examiners use the North arrow to match your plans with city GIS property maps and verify solar access, wind loads, and street frontage.",
        "how_to_fix": "Ask your drafter to place a standard North arrow symbol in the drawing area or title block of your site plan sheet.",
        "required_category": "Site Plan",
        "required_field": "has_north_arrow",
        "applicable_project_types": ["Residential Addition", "New Construction", "ADU (Accessory Dwelling Unit)", "Garage Conversion"]
    },
    {
        "category": "Site & Zoning Plans",
        "requirement_code": "CHK-SETBACK-VERIF",
        "title": "Zoning Property Line Setback Distances",
        "description": "Clear distance measurements from the exterior walls of the proposed construction to the front, rear, and side property boundaries.",
        "why_it_matters": "Every residential zone has minimum legal distances (setbacks) you must maintain from property lines. Unlabeled setbacks halt plan review.",
        "how_to_fix": "Ensure your site plan has dimension arrows showing the exact distance in feet and inches from each side of the new building to the nearest property line.",
        "required_category": "Site Plan",
        "required_field": "setback_side",
        "applicable_project_types": ["Residential Addition", "New Construction", "ADU (Accessory Dwelling Unit)", "Garage Conversion"]
    },
    {
        "category": "Architectural Blueprints",
        "requirement_code": "CHK-FLOOR-PLAN",
        "title": "Dimensioned Floor Plans (Existing & Proposed)",
        "description": "To-scale layout of interior rooms, wall thicknesses, doors, windows, and room labels (e.g. Master Bedroom, Kitchen, Bathroom).",
        "why_it_matters": "Examiners review room uses to verify emergency escape windows (egress), minimum ceiling heights, natural light/ventilation, and smoke detector placement.",
        "how_to_fix": "Provide a complete floor plan showing wall dimensions, door swing directions, window sizes, and clearly labeled existing versus proposed spaces.",
        "required_category": "Floor Plan",
        "required_field": "identified_rooms",
        "applicable_project_types": None
    },
    {
        "category": "Architectural Blueprints",
        "requirement_code": "CHK-ELEVATION",
        "title": "Exterior Elevations (All 4 Sides)",
        "description": "Drawings showing the exterior appearance of the building from the Front, Rear, Left, and Right sides, including wall heights and finish materials.",
        "why_it_matters": "Building inspectors use elevations to verify overall building height limits, roof pitch, exterior siding fire ratings, and window positions.",
        "how_to_fix": "Include exterior elevation drawings for every side of the building that is being added or altered, clearly labeling total building height from ground to roof ridge.",
        "required_category": "Elevation Drawing",
        "required_field": None,
        "applicable_project_types": ["Residential Addition", "New Construction", "ADU (Accessory Dwelling Unit)", "Garage Conversion"]
    },
    {
        "category": "Architectural Blueprints",
        "requirement_code": "CHK-SCALE-NOTE",
        "title": "Drawing Scale Note & Graphic Scale Bar",
        "description": "Architectural scale ratio (such as 1/4\" = 1'-0\" or 1/8\" = 1'-0\") and a printed graphic bar scale on all plan sheets.",
        "why_it_matters": "City plan examiners must verify that drawings can be accurately measured on paper or digital plan review software.",
        "how_to_fix": "Confirm that every drawing sheet includes a written scale note (e.g. 'Scale: 1/4\" = 1'-0\"') and a graphic bar scale in the title block.",
        "required_category": None,
        "required_field": "scale_annotation",
        "applicable_project_types": None
    },
    {
        "category": "Structural & Engineering",
        "requirement_code": "CHK-STRUCT-PLAN",
        "title": "Foundation & Structural Framing Plans",
        "description": "Detailed engineering plans showing concrete foundation footings, anchor bolts, floor joists, wall studs, roof rafters, and shear walls.",
        "why_it_matters": "Structural drawings ensure your addition is structurally sound and safely withstands gravity, wind storms, and seismic ground motion.",
        "how_to_fix": "Have your licensed structural engineer or qualified designer supply foundation plans, roof framing layouts, and structural connection schedules.",
        "required_category": "Structural Plans",
        "required_field": None,
        "applicable_project_types": ["Residential Addition", "New Construction", "ADU (Accessory Dwelling Unit)"]
    },
    {
        "category": "Structural & Engineering",
        "requirement_code": "CHK-STAMP-SEAL",
        "title": "Architect or Engineer Professional Stamp",
        "description": "Digital or physical professional registration seal and signature of the licensed architect or professional engineer (PE) responsible for the design.",
        "why_it_matters": "State law and city building codes require plans involving structural alterations or second-story framing to be certified by a licensed professional.",
        "how_to_fix": "Request that your licensed architect or engineer digitally stamp and sign the title sheet and structural sheets prior to permit submittal.",
        "required_category": None,
        "required_field": "has_professional_stamp",
        "applicable_project_types": ["New Construction", "Residential Addition"]
    },
    {
        "category": "Energy & Environmental",
        "requirement_code": "CHK-ENERGY-DOC",
        "title": "Energy Compliance & Title 24 Documentation",
        "description": "Calculations showing insulation R-values, window U-factors/SHGC, HVAC efficiency, and lighting compliance for energy conservation codes.",
        "why_it_matters": "Most states (e.g. California Title 24, IECC energy codes) require documented energy compliance before issuing residential building permits.",
        "how_to_fix": "Obtain an energy compliance report (CF1R / Title 24 certificate) from your designer or an energy consultant and upload it with your plans.",
        "required_category": "Energy Documentation",
        "required_field": None,
        "applicable_project_types": ["New Construction", "ADU (Accessory Dwelling Unit)"]
    }
]

def evaluate_checklist(
    project_data: Dict[str, Any],
    documents_data: List[Dict[str, Any]],
    findings_data: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Evaluates the residential pre-submission checklist against uploaded documents and findings.
    
    Produces high-clarity, production-grade checklist items with plain-language explanations,
    concrete next steps, and exact document citations. Avoids robotic or overly technical jargon.
    """
    results: List[Dict[str, Any]] = []

    project_type = project_data.get("project_type", "Residential Addition") if project_data else "Residential Addition"
    project_address = (project_data.get("address") or "").strip() if project_data else ""

    # Build fast indexed lookups for documents and fields
    docs_by_cat: Dict[str, List[Dict[str, Any]]] = {}
    found_fields: Dict[str, Any] = {}
    field_doc_map: Dict[str, Dict[str, Any]] = {}
    
    for doc in documents_data:
        if not isinstance(doc, dict):
            continue
        raw_cat = doc.get("category")
        cat = str(raw_cat) if raw_cat else "Other Supporting Document"
        docs_by_cat.setdefault(cat, []).append(doc)
        
        pages = doc.get("pages_data", [])
        raw_fields = doc.get("extracted_fields")
        fields = raw_fields if isinstance(raw_fields, dict) else {}
        field_pages = fields.get("_field_pages", {}) if isinstance(fields.get("_field_pages"), dict) else {}
        for k, v in fields.items():
            if k == "_field_pages":
                continue
            if v is not None and v is not False and v != "":
                found_fields[k] = v
                page_num = field_pages.get(k)
                if page_num is None and pages and isinstance(v, str):
                    loc = locate_evidence_in_pages(pages, v)
                    if loc:
                        page_num = loc[0]
                field_doc_map[k] = {
                    "id": doc.get("id"),
                    "name": str(doc.get("filename") or "Uploaded Plan"),
                    "page": page_num
                }

    # Extract finding signals to provide rich, human-friendly context in notes
    address_mismatch_findings = [f for f in findings_data if isinstance(f, dict) and (f.get("rule_code") or "") == "CROSS-DOC-ADDR-MISMATCH"]
    area_mismatch_findings = [f for f in findings_data if isinstance(f, dict) and (f.get("rule_code") or "") == "CROSS-DOC-AREA-MISMATCH"]
    setback_findings = [f for f in findings_data if isinstance(f, dict) and "SETBACK" in (f.get("rule_code") or "")]

    for item in STANDARD_CHECKLIST_TEMPLATE:
        code = item["requirement_code"]
        req_cat = item["required_category"]
        req_field = item["required_field"]
        applicable_types = item.get("applicable_project_types")

        # Check if item is applicable to this project type
        if applicable_types is not None and project_type not in applicable_types:
            results.append({
                "requirement_code": code,
                "category": item["category"],
                "title": item["title"],
                "description": item["description"],
                "status": "not_applicable",
                "notes": f"Not required for {project_type} projects.",
                "evidence_document_id": None,
                "evidence_document_name": None,
                "evidence_page_number": None,
                "rule_reference": f"Standard Permitting Checklist ({code})"
            })
            continue

        status = "missing"
        notes = ""
        evidence_doc_id = None
        evidence_doc_name = None
        evidence_page = None

        # 1. Address Verification Item
        if code == "CHK-ADDR-MATCH":
            if address_mismatch_findings:
                status = "needs_verification"
                first_mismatch = address_mismatch_findings[0]
                evidence_doc_id = first_mismatch.get("document_id")
                evidence_doc_name = first_mismatch.get("document_name")
                evidence_page = first_mismatch.get("page_number")
                page_str = f" on Sheet Page {evidence_page}" if evidence_page is not None else ""
                notes = (
                    f"Address conflict detected: Drawing title block{page_str} in '{evidence_doc_name}' does not match "
                    f"the project address ('{project_address}'). This discrepancy may need to be corrected or verified before submission."
                )
            elif "property_address" in found_fields:
                status = "complete"
                evidence_doc_id = field_doc_map["property_address"]["id"]
                evidence_doc_name = field_doc_map["property_address"]["name"]
                evidence_page = field_doc_map["property_address"]["page"]
                page_str = f" (Sheet Page {evidence_page})" if evidence_page is not None else ""
                notes = f"Property address successfully verified on '{evidence_doc_name}'{page_str}: {found_fields['property_address']}."
            elif len(documents_data) > 0:
                status = "needs_verification"
                notes = "Plans are uploaded, but the parcel address could not be automatically confirmed on the title sheet. Please verify title blocks manually."
            else:
                status = "missing"
                notes = "No plans uploaded yet. Once uploaded, we will check that your property address is consistent across every sheet."

        # 2. Floor Plan & Area Verification Item
        elif code == "CHK-FLOOR-PLAN":
            cat_present = "Floor Plan" in docs_by_cat and len(docs_by_cat["Floor Plan"]) > 0
            field_present = "identified_rooms" in found_fields or "stated_building_area" in found_fields
            
            if area_mismatch_findings and cat_present:
                status = "needs_verification"
                first_area_issue = area_mismatch_findings[0]
                evidence_doc_id = first_area_issue.get("document_id")
                evidence_doc_name = first_area_issue.get("document_name")
                evidence_page = first_area_issue.get("page_number", 1)
                notes = (
                    f"Floor plan found in '{evidence_doc_name}', but building square footage conflicts with another sheet. "
                    f"Reconcile square footage so permit fee calculations are accurate."
                )
            elif cat_present and field_present:
                status = "complete"
                fp_doc = docs_by_cat["Floor Plan"][0]
                evidence_doc_id = fp_doc["id"]
                evidence_doc_name = fp_doc["filename"]
                if "identified_rooms" in field_doc_map:
                    evidence_page = field_doc_map["identified_rooms"]["page"]
                elif "stated_building_area" in field_doc_map:
                    evidence_page = field_doc_map["stated_building_area"]["page"]
                else:
                    evidence_page = 1
                rooms_info = found_fields.get("identified_rooms")
                if isinstance(rooms_info, list) and len(rooms_info) > 0:
                    room_str = ", ".join(rooms_info[:3])
                    notes = f"Floor plan verified in '{evidence_doc_name}' (Sheet Page {evidence_page}) with identified spaces ({room_str})."
                else:
                    notes = f"Dimensioned floor plan verified in '{evidence_doc_name}' (Sheet Page {evidence_page})."
            elif cat_present:
                status = "needs_verification"
                fp_doc = docs_by_cat["Floor Plan"][0]
                evidence_doc_id = fp_doc["id"]
                evidence_doc_name = fp_doc["filename"]
                evidence_page = 1
                notes = f"Floor plan drawing found ('{evidence_doc_name}'). Ensure all room names, door swings, and wall dimensions are clearly readable."
            else:
                status = "missing"
                notes = "Missing required floor plan. Building departments require dimensioned layouts showing proposed versus existing construction."

        # 3. Site Plan & Setback Verification Items
        elif code in ("CHK-SITE-PLAN", "CHK-SETBACK-VERIF"):
            site_plan_present = "Site Plan" in docs_by_cat and len(docs_by_cat["Site Plan"]) > 0
            
            if code == "CHK-SITE-PLAN":
                if site_plan_present and ("setback_front" in found_fields or "has_north_arrow" in found_fields):
                    status = "complete"
                    sp_doc = docs_by_cat["Site Plan"][0]
                    evidence_doc_id = sp_doc["id"]
                    evidence_doc_name = sp_doc["filename"]
                    if "setback_front" in field_doc_map:
                        evidence_page = field_doc_map["setback_front"]["page"]
                    elif "has_north_arrow" in field_doc_map:
                        evidence_page = field_doc_map["has_north_arrow"]["page"]
                    else:
                        evidence_page = 1
                    notes = f"Site plan confirmed in '{evidence_doc_name}' (Sheet Page {evidence_page}) with property boundaries and building footprint."
                elif site_plan_present:
                    status = "needs_verification"
                    sp_doc = docs_by_cat["Site Plan"][0]
                    evidence_doc_id = sp_doc["id"]
                    evidence_doc_name = sp_doc["filename"]
                    evidence_page = 1
                    notes = f"Site plan sheet is uploaded ('{evidence_doc_name}'), but setback distances from property lines should be clearly labeled."
                else:
                    status = "missing"
                    notes = "Missing site plot plan. Required by zoning examiners to check property boundaries, driveways, and building placement."
            
            elif code == "CHK-SETBACK-VERIF":
                if setback_findings:
                    status = "needs_verification"
                    sb_find = setback_findings[0]
                    evidence_doc_id = sb_find.get("document_id")
                    evidence_doc_name = sb_find.get("document_name")
                    evidence_page = sb_find.get("page_number", 1)
                    notes = f"Setback alert (Sheet Page {evidence_page}): {sb_find.get('explanation', 'Distance to property line appears close to or below zoning minimums.')}"
                elif site_plan_present and ("setback_front" in found_fields or "setback_side" in found_fields):
                    status = "complete"
                    sp_doc = docs_by_cat["Site Plan"][0]
                    evidence_doc_id = sp_doc["id"]
                    evidence_doc_name = sp_doc["filename"]
                    if "setback_front" in field_doc_map:
                        evidence_page = field_doc_map["setback_front"]["page"]
                    elif "setback_side" in field_doc_map:
                        evidence_page = field_doc_map["setback_side"]["page"]
                    else:
                        evidence_page = 1
                    notes = f"Property setbacks detected and verified on '{evidence_doc_name}' (Sheet Page {evidence_page})."
                elif site_plan_present:
                    status = "needs_verification"
                    notes = "Site plan is present, but exact front and side yard setback dimensions need to be checked against local zoning rules."
                else:
                    status = "missing"
                    notes = "Cannot evaluate property setbacks until a scaled Site Plan is uploaded."

        # 4. North Arrow Verification
        elif code == "CHK-NORTH-ARROW":
            site_plan_present = "Site Plan" in docs_by_cat and len(docs_by_cat["Site Plan"]) > 0
            if found_fields.get("has_north_arrow"):
                status = "complete"
                evidence_doc_id = field_doc_map["has_north_arrow"]["id"]
                evidence_doc_name = field_doc_map["has_north_arrow"]["name"]
                evidence_page = field_doc_map["has_north_arrow"]["page"]
                notes = f"North orientation arrow confirmed on '{evidence_doc_name}' (Sheet Page {evidence_page})."
            elif site_plan_present:
                status = "needs_verification"
                sp_doc = docs_by_cat["Site Plan"][0]
                evidence_doc_id = sp_doc["id"]
                evidence_doc_name = sp_doc["filename"]
                evidence_page = 1
                notes = f"Site plan found ('{evidence_doc_name}'), but no North arrow was detected. Have your drafter add an orientation arrow."
            else:
                status = "missing"
                notes = "Site plan not yet uploaded. North arrow will be evaluated once your site plan is provided."

        # 5. Generic Category & Field Check
        else:
            cat_present = req_cat is None or (req_cat in docs_by_cat and len(docs_by_cat[req_cat]) > 0)
            field_present = req_field is None or req_field in found_fields

            if cat_present and field_present:
                status = "complete"
                if req_field and req_field in field_doc_map:
                    evidence_doc_id = field_doc_map[req_field]["id"]
                    evidence_doc_name = field_doc_map[req_field]["name"]
                    evidence_page = field_doc_map[req_field]["page"]
                    notes = f"Verified in '{evidence_doc_name}' (Sheet Page {evidence_page})."
                elif req_cat and req_cat in docs_by_cat:
                    first_doc = docs_by_cat[req_cat][0]
                    evidence_doc_id = first_doc["id"]
                    evidence_doc_name = first_doc["filename"]
                    evidence_page = 1
                    notes = f"Document found and classified as '{req_cat}' ('{evidence_doc_name}')."
                else:
                    notes = "Requirement met based on uploaded plans."
            elif cat_present and not field_present:
                status = "needs_verification"
                human_field = req_field.replace('_', ' ') if req_field else 'required details'
                if req_cat and req_cat in docs_by_cat:
                    first_doc = docs_by_cat[req_cat][0]
                    evidence_doc_id = first_doc["id"]
                    evidence_doc_name = first_doc["filename"]
                    evidence_page = 1
                    notes = f"'{req_cat}' is uploaded ('{evidence_doc_name}'), but {human_field} should be reviewed for completeness."
                else:
                    notes = f"Plans uploaded, but {human_field} should be reviewed manually."
            else:
                status = "missing"
                if req_cat:
                    notes = f"Missing {req_cat}. Please upload this sheet to satisfy standard municipal requirements."
                else:
                    notes = f"Required information ({item['title'].lower()}) was not detected in any uploaded sheet."

        results.append({
            "requirement_code": code,
            "category": item["category"],
            "title": item["title"],
            "description": item["description"],
            "status": status,
            "notes": notes,
            "evidence_document_id": evidence_doc_id,
            "evidence_document_name": evidence_doc_name,
            "evidence_page_number": evidence_page,
            "rule_reference": f"Standard Permitting Checklist ({code})"
        })

    return results
