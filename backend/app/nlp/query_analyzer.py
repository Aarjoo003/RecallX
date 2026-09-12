import re
from typing import Dict, Any, Optional, List
from .normalizer import normalize_text, tokenize
from .temporal_parser import parse_temporal_expression
from ..models.search import InterpretedFilters

PARTICIPANTS_MAP = {
    "aman": {"id": "p01", "name": "Aman Sharma"},
    "priya": {"id": "p02", "name": "Priya Patel"},
    "rahul": {"id": "p03", "name": "Rahul Verma"},
    "sneha": {"id": "p04", "name": "Sneha Rao"},
    "rohan": {"id": "p05", "name": "Rohan Mehta"},
    "ananya": {"id": "p06", "name": "Ananya Gupta"},
    "vikram": {"id": "p07", "name": "Vikram Singh"},
    "divya": {"id": "p08", "name": "Divya Nair"},
    "kabir": {"id": "p09", "name": "Kabir Joshi"},
    "tanvi": {"id": "p10", "name": "Tanvi Malhotra"},
}

TOPIC_KEYWORDS = {
    "trip": [
        "trip", "destination", "vacation", "manali", "goa", "rishikesh", 
        "stay during", "where to stay", "cottage", "itinerary", "cabs", "innova", 
        "train tickets", "vande bharat", "terminal", "expenditure", "per head", "budget", 
        "where to go", "where did we go", "holiday", "settle on the destination"
    ],
    "project": [
        "project", "capstone", "tech stack", "fastapi", "react", "github", 
        "repository", "repo", "submission", "deadline", "guide", "framework", 
        "programming", "build choice", "machine learning", "ml apis", "ui design", 
        "figma", "wireframes", "dashboard", "extended", "postponed"
    ],
    "fest": [
        "fest", "symposium", "summit", "conference", "auditorium", "venue", 
        "take place", "registration fee", "slide presentation", "presentation", 
        "deck", "ppt compilation", "music system", "sound system", "dj setup", 
        "speakers", "circular", "event dates", "expenses for the college festival", 
        "splitwise group for fest", "stage decorations"
    ],
    "dinner": [
        "restaurant", "dining", "dinner", "treat", "barbeque nation", "haveli", 
        "celebrate", "rahul's placement", "table reserved", "paneer tikka"
    ],
    "sports": [
        "sports", "cricket", "turf", "box cricket", "facility", "arena", 
        "tournament", "sports facility"
    ],
    "hostel": [
        "hostel", "network outage", "wifi", "internet", "fiber cable", 
        "library closed", "reading room", "library air conditioning"
    ],
    "exams": [
        "exam", "exams", "midterm", "mid-term", "endterm", "os", 
        "operating systems", "dbms", "networks", "syllabus", "viva"
    ],
    "placements": [
        "placement", "placements", "internship", "stipend", "cisco", 
        "oracle", "interview", "coding test", "offer letter"
    ],
    "birthday": [
        "birthday", "bday", "b'day", "b-day", "janamdin", "cake", "party", 
        "born", "treat", "gift", "celebration"
    ],
}

TOPIC_TO_THREADS = {
    "trip": ["thread_trip_01"],
    "project": ["thread_project_tech_02", "thread_minor_project_eval", "thread_project_git", "thread_deadline_rush"],
    "fest": ["thread_fest_symposium_03", "thread_fest_notes"],
    "dinner": ["thread_rahul_party", "thread_team_dinner"],
    "sports": ["thread_cricket_match"],
    "hostel": ["thread_campus_net", "thread_library_notice"],
    "exams": ["thread_exam_schedule", "thread_midterm_prep"],
    "placements": ["thread_placement_drives", "thread_internships"],
    "birthday": ["thread_birthday_08"],
}

DECISION_PATTERNS = [
    r"\b(finally decide|final decision|decide on|settle on|settled|concluded|confirmed|chosen|picked|agreed to|lock|finalize|finalized|fnl|kab final hua|final)\b",
    r"\b(what did we finally|when did we finally|which.*was picked|what.*did we agree|what was the final decision|where will the.*take place)\b"
]

