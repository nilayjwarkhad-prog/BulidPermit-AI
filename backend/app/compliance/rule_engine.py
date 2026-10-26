import re
from typing import List, Dict, Any
from app.compliance.source_registry import SAMPLE_RULES
from app.document_processing.evidence_locator import locate_evidence_in_pages

def parse_distance_feet(val_str: Any) -> float:
    """Parses a distance string like 15', 15 ft, 15'-6", or 15.5 into float feet."""
    if val_str is None:
        return 0.0
    if isinstance(val_str, (int, float)):
        return float(val_str)
    
    text = str(val_str).lower().strip()
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(?:'|ft|feet)?", text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return 0.0
    return 0.0

def evaluate_jurisdiction_rules(
    project_data: Dict[str, Any],
    documents_data: List[Dict[str, Any]],
    jurisdiction_id: str
) -> List[Dict[str, Any]]:
    """
    Evaluates applicable jurisdiction rules against extracted parameters.
    Clearly marks any rules as non-regulatory development examples.
    Produces clear, practical, homeowner-friendly recommendations.
    """
    findings: List[Dict[str, Any]] = []
    
    # Filter rules for jurisdiction or fallback
    applicable_rules = [r for r in SAMPLE_RULES if r.get("jurisdiction_id") in (jurisdiction_id, "US-CA-GENERIC")]
    
    # Collect all extracted fields from documents
    all_fields: Dict[str, Any] = {}
    doc_field_sources: Dict[str, Dict[str, Any]] = {}
    
    for doc in documents_data:
        fields = doc.get("extracted_fields") or {}
        pages = doc.get("pages_data", [])
        field_pages = fields.get("_field_pages", {}) if isinstance(fields, dict) else {}
        for k, v in fields.items():
            if k == "_field_pages":
                continue
            if v is not None:
                all_fields[k] = v
                page_num = field_pages.get(k)
                if page_num is None and pages and isinstance(v, str):
                    loc = locate_evidence_in_pages(pages, v)
                    if loc:
                        page_num = loc[0]
                doc_field_sources[k] = {
                    "doc_id": doc["id"],
                    "doc_name": doc["filename"],
                    "page_number": page_num
                }

    friendly_field_names = {
        "setback_front": "Front Yard",
        "setback_rear": "Rear Yard",
        "setback_side": "Side Yard",
        "building_height": "Building Height",
        "lot_coverage": "Lot Coverage"
    }

    for rule in applicable_rules:
        code = rule["rule_code"]
        logic = rule.get("validation_logic", {})
        field_name = logic.get("field")
        
        if not field_name:
            continue
            
        val = all_fields.get(field_name)
        source = doc_field_sources.get(field_name, {})
        human_name = friendly_field_names.get(field_name, field_name.replace("_", " ").title())
        
        # Check minimum feet requirement (e.g. setback)
        if "min_feet" in logic and val is not None:
            min_required = float(logic["min_feet"])
            extracted_feet = parse_distance_feet(val)
            if 0.0 < extracted_feet < min_required:
                page_num = source.get("page_number")
                if page_num is not None:
                    doc_label = f" in '{source.get('doc_name')}' (Sheet Page {page_num})" if source.get("doc_name") else f" (Sheet Page {page_num})"
                else:
                    doc_label = f" in '{source.get('doc_name')}' (Page uncertain)" if source.get("doc_name") else " (Page uncertain)"
                findings.append({
                    "rule_code": code,
                    "title": f"{human_name} Setback Distance Too Short ({extracted_feet:.1f} ft vs {min_required:.1f} ft Required)",
                    "category": rule["category"],
                    "severity": rule["severity"],
                    "document_id": source.get("doc_id"),
                    "document_name": source.get("doc_name"),
                    "page_number": page_num,
                    "explanation": (
                        f"Your site plan indicates a {human_name.lower()} setback of {extracted_feet:.1f} feet{doc_label}, "
                        f"which is less than the benchmark requirement of {min_required:.1f} feet from the property line. "
                        "Note: This check is based on unverified sample guidance. Local municipal zoning ordinances vary. "
                        "Building additions within buffer zones may require planning department variance approval."
                    ),
                    "evidence_text": f"Drawn Setback: '{val}' ({extracted_feet:.1f} ft) | Benchmark Minimum: {min_required:.1f} ft",
                    "rule_reference": f"{code} [Sample Rule - Unverified Local Guidance]",
                    "recommended_action": (
                        f"Ask your drafter if the addition can be adjusted to provide the full {min_required:.1f} ft setback, "
                        "or contact your city planning department to confirm if your property qualifies for an existing non-conforming exception or administrative variance."
                    ),
                    "confidence": 0.85,
                    "human_review_required": True
                })

    return findings
