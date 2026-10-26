import re
from typing import List, Dict, Any, Optional, Tuple

SYNONYMS = {
    "st": "(?:st|street)",
    "street": "(?:st|street)",
    "ave": "(?:ave|avenue)",
    "avenue": "(?:ave|avenue)",
    "rd": "(?:rd|road)",
    "road": "(?:rd|road)",
    "dr": "(?:dr|drive)",
    "drive": "(?:dr|drive)",
    "blvd": "(?:blvd|boulevard)",
    "boulevard": "(?:blvd|boulevard)",
    "ln": "(?:ln|lane)",
    "lane": "(?:ln|lane)",
    "ct": "(?:ct|court)",
    "court": "(?:ct|court)",
    "cir": "(?:cir|circle)",
    "circle": "(?:cir|circle)",
    "sq": "(?:sq|square)",
    "square": "(?:sq|square)",
    "ft": "(?:ft|feet)",
    "feet": "(?:ft|feet)"
}

def build_flexible_search_pattern(search_term: str) -> Optional[re.Pattern]:
    """
    Builds a regex pattern that matches the search term even when words are split
    across lines, contain commas/hyphens, or use common architectural abbreviations.
    """
    cleaned = search_term.strip()
    words = re.findall(r"[A-Za-z0-9]+", cleaned)
    if not words:
        return None

    pattern_parts = []
    for w in words:
        lower_w = w.lower()
        if lower_w in SYNONYMS:
            pattern_parts.append(SYNONYMS[lower_w])
        elif re.match(r"^\d{4,6}$", w):
            # E.g. 2850 -> 2[,.\s]?850 or 12500 -> 12[,.\s]?500
            prefix = w[:-3]
            suffix = w[-3:]
            pattern_parts.append(rf"{prefix}[,.\s]?{suffix}")
        else:
            pattern_parts.append(re.escape(w))

    regex_str = r"\b" + r"\s*[\n,\-\./:]*\s*".join(pattern_parts) + r"\b"
    return re.compile(regex_str, re.IGNORECASE)

def locate_all_evidence_in_pages(
    pages_data: List[Dict[str, Any]], 
    search_term: str
) -> List[Dict[str, Any]]:
    """
    Locates all occurrences of a search term across multi-page extraction data.
    Handles values split across lines, duplicate matches on multiple sheets,
    and returns a list of matching records with 1-indexed page numbers and snippets.
    """
    if not search_term or not pages_data:
        return []

    pattern = build_flexible_search_pattern(search_term)
    matches: List[Dict[str, Any]] = []
    seen_pages = set()

    # Pass 1: Flexible regex matching (handles newlines, abbreviations, formatting)
    if pattern:
        for page in pages_data:
            page_num = page.get("page_number")
            if page_num is None:
                continue
            text = page.get("text", "")
            match = pattern.search(text)
            if match and page_num not in seen_pages:
                start = max(0, match.start() - 40)
                end = min(len(text), match.end() + 40)
                snippet = re.sub(r"\s+", " ", text[start:end]).strip()
                matches.append({
                    "page_number": page_num,
                    "snippet": snippet,
                    "exact": True
                })
                seen_pages.add(page_num)

    if matches:
        return matches

    # Pass 2: Direct lowercase substring match
    cleaned_term = re.sub(r"\s+", " ", search_term.strip().lower())
    for page in pages_data:
        page_num = page.get("page_number")
        if page_num is None or page_num in seen_pages:
            continue
        text = page.get("text", "")
        norm_text = re.sub(r"\s+", " ", text.lower())
        pos = norm_text.find(cleaned_term)
        if pos != -1:
            start = max(0, pos - 40)
            end = min(len(norm_text), pos + len(cleaned_term) + 40)
            snippet = norm_text[start:end].strip()
            matches.append({
                "page_number": page_num,
                "snippet": snippet,
                "exact": True
            })
            seen_pages.add(page_num)

    if matches:
        return matches

    # Pass 3: Significant word co-occurrence (e.g. house number + street name)
    words = [w.lower() for w in re.findall(r"[A-Za-z0-9]+", search_term) if len(w) > 2]
    if len(words) >= 2:
        for page in pages_data:
            page_num = page.get("page_number")
            if page_num is None or page_num in seen_pages:
                continue
            text = page.get("text", "")
            text_lower = text.lower()
            if all(w in text_lower for w in words):
                pos = text_lower.find(words[0])
                start = max(0, pos - 40)
                end = min(len(text), pos + 120)
                snippet = re.sub(r"\s+", " ", text[start:end]).strip()
                matches.append({
                    "page_number": page_num,
                    "snippet": snippet,
                    "exact": False
                })
                seen_pages.add(page_num)

    return matches

def locate_evidence_in_pages(
    pages_data: List[Dict[str, Any]], 
    search_term: str,
    prefer_page: Optional[int] = None
) -> Optional[Tuple[int, str]]:
    """
    Finds which 1-indexed page and surrounding snippet contains the search term.
    Returns (page_number, snippet_text) or None if cannot be located confidently.
    Never invents or defaults to page 1.
    """
    matches = locate_all_evidence_in_pages(pages_data, search_term)
    if not matches:
        return None

    if prefer_page is not None:
        for m in matches:
            if m["page_number"] == prefer_page:
                return m["page_number"], m["snippet"]

    # Return first confident match
    return matches[0]["page_number"], matches[0]["snippet"]