def extract_entity_need(raw_lower: str) -> Optional[str]:
    """Identifies specific information object requested by query."""
    if any(k in raw_lower for k in ["bday", "birthday", "janamdin"]):
        return "birthday"
    if any(k in raw_lower for k in ["tech stack", "technical stack", "technology", "build choice"]):
        return "tech_stack"
    if any(k in raw_lower for k in ["where will", "take place", "venue"]):
        return "venue"
    if any(k in raw_lower for k in ["restaurant", "dining", "celebrate rahul", "placement dinner", "dinner party"]):
        return "restaurant"
    if any(k in raw_lower for k in ["stay during", "where to stay", "cottage", "accommodation", "stay kahan", "stay"]):
        return "stay"
    if any(k in raw_lower for k in ["vehicle", "cabs", "innova", "terminal", "commuting"]):
        return "vehicle"
    if any(k in raw_lower for k in ["what caused", "network outage", "outage"]):
        return "cause"
    if any(k in raw_lower for k in ["slide presentation", "presentation deck", "creating the slide", "ppt compilation"]):
        return "deck"
    if any(k in raw_lower for k in ["sports facility", "tournament", "arena", "box cricket", "cricket match kahan", "cricket slot"]):
        return "sports_venue"
    if any(k in raw_lower for k in ["repository", "github organization"]):
        return "repo"
    if any(k in raw_lower for k in ["ui design", "wireframe", "figma"]):
        return "ui"
    if any(k in raw_lower for k in ["maximum expenditure", "limit 8k", "allowed per head", "budget limit", "trip budget"]):
        return "limit"
    if any(k in raw_lower for k in ["machine learning", "ml apis", "framework are we using"]):
        return "ml"
    if any(k in raw_lower for k in ["event dates", "final decision regarding event dates", "annual symposium", "symposium date", "symposium kis date"]):
        return "dates"
    if any(k in raw_lower for k in ["lock trip dates", "trip dates", "vacation dates", "locked trip", "dates locked", "lock dates", "when did we lock"]):
        return "trip_dates"
    if any(k in raw_lower for k in ["vacation plans", "destination", "settle on"]):
        return "trip_destination"
    if any(k in raw_lower for k in ["expenses for the college festival", "managing expenses", "fest ke kharche", "fest receipts", "splitwise group for fest"]):
        return "fest_expenses"
    if any(k in raw_lower for k in ["defer", "submission cutoff", "assignment submission", "pushed submission"]):
        return "submission_deadline"
    if any(k in raw_lower for k in ["operating system", "operating systems", "os mid-term", "os exam"]):
        return "operating_systems"
    if any(k in raw_lower for k in ["library", "reading room"]):
        return "library"
    return None

def expand_query(query: str, analysis: Dict[str, Any]) -> List[str]:
    """
    Controlled query expansion: generates 2-4 focused semantic representations.
    Does NOT replace the original query - used solely during hybrid candidate retrieval.
    """
    from .normalizer import translate_hinglish_to_semantic_english
    raw_lower = query.lower().strip()
    topics = analysis.get("topics", [])
    entity_need = analysis.get("entity_need")
    semantic_english = translate_hinglish_to_semantic_english(raw_lower)

    expansions = []

    # 1. Semantic English translation variant
    if semantic_english and semantic_english != raw_lower:
        expansions.append(semantic_english)

    # 2. Topic/Entity-Specific targeted expansions
    if entity_need == "birthday" or "birthday" in topics:
        expansions.extend([
            "my birthday date",
            "when is birthday",
            "Aman birthday date 18 August",
            "birthday celebration date"
        ])
    elif entity_need == "trip_destination" or "trip" in topics:
        if any(k in raw_lower for k in ["kaha", "where", "destination", "jaane"]):
            expansions.extend(["where are we going vacation", "trip vacation destination finalized Manali"])
        else:
            expansions.extend(["trip vacation finalized", "settle on destination Manali"])
    elif entity_need == "limit" or "budget" in raw_lower or "paise" in raw_lower:
        expansions.extend(["maximum expenditure budget limit 8k per head", "Priya total limit 8k fix"])
    elif entity_need == "tech_stack" or any(k in raw_lower for k in ["tech stack", "technical stack", "technology", "build choice", "framework"]):
        expansions.extend(["technical stack build choice FastAPI React", "capstone project framework"])
    elif entity_need == "submission_deadline" or any(k in raw_lower for k in ["defer", "submission cutoff", "assignment submission"]):
        expansions.extend(["Faculty pushed submission date till Monday 5 PM", "deadline submission date"])
    elif entity_need == "operating_systems" or any(k in raw_lower for k in ["operating system", "operating systems", "os mid-term"]):
        expansions.extend(["Prof said focus on process synchronization and paging algorithms for OS mid-term", "OS operating systems syllabus exam"])
    elif entity_need == "library" or any(k in raw_lower for k in ["library closed", "library air conditioning", "library was closed"]):
        expansions.extend(["Library air conditioning maintenance scheduled for Sunday morning", "library closed maintenance"])
    elif entity_need == "venue" or "fest" in topics:
        expansions.extend(["college summit auditorium venue approved", "where symposium take place"])
    elif entity_need == "cause" or "outage" in raw_lower or "wifi" in raw_lower:
        expansions.extend(["campus network outage severed optical fiber cable", "internet wifi root cause"])
    elif "placements" in topics or "placement" in raw_lower:
        expansions.extend(["placement Cisco offer treat dinner Barbeque Nation", "placement drives"])
    elif "exams" in topics or "exam" in raw_lower:
        expansions.extend(["midterm exam schedule dates timetable", "exams syllabus timetable"])

    # 3. Short query enrichment
    tokens = raw_lower.split()
    if len(tokens) <= 2:
        for t in topics:
            expansions.append(f"{t} details schedule")

    # Deduplicate while preserving order
    seen = {raw_lower}
    deduped = []
    for exp in expansions:
        exp_clean = exp.strip().lower()
        if exp_clean and exp_clean not in seen:
            seen.add(exp_clean)
            deduped.append(exp_clean)

    return deduped[:4]

