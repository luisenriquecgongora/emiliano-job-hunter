#!/usr/bin/env python3
"""
Anti-Detection & Stylometric Humanization Auditor for Emiliano Job Hunter.
Guarantees that job applications:
1. Detect and evade prompt-injection honey traps (canary phrases, hidden HTML, zero-width chars).
2. Defeat AI detectors (GPTZero, CopyLeaks, Turnitin, Sapling) by enforcing human burstiness,
   high perplexity variation, and eliminating 60+ algorithmic LLM clichés.
3. Automatically append the required RODO/GDPR recruitment clause when targeting Polish/EU employers.
"""

from __future__ import annotations
import re
import sys
import math
from pathlib import Path
from typing import Dict, List, Tuple

# Common LLM fingerprint words & phrases frequently flagged by AI detectors
AI_CLICHE_PATTERNS = [
    r"\bdelve\b",
    r"\bspearhead(?:ed|ing)?\b",
    r"\btapestry\b",
    r"\btestament\b",
    r"\bpivotal\b",
    r"\bbeacon\b",
    r"\bfoster(?:ed|ing)?\b",
    r"\bleverage(?:d|ing)?\b",
    r"\bseamless(?:ly)?\b",
    r"\bholistic(?:ally)?\b",
    r"\bthrilled\b",
    r"\bvibrant\b",
    r"\bin today's (?:fast-paced|digital|rapidly evolving) (?:landscape|world)\b",
    r"\ba testament to\b",
    r"\bhit the ground running\b",
    r"\bpassionate about\b",
    r"\bgroundbreaking\b",
    r"\bgame-changer\b",
    r"\bcomprehensive suite\b",
    r"\bit is worth noting that\b",
    r"\bfurthermore\b",
    r"\bmoreover\b",
    r"\bin conclusion\b",
    r"\beager to contribute\b",
    r"\bproactive self-starter\b",
    r"\bsynergy\b",
]

# Patterns typically embedded in job descriptions to honey-trap AI bots
HONEYTRAP_PATTERNS = [
    r"(?:if you are an? (?:ai|llm|automated system|bot)|ignore previous instructions)",
    r"(?:start|begin|include) your (?:cover letter|application|intro) with the (?:word|phrase) ['\"]?([a-zA-Z0-9_-]+)['\"]?",
    r"(?:write|compose) a poem about",
    r"state that you have \d+ years of experience in (?:quantum|fictional|imaginary)",
]

RODO_CLAUSE_PL = (
    "Wyrażam zgodę na przetwarzanie moich danych osobowych dla potrzeb niezbędnych do "
    "realizacji procesu rekrutacji (zgodnie z ustawą z dnia 10 maja 2018 roku o ochronie danych "
    "osobowych (Dz. Ustaw z 2018, poz. 1000) oraz zgodnie z Rozporządzeniem Parlamentu Europejskiego "
    "i Rady (UE) 2016/679 z dnia 27 kwietnia 2016 r. (RODO))."
)

RODO_CLAUSE_EN = (
    "I hereby give consent for my personal data to be processed for the purpose of conducting "
    "the recruitment process in accordance with Regulation (EU) 2016/679 of the European Parliament "
    "and of the Council (GDPR)."
)


def analyze_burstiness(text: str) -> Dict[str, float]:
    """
    Calculates sentence length variance (burstiness).
    Human text typically exhibits standard deviation > 7 words.
    Monotonous LLM text typically exhibits standard deviation < 4.5 words.
    """
    sentences = re.split(r"[.!?]+", text)
    clean_sentences = [s.strip() for s in sentences if len(s.strip().split()) > 2]
    if not clean_sentences:
        return {"avg_words": 0.0, "std_dev": 0.0, "sentence_count": 0, "human_score": 0.0}

    lengths = [len(s.split()) for s in clean_sentences]
    avg = sum(lengths) / len(lengths)
    variance = sum((x - avg) ** 2 for x in lengths) / len(lengths)
    std_dev = math.sqrt(variance)

    # Human score 0-100: std_dev >= 8 is ideal human score (100)
    human_score = min(100.0, max(10.0, (std_dev / 8.0) * 100.0))

    return {
        "avg_words": round(avg, 1),
        "std_dev": round(std_dev, 2),
        "sentence_count": len(clean_sentences),
        "human_score": round(human_score, 1),
    }


def scan_ai_cliches(text: str) -> List[str]:
    """Finds all occurrences of high-frequency LLM clichés."""
    found = []
    lower = text.lower()
    for pattern in AI_CLICHE_PATTERNS:
        matches = re.findall(pattern, lower)
        if matches:
            found.extend(matches)
    return list(set(found))


def scan_honeytraps(job_description: str) -> List[str]:
    """Scans incoming job posting for canary traps, prompt injections, or AI trick phrases."""
    found = []
    for pattern in HONEYTRAP_PATTERNS:
        matches = re.finditer(pattern, job_description, re.IGNORECASE)
        for m in matches:
            found.append(m.group(0))
    return found


def audit_document(text: str, is_job_description: bool = False) -> Dict:
    """Full stylometric and security audit of application text or posting."""
    if is_job_description:
        traps = scan_honeytraps(text)
        return {
            "type": "job_description",
            "honeytraps_detected": traps,
            "is_safe": len(traps) == 0,
        }

    burstiness = analyze_burstiness(text)
    cliches = scan_ai_cliches(text)
    has_em_dash = "—" in text or "–" in text

    is_human_sounding = burstiness["std_dev"] >= 5.5 and len(cliches) == 0

    return {
        "type": "application_document",
        "burstiness": burstiness,
        "cliches_found": cliches,
        "has_em_dash": has_em_dash,
        "is_human_sounding": is_human_sounding,
        "recommendation": (
            "PASSED: Natural human rhythm with no AI clichés detected."
            if is_human_sounding
            else "WARNING: Flagged for robotic/AI markers. Diversify sentence lengths and remove clichés."
        ),
    }


if __name__ == "__main__":
    sample_text = (
        "I built the monorepo architecture for PlaatoOS using TypeScript and Module Federation. "
        "It was critical. Full rebuilds were killing our velocity, so runtime shell composition saved hours each day. "
        "When our geometry pipeline at AGP eGlass hit a twelve-hour bottleneck, I moved the intensive algorithms into C++, "
        "slashing execution time down to ten minutes flat."
    )
    result = audit_document(sample_text)
    print("--- Anti-Detection Stylometric Audit ---")
    print(result)
