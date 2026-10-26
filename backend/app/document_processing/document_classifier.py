import re
from typing import Dict, Any, List, Tuple

DOCUMENT_CATEGORIES = [
    "Permit Application",
    "Site Plan",
    "Property Survey",
    "Floor Plan",
    "Elevation Drawing",
    "Building Sections",
    "Structural Plans",
    "Structural Calculations",
    "Energy Documentation",
    "Electrical Plans",
    "Plumbing Plans",
    "Mechanical Plans",
    "Drainage and Grading",
    "Geotechnical Report",
    "Professional Signatures & Seals",
    "Other Supporting Document"
]

CATEGORY_PATTERNS = {
    "Permit Application": [
        (r"building\s+permit\s+application", 10),
        (r"permit\s+application", 8),
        (r"department\s+of\s+building\s+and\s+safety", 7),
        (r"owner\s*-\s*builder\s+declaration", 8),
        (r"applicant\s+signature", 6),
        (r"parcel\s+number|apn\b", 5),
        (r"contractor\s+license", 5),
        (r"scope\s+of\s+work", 5),
        (r"valuation\s+of\s+work", 6),
    ],
    "Site Plan": [
        (r"site\s+plan", 10),
        (r"plot\s+plan", 9),
        (r"property\s+line[s]?", 7),
        (r"front\s+setback|rear\s+setback|side\s+setback", 8),
        (r"setback[s]?", 6),
        (r"north\s+arrow", 5),
        (r"lot\s+coverage", 7),
        (r"proposed\s+addition|proposed\s+structure", 6),
        (r"easement[s]?", 5),
        (r"zoning\s+district", 5),
    ],
    "Property Survey": [
        (r"boundary\s+survey", 10),
        (r"property\s+survey", 9),
        (r"land\s+surveyor", 8),
        (r"monument\s+found", 7),
        (r"iron\s+pin", 6),
        (r"metes\s+and\s+bounds", 8),
    ],
    "Floor Plan": [
        (r"floor\s+plan", 10),
        (r"first\s+floor\s+plan|second\s+floor\s+plan|ground\s+floor\s+plan", 10),
        (r"living\s+room|bedroom|kitchen|bathroom|dining\s+room", 6),
        (r"door\s+schedule|window\s+schedule", 6),
        (r"ceiling\s+height", 5),
        (r"habitable\s+space", 5),
        (r"hallway|closet|pantry", 4),
    ],
    "Elevation Drawing": [
        (r"elevation[s]?", 9),
        (r"north\s+elevation|south\s+elevation|east\s+elevation|west\s+elevation", 10),
        (r"front\s+elevation|rear\s+elevation|side\s+elevation", 10),
        (r"roof\s+pitch|ridge\s+height|plate\s+height", 7),
        (r"exterior\s+finish|stucco|siding", 5),
    ],
    "Building Sections": [
        (r"building\s+section", 10),
        (r"cross\s+section|longitudinal\s+section", 9),
        (r"wall\s+section|section\s+a-a", 9),
        (r"foundation\s+detail|framing\s+detail", 7),
        (r"joist\s+spacing|rafter\s+spacing", 6),
    ],
    "Structural Plans": [
        (r"structural\s+plan[s]?", 10),
        (r"structural\s+notes", 9),
        (r"foundation\s+plan", 9),
        (r"framing\s+plan|roof\s+framing|floor\s+framing", 9),
        (r"seismic\s+design\s+category|wind\s+speed\s+exposure", 8),
        (r"anchor\s+bolts|holdowns|shear\s+wall", 7),
        (r"concrete\s+strength|f'c\s*=", 7),
    ],
    "Structural Calculations": [
        (r"structural\s+calculation[s]?", 10),
        (r"engineering\s+calculation[s]?", 9),
        (r"moment\s+distribution|deflection\s+check", 8),
        (r"load\s+combination|dead\s+load|live\s+load", 7),
        (r"professional\s+engineer|pe\s+stamp", 6),
    ],
    "Energy Documentation": [
        (r"title\s*24", 10),
        (r"energy\s+compliance|energy\s+conservation", 9),
        (r"cf1r|energy\s+calculation", 9),
        (r"u-factor|shgc\b", 8),
        (r"insulation\s+r-value", 8),
        (r"hvac\s+efficiency|seer\b", 7),
    ],
    "Electrical Plans": [
        (r"electrical\s+plan", 10),
        (r"panel\s+schedule|single\s+line\s+diagram", 9),
        (r"lighting\s+plan|receptacle\s+layout", 8),
        (r"circuit\s+breaker|amp\s+service", 7),
        (r"smoke\s+alarm|carbon\s+monoxide", 6),
    ],
    "Plumbing Plans": [
        (r"plumbing\s+plan", 10),
        (r"water\s+supply|drainage\s+waste\s+vent|dwv", 9),
        (r"fixture\s+count|fixture\s+units", 8),
        (r"water\s+heater|cleanout", 7),
    ],
    "Mechanical Plans": [
        (r"mechanical\s+plan", 10),
        (r"hvac\s+layout|ductwork|cfm\b", 9),
        (r"furnace|heat\s+pump|air\s+conditioning", 8),
        (r"ventilation\s+calculation", 7),
    ],
    "Drainage and Grading": [
        (r"grading\s+plan", 10),
        (r"drainage\s+plan", 10),
        (r"topography|contour\s+lines", 8),
        (r"retaining\s+wall|swale|catch\s+basin", 7),
        (r"cut\s+and\s+fill", 7),
    ],
    "Geotechnical Report": [
        (r"geotechnical\s+report|soils\s+report", 10),
        (r"soil\s+boring|bearing\s+capacity", 9),
        (r"foundation\s+recommendation[s]?", 8),
        (r"liquefaction|slope\s+stability", 8),
    ],
    "Professional Signatures & Seals": [
        (r"licensed\s+architect|professional\s+engineer", 8),
        (r"registration\s+seal|stamp\s+and\s+signature", 9),
        (r"state\s+of\s+california\s+board", 7),
        (r"certificate\s+of\s+compliance", 7),
    ],
}

