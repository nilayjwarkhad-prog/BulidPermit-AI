import re
from typing import Dict, Any, Optional, List

ADDR_PATTERN = re.compile(
    r"(?:project\s+address|property\s+address|job\s+address|site\s+address|project\s+location|site\s+location|job\s+location|location|fictional\s+project\s+address)\s*[:\n\-]\s*([0-9]{1,6}\s+[A-Za-z0-9\.\s,]+?(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct|Circle|Cir)\b(?:[,\s\n]+[A-Za-z\s]+,?\s+[A-Z]{2}\b)?(?:\s+[0-9]{5}(?:-[0-9]{4})?)?)",
    re.IGNORECASE
)

FALLBACK_ADDR_PATTERN = re.compile(
    r"\b([0-9]{1,5}\s+[A-Za-z0-9\.\s,]+?(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Way|Lane|Ln|Court|Ct|Circle|Cir)\b(?:[,\s\n]+[A-Za-z\s]+,?\s+[A-Z]{2}\b)?(?:\s+[0-9]{5}(?:-[0-9]{4})?)?)",
    re.IGNORECASE
)

ADDITION_AREA_PATTERN = re.compile(
    r"(?:(?:declared\s+)?(?:proposed\s+)?addition\s+area|proposed\s+addition|addition\s+area)\s*[:\-\s]*([0-9,]+(?:\.[0-9]+)?)\s*(?:sq(?:uare)?\.?\s*(?:ft|feet)|sf)",
    re.IGNORECASE
)

BUILDING_AREA_PATTERN = re.compile(
    r"(?:total\s+(?:floor\s+|living\s+)?area|living\s+area|building\s+area|gross\s+area|proposed\s+area|habitable\s+area|square\s+footage)\s*[:\-\s]*([0-9,]+(?:\.[0-9]+)?)\s*(?:sq(?:uare)?\.?\s*(?:ft|feet)|sf|m2|sq\s*m)",
    re.IGNORECASE
)

SEC_AREA_PATTERN = re.compile(
    r"\b([0-9]{1,2},[0-9]{3}|[0-9]{3,5})\s*(?:sq\.?\s*ft\.?|sf|sqft)\b",
    re.IGNORECASE
)

