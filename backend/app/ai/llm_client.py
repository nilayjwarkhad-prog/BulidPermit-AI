import json
import httpx
from typing import Optional, Dict, Any, List
from app.config import settings
from app.core.logging import log_info, log_warning, log_error
from app.ai.output_schemas import AIClassificationOutput, AIFindingRecommendation

class LLMClient:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL
        self.enabled = settings.AI_ENABLED
        self.timeout = float(settings.AI_REQUEST_TIMEOUT)

    async def check_health(self) -> Dict[str, Any]:
        """Checks Ollama server connectivity and model availability."""
        if not self.enabled:
            return {
                "available": False,
                "ai_enabled": False,
                "model": self.model,
                "message": "AI functionality is disabled via configuration (AI_ENABLED=False).",
                "installed_models": []
            }

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    model_found = any(self.model in m for m in models)
                    return {
                        "available": True,
                        "ai_enabled": True,
                        "model": self.model,
                        "model_ready": model_found,
                        "installed_models": models,
                        "message": f"Ollama is online. Model '{self.model}' {'is ready' if model_found else 'needs to be pulled'}"
                    }
                else:
                    return {
                        "available": False,
                        "ai_enabled": True,
                        "model": self.model,
                        "message": f"Ollama returned HTTP {res.status_code}",
                        "installed_models": []
                    }
        except Exception as e:
            return {
                "available": False,
                "ai_enabled": True,
                "model": self.model,
                "message": f"Could not reach Ollama server at {self.base_url}: {str(e)}",
                "installed_models": []
            }

    async def classify_document_text(self, text_snippet: str, filename: str) -> Optional[AIClassificationOutput]:
        """Classifies document content using the local Qwen model if available."""
        if not self.enabled:
            return None

        prompt = f"""You are an expert municipal building permit document processor.
Classify the following uploaded building permit document based on its text and filename.

Filename: {filename}
Text sample:
\"\"\"{text_snippet[:1500]}\"\"\"

Allowed Categories:
- Permit Application
- Site Plan
- Property Survey
- Floor Plan
- Elevation Drawing
- Building Sections
- Structural Plans
- Structural Calculations
- Energy Documentation
- Electrical Plans
- Plumbing Plans
- Mechanical Plans
- Drainage and Grading
- Geotechnical Report
- Professional Signatures & Seals
- Other Supporting Document

Respond ONLY with valid JSON in this exact structure:
{{
  "category": "<One of the allowed categories above>",
  "confidence": <float between 0.0 and 1.0>,
  "evidence": ["<specific word or phrase 1>", "<specific word or phrase 2>"],
  "requires_human_confirmation": <true or false>,
  "reasoning": "<short sentence explaining why>"
}}
"""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
                res = await client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    resp_json = res.json()
                    raw_text = resp_json.get("response", "").strip()
                    parsed = json.loads(raw_text)
                    return AIClassificationOutput(**parsed)
        except Exception as e:
            log_warning(f"AI Classification call failed or timed out: {e}. Falling back to deterministic rules.")
            return None

    async def explain_finding(self, title: str, explanation: str, rule_reference: Optional[str] = None) -> Optional[AIFindingRecommendation]:
        """Uses LLM to provide clear, actionable advice for resolving a permit pre-check finding."""
        if not self.enabled:
            return None

        prompt = f"""You are an experienced residential plan examiner helping a homeowner or contractor fix permit issues before filing with the city.
Explain this pre-check issue in simple, everyday English. Do NOT use dry engineering jargon, legal disclaimers, or robotic boilerplate (never say 'As an AI...').

Issue Found: {title}
Details: {explanation}
Permit Standard: {rule_reference or 'Standard Residential Building Code'}

Provide:
1. A clear 1-2 sentence explanation of what this means and why the city building counter cares.
2. A concrete, practical instruction the owner can take or tell their drafter/architect to fix it.

Respond ONLY with valid JSON in this exact structure:
{{
  "explanation": "<Simple 1-2 sentence explanation in plain conversational English>",
  "recommended_action": "<Concrete practical instruction on how to fix this>",
  "severity": "warning",
  "confidence": 0.90
}}
"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
                res = await client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    parsed = json.loads(data.get("response", "{}"))
                    return AIFindingRecommendation(**parsed)
        except Exception as e:
            log_warning(f"AI Finding Explanation failed: {e}. Falling back to default recommendation.")
            return None

llm_client = LLMClient()
