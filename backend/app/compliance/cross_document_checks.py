import re
from typing import List, Dict, Any, Optional
from app.document_processing.evidence_locator import locate_evidence_in_pages, locate_all_evidence_in_pages

def normalize_address(addr: Optional[str]) -> str:
    """Normalizes street address for fair, human-friendly comparison."""
    if not addr:
        return ""
    cleaned = addr.lower().strip()
    replacements = {
        r"\bstreet\b": "st",
        r"\bavenue\b": "ave",
        r"\broad\b": "rd",
        r"\bboulevard\b": "blvd",
        r"\bdrive\b": "dr",
        r"\blane\b": "ln",
        r"\bcourt\b": "ct",
        r"\bcircle\b": "cir",
        r"[,\.]": " ",
        r"\s+": " "
    }
    for pat, rep in replacements.items():
        cleaned = re.sub(pat, rep, cleaned)
    return cleaned.strip()

def run_cross_document_checks(
    project_data: Dict[str, Any],
    documents_data: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Performs deterministic cross-document consistency checks:
    - Address matching between project, application form, and plans with real page citations
    - Building square footage consistency across sheets with exact page references
    - Missing required categories for project type
    - Unreadable or blank pages
    - Missing drawing annotations (north arrow, scale)
    
    All findings are written in plain, clear language that any homeowner,
    contractor, or architect can immediately understand and act on.
    """
    findings: List[Dict[str, Any]] = []

    project_address = project_data.get("address", "").strip()
    norm_project_address = normalize_address(project_address)
    project_type = project_data.get("project_type", "Residential Addition")

    # Group documents by category
    docs_by_cat: Dict[str, List[Dict[str, Any]]] = {}
    all_page_addresses: List[Dict[str, Any]] = []
    all_page_areas: List[Dict[str, Any]] = []

    def addresses_conflict(norm_a: str, norm_b: str) -> bool:
        """Determines whether two normalized address strings have an unambiguous conflict."""
        if not norm_a or not norm_b:
            return False
        if norm_a == norm_b:
            return False
        
        nums_a = re.findall(r"\b\d+\b", norm_a)
        nums_b = re.findall(r"\b\d+\b", norm_b)
        
        if nums_a and nums_b:
            if nums_a[0] != nums_b[0]:
                return True
            if norm_a in norm_b or norm_b in norm_a:
                return False
                
        if norm_a not in norm_b and norm_b not in norm_a:
            return True
            
        return False

    for doc in documents_data:
        cat = doc.get("category", "Other Supporting Document")
        docs_by_cat.setdefault(cat, []).append(doc)
        pages = doc.get("pages_data", [])
        fields = doc.get("extracted_fields") or {}
        page_fields = fields.get("_page_fields") if isinstance(fields, dict) else None
        field_pages = fields.get("_field_pages", {}) if isinstance(fields, dict) else {}
        field_all_pages = fields.get("_field_all_pages", {}) if isinstance(fields, dict) else {}

        # 1. Collect page addresses for this document
        doc_page_addrs: List[Dict[str, Any]] = []
        if page_fields and isinstance(page_fields, list):
            for pf in page_fields:
                p_addr = pf.get("property_address")
                if p_addr:
                    doc_page_addrs.append({
                        "doc_id": doc["id"],
                        "doc_name": doc["filename"],
                        "category": cat,
                        "page_number": pf.get("page_number", 1),
                        "address": p_addr,
                        "norm_address": normalize_address(p_addr),
                        "snippet": pf.get("address_snippet") or p_addr
                    })

        # Fallback if _page_fields was not present or had no addresses
        if not doc_page_addrs and isinstance(fields, dict):
            doc_addr = fields.get("property_address")
            if doc_addr:
                p_num = field_pages.get("property_address")
                all_p = field_all_pages.get("property_address") or []
                snippet = doc_addr
                if p_num is None and pages:
                    all_locs = locate_all_evidence_in_pages(pages, doc_addr)
                    if all_locs:
                        p_num = all_locs[0]["page_number"]
                        snippet = all_locs[0]["snippet"]
                        all_p = [m["page_number"] for m in all_locs]
                elif p_num is not None and not all_p and pages:
                    all_locs = locate_all_evidence_in_pages(pages, doc_addr)
                    if all_locs:
                        all_p = [m["page_number"] for m in all_locs]
                        snippet = all_locs[0]["snippet"]
                
                if all_p:
                    for pn in all_p:
                        doc_page_addrs.append({
                            "doc_id": doc["id"],
                            "doc_name": doc["filename"],
                            "category": cat,
                            "page_number": pn,
                            "address": doc_addr,
                            "norm_address": normalize_address(doc_addr),
                            "snippet": snippet
                        })
                else:
                    doc_page_addrs.append({
                        "doc_id": doc["id"],
                        "doc_name": doc["filename"],
                        "category": cat,
                        "page_number": p_num,
                        "address": doc_addr,
                        "norm_address": normalize_address(doc_addr),
                        "snippet": snippet
                    })

        all_page_addresses.extend(doc_page_addrs)

        # 2. Collect page areas for this document
        doc_page_areas: List[Dict[str, Any]] = []
        if page_fields and isinstance(page_fields, list):
            for pf in page_fields:
                pn = pf.get("page_number", 1)
                if pf.get("addition_area") is not None:
                    doc_page_areas.append({
                        "doc_id": doc["id"],
                        "doc_name": doc["filename"],
                        "category": cat,
                        "page_number": pn,
                        "area": pf["addition_area"],
                        "area_type": "addition",
                        "label": "proposed addition area",
                        "snippet": pf.get("addition_area_snippet") or f"{pf['addition_area']:,.0f} sq ft"
                    })
                if pf.get("stated_building_area") is not None:
                    doc_page_areas.append({
                        "doc_id": doc["id"],
                        "doc_name": doc["filename"],
                        "category": cat,
                        "page_number": pn,
                        "area": pf["stated_building_area"],
                        "area_type": "building",
                        "label": "stated building area",
                        "snippet": pf.get("building_area_snippet") or f"{pf['stated_building_area']:,.0f} sq ft"
                    })

        # Fallback if _page_fields not present or had no areas
        if not doc_page_areas and isinstance(fields, dict):
            if fields.get("addition_area") is not None:
                area_val = fields["addition_area"]
                pn = field_pages.get("addition_area")
                all_p = field_all_pages.get("addition_area") or []
                snippet = f"{area_val:,.0f} sq ft"
                if pn is None and pages:
                    all_locs = locate_all_evidence_in_pages(pages, str(int(area_val)))
                    if all_locs:
                        pn = all_locs[0]["page_number"]
                        snippet = all_locs[0]["snippet"]
                        all_p = [m["page_number"] for m in all_locs]
                pages_to_add = all_p if all_p else ([pn] if pn is not None else [None])
                for p_idx in pages_to_add:
                    doc_page_areas.append({
                        "doc_id": doc["id"],
                        "doc_name": doc["filename"],
                        "category": cat,
                        "page_number": p_idx,
                        "area": area_val,
                        "area_type": "addition",
                        "label": "proposed addition area",
                        "snippet": snippet
                    })
            if fields.get("stated_building_area") is not None:
                area_val = fields["stated_building_area"]
                pn = field_pages.get("stated_building_area")
                all_p = field_all_pages.get("stated_building_area") or []
                snippet = f"{area_val:,.0f} sq ft"
                if pn is None and pages:
                    all_locs = locate_all_evidence_in_pages(pages, str(int(area_val)))
                    if all_locs:
                        pn = all_locs[0]["page_number"]
                        snippet = all_locs[0]["snippet"]
                        all_p = [m["page_number"] for m in all_locs]
                pages_to_add = all_p if all_p else ([pn] if pn is not None else [None])
                for p_idx in pages_to_add:
                    doc_page_areas.append({
                        "doc_id": doc["id"],
                        "doc_name": doc["filename"],
                        "category": cat,
                        "page_number": p_idx,
                        "area": area_val,
                        "area_type": "building",
                        "label": "stated building area",
                        "snippet": snippet
                    })

        all_page_areas.extend(doc_page_areas)

        # Check for unreadable / empty pages
        for p in pages:
            if p.get("is_empty") and doc.get("page_count", 0) > 0 and not doc.get("mime_type", "").startswith("image/"):
                p_num = p.get("page_number", 1)
                findings.append({
                    "rule_code": "DOC-PAGE-READABILITY",
                    "title": f"Page {p_num} May Be Blank or Difficult to Read",
                    "category": "Page Quality",
                    "severity": "info",
                    "document_id": doc["id"],
                    "document_name": doc["filename"],
                    "page_number": p_num,
                    "explanation": f"Page {p_num} in '{doc['filename']}' contains almost no readable text. If this is a blueprint scan or drawing sheet, make sure notes and lines are clear and not washed out.",
                    "evidence_text": "Extracted text has less than 5 words",
                    "recommended_action": f"Check Page {p_num} in the plan previewer. If it is blank or blurry, ask your drafter to re-export a clear PDF.",
                    "confidence": 0.95,
                    "human_review_required": True
                })

    # =========================================================================
    # 1. Address Inconsistency Checks (Same-PDF and Cross-Document)
    # =========================================================================
    # Cluster addresses by document to identify intra-document discrepancies
    docs_with_intra_addr_conflict = set()

    for doc in documents_data:
        doc_id = doc["id"]
        doc_addrs = [a for a in all_page_addresses if a["doc_id"] == doc_id]
        if len(doc_addrs) < 2:
            continue

        # Cluster by address within this doc
        doc_clusters: List[Dict[str, Any]] = []
        for item in doc_addrs:
            matched = False
            for cl in doc_clusters:
                if not addresses_conflict(cl["norm_address"], item["norm_address"]):
                    if item["page_number"] is not None and item["page_number"] not in cl["pages"]:
                        cl["pages"].append(item["page_number"])
                    cl["snippets"].append(item["snippet"])
                    if len(item["address"]) > len(cl["address"]):
                        cl["address"] = item["address"]
                        cl["norm_address"] = item["norm_address"]
                    matched = True
                    break
            if not matched:
                doc_clusters.append({
                    "doc_id": doc_id,
                    "doc_name": doc["filename"],
                    "category": doc.get("category", "Other Supporting Document"),
                    "address": item["address"],
                    "norm_address": item["norm_address"],
                    "pages": [item["page_number"]] if item["page_number"] is not None else [],
                    "snippets": [item["snippet"]]
                })

        # Check for conflicts between clusters in the same document
        if len(doc_clusters) >= 2:
            for i in range(len(doc_clusters)):
                for j in range(i + 1, len(doc_clusters)):
                    cl_a = doc_clusters[i]
                    cl_b = doc_clusters[j]
                    if addresses_conflict(cl_a["norm_address"], cl_b["norm_address"]):
                        docs_with_intra_addr_conflict.add(doc_id)
                        pages_a = sorted(cl_a["pages"])
                        pages_b = sorted(cl_b["pages"])
                        page_a_str = f"Pages {', '.join(str(p) for p in pages_a)}" if len(pages_a) > 1 else (f"Page {pages_a[0]}" if pages_a else "Page uncertain")
                        page_b_str = f"Pages {', '.join(str(p) for p in pages_b)}" if len(pages_b) > 1 else (f"Page {pages_b[0]}" if pages_b else "Page uncertain")

                        finding_page = pages_b[0] if pages_b else (pages_a[0] if pages_a else None)

                        page_a_verb = "shows" if len(pages_a) <= 1 else "show"
                        page_b_verb = "shows" if len(pages_b) <= 1 else "show"

                        findings.append({
                            "rule_code": "CROSS-DOC-ADDR-MISMATCH",
                            "title": f"Property Address Conflict Across Plan Sheets in {doc['filename']}",
                            "category": "Inconsistency",
                            "severity": "critical",
                            "document_id": doc["id"],
                            "document_name": doc["filename"],
                            "page_number": finding_page,
                            "explanation": (
                                f"Conflicting property addresses were detected across sheets in '{doc['filename']}': "
                                f"{page_a_str} {page_a_verb} '{cl_a['address']}', while {page_b_str} {page_b_verb} '{cl_b['address']}'. "
                                "This discrepancy may need to be corrected or verified before submission."
                            ),
                            "evidence_text": f"{doc['filename']} ({page_a_str}): '{cl_a['snippets'][0]}' vs ({page_b_str}): '{cl_b['snippets'][0]}'",
                            "rule_reference": "Uniform Property Identification Standard",
                            "recommended_action": (
                                f"Ask your designer to update title blocks across '{doc['filename']}' "
                                f"so all sheets consistently display '{project_address or cl_a['address']}' before submitting."
                            ),
                            "confidence": 0.95,
                            "human_review_required": True
                        })

    # For documents without internal conflict, check against project address registration
    if norm_project_address:
        # Cluster per document
        for doc in documents_data:
            doc_id = doc["id"]
            if doc_id in docs_with_intra_addr_conflict:
                continue

            doc_addrs = [a for a in all_page_addresses if a["doc_id"] == doc_id]
            if not doc_addrs:
                continue

            # Group pages sharing this document's address
            doc_address_val = doc_addrs[0]["address"]
            doc_norm_val = doc_addrs[0]["norm_address"]
            all_pages_doc = sorted(list(set(a["page_number"] for a in doc_addrs if a["page_number"] is not None)))
            snippet = doc_addrs[0]["snippet"]

            if addresses_conflict(norm_project_address, doc_norm_val):
                if len(all_pages_doc) > 1:
                    page_cite = f"Pages {', '.join(str(p) for p in all_pages_doc)}"
                    explanation = (
                        f"The address found on {page_cite} of '{doc['filename']}' is '{doc_address_val}', but your project application is registered as '{project_address}'. "
                        "This discrepancy may need to be corrected or verified before submission."
                    )
                    recommended_action = f"Ask your designer to update title blocks across {page_cite} in '{doc['filename']}' so the address matches '{project_address}' exactly before submitting."
                    evidence_text = f"Project Address: '{project_address}' vs Drawing {page_cite}: '{snippet}'"
                    finding_page = all_pages_doc[0]
                    finding_confidence = 0.92
                elif len(all_pages_doc) == 1:
                    page_cite = f"Page {all_pages_doc[0]}"
                    explanation = (
                        f"The address found on {page_cite} of '{doc['filename']}' is '{doc_address_val}', but your project application is registered as '{project_address}'. "
                        "This discrepancy may need to be corrected or verified before submission."
                    )
                    recommended_action = f"Ask your designer to update the title block on {page_cite} in '{doc['filename']}' so the address matches '{project_address}' exactly before submitting."
                    evidence_text = f"Project Address: '{project_address}' vs Drawing {page_cite}: '{snippet}'"
                    finding_page = all_pages_doc[0]
                    finding_confidence = 0.92
                else:
                    page_cite = "Page location uncertain"
                    explanation = (
                        f"An address '{doc_address_val}' was detected in '{doc['filename']}', which conflicts with project registration '{project_address}', "
                        "but the exact sheet page location is uncertain and could not be determined confidently. Please review all title blocks manually."
                    )
                    recommended_action = f"Review title blocks in '{doc['filename']}' manually and ensure the project address matches '{project_address}' exactly."
                    evidence_text = f"Project Address: '{project_address}' vs Drawing (Page uncertain): '{snippet}'"
                    finding_page = None
                    finding_confidence = 0.65

                findings.append({
                    "rule_code": "CROSS-DOC-ADDR-MISMATCH",
                    "title": f"Property Address Does Not Match in {doc['filename']}",
                    "category": "Inconsistency",
                    "severity": "critical",
                    "document_id": doc["id"],
                    "document_name": doc["filename"],
                    "page_number": finding_page,
                    "explanation": explanation,
                    "evidence_text": evidence_text,
                    "rule_reference": "Uniform Property Identification Standard",
                    "recommended_action": recommended_action,
                    "confidence": finding_confidence,
                    "human_review_required": True
                })

    # =========================================================================
    # 2. Building Area Inconsistency Checks (Same-PDF and Cross-Document)
    # =========================================================================
    # Group area items by area_type to avoid comparing addition area to total house area
    areas_by_type: Dict[str, List[Dict[str, Any]]] = {}
    for item in all_page_areas:
        areas_by_type.setdefault(item["area_type"], []).append(item)

    for area_type, type_items in areas_by_type.items():
        if len(type_items) < 2:
            continue

        # Cluster area measurements within 5% tolerance
        clusters: List[Dict[str, Any]] = []
        for it in type_items:
            val = it["area"]
            matched = False
            for cl in clusters:
                if abs(cl["area"] - val) / max(cl["area"], val) <= 0.05:
                    cl["items"].append(it)
                    matched = True
                    break
            if not matched:
                clusters.append({
                    "area": val,
                    "label": it["label"],
                    "items": [it]
                })

        if len(clusters) >= 2:
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    cl_a = clusters[i]
                    cl_b = clusters[j]
                    diff_pct = abs(cl_a["area"] - cl_b["area"]) / max(cl_a["area"], cl_b["area"])
                    if diff_pct <= 0.05:
                        continue

                    # Check if both clusters appear in the same document
                    docs_a = set(it["doc_name"] for it in cl_a["items"])
                    docs_b = set(it["doc_name"] for it in cl_b["items"])
                    common_docs = docs_a.intersection(docs_b)

                    if common_docs:
                        # Intra-document area conflict
                        for c_doc in common_docs:
                            pages_a = sorted(list(set(it["page_number"] for it in cl_a["items"] if it["doc_name"] == c_doc and it["page_number"] is not None)))
                            pages_b = sorted(list(set(it["page_number"] for it in cl_b["items"] if it["doc_name"] == c_doc and it["page_number"] is not None)))
                            page_a_str = f"Pages {', '.join(str(p) for p in pages_a)}" if len(pages_a) > 1 else (f"Page {pages_a[0]}" if pages_a else "Page uncertain")
                            page_b_str = f"Pages {', '.join(str(p) for p in pages_b)}" if len(pages_b) > 1 else (f"Page {pages_b[0]}" if pages_b else "Page uncertain")
                            
                            c_doc_id = next(it["doc_id"] for it in cl_a["items"] if it["doc_name"] == c_doc)

                            findings.append({
                                "rule_code": "CROSS-DOC-AREA-MISMATCH",
                                "title": "Square Footage Conflict Between Plan Sheets",
                                "category": "Inconsistency",
                                "severity": "warning",
                                "document_id": c_doc_id,
                                "document_name": c_doc,
                                "page_number": pages_a[0] if pages_a else None,
                                "explanation": (
                                    f"Stated square footage on {page_a_str} of '{c_doc}' ({cl_a['area']:,.0f} sq ft) conflicts with {page_b_str} of '{c_doc}' ({cl_b['area']:,.0f} sq ft) - a difference of {diff_pct*100:.1f}%. "
                                    "This square footage discrepancy may need to be verified or reconciled across sheets before submission."
                                ),
                                "evidence_text": f"{c_doc} ({page_a_str}): {cl_a['area']:,.0f} sq ft vs {c_doc} ({page_b_str}): {cl_b['area']:,.0f} sq ft",
                                "rule_reference": "Building Area Accuracy Standard",
                                "recommended_action": "Check with your designer or architect to confirm the true proposed square footage, and make sure all sheets use the identical number.",
                                "confidence": 0.92,
                                "human_review_required": True
                            })
                    else:
                        # Cross-document area conflict
                        first_a = cl_a["items"][0]
                        first_b = cl_b["items"][0]
                        doc_a_name = first_a["doc_name"]
                        doc_b_name = first_b["doc_name"]
                        pages_a = sorted(list(set(it["page_number"] for it in cl_a["items"] if it["doc_name"] == doc_a_name and it["page_number"] is not None)))
                        pages_b = sorted(list(set(it["page_number"] for it in cl_b["items"] if it["doc_name"] == doc_b_name and it["page_number"] is not None)))
                        page_a_str = f"Pages {', '.join(str(p) for p in pages_a)}" if len(pages_a) > 1 else (f"Page {pages_a[0]}" if pages_a else "Page uncertain")
                        page_b_str = f"Pages {', '.join(str(p) for p in pages_b)}" if len(pages_b) > 1 else (f"Page {pages_b[0]}" if pages_b else "Page uncertain")

                        findings.append({
                            "rule_code": "CROSS-DOC-AREA-MISMATCH",
                            "title": "Square Footage Conflict Between Plan Sheets",
                            "category": "Inconsistency",
                            "severity": "warning",
                            "document_id": first_a["doc_id"],
                            "document_name": doc_a_name,
                            "page_number": pages_a[0] if pages_a else None,
                            "explanation": (
                                f"Stated square footage on {page_a_str} of '{doc_a_name}' ({cl_a['area']:,.0f} sq ft) conflicts with {page_b_str} of '{doc_b_name}' ({cl_b['area']:,.0f} sq ft) - a difference of {diff_pct*100:.1f}%. "
                                "This square footage discrepancy may need to be verified or reconciled across sheets before submission."
                            ),
                            "evidence_text": f"{doc_a_name} ({page_a_str}): {cl_a['area']:,.0f} sq ft vs {doc_b_name} ({page_b_str}): {cl_b['area']:,.0f} sq ft",
                            "rule_reference": "Building Area Accuracy Standard",
                            "recommended_action": "Check with your designer or architect to confirm the true proposed square footage, and make sure all sheets use the identical number.",
                            "confidence": 0.88,
                            "human_review_required": True
                        })


    # 3. Missing Required Documents Check
    required_docs_map = {
        "Residential Addition": [
            ("Permit Application", "Permit Application Form"),
            ("Site Plan", "Site / Plot Plan"),
            ("Floor Plan", "Floor Plan Drawings")
        ],
        "New Construction": [
            ("Permit Application", "Permit Application Form"),
            ("Site Plan", "Site / Plot Plan"),
            ("Floor Plan", "Floor Plan Drawings"),
            ("Elevation Drawing", "Exterior Elevations"),
            ("Structural Plans", "Structural Framing & Foundation Plans")
        ],
        "ADU (Accessory Dwelling Unit)": [
            ("Permit Application", "Permit Application Form"),
            ("Site Plan", "Site / Plot Plan"),
            ("Floor Plan", "Floor Plan with Kitchen & Bath"),
            ("Energy Documentation", "Energy Compliance / Title 24")
        ],
        "Renovation / Remodel": [
            ("Permit Application", "Permit Application Form"),
            ("Floor Plan", "Floor Plan (Existing & Proposed)")
        ],
        "Garage Conversion": [
            ("Permit Application", "Permit Application Form"),
            ("Site Plan", "Site Plan showing Replacement Parking"),
            ("Floor Plan", "Conversion Floor Plan")
        ]
    }
    
    expected_categories = required_docs_map.get(
        project_type,
        [("Permit Application", "Permit Application Form"), ("Site Plan", "Site / Plot Plan"), ("Floor Plan", "Floor Plan Drawings")]
    )
    
    for req_cat, friendly_name in expected_categories:
        if req_cat not in docs_by_cat or len(docs_by_cat[req_cat]) == 0:
            findings.append({
                "rule_code": f"MISSING-DOC-{req_cat.upper().replace(' ', '-')}",
                "title": f"Potentially Missing Document: {friendly_name}",
                "category": "Missing Document",
                "severity": "warning",
                "document_id": None,
                "document_name": None,
                "page_number": None,
                "explanation": (
                    f"A '{friendly_name}' is typically expected for {project_type} permit submittals. "
                    "No document has been classified under this category yet."
                ),
                "evidence_text": f"Uploaded Categories: {', '.join(docs_by_cat.keys()) if docs_by_cat else 'None uploaded yet'}",
                "rule_reference": "Standard Submittal Checklist (Sample Guidance)",
                "recommended_action": f"Upload your {friendly_name} PDF or re-categorize an existing document if it is already included.",
                "confidence": 0.99,
                "human_review_required": False
            })

    # 4. Site Plan Specific Checks with real page citations
    site_plans = docs_by_cat.get("Site Plan", [])
    for sp in site_plans:
        fields = sp.get("extracted_fields") or {}
        pages = sp.get("pages_data", [])
        
        # Determine actual site plan sheet page in multi-sheet plan sets
        sp_page = 1
        for p in pages:
            p_text = (p.get("text") or "").lower()
            if "site plan" in p_text or "plot plan" in p_text or "property line" in p_text:
                sp_page = p.get("page_number", 1)
                break

        if not fields.get("has_north_arrow"):
            findings.append({
                "rule_code": "SITEPLAN-MISSING-NORTH-ARROW",
                "title": "Site Plan Missing North Arrow",
                "category": "Missing Field",
                "severity": "warning",
                "document_id": sp["id"],
                "document_name": sp["filename"],
                "page_number": sp_page,
                "explanation": (
                    f"The Site Plan on Page {sp_page} in '{sp['filename']}' does not show a standard North orientation arrow. "
                    "Orientation indicators assist reviewers in verifying boundary setbacks and street frontages."
                ),
                "evidence_text": f"No compass or 'North' notation found on Page {sp_page}",
                "rule_reference": "Plan Drawing Guidelines (Sample Guidance)",
                "recommended_action": f"Ask your plan designer to place a standard North arrow icon in the title block or near the property lines on Page {sp_page}.",
                "confidence": 0.82,
                "human_review_required": True
            })
        
        if not fields.get("scale_annotation"):
            findings.append({
                "rule_code": "SITEPLAN-MISSING-SCALE",
                "title": "Drawing Scale Missing from Plans",
                "category": "Missing Field",
                "severity": "warning",
                "document_id": sp["id"],
                "document_name": sp["filename"],
                "page_number": sp_page,
                "explanation": (
                    f"No architectural scale (e.g., 1/4\" = 1'-0\" or graphic bar scale) was detected on Page {sp_page} in '{sp['filename']}'. "
                    "Stated drawing scales are needed to verify plan dimensions accurately."
                ),
                "evidence_text": f"No scale notation or bar scale detected on Page {sp_page}",
                "rule_reference": "Plan Drawing Guidelines (Sample Guidance)",
                "recommended_action": f"Ensure that Page {sp_page} displays a clear scale note (such as 'Scale: 1/4\" = 1'-0\"') and a graphic bar scale in the title block.",
                "confidence": 0.80,
                "human_review_required": True
            })

    return findings