def classify_document(text: str, filename: str = "") -> Dict[str, Any]:
    """
    Classifies a document based on extracted text and filename cues.
    Returns category, confidence score (0.0 to 1.0), matching keywords, and explanation.
    """
    cleaned_text = text.lower()
    cleaned_fn = filename.lower()
    
    scores: Dict[str, float] = {cat: 0.0 for cat in DOCUMENT_CATEGORIES}
    matched_evidences: Dict[str, List[str]] = {cat: [] for cat in DOCUMENT_CATEGORIES}
    
    # Filename bonuses
    for cat in DOCUMENT_CATEGORIES:
        cat_words = [w.lower() for w in cat.split() if len(w) > 3]
        for w in cat_words:
            if w in cleaned_fn:
                scores[cat] += 4.0
                matched_evidences[cat].append(f"Filename contains '{w}'")

    # Regex pattern matching
    for cat, patterns in CATEGORY_PATTERNS.items():
        for pattern, weight in patterns:
            matches = list(re.finditer(pattern, cleaned_text, re.IGNORECASE))
            if matches:
                # Add score with diminishing returns for repetitions
                match_count = min(len(matches), 3)
                scores[cat] += weight * (1.0 + 0.2 * (match_count - 1))
                matched_evidences[cat].append(f"Found '{matches[0].group(0)}'")

    # Sort categories by score
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_cat, top_score = sorted_scores[0]
    
    if top_score < 4.0:
        return {
            "category": "Other Supporting Document",
            "suggested_category": "Other Supporting Document",
            "confidence": 0.45,
            "evidence": ["Insufficient text keywords to reliably identify category"],
            "requires_confirmation": True
        }
    
    # Calculate relative confidence
    second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0.0
    margin = top_score - second_score
    confidence = min(0.98, max(0.55, (top_score / (top_score + 10.0)) * 0.7 + (margin / (top_score + 1.0)) * 0.3))

    return {
        "category": best_cat,
        "suggested_category": best_cat,
        "confidence": round(confidence, 2),
        "evidence": matched_evidences[best_cat][:5],
        "requires_confirmation": confidence < 0.75
    }