def extract_page_fields(text: str, page_number: int = 1) -> Dict[str, Any]:
    """Extracts structured fields from an individual page's text."""
    p_fields: Dict[str, Any] = {
        "page_number": page_number,
        "property_address": None,
        "address_snippet": None,
        "addition_area": None,
        "addition_area_snippet": None,
        "stated_building_area": None,
        "building_area_snippet": None,
        "parcel_number": None,
        "applicant_name": None,
        "license_number": None,
        "setback_front": None,
        "setback_rear": None,
        "setback_side": None,
        "scale_annotation": None,
        "has_north_arrow": False,
        "has_professional_stamp": False,
        "identified_rooms": None,
        "sheet_number": None
    }

    if not text:
        return p_fields

    # Address
    addr_match = ADDR_PATTERN.search(text)
    if addr_match:
        raw_addr = addr_match.group(1)
        p_fields["property_address"] = re.sub(r"\s+", " ", raw_addr).strip()
        start = max(0, addr_match.start())
        end = min(len(text), addr_match.end() + 25)
        p_fields["address_snippet"] = re.sub(r"\s+", " ", text[start:end]).strip()
    else:
        fb_match = FALLBACK_ADDR_PATTERN.search(text)
        if fb_match:
            raw_addr = fb_match.group(1)
            p_fields["property_address"] = re.sub(r"\s+", " ", raw_addr).strip()
            start = max(0, fb_match.start())
            end = min(len(text), fb_match.end() + 25)
            p_fields["address_snippet"] = re.sub(r"\s+", " ", text[start:end]).strip()

    # Addition area
    add_match = ADDITION_AREA_PATTERN.search(text)
    if add_match:
        try:
            p_fields["addition_area"] = float(add_match.group(1).replace(",", ""))
            start = max(0, add_match.start())
            end = min(len(text), add_match.end() + 20)
            p_fields["addition_area_snippet"] = re.sub(r"\s+", " ", text[start:end]).strip()
        except ValueError:
            pass

    # Stated building area
    bld_match = BUILDING_AREA_PATTERN.search(text)
    if bld_match:
        try:
            p_fields["stated_building_area"] = float(bld_match.group(1).replace(",", ""))
            start = max(0, bld_match.start())
            end = min(len(text), bld_match.end() + 20)
            p_fields["building_area_snippet"] = re.sub(r"\s+", " ", text[start:end]).strip()
        except ValueError:
            pass
    else:
        for sec_match in SEC_AREA_PATTERN.finditer(text):
            # Do not match if this area overlaps the addition area already matched
            if add_match and (sec_match.start() < add_match.end() and sec_match.end() > add_match.start()):
                continue
            # Check if immediately preceded by addition / extension
            prefix = text[max(0, sec_match.start() - 25):sec_match.start()].lower()
            if "addition" in prefix or "extension" in prefix:
                continue
            try:
                p_fields["stated_building_area"] = float(sec_match.group(1).replace(",", ""))
                start = max(0, sec_match.start())
                end = min(len(text), sec_match.end() + 20)
                p_fields["building_area_snippet"] = re.sub(r"\s+", " ", text[start:end]).strip()
                break
            except ValueError:
                pass

    # APN / Parcel Number
    apn_match = re.search(r"(?:APN|A\.P\.N\.|Parcel\s+(?:No|Number|ID|#))\s*[:\-\s]*([0-9]{3,4}[\-\s]?[0-9]{3,4}[\-\s]?[0-9]{2,4})", text, re.IGNORECASE)
    if apn_match:
        p_fields["parcel_number"] = apn_match.group(1).strip()

    # Applicant / Owner Name
    owner_match = re.search(r"(?:owner|applicant|client|property\s+owner)\s*(?:name)?\s*[:\n\-]\s*([A-Za-z\s,\.]{3,40})(?:\n|$|phone|email|address)", text, re.IGNORECASE)
    if owner_match:
        p_fields["applicant_name"] = re.sub(r"\s+", " ", owner_match.group(1)).strip()

    # Contractor / Architect License
    license_match = re.search(r"(?:license|registration|cslb|lic\s*#)\s*[:\-\s]*([A-Za-z0-9\-\s]{5,15})", text, re.IGNORECASE)
    if license_match:
        p_fields["license_number"] = license_match.group(1).strip()

    # Setbacks
    front_setback = re.search(r"front\s*(?:yard)?\s*setback\s*[:\-\s]*([0-9]+(?:\.[0-9]+)?(?:'|ft|\s*feet)?(?:\s*[0-9]+(?:\")?)?)", text, re.IGNORECASE)
    rear_setback = re.search(r"rear\s*(?:yard)?\s*setback\s*[:\-\s]*([0-9]+(?:\.[0-9]+)?(?:'|ft|\s*feet)?(?:\s*[0-9]+(?:\")?)?)", text, re.IGNORECASE)
    side_setback = re.search(r"side\s*(?:yard)?\s*setback\s*[:\-\s]*([0-9]+(?:\.[0-9]+)?(?:'|ft|\s*feet)?(?:\s*[0-9]+(?:\")?)?)", text, re.IGNORECASE)
    
    p_fields["setback_front"] = front_setback.group(1).strip() if front_setback else None
    p_fields["setback_rear"] = rear_setback.group(1).strip() if rear_setback else None
    p_fields["setback_side"] = side_setback.group(1).strip() if side_setback else None

    # Scale annotation
    scale_match = re.search(r"scale\s*[:\-\s]*((?:[0-9]+/[0-9]+\"\s*=\s*[0-9]+['\"][0-9]*\"?)|(?:1\s*:\s*[0-9]+)|(?:not\s+to\s+scale|NTS))", text, re.IGNORECASE)
    p_fields["scale_annotation"] = scale_match.group(1).strip() if scale_match else None

    # North arrow & stamp
    p_fields["has_north_arrow"] = bool(re.search(r"\b(?:north\s+arrow|true\s+north|compass\s+arrow|project\s+north)\b", text, re.IGNORECASE))
    p_fields["has_professional_stamp"] = bool(re.search(r"\b(?:professional\s+engineer|licensed\s+architect|registration\s+seal|pe\s+stamp|board\s+of\s+architects)\b", text, re.IGNORECASE))

    # Room labels
    rooms = []
    for r in ["Living Room", "Dining Room", "Kitchen", "Master Bedroom", "Bedroom 2", "Bedroom 3", "Bathroom", "Bath 1", "Bath 2", "Laundry", "Garage", "Pantry", "Office"]:
        if re.search(rf"\b{re.escape(r)}\b", text, re.IGNORECASE):
            rooms.append(r)
    p_fields["identified_rooms"] = rooms if rooms else None

    # Sheet number
    sheet_match = re.search(r"(?:sheet|drawing)\s*(?:no\.?|#)?\s*[:\-\s]*([A-Z]{1,2}[\-\.]?[0-9]{1,3})", text, re.IGNORECASE)
    p_fields["sheet_number"] = sheet_match.group(1).strip() if sheet_match else None

    return p_fields


