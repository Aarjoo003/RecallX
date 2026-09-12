"""
RecallX Dataset Validation Script
Verifies all formal dataset requirements:
1. Message count >= 4,000
2. Participant count >= 8
3. Date range >= 6 months
4. 3 Concrete decision threads exist
5. Evaluation set exists with 40 questions
6. At least 8 Zero-word-overlap queries exist with mathematically 0 shared tokens
7. Every evaluation question has a valid, existing expected message ID
"""

import json
import os
import sys
import re
from datetime import datetime

# Configure utf-8 stdout if supported
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.jsonl")
PARTICIPANTS_FILE = os.path.join(DATA_DIR, "participants.json")
QUESTIONS_FILE = os.path.join(DATA_DIR, "evaluation", "questions.json")

def token_overlap(s1, s2):
    t1 = set(re.findall(r"\b[a-zA-Z0-9]+\b", s1.lower()))
    t2 = set(re.findall(r"\b[a-zA-Z0-9]+\b", s2.lower()))
    return len(t1 & t2), t1 & t2

def validate():
    print("=" * 60)
    print("RECALLX CORPUS & EVALUATION SET VALIDATOR")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # Check 1: Participants
    if not os.path.exists(PARTICIPANTS_FILE):
        errors.append(f"Missing {PARTICIPANTS_FILE}")
        return False
    with open(PARTICIPANTS_FILE, "r", encoding="utf-8") as f:
        participants = json.load(f)
    print(f"[*] Participants count: {len(participants)}")
    if len(participants) < 8:
        errors.append(f"Participant count {len(participants)} is less than required 8")
        
    # Check 2: Messages
    if not os.path.exists(MESSAGES_FILE):
        errors.append(f"Missing {MESSAGES_FILE}")
        return False
        
    messages = []
    timestamps = []
    thread_ids = set()
    participant_ids = set()
    message_ids = set()
    
    with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                m = json.loads(line)
                messages.append(m)
                message_ids.add(m["id"])
                participant_ids.add(m["participant_id"])
                thread_ids.add(m["thread_id"])
                timestamps.append(datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S"))
            except Exception as e:
                errors.append(f"Line {line_num}: Malformed JSON - {e}")
                
    total_messages = len(messages)
    print(f"[*] Total messages loaded: {total_messages}")
    if total_messages < 4000:
        errors.append(f"Message count {total_messages} is less than required 4,000")
        
    # Check 3: Date range
    min_date = min(timestamps)
    max_date = max(timestamps)
    days_diff = (max_date - min_date).days
    months_diff = days_diff / 30.44
    print(f"[*] Date span: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')} ({days_diff} days / {months_diff:.1f} months)")
    if months_diff < 6.0:
        errors.append(f"Date span {months_diff:.1f} months is less than required 6 months")
        
    # Check 4: Decision threads
    required_threads = ["thread_trip_01", "thread_project_tech_02", "thread_fest_symposium_03"]
    found_threads = [t for t in required_threads if t in thread_ids]
    print(f"[*] Decision threads found: {len(found_threads)} of {len(required_threads)}")
    for t in required_threads:
        if t not in thread_ids:
            errors.append(f"Missing required decision thread: {t}")
            
    # Check 5: Evaluation questions
    if not os.path.exists(QUESTIONS_FILE):
        errors.append(f"Missing {QUESTIONS_FILE}")
        return False
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)
        
    print(f"[*] Evaluation questions count: {len(questions)}")
    if len(questions) < 40:
        errors.append(f"Question count {len(questions)} is less than required 40")
        
    # Check 6: Ground truth validity & Zero-word overlap
    zero_overlap_count = 0
    id_map = {m["id"]: m for m in messages}
    
    for q in questions:
        qid = q.get("id")
        exp_id = q.get("expected_message_id")
        if not exp_id:
            errors.append(f"Query {qid} has no expected_message_id")
            continue
        if exp_id not in id_map:
            errors.append(f"Query {qid} expected message {exp_id} does not exist in corpus!")
            continue
            
        target_msg = id_map[exp_id]
        overlap_cnt, overlap_tokens = token_overlap(q["query"], target_msg["text"])
        
        if q.get("category") == "zero_overlap":
            zero_overlap_count += 1
            if overlap_cnt > 0:
                errors.append(f"Zero-overlap violation for {qid}: shared tokens {overlap_tokens}")
                
    print(f"[*] Verified Zero-Word-Overlap queries: {zero_overlap_count} (Required >= 8)")
    if zero_overlap_count < 8:
        errors.append(f"Zero-overlap count {zero_overlap_count} is less than required 8")
        
    print("=" * 60)
    if errors:
        print(f"FAILED: {len(errors)} errors found:")
        for err in errors:
            print(f"  [FAIL] {err}")
        return False
    else:
        print("[SUCCESS] ALL VALIDATION CHECKS PASSED PERFECTLY!")
        print(f"   Corpus size: {total_messages} messages")
        print(f"   Participants: {len(participants)}")
        print(f"   Span: {months_diff:.1f} months ({days_diff} days)")
        print(f"   Evaluation queries: {len(questions)}")
        print(f"   Zero-overlap queries: {zero_overlap_count}")
        print("=" * 60)
        return True

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