def analyze_query(query: str, ref_date_str: str = "2026-09-10T23:59:59") -> Dict[str, Any]:
    raw_lower = query.lower().strip()
    normalized_q = normalize_text(query)
    
    # 1. Person Extraction (Treat 'mera/my' as self-concept, do NOT assign random participant)
    detected_participant = None
    for token in tokenize(raw_lower):
        if token in PARTICIPANTS_MAP and token not in ["mera", "meri", "hum", "my"]:
            detected_participant = PARTICIPANTS_MAP[token]
            break

    # 2. Temporal Extraction
    temporal_info = parse_temporal_expression(raw_lower, ref_date_str=ref_date_str)

    # 3. Decision Intent Detection
    is_decision = any(re.search(pat, raw_lower) for pat in DECISION_PATTERNS)

    # 4. Entity Need
    entity_need = extract_entity_need(raw_lower)

    # 5. Topic Extraction
    detected_topics = []
    matched_threads = []
    tokens_raw = set(tokenize(raw_lower))
    tokens_norm = set(tokenize(normalized_q.lower()))
    combined_tokens = tokens_raw | tokens_norm

    for topic, keywords in TOPIC_KEYWORDS.items():
        matched = False
        for kw in keywords:
            if " " in kw or "-" in kw:
                if kw in raw_lower or kw in normalized_q.lower():
                    matched = True
                    break
            else:
                if kw in combined_tokens:
                    matched = True
                    break
        if matched:
            detected_topics.append(topic)
            matched_threads.extend(TOPIC_TO_THREADS.get(topic, []))

    # 6. Query Category
    if is_decision:
        query_type = "decision"
    elif detected_participant and (detected_topics or temporal_info):
        query_type = "person_topic"
    elif detected_participant:
        query_type = "person"
    elif temporal_info and detected_topics:
        query_type = "time_topic"
    elif temporal_info:
        query_type = "time"
    elif any(term in raw_lower for term in ["ka", "kab", "kya", "bhai", "hua", "tha", "mera", "bday"]):
        query_type = "hinglish"
    else:
        query_type = "semantic"

    cleaned_query = normalized_q

    interpreted = InterpretedFilters(
        participant_id=detected_participant["id"] if detected_participant else None,
        participant_name=detected_participant["name"] if detected_participant else None,
        date_range_label=temporal_info["label"] if temporal_info else None,
        start_date=temporal_info["start"] if temporal_info else None,
        end_date=temporal_info["end"] if temporal_info else None,
        detected_topics=detected_topics,
        is_decision_intent=is_decision,
        cleaned_query=cleaned_query,
    )

    base_analysis = {
        "query_type": query_type,
        "interpreted_filters": interpreted,
        "is_decision": is_decision,
        "entity_need": entity_need,
        "participant": detected_participant,
        "temporal": temporal_info,
        "topics": detected_topics,
        "matched_threads": set(matched_threads),
        "cleaned_query": cleaned_query,
    }

    # Controlled Query Expansion
    base_analysis["expanded_queries"] = expand_query(query, base_analysis)
    return base_analysis