def extract_fields_from_document(category: str, text: str, pages_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Extracts category-specific structured fields from document text and records per-page attribution.
    Preserves all extracted values per page in _page_fields so conflicting values across sheets are never discarded.
    """
    fields: Dict[str, Any] = {}
    page_fields_list: List[Dict[str, Any]] = []

    if pages_data and len(pages_data) > 0:
        for p in pages_data:
            p_num = p.get("page_number", len(page_fields_list) + 1)
            p_text = p.get("text", "")
            p_fields = extract_page_fields(p_text, p_num)
            page_fields_list.append(p_fields)
    else:
        # Single page fallback from concatenated text
        p_fields = extract_page_fields(text, 1)
        page_fields_list.append(p_fields)

    fields["_page_fields"] = page_fields_list

    # Document-level field aggregation (preserving backward compatibility)
    # 1. Address
    addrs_found = [p["property_address"] for p in page_fields_list if p.get("property_address")]
    fields["property_address"] = addrs_found[0] if addrs_found else None

    # 2. Addition Area
    add_areas = [p["addition_area"] for p in page_fields_list if p.get("addition_area") is not None]
    fields["addition_area"] = add_areas[0] if add_areas else None

    # 3. Stated Building Area
    bld_areas = [p["stated_building_area"] for p in page_fields_list if p.get("stated_building_area") is not None]
    fields["stated_building_area"] = bld_areas[0] if bld_areas else None

    # 4. Other fields
    apns = [p["parcel_number"] for p in page_fields_list if p.get("parcel_number")]
    fields["parcel_number"] = apns[0] if apns else None

    owners = [p["applicant_name"] for p in page_fields_list if p.get("applicant_name")]
    fields["applicant_name"] = owners[0] if owners else None

    licenses = [p["license_number"] for p in page_fields_list if p.get("license_number")]
    fields["license_number"] = licenses[0] if licenses else None

    front_sb = [p["setback_front"] for p in page_fields_list if p.get("setback_front")]
    fields["setback_front"] = front_sb[0] if front_sb else None

    rear_sb = [p["setback_rear"] for p in page_fields_list if p.get("setback_rear")]
    fields["setback_rear"] = rear_sb[0] if rear_sb else None

    side_sb = [p["setback_side"] for p in page_fields_list if p.get("setback_side")]
    fields["setback_side"] = side_sb[0] if side_sb else None

    scales = [p["scale_annotation"] for p in page_fields_list if p.get("scale_annotation")]
    fields["scale_annotation"] = scales[0] if scales else None

    fields["has_north_arrow"] = any(p.get("has_north_arrow") for p in page_fields_list)
    fields["has_professional_stamp"] = any(p.get("has_professional_stamp") for p in page_fields_list)

    all_rooms = []
    for p in page_fields_list:
        if p.get("identified_rooms"):
            all_rooms.extend(p["identified_rooms"])
    fields["identified_rooms"] = list(dict.fromkeys(all_rooms)) if all_rooms else None

    sheets = [p["sheet_number"] for p in page_fields_list if p.get("sheet_number")]
    fields["sheet_number"] = sheets[0] if sheets else None

    # Dynamic Page Mapping: Record exact 1-indexed page number where each primary field is located
    field_pages: Dict[str, Optional[int]] = {}
    field_all_pages: Dict[str, List[int]] = {}

    if pages_data:
        from app.document_processing.evidence_locator import locate_all_evidence_in_pages
        mapping_targets = [
            ("property_address", fields.get("property_address")),
            ("stated_building_area", str(int(fields["stated_building_area"])) if fields.get("stated_building_area") else None),
            ("addition_area", str(int(fields["addition_area"])) if fields.get("addition_area") else None),
            ("setback_front", str(fields["setback_front"]) if fields.get("setback_front") else None),
            ("setback_side", str(fields["setback_side"]) if fields.get("setback_side") else None),
            ("has_north_arrow", "north" if fields.get("has_north_arrow") else None)
        ]
        for f_name, f_val in mapping_targets:
            if f_val:
                matches = locate_all_evidence_in_pages(pages_data, str(f_val))
                if matches:
                    field_pages[f_name] = matches[0]["page_number"]
                    field_all_pages[f_name] = [m["page_number"] for m in matches]
                else:
                    field_pages[f_name] = None
                    field_all_pages[f_name] = []
    
    fields["_field_pages"] = field_pages
    fields["_field_all_pages"] = field_all_pages

    return fields

