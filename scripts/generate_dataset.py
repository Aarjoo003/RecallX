"""
RecallX Synthetic Dataset Generator
Generates a realistic student group-chat corpus:
- 5,200 messages
- 10 participants
- Spanning 7 months (Feb 15, 2026 to Sep 10, 2026)
- Messy code-mixed Hinglish, typos, emojis, forwarded text, media placeholders, one-word replies
- 3 Concrete major decision threads (Trip, Tech Stack, Event Venue & Date)
- 40 Comprehensive evaluation queries with ground truth IDs & >=8 zero-word-overlap queries
"""

import json
import os
import random
import re
from datetime import datetime, timedelta

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
EVAL_DIR = os.path.join(DATA_DIR, "evaluation")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EVAL_DIR, exist_ok=True)

PARTICIPANTS = [
    {"id": "p01", "name": "Aman Sharma", "handle": "aman_s", "role": "Tech Lead & Group Admin", "color": "#6366F1", "avatar": "AS"},
    {"id": "p02", "name": "Priya Patel", "handle": "priya_p", "role": "Finance & Event Coordinator", "color": "#EC4899", "avatar": "PP"},
    {"id": "p03", "name": "Rahul Verma", "handle": "rahul_v", "role": "Logistics & Food In-Charge", "color": "#F59E0B", "avatar": "RV"},
    {"id": "p04", "name": "Sneha Rao", "handle": "sneha_r", "role": "Frontend Dev & Class Rep", "color": "#10B981", "avatar": "SR"},
    {"id": "p05", "name": "Rohan Mehta", "handle": "rohan_m", "role": "Backend Dev & Placement Rep", "color": "#3B82F6", "avatar": "RM"},
    {"id": "p06", "name": "Ananya Gupta", "handle": "ananya_g", "role": "Fest Organizer & Design Lead", "color": "#8B5CF6", "avatar": "AG"},
    {"id": "p07", "name": "Vikram Singh", "handle": "vikram_s", "role": "Sports Secretary & Transit", "color": "#EF4444", "avatar": "VS"},
    {"id": "p08", "name": "Divya Nair", "handle": "divya_n", "role": "Academics & Seminar Lead", "color": "#14B8A6", "avatar": "DN"},
    {"id": "p09", "name": "Kabir Joshi", "handle": "kabir_j", "role": "Cultural Head & Memes", "color": "#F97316", "avatar": "KJ"},
    {"id": "p10", "name": "Tanvi Malhotra", "handle": "tanvi_m", "role": "Sponsorship & Documentation", "color": "#06B6D4", "avatar": "TM"},
]

P_MAP = {p["name"].split()[0]: p for p in PARTICIPANTS}

def get_p(first_name):
    return P_MAP.get(first_name, PARTICIPANTS[0])

# Verify token overlap
def compute_token_overlap(str1, str2):
    t1 = set(re.findall(r"\b[a-zA-Z0-9]+\b", str1.lower()))
    t2 = set(re.findall(r"\b[a-zA-Z0-9]+\b", str2.lower()))
    return len(t1 & t2), t1 & t2

def main():
    print("Generating RecallX group chat corpus (5,200 messages)...")
    
    # We will build messages chronologically.
    # Start: Feb 15, 2026 09:00:00
    # End: Sep 10, 2026 23:30:00 (approx 207 days)
    # Average ~25 messages per day
    
    current_time = datetime(2026, 2, 15, 9, 0, 0)
    messages = []
    
    # Global tracking for ground-truth keys
    ground_truth_map = {}
    
    def add_msg(speaker, text, thread_id="thread_general", reply_offset=None, is_fwd=False, is_media=False, dt_minutes=None, exact_dt=None):
        nonlocal current_time
        if exact_dt:
            msg_dt = exact_dt
            current_time = max(current_time, exact_dt + timedelta(minutes=random.randint(2, 6)))
        else:
            gap = dt_minutes if dt_minutes is not None else random.randint(2, 18)
            current_time += timedelta(minutes=gap)
            # Avoid middle of the night (2:30 AM to 7:30 AM) unless night owl chat
            if current_time.hour >= 3 and current_time.hour < 7:
                current_time = current_time.replace(hour=8, minute=random.randint(5, 30))
            msg_dt = current_time
            
        msg_id = f"msg_{len(messages)+1:04d}"
        reply_to = None
        if reply_offset and len(messages) >= reply_offset:
            reply_to = messages[-reply_offset]["id"]
            
        p = get_p(speaker) if isinstance(speaker, str) else speaker
        msg_obj = {
            "id": msg_id,
            "participant_id": p["id"],
            "participant_name": p["name"],
            "timestamp": msg_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "text": text,
            "thread_id": thread_id,
            "reply_to": reply_to,
            "message_type": "forwarded" if is_fwd else ("media" if is_media else "text"),
            "is_forwarded": is_fwd,
            "is_media": is_media,
        }
        messages.append(msg_obj)
        return msg_id

    # We will curate threads anchored at specific dates across the 7-month calendar.
    # Let's define the timeline milestones:
    
    # Milestone 1: Feb 15-28 (Semester kickoff, Cultural Fest prep, Minor Project kick-off)
    # Milestone 2: March 1-25 (Midterm exam prep, fest execution, campus life)
    # Milestone 3: March 26 - April 20 (Midterms, Major Tech Stack debate - DECISION 2)
    # Milestone 4: April 21 - May 25 (IPL fever, project sprints, turf cricket)
    # Milestone 5: May 26 - June 25 (Summer internships, endterms prep, hostel life)
    # Milestone 6: June 26 - July 20 (Trip planning debate & finalization - DECISION 1)
    # Milestone 7: July 21 - August 15 (Trip photos, placement season launch, LeetCode grind)
    # Milestone 8: August 16 - August 31 (Annual Tech Symposium venue/date - DECISION 3)
    # Milestone 9: September 1 - September 10 (Hackathon, mock interviews, campus buzz)

    # Let's define the 3 concrete decision threads and key target messages carefully!
    
    # TARGET MESSAGES AND GROUND TRUTH IDENTIFIERS
    # Target 1: Trip destination decision
    # Aman: "Done bhai, Manali final. I'll book tomorrow."
    
    # Target 2: Capstone Tech Stack decision
    # Sneha: "FastAPI with React confirmed as our build choice."
    
    # Target 3: Symposium Venue decision
    # Ananya: "Auditorium slot approved, booking receipt signed."
    
    # Target 4: Expense limit
    # Priya: "Sabhi log suno, total limit 8k fix kar di."
    
    # Target 5: Slide deck compilation
    # Divya: "Divya handles PPT compilation tonight."
    
    # Target 6: Network outage root cause
    # Vikram: "Severed optical fiber cable near main hostel gate."
    
    # Target 7: Project submission postponement
    # Aman: "Faculty pushed submission date till Monday 5 PM."
    
    # Target 8: Terminal commute vehicle
    # Rahul: "Reserved two Innova cabs leaving campus 4am."
    
    # Target 9: Rahul placement celebration restaurant
    # Rohan: "Treat arranged inside Barbeque Nation Saturday evening."
    
    # Target 10: Turf arena slot reservation
    # Vikram: "Apex box cricket arena slot confirmed Sunday dawn."

    print("Generating conversational threads...")
    
    # -------------------------------------------------------------
    # PHASE 1: FEB 15 - FEB 28 (Semester 6 Opening, Minor Project)
    # -------------------------------------------------------------
    current_time = datetime(2026, 2, 15, 9, 30, 0)
    add_msg("Aman", "Good morning sabhi ko! Semester 6 registration complete hui sabki?", "thread_semester_reg")
    add_msg("Priya", "Haan maine subah hi ERP portal pe submit kar diya tha.", "thread_semester_reg", reply_offset=1)
    add_msg("Rahul", "Bhai mera elective subjects crash ho gaya tha site pe 😂", "thread_semester_reg")
    add_msg("Sneha", "Classic college server issues as always. Try in incognito tab Rahul.", "thread_semester_reg")
    add_msg("Rohan", "Works now, just refreshed. ML and Cloud Computing locked!", "thread_semester_reg")
    add_msg("Divya", "Don't forget to submit physical copy to department coordinator by 4 PM.", "thread_semester_reg")
    add_msg("Aman", "Noted Divya, let's meet near Nescafe at 3:30.", "thread_semester_reg")
    add_msg("Vikram", "Chalo, main bhi aa raha hoon canteen se.", "thread_semester_reg")
    
    # Minor project kick-off discussion (Feb 18)
    current_time = datetime(2026, 2, 18, 14, 15, 0)
    add_msg("Aman", "Minor project teams need to submit initial synopses by Friday.", "thread_minor_project")
    add_msg("Rohan", "What domains are we looking at? Autonomous drones or NLP system?", "thread_minor_project")
    add_msg("Sneha", "NLP conversation search or semantic indexing would be super cool and practical.", "thread_minor_project")
    add_msg("Priya", "Agreed, much easier to demo in 10 minutes than hardware.", "thread_minor_project")
    add_msg("Divya", "I found 3 research papers on dense passage retrieval. Sharing drive link.", "thread_minor_project")
    add_msg("Divya", "<Media omitted>", "thread_minor_project", is_media=True)
    add_msg("Kabir", "Bhai project koi bhi ho, UI clean aur slick hona chahiye.", "thread_minor_project")
    add_msg("Tanvi", "Main abstract draft kar leti hoon template me.", "thread_minor_project")

    # Campus life & hostel banter (Feb 21-25)
    current_time = datetime(2026, 2, 21, 23, 10, 0)
    add_msg("Rahul", "Hostel Block C me kisi ke paas extra Maggi packet h kya?", "thread_hostel_life")
    add_msg("Vikram", "Room 304 me aa ja, butter toast bhi hai.", "thread_hostel_life")
    add_msg("Rahul", "On my way bro! 🏃‍♂️", "thread_hostel_life")
    add_msg("Kabir", "Late night canteen roll order kar rahe ho koi?", "thread_hostel_life")
    add_msg("Aman", "Mera ek paneer roll add krna please.", "thread_hostel_life")
    add_msg("Rohan", "Same here, single egg double chicken if available.", "thread_hostel_life")
    add_msg("Priya", "Girls hostel gate is already locked, send photos of food 😭", "thread_hostel_life")

    # -------------------------------------------------------------
    # PHASE 2: MARCH 1 - MARCH 25 (Tech Fest Prep, Midterm Announcements)
    # -------------------------------------------------------------
    current_time = datetime(2026, 3, 3, 11, 45, 0)
    # Query 21 anchor: "What did we discuss in the first week of March?"
    target_q21 = add_msg("Ananya", "March 3rd meeting notes: stage decorations budget approved by faculty advisor.", "thread_fest_notes")
    ground_truth_map["q21"] = target_q21
    
    add_msg("Tanvi", "Great! Sponsorship team also got 4 brand confirmations for hoardings.", "thread_fest_notes")
    add_msg("Priya", "Keep all GST bills safely in the accounts folder.", "thread_fest_notes")
    
    # Campus network outage event (March 12) - Zero overlap Q6
    current_time = datetime(2026, 3, 12, 16, 20, 0)
    add_msg("Rohan", "Arre campus internet down h kya pure campus me?", "thread_campus_net")
    add_msg("Sneha", "Haan library wifi is completely dead. Cellular network is also jamming.", "thread_campus_net")
    add_msg("Aman", "Admin office me pucha kisi ne kya issue hua?", "thread_campus_net")
    # TARGET Q6: Zero word overlap with "What caused the campus network outage?"
    target_q6 = add_msg("Vikram", "Severed optical fiber cable near main hostel gate.", "thread_campus_net")
    ground_truth_map["q6"] = target_q6
    add_msg("Divya", "Ah excavation work chal raha tha drainage ka, unhone cut kar diya hoga.", "thread_campus_net")
    add_msg("Rahul", "Electrician team repair kar rahi h, should be back by 8 PM.", "thread_campus_net")

    # Midterm exam tips (March 22) - Query 29
    current_time = datetime(2026, 3, 22, 20, 15, 0)
    add_msg("Aman", "OS teacher ne koi important topics bataye exam ke liye?", "thread_midterm_prep")
    target_q29 = add_msg("Divya", "Prof said focus on process synchronization and paging algorithms for OS mid-term.", "thread_midterm_prep")
    ground_truth_map["q29"] = target_q29
    add_msg("Sneha", "Semaphore code dry run pakka aayega 10 marks ka.", "thread_midterm_prep")
    add_msg("Rohan", "Deadlock detection bank algorithm bhi dekh lena sabhi.", "thread_midterm_prep")

    # -------------------------------------------------------------
    # PHASE 3: MARCH 26 - APRIL 15 (DECISION 2: MAJOR TECH STACK DEBATE)
    # -------------------------------------------------------------
    # Detailed 40+ message thread on Capstone tech stack
    current_time = datetime(2026, 4, 8, 15, 0, 0)
    add_msg("Aman", "Team, major project guide assigned: Prof. Kulkarni.", "thread_project_tech_02")
    add_msg("Rohan", "He asked us to submit architecture and framework selections before April 12.", "thread_project_tech_02")
    add_msg("Sneha", "Let's decide our stack properly. Frontend React or Next.js or Vue?", "thread_project_tech_02")
    add_msg("Aman", "What about backend? Python FastAPI vs Java Spring Boot vs Go?", "thread_project_tech_02")
    add_msg("Rohan", "Spring Boot is too heavy and enterprise boilerplate for our 3-month prototype.", "thread_project_tech_02")
    add_msg("Divya", "Plus our core logic needs PyTorch and sentence-transformers for vector search.", "thread_project_tech_02")
    add_msg("Sneha", "FastAPI is way faster for async endpoints and ML inference.", "thread_project_tech_02")
    ground_truth_map["q13"] = messages[-1]["id"]  # Q13: "What framework are we using for our machine learning APIs?"
    
    add_msg("Priya", "Django has admin panel built-in, but async latency is poor.", "thread_project_tech_02")
    add_msg("Kabir", "Frontend me React with Tailwind CSS and Framer Motion will make it look modern SaaS.", "thread_project_tech_02")
    add_msg("Tanvi", "Agreed, React ecosystem is huge and everyone in team knows TypeScript.", "thread_project_tech_02")
    add_msg("Vikram", "So FastAPI backend + React Vite frontend?", "thread_project_tech_02")
    add_msg("Aman", "Wait, what about database? Postgres vs SQLite for local standalone demo?", "thread_project_tech_02")
    add_msg("Rohan", "SQLite with FTS5 is super fast, zero maintenance, runs on any student laptop!", "thread_project_tech_02")
    add_msg("Sneha", "Exactly. No Docker daemon crashes during evaluator grading.", "thread_project_tech_02")
    
    current_time = datetime(2026, 4, 10, 19, 30, 0)
    add_msg("Aman", "Guys, guide is asking for final framework confirmation today evening.", "thread_project_tech_02")
    add_msg("Rohan", "I vote FastAPI + SQLite for backend services.", "thread_project_tech_02")
    add_msg("Divya", "I vote React frontend with clean Tailwind styling.", "thread_project_tech_02")
    add_msg("Priya", "Done from my side too. Let's make it official.", "thread_project_tech_02")
    
    # TARGET Q2 (Zero word overlap): "Which technical stack was picked for the capstone?"
    # Zero word overlap with: "FastAPI with React confirmed as our build choice."
    target_q2 = add_msg("Sneha", "FastAPI with React confirmed as our build choice.", "thread_project_tech_02")
    ground_truth_map["q2"] = target_q2
    ground_truth_map["q37"] = target_q2  # Q37: "What tech stack did we agree to use?"
    
    # Query 23: "What did we plan around mid-April?"
    current_time = datetime(2026, 4, 11, 10, 0, 0)
    target_q23 = add_msg("Sneha", "April 10 tech review: team agreed on React frontend architecture.", "thread_project_tech_02")
    ground_truth_map["q23"] = target_q23

    # Q31: "What did we discuss about exams in April?"
    current_time = datetime(2026, 4, 15, 12, 10, 0)
    target_q31 = add_msg("Sneha", "April 15 exam schedule published: DBMS exam on April 22, Networks on April 25.", "thread_exam_schedule")
    ground_truth_map["q31"] = target_q31
    add_msg("Rahul", "Bhai back to back exams h dono! Ek din ka bhi gap nahi diya.", "thread_exam_schedule")
    add_msg("Divya", "Networks syllabus is huge, especially subnetting and TCP sliding window.", "thread_exam_schedule")

    # Q7: "At what moment did the professor declare the project deadline extended?" (Zero overlap)
    # Target: "Faculty pushed submission date till Monday 5 PM."
    current_time = datetime(2026, 4, 20, 17, 45, 0)
    add_msg("Rohan", "Guys portal closes at 6 PM! Still fixing CORS error in API.", "thread_deadline_rush")
    add_msg("Sneha", "Wait, did anyone email HOD for extension?", "thread_deadline_rush")
    target_q7 = add_msg("Aman", "Faculty pushed submission date till Monday 5 PM.", "thread_deadline_rush")
    ground_truth_map["q7"] = target_q7
    add_msg("Rahul", "Bhagwan ka shukr h! 😭🙏 breathing room mil gaya.", "thread_deadline_rush")
    add_msg("Priya", "Weekend pe acche se polish kar lete hain phir report.", "thread_deadline_rush")

    # -------------------------------------------------------------
    # PHASE 4: APRIL 21 - MAY 25 (Sports, Turf, Minor Project Review)
    # -------------------------------------------------------------
    # Q10 (Zero overlap): "What sports facility did the group reserve for the weekend tournament?"
    # Target: "Apex box cricket arena slot confirmed Sunday dawn."
    current_time = datetime(2026, 4, 25, 18, 30, 0)
    add_msg("Vikram", "Sunday cricket match fix karein? Weather clear hai.", "thread_cricket_match")
    add_msg("Kabir", "Yes! 8v8 box cricket match, losers pay canteen chai-samosa.", "thread_cricket_match")
    add_msg("Rohan", "Which turf is open early morning? Afternoon is too hot.", "thread_cricket_match")
    target_q10 = add_msg("Vikram", "Apex box cricket arena slot confirmed Sunday dawn.", "thread_cricket_match")
    ground_truth_map["q10"] = target_q10
    add_msg("Aman", "Subah 6 baje wake up call sabko lagana Vikram.", "thread_cricket_match")
    add_msg("Rahul", "Main bat aur new Cosco balls le aaunga.", "thread_cricket_match")

    # Q20: "What did Vikram say about the turf booking?"
    current_time = datetime(2026, 5, 2, 17, 0, 0)
    target_q20 = add_msg("Vikram", "Box cricket turf booked at Sector 62 from 7 to 9 PM, bring studs.", "thread_cricket_match")
    ground_truth_map["q20"] = target_q20

    # Q34: "What did we discuss about project submission in May?"
    current_time = datetime(2026, 5, 18, 11, 20, 0)
    target_q34 = add_msg("Aman", "May 18 minor project demo: report spiral binding and IEEE format mandatory.", "thread_minor_project_eval")
    ground_truth_map["q34"] = target_q34
    add_msg("Divya", "I have IEEE LaTeX template ready. Will share git repo.", "thread_minor_project_eval")
    add_msg("Sneha", "Figma wireframes for dashboard and landing page are updated in drive.", "thread_minor_project_eval")
    ground_truth_map["q18"] = messages[-1]["id"]  # Q18: "What did Sneha say about the UI design?"

    # -------------------------------------------------------------
    # PHASE 5: MAY 26 - JUNE 25 (Internships, Library & Endterm exams)
    # -------------------------------------------------------------
    # Q28: "What did Rohan say about the internship stipend?"
    current_time = datetime(2026, 5, 28, 14, 0, 0)
    add_msg("Rohan", "Guys offer letter aa gaya finally! 🎉", "thread_internships")
    target_q28 = add_msg("Rohan", "Bangalore startup offered 45k monthly stipend for 2 months internship.", "thread_internships")
    ground_truth_map["q28"] = target_q28
    add_msg("Priya", "Party banti h Rohan bhai! Big congratulations! 🥳", "thread_internships")
    add_msg("Aman", "Super proud of you bro! Role kya h?", "thread_internships")
    add_msg("Rohan", "Backend engineering, working on distributed caching and Kafka.", "thread_internships")

    # Q15: "What was the reason the library was closed on Sunday?"
    current_time = datetime(2026, 6, 7, 10, 15, 0)
    add_msg("Tanvi", "Is central reading room open today? Wanted to study peacefully.", "thread_library_notice")
    target_q15 = add_msg("Divya", "Library air conditioning maintenance scheduled for Sunday morning.", "thread_library_notice")
    ground_truth_map["q15"] = target_q15
    add_msg("Tanvi", "Oh okay, SAC study hall chalte hain phir.", "thread_library_notice")

    # -------------------------------------------------------------
    # PHASE 6: JUNE 26 - JULY 20 (DECISION 1: THE BIG TRIP PLANNING)
    # -------------------------------------------------------------
    # Rich multi-day debate: Manali vs Goa vs Rishikesh
    current_time = datetime(2026, 7, 2, 20, 0, 0)
    add_msg("Kabir", "Semesters 6 is officially over! We desperately need a group trip before placements start.", "thread_trip_01")
    add_msg("Rahul", "100% agreed! Either Goa beach or Himachal mountains.", "thread_trip_01")
    add_msg("Priya", "Goa in July will be heavy monsoons, beaches might be closed.", "thread_trip_01")
    add_msg("Vikram", "Rishikesh river rafting is also shut during rains.", "thread_trip_01")
    add_msg("Sneha", "Manali weather looks pleasant! Old Manali, Rohtang pass, Solang valley.", "thread_trip_01")
    add_msg("Aman", "Let's check budget and dates first before dreaming.", "thread_trip_01")
    
    current_time = datetime(2026, 7, 5, 21, 30, 0)
    add_msg("Priya", "Total estimated budget per head for Manali trip comes to 7500 including travel.", "thread_trip_01")
    ground_truth_map["q26"] = messages[-1]["id"]  # Q26: "What did Priya say about the budget?"
    
    # Q4 (Zero overlap): "What is the maximum expenditure allowed per head?"
    # Target: "Sabhi log suno, total limit 8k fix kar di."
    current_time = datetime(2026, 7, 6, 12, 40, 0)
    add_msg("Rahul", "Kuch hotels 10k quote kar rahe hain package ka.", "thread_trip_01")
    target_q4 = add_msg("Priya", "Sabhi log suno, total limit 8k fix kar di.", "thread_trip_01")
    ground_truth_map["q4"] = target_q4
    add_msg("Aman", "Understood Priya, no hotel above 2k per room per night.", "thread_trip_01")

    # Q17: "What did Rahul say about the train tickets?"
    current_time = datetime(2026, 7, 8, 16, 10, 0)
    add_msg("Vikram", "Train availability check kiya Delhi to Chandigarh?", "thread_trip_01")
    target_q17 = add_msg("Rahul", "Vande Bharat tickets available for July 14 morning, Tatkal not needed.", "thread_trip_01")
    ground_truth_map["q17"] = target_q17
    add_msg("Aman", "Perfect, from Chandigarh we can take private traveller cab.", "thread_trip_01")

    # Q8 (Zero overlap): "Which vehicle arrangement did we confirm for commuting to the train terminal?"
    # Target: "Reserved two Innova cabs leaving campus 4am."
    current_time = datetime(2026, 7, 10, 18, 0, 0)
    add_msg("Sneha", "Campus se railway station subah 4 AM kaise pahunchenge? Auto nahi milte us waqt.", "thread_trip_01")
    target_q8 = add_msg("Rahul", "Reserved two Innova cabs leaving campus 4am.", "thread_trip_01")
    ground_truth_map["q8"] = target_q8
    add_msg("Tanvi", "Super, driver contact details spreadsheet me daal do.", "thread_trip_01")

    # Q32: "What did we discuss about the trip in July?"
    current_time = datetime(2026, 7, 12, 14, 0, 0)
    target_q32 = add_msg("Priya", "July 12 itinerary draft: Day 1 Solang valley, Day 2 Kasol trek, Day 3 local market.", "thread_trip_01")
    ground_truth_map["q32"] = target_q32
    add_msg("Kabir", "Kasol cafe culture is amazing, heard good things about German Bakery.", "thread_trip_01")

    # Q12: "Where did we decide to stay during the trip?"
    current_time = datetime(2026, 7, 13, 19, 20, 0)
    target_q12 = add_msg("Rahul", "Found a riverside cottage in Old Manali with bonfire, booked 3 rooms.", "thread_trip_01")
    ground_truth_map["q12"] = target_q12
    add_msg("Sneha", "Photos look stunning! Wooden balcony facing mountains 🏔️", "thread_trip_01")

    # THE CORE DECISION 1 (TARGET Q1, Q11, Q22, Q36, Q39, Q40):
    # Query 1 (Zero-word overlap): "When did we finally settle on the destination?"
    # Query 11: "When did we finalize our vacation plans?"
    # Query 22: "What happened on July 14?"
    # Query 36: "What was the final decision on the trip destination?"
    # Query 39 (Hinglish): "trip ka final decision kab hua?"
    # Query 40 (Typo): "manali kab fnl hua tha?"
    # Target text: "Done bhai, Manali final. I'll book tomorrow."
    current_time = datetime(2026, 7, 14, 21, 42, 0)
    add_msg("Rahul", "Goa tickets cancel kar doon pakka?", "thread_trip_01")
    add_msg("Priya", "Haan sabhi ne vote de diya group poll me.", "thread_trip_01")
    add_msg("Sneha", "14-18 dates are locked from my side too.", "thread_trip_01")
    target_q1 = add_msg("Aman", "Done bhai, Manali final. I'll book tomorrow.", "thread_trip_01")
    ground_truth_map["q1"] = target_q1
    ground_truth_map["q11"] = target_q1
    ground_truth_map["q22"] = target_q1
    ground_truth_map["q36"] = target_q1
    ground_truth_map["q39"] = target_q1
    ground_truth_map["q40"] = target_q1
    add_msg("Rahul", "I'll check the hotels then, sleep well guys! 🌲", "thread_trip_01")

    # -------------------------------------------------------------
    # PHASE 7: JULY 21 - AUGUST 15 (Placements & Rahul's Celebration)
    # -------------------------------------------------------------
    # Q27: "What did Aman say about the project repository?"
    current_time = datetime(2026, 7, 26, 11, 0, 0)
    target_q27 = add_msg("Aman", "Created the GitHub organization and added main branch protection rules.", "thread_project_git")
    ground_truth_map["q27"] = target_q27
    add_msg("Sneha", "Cloned repo. Setting up Vite frontend template now.", "thread_project_git")
    add_msg("Rohan", "Added FastAPI skeleton with Poetry and pre-commit hooks.", "thread_project_git")

    # Q33: "What did we discuss about placements in August?"
    current_time = datetime(2026, 8, 5, 10, 0, 0)
    target_q33 = add_msg("Rohan", "August 5 placement briefing: Oracle and Cisco campus drives scheduled next week.", "thread_placement_drives")
    ground_truth_map["q33"] = target_q33
    add_msg("Divya", "Eligibility criteria is 7.5 CGPA with zero active backlogs.", "thread_placement_drives")
    add_msg("Aman", "Revise core CS subjects: OS, DBMS, OOP, and CN.", "thread_placement_drives")

    # Q19: "What did Rohan say about the placement coding test?"
    current_time = datetime(2026, 8, 10, 16, 45, 0)
    target_q19 = add_msg("Rohan", "The coding test had 3 questions: dynamic programming, graphs, and SQL.", "thread_placement_drives")
    ground_truth_map["q19"] = target_q19
    add_msg("Rahul", "Graph question was standard Dijkstra right?", "thread_placement_drives")
    add_msg("Rohan", "Yes, finding shortest path in weighted network with delay penalties.", "thread_placement_drives")

    # Q9 (Zero overlap): "Which restaurant was selected to celebrate Rahul's placement offer?"
    # Target: "Treat arranged inside Barbeque Nation Saturday evening."
    current_time = datetime(2026, 8, 14, 18, 10, 0)
    add_msg("Rahul", "Brothers and sisters, Cisco offer letter received!! 😭🎉🎉", "thread_rahul_party")
    add_msg("Aman", "LET'S GOOOOOO!! Party time Rahul! 🥳🥂", "thread_rahul_party")
    add_msg("Sneha", "Treat kidhar de raha h jaldi bata!", "thread_rahul_party")
    target_q9 = add_msg("Rohan", "Treat arranged inside Barbeque Nation Saturday evening.", "thread_rahul_party")
    ground_truth_map["q9"] = target_q9
    add_msg("Kabir", "Buffet tables book kar lo advance me, weekend rush rehta hai.", "thread_rahul_party")
    add_msg("Tanvi", "Confirm RSVP: 10 people at 7:30 PM.", "thread_rahul_party")

    # -------------------------------------------------------------
    # PHASE 8: AUGUST 16 - AUGUST 31 (DECISION 3: ANNUAL SYMPOSIUM)
    # -------------------------------------------------------------
    # Q14: "How are we managing expenses for the college festival?"
    current_time = datetime(2026, 8, 18, 11, 30, 0)
    target_q14 = add_msg("Priya", "Created a dedicated Splitwise group for fest receipts, upload all bills there.", "thread_fest_symposium_03")
    ground_truth_map["q14"] = target_q14
    add_msg("Ananya", "Please keep photos of physical vouchers too.", "thread_fest_symposium_03")

    # Q16: "What did Priya say about the registration fee?"
    current_time = datetime(2026, 8, 20, 15, 20, 0)
    target_q16 = add_msg("Priya", "Symposium registration fee will be 250 rupees per team including lunch coupons.", "thread_fest_symposium_03")
    ground_truth_map["q16"] = target_q16
    add_msg("Tanvi", "Posters need to be published on Unstop and college portal tonight.", "thread_fest_symposium_03")

    # DECISION 3: Venue & Date Debate for Symposium
    # Target Q3 (Zero overlap): "Where will the grand college summit take place?"
    # Target: "Auditorium slot approved, booking receipt signed."
    # Also Target Q35: "What did we finally decide about the venue?"
    # Target Q38: "What was the final decision regarding event dates?"
    current_time = datetime(2026, 8, 22, 14, 0, 0)
    add_msg("Ananya", "Meeting with Dean of Student Affairs finished.", "thread_fest_symposium_03")
    add_msg("Aman", "Did he allow the Main Auditorium or are we stuck with SAC Hall?", "thread_fest_symposium_03")
    add_msg("Rahul", "SAC Hall is too cramped for 400 attendees.", "thread_fest_symposium_03")
    target_q3 = add_msg("Ananya", "Auditorium slot approved, booking receipt signed.", "thread_fest_symposium_03")
    ground_truth_map["q3"] = target_q3
    ground_truth_map["q35"] = target_q3
    
    current_time = datetime(2026, 8, 22, 16, 45, 0)
    add_msg("Tanvi", "What about the date? September 12 or September 18?", "thread_fest_symposium_03")
    target_q38 = add_msg("Priya", "September 18 finalized for annual symposium, circular released.", "thread_fest_symposium_03")
    ground_truth_map["q38"] = target_q38
    add_msg("Ananya", "Perfect, exactly 4 weeks to execute everything.", "thread_fest_symposium_03")

    # Q30: "What did Kabir say about the fest music system?"
    current_time = datetime(2026, 8, 25, 17, 30, 0)
    target_q30 = add_msg("Kabir", "DJ setup and 4 JBL line array speakers reserved for cultural night.", "thread_fest_symposium_03")
    ground_truth_map["q30"] = target_q30
    add_msg("Vikram", "Bass should be heavy for the afterparty! 🔊", "thread_fest_symposium_03")

    # Q24: "What was announced in late August?"
    current_time = datetime(2026, 8, 28, 12, 15, 0)
    target_q24 = add_msg("Tanvi", "August 28 announcement: sponsorship partner confirmed with 50k grant.", "thread_fest_symposium_03")
    ground_truth_map["q24"] = target_q24
    add_msg("Priya", "This covers stage lighting and guest gifts comfortably!", "thread_fest_symposium_03")

    # Q5 (Zero overlap): "Who accepted responsibility for creating the slide presentation?"
    # Target: "Divya handles PPT compilation tonight."
    current_time = datetime(2026, 8, 30, 20, 45, 0)
    add_msg("Aman", "Tomorrow 9 AM is department review of event plan with Director.", "thread_fest_symposium_03")
    add_msg("Sneha", "Who is finishing the final presentation deck?", "thread_fest_symposium_03")
    target_q5 = add_msg("Divya", "Divya handles PPT compilation tonight.", "thread_fest_symposium_03")
    ground_truth_map["q5"] = target_q5
    add_msg("Aman", "Awesome, send pdf preview when done Divya.", "thread_fest_symposium_03")

    # -------------------------------------------------------------
    # PHASE 9: SEPTEMBER 1 - SEPTEMBER 10 (Hackathon, Final Review)
    # -------------------------------------------------------------
    current_time = datetime(2026, 9, 2, 10, 0, 0)
    add_msg("Rohan", "Smart India Hackathon internal shortlist just dropped on board.", "thread_hackathon_sih")
    add_msg("Sneha", "Did team RecallX qualify for round 2?", "thread_hackathon_sih")
    add_msg("Aman", "YES! Ranked #3 across institute in software category! 🚀", "thread_hackathon_sih")
    add_msg("Divya", "Fantastic news! Mentors feedback said search relevance was impressive.", "thread_hackathon_sih")
    
    # Q25: "What did we decide yesterday?" (relative time test with fixed date reference)
    current_time = datetime(2026, 9, 8, 19, 0, 0)
    target_q25 = add_msg("Kabir", "Yesterday's plan confirmed, team dinner at Haveli tonight.", "thread_team_dinner")
    ground_truth_map["q25"] = target_q25
    add_msg("Rahul", "Table reserved for 8:30 PM, paneer tikka on Kabir!", "thread_team_dinner")
    add_msg("Aman", "See everyone at main campus circle at 8:15.", "thread_team_dinner")

    # Now, we have placed our anchor threads and specific targets.
    # To reach 5,200 messages with high variety, realism, and conversational flow,
    # let's generate realistic conversational clusters across the calendar!
    
    print(f"Generated {len(messages)} milestone messages. Now scaling corpus to 5,200 messages...")
    
    # Realism pools:
    casual_greetings = [
        "Good morning sabhi ko! Aaj 10 am class attend kar rahe ho?",
        "Subah subah itni baarish ho rahi h, kaun jayega lecture me 😴",
        "Proxy lagwa dena koi please roll no 24 ki!",
        "Prof attendance portal live kar chuka h, jaldi aao class",
        "Late night coding sessions are ruining my sleep cycle lol",
        "Coffee break near gate 2 in 15 mins?",
        "Chalo Nescafe chalte hain, brain recharge needed",
        "Assignment ki deadline extend karwayi kya CR ne?",
        "Aaj mess me kya bana h? Rajma chawal ya khichdi?",
        "Sunday match summary: 4 wickets in 2 overs, pure masterclass!",
        "Gym session evening 6 PM anyone joining?",
        "Lab manual sign karwa lo viva se pehle sabhi",
    ]
    
    hinglish_chatter = [
        "arre yaar ye bug fix hone ka naam nahi le raha",
        "bhai ek baar syntax dekhna console me",
        "stack overflow pe bhi solution outdated h iska",
        "done bhai, test cases pass ho gaye",
        "kaun kaun aa raha h Sham ke session me?",
        "haan main 10 min me reach kar raha hoon",
        "budget dekh ke order karna bhai sabhi",
        "splitwise pe bill add kar diya h check karlo",
        "prof ne bola internal marks Monday display honge",
        "sahi me? Attendance short toh nahi h meri?",
        "library chalte h Shaam ko, viva preparation karni h",
        "hostel wifi switch off karke on karo, chal jayega",
        "notes drive folder ka access request accept karna",
        "bhai kal morning 8 AM practical exam h yaad h na?",
        "haan admit card print nikalwa liya maine stationery se",
        "Zomato promo code work kar raha h 40% off wala!",
    ]
    
    one_word_replies = [
        "done", "cool", "haan", "ok", "yes", "sahi", "pakka", "chal", "nahi", "wait", "same", "great", "nice", "yep", "sure", "confirmed", "100%", "done bro"
    ]
    
    typo_variants = [
        "kal milte h clg me",
        "projct repo update krdi maine",
        "thnks bro send krdio",
        "prso submission h yaad rkhna",
        "assignmnt pdf bhej do plzzz",
        "portal pr login ni ho rha",
        "kahan ho sabhi log?",
        "canteen me aao jaldi",
        "attendnce short ho jayegi meri aise toh",
        "sir se baat krte h kal",
        "presentation ready h kya?",
        "code push krdia branch pe",
    ]
    
    forwarded_notices = [
        "Forwarded: NOTICE: Mid-semester grade review meeting scheduled for Friday 3 PM in Room 402.",
        "Forwarded: Training & Placement Cell: Google & Microsoft hackathon pre-registration open for pre-final year.",
        "Forwarded: Important: University library will remain open 24x7 during exam week starting May 10.",
        "Forwarded: Sports Council: Inter-college basketball trials on Thursday at Sports Complex.",
        "Forwarded: Hostellers: Maintenance shutdown for solar water heaters on Wednesday 9am-1pm.",
        "Forwarded: Academic Section: Fee receipt submission deadline extended till end of month without fine.",
    ]
    
    media_messages = [
        "<Media omitted>",
        "IMG_20260315_WA0023.jpg (file attached)",
        "IMG_20260421_WA0088.jpg (file attached)",
        "IMG_20260715_WA0112.jpg (file attached)",
        "audio_note_0320.opus (voice message, 0:34)",
        "audio_note_0612.opus (voice message, 1:12)",
        "Doc_Lab_Manual_CS601.pdf (file attached)",
        "Lecture_Slides_Week7.pdf (file attached)",
    ]

    thread_topics = [
        "thread_daily_chatter_01", "thread_canteen_food_02", "thread_hostel_misc_03",
        "thread_weekend_hangout_04", "thread_study_room_05", "thread_general_banter_06"
    ]
    
    # We want to interleave messages smoothly between Feb 15 and Sep 10
    # Let's create realistic daily conversation bursts
    total_target = 5200
    needed = total_target - len(messages)
    
    # Create timestamps distributed across the range
    start_sec = datetime(2026, 2, 15, 8, 0, 0).timestamp()
    end_sec = datetime(2026, 9, 10, 23, 0, 0).timestamp()
    
    # Pre-generate burst timestamps
    extra_timestamps = []
    for _ in range(needed):
        t_rand = random.uniform(start_sec, end_sec)
        dt = datetime.fromtimestamp(t_rand)
        # Weight towards daytime and evening (8 AM to 1 AM)
        if dt.hour in [3, 4, 5, 6]:
            dt = dt.replace(hour=random.choice([9, 14, 19, 21, 22]))
        extra_timestamps.append(dt)
        
    extra_timestamps.sort()
    
    extra_messages = []
    for dt in extra_timestamps:
        p = random.choice(PARTICIPANTS)
        dice = random.random()
        
        thread = random.choice(thread_topics)
        is_fwd = False
        is_media = False
        
        if dice < 0.35:
            text = random.choice(hinglish_chatter)
        elif dice < 0.60:
            text = random.choice(casual_greetings)
        elif dice < 0.75:
            text = random.choice(one_word_replies)
        elif dice < 0.88:
            text = random.choice(typo_variants)
        elif dice < 0.94:
            text = random.choice(media_messages)
            is_media = True
        else:
            text = random.choice(forwarded_notices)
            is_fwd = True
            
        extra_messages.append({
            "participant": p,
            "text": text,
            "thread_id": thread,
            "dt": dt,
            "is_forwarded": is_fwd,
            "is_media": is_media,
        })
        
    # Combine original milestone messages and extra messages, then sort strictly by timestamp!
    # Convert milestone messages to intermediate structure
    all_raw = []
    for m in messages:
        dt = datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S")
        all_raw.append({
            "participant_id": m["participant_id"],
            "participant_name": m["participant_name"],
            "text": m["text"],
            "thread_id": m["thread_id"],
            "dt": dt,
            "is_forwarded": m["is_forwarded"],
            "is_media": m["is_media"],
            "old_id": m["id"],
        })
        
    for em in extra_messages:
        all_raw.append({
            "participant_id": em["participant"]["id"],
            "participant_name": em["participant"]["name"],
            "text": em["text"],
            "thread_id": em["thread_id"],
            "dt": em["dt"],
            "is_forwarded": em["is_forwarded"],
            "is_media": em["is_media"],
            "old_id": None,
        })
        
    all_raw.sort(key=lambda x: x["dt"])
    
    # Assign final sequential IDs: msg_0001 to msg_5200
    final_messages = []
    old_to_new_id = {}
    
    for idx, item in enumerate(all_raw, 1):
        mid = f"msg_{idx:04d}"
        if item["old_id"]:
            old_to_new_id[item["old_id"]] = mid
            
        mtype = "forwarded" if item["is_forwarded"] else ("media" if item["is_media"] else "text")
        
        # Decision indicator heuristic
        t_lower = item["text"].lower()
        is_decision = False
        decision_keywords = ["final", "confirmed", "decided", "approved", "booked", "locked", "settled", "fix kar"]
        if any(k in t_lower for k in decision_keywords) and not item["is_media"]:
            is_decision = True
            
        final_messages.append({
            "id": mid,
            "participant_id": item["participant_id"],
            "participant_name": item["participant_name"],
            "timestamp": item["dt"].strftime("%Y-%m-%dT%H:%M:%S"),
            "text": item["text"],
            "thread_id": item["thread_id"],
            "reply_to": None,
            "message_type": mtype,
            "is_forwarded": item["is_forwarded"],
            "is_media": item["is_media"],
            "is_decision": is_decision,
        })
        
    print(f"Total compiled messages: {len(final_messages)}")
    
    # Update ground truth mappings with new IDs
    final_ground_truth = {}
    for q_key, old_id in ground_truth_map.items():
        new_id = old_to_new_id.get(old_id)
        final_ground_truth[q_key] = new_id
        
    # Write messages.jsonl
    messages_path = os.path.join(DATA_DIR, "messages.jsonl")
    with open(messages_path, "w", encoding="utf-8") as f:
        for m in final_messages:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    print(f"Saved messages to {messages_path}")

    # Build the 40 evaluation queries and verify them
    id_lookup = {m["id"]: m for m in final_messages}
    
    eval_queries = [
        # --- ZERO-WORD-OVERLAP (10 queries, requirement was >= 8) ---
        {
            "id": "eval_01",
            "category": "zero_overlap",
            "query": "When did we finally settle on the destination?",
            "expected_message_id": final_ground_truth["q1"],
            "description": "Zero-word overlap query asking about vacation destination confirmation",
            "expected_participant": "Aman Sharma"
        },
        {
            "id": "eval_02",
            "category": "zero_overlap",
            "query": "Which technical stack was picked for the capstone?",
            "expected_message_id": final_ground_truth["q2"],
            "description": "Zero-word overlap query on capstone technology choice",
            "expected_participant": "Sneha Rao"
        },
        {
            "id": "eval_03",
            "category": "zero_overlap",
            "query": "Where will the grand college summit take place?",
            "expected_message_id": final_ground_truth["q3"],
            "description": "Zero-word overlap query on symposium venue approval",
            "expected_participant": "Ananya Gupta"
        },
        {
            "id": "eval_04",
            "category": "zero_overlap",
            "query": "What is the maximum expenditure allowed per head?",
            "expected_message_id": final_ground_truth["q4"],
            "description": "Zero-word overlap query on trip financial ceiling",
            "expected_participant": "Priya Patel"
        },
        {
            "id": "eval_05",
            "category": "zero_overlap",
            "query": "Who accepted responsibility for creating the slide presentation?",
            "expected_message_id": final_ground_truth["q5"],
            "description": "Zero-word overlap query on presentation deck owner",
            "expected_participant": "Divya Nair"
        },
        {
            "id": "eval_06",
            "category": "zero_overlap",
            "query": "What caused the campus network outage?",
            "expected_message_id": final_ground_truth["q6"],
            "description": "Zero-word overlap query on internet fiber cut",
            "expected_participant": "Vikram Singh"
        },
        {
            "id": "eval_07",
            "category": "zero_overlap",
            "query": "At what moment did the professor declare the project deadline extended?",
            "expected_message_id": final_ground_truth["q7"],
            "description": "Zero-word overlap query on deadline postponement",
            "expected_participant": "Aman Sharma"
        },
        {
            "id": "eval_08",
            "category": "zero_overlap",
            "query": "Which vehicle arrangement did we confirm for commuting to the train terminal?",
            "expected_message_id": final_ground_truth["q8"],
            "description": "Zero-word overlap query on morning taxi cab booking",
            "expected_participant": "Rahul Verma"
        },
        {
            "id": "eval_09",
            "category": "zero_overlap",
            "query": "Which restaurant was selected to celebrate Rahul's placement offer?",
            "expected_message_id": final_ground_truth["q9"],
            "description": "Zero-word overlap query on placement treat dinner venue",
            "expected_participant": "Rohan Mehta"
        },
        {
            "id": "eval_10",
            "category": "zero_overlap",
            "query": "What sports facility did the group reserve for the weekend tournament?",
            "expected_message_id": final_ground_truth["q10"],
            "description": "Zero-word overlap query on cricket box arena booking",
            "expected_participant": "Vikram Singh"
        },

        # --- SEMANTIC / MEANING (5 queries) ---
        {
            "id": "eval_11",
            "category": "semantic",
            "query": "When did we finalize our vacation plans?",
            "expected_message_id": final_ground_truth["q11"],
            "description": "Semantic query matching vacation conclusion",
            "expected_participant": "Aman Sharma"
        },
        {
            "id": "eval_12",
            "category": "semantic",
            "query": "Where did we decide to stay during the trip?",
            "expected_message_id": final_ground_truth["q12"],
            "description": "Semantic query on trip cottage accommodation",
            "expected_participant": "Rahul Verma"
        },
        {
            "id": "eval_13",
            "category": "semantic",
            "query": "What framework are we using for our machine learning APIs?",
            "expected_message_id": final_ground_truth["q13"],
            "description": "Semantic query on ML endpoint framework",
            "expected_participant": "Sneha Rao"
        },
        {
            "id": "eval_14",
            "category": "semantic",
            "query": "How are we managing expenses for the college festival?",
            "expected_message_id": final_ground_truth["q14"],
            "description": "Semantic query on festival accounting and Splitwise",
            "expected_participant": "Priya Patel"
        },
        {
            "id": "eval_15",
            "category": "semantic",
            "query": "What was the reason the library was closed on Sunday?",
            "expected_message_id": final_ground_truth["q15"],
            "description": "Semantic query on library maintenance closure",
            "expected_participant": "Divya Nair"
        },

        # --- PERSON-BASED (5 queries) ---
        {
            "id": "eval_16",
            "category": "person",
            "query": "What did Priya say about the registration fee?",
            "expected_message_id": final_ground_truth["q16"],
            "description": "Person entity search on Priya's fee announcement",
            "expected_participant": "Priya Patel"
        },
        {
            "id": "eval_17",
            "category": "person",
            "query": "What did Rahul say about the train tickets?",
            "expected_message_id": final_ground_truth["q17"],
            "description": "Person entity search on Rahul's Vande Bharat check",
            "expected_participant": "Rahul Verma"
        },
        {
            "id": "eval_18",
            "category": "person",
            "query": "What did Sneha say about the UI design?",
            "expected_message_id": final_ground_truth["q18"],
            "description": "Person entity search on Sneha's Figma wireframes",
            "expected_participant": "Sneha Rao"
        },
        {
            "id": "eval_19",
            "category": "person",
            "query": "What did Rohan say about the placement coding test?",
            "expected_message_id": final_ground_truth["q19"],
            "description": "Person entity search on Rohan's coding assessment questions",
            "expected_participant": "Rohan Mehta"
        },
        {
            "id": "eval_20",
            "category": "person",
            "query": "What did Vikram say about the turf booking?",
            "expected_message_id": final_ground_truth["q20"],
            "description": "Person entity search on Vikram's turf slot timings",
            "expected_participant": "Vikram Singh"
        },

        # --- TIME-BASED (5 queries) ---
        {
            "id": "eval_21",
            "category": "time",
            "query": "What did we discuss in the first week of March?",
            "expected_message_id": final_ground_truth["q21"],
            "description": "Temporal search targeting March 1-7 window",
            "expected_participant": "Ananya Gupta"
        },
        {
            "id": "eval_22",
            "category": "time",
            "query": "What happened on July 14?",
            "expected_message_id": final_ground_truth["q22"],
            "description": "Exact day temporal search for July 14 decision",
            "expected_participant": "Aman Sharma"
        },
        {
            "id": "eval_23",
            "category": "time",
            "query": "What did we plan around mid-April?",
            "expected_message_id": final_ground_truth["q23"],
            "description": "Mid-month temporal search for mid-April review",
            "expected_participant": "Sneha Rao"
        },
        {
            "id": "eval_24",
            "category": "time",
            "query": "What was announced in late August?",
            "expected_message_id": final_ground_truth["q24"],
            "description": "Late-month temporal search for August 28 announcement",
            "expected_participant": "Tanvi Malhotra"
        },
        {
            "id": "eval_25",
            "category": "time",
            "query": "What did we decide about dinner yesterday?",
            "expected_message_id": final_ground_truth["q25"],
            "description": "Relative time search for team dinner confirmation",
            "expected_participant": "Kabir Joshi"
        },

        # --- PERSON + TOPIC (5 queries) ---
        {
            "id": "eval_26",
            "category": "person_topic",
            "query": "What did Priya say about the budget?",
            "expected_message_id": final_ground_truth["q26"],
            "description": "Joint person + topic search on Priya and trip budget",
            "expected_participant": "Priya Patel"
        },
        {
            "id": "eval_27",
            "category": "person_topic",
            "query": "What did Aman say about the project repository?",
            "expected_message_id": final_ground_truth["q27"],
            "description": "Joint person + topic search on Aman and GitHub repo setup",
            "expected_participant": "Aman Sharma"
        },
        {
            "id": "eval_28",
            "category": "person_topic",
            "query": "What did Rohan say about the internship stipend?",
            "expected_message_id": final_ground_truth["q28"],
            "description": "Joint person + topic search on Rohan and 45k stipend offer",
            "expected_participant": "Rohan Mehta"
        },
        {
            "id": "eval_29",
            "category": "person_topic",
            "query": "What did Divya say about the operating systems exam?",
            "expected_message_id": final_ground_truth["q29"],
            "description": "Joint person + topic search on Divya and OS exam topics",
            "expected_participant": "Divya Nair"
        },
        {
            "id": "eval_30",
            "category": "person_topic",
            "query": "What did Kabir say about the fest music system?",
            "expected_message_id": final_ground_truth["q30"],
            "description": "Joint person + topic search on Kabir and JBL sound equipment",
            "expected_participant": "Kabir Joshi"
        },

        # --- TIME + TOPIC (4 queries) ---
        {
            "id": "eval_31",
            "category": "time_topic",
            "query": "What did we discuss about exams in April?",
            "expected_message_id": final_ground_truth["q31"],
            "description": "Time + topic search on April exam schedule",
            "expected_participant": "Sneha Rao"
        },
        {
            "id": "eval_32",
            "category": "time_topic",
            "query": "What did we discuss about the trip in July?",
            "expected_message_id": final_ground_truth["q32"],
            "description": "Time + topic search on July trip itinerary",
            "expected_participant": "Priya Patel"
        },
        {
            "id": "eval_33",
            "category": "time_topic",
            "query": "What did we discuss about placements in August?",
            "expected_message_id": final_ground_truth["q33"],
            "description": "Time + topic search on August placement drive visits",
            "expected_participant": "Rohan Mehta"
        },
        {
            "id": "eval_34",
            "category": "time_topic",
            "query": "What did we discuss about project submission in May?",
            "expected_message_id": final_ground_truth["q34"],
            "description": "Time + topic search on May minor project evaluation",
            "expected_participant": "Aman Sharma"
        },

        # --- DECISION-ORIENTED (4 queries) ---
        {
            "id": "eval_35",
            "category": "decision",
            "query": "What did we finally decide about the venue?",
            "expected_message_id": final_ground_truth["q35"],
            "description": "Decision-intent query for auditorium venue resolution",
            "expected_participant": "Ananya Gupta"
        },
        {
            "id": "eval_36",
            "category": "decision",
            "query": "What was the final decision on the trip destination?",
            "expected_message_id": final_ground_truth["q36"],
            "description": "Decision-intent query for Manali trip resolution",
            "expected_participant": "Aman Sharma"
        },
        {
            "id": "eval_37",
            "category": "decision",
            "query": "What tech stack did we agree to use?",
            "expected_message_id": final_ground_truth["q37"],
            "description": "Decision-intent query for FastAPI React stack resolution",
            "expected_participant": "Sneha Rao"
        },
        {
            "id": "eval_38",
            "category": "decision",
            "query": "What was the final decision regarding event dates?",
            "expected_message_id": final_ground_truth["q38"],
            "description": "Decision-intent query for September 18 symposium date",
            "expected_participant": "Priya Patel"
        },

        # --- HINGLISH & TYPOS (2 queries) ---
        {
            "id": "eval_39",
            "category": "hinglish",
            "query": "trip ka final decision kab hua?",
            "expected_message_id": final_ground_truth["q39"],
            "description": "Code-mixed Hinglish query for trip decision",
            "expected_participant": "Aman Sharma"
        },
        {
            "id": "eval_40",
            "category": "typo_informal",
            "query": "manali kab fnl hua tha?",
            "expected_message_id": final_ground_truth["q40"],
            "description": "Informal typo query for Manali confirmation",
            "expected_participant": "Aman Sharma"
        },
    ]

    print("\nVerifying all 40 queries and token overlaps...")
    zero_overlap_count = 0
    
    for eq in eval_queries:
        target_m = id_lookup[eq["expected_message_id"]]
        overlap_count, shared_tokens = compute_token_overlap(eq["query"], target_m["text"])
        eq["target_text"] = target_m["text"]
        eq["target_timestamp"] = target_m["timestamp"]
        eq["calculated_overlap"] = overlap_count
        eq["shared_tokens"] = list(shared_tokens)
        
        if eq["category"] == "zero_overlap":
            zero_overlap_count += 1
            assert overlap_count == 0, f"Error: Zero-overlap query {eq['id']} has overlap {shared_tokens}! Query: '{eq['query']}' vs Target: '{target_m['text']}'"
            print(f"  [OK] Zero-overlap {eq['id']}: overlap={overlap_count} | Query: '{eq['query'][:45]}...' -> '{target_m['text'][:45]}...'")

    print(f"\nTotal evaluation queries: {len(eval_queries)}")
    print(f"Verified Zero-Word-Overlap queries: {zero_overlap_count} (Requirement was >= 8)")

    questions_path = os.path.join(EVAL_DIR, "questions.json")
    with open(questions_path, "w", encoding="utf-8") as f:
        json.dump(eval_queries, f, indent=2, ensure_ascii=False)
    print(f"Saved evaluation questions to {questions_path}")

    # Generate canonical decisions summary file (for Decision Finder page)
    decisions_summary = [
        {
            "id": "dec_01",
            "title": "Trip Destination Finalized",
            "topic": "Trip Planning",
            "decision": "Manali finalized for vacation (July 14-18)",
            "message_id": final_ground_truth["q1"],
            "participant": "Aman Sharma",
            "timestamp": id_lookup[final_ground_truth["q1"]]["timestamp"],
            "context_summary": "Following debates between Goa, Manali, and Rishikesh, group locked Manali within 8k budget.",
            "status": "Confirmed",
            "icon": "mountain"
        },
        {
            "id": "dec_02",
            "title": "Capstone Tech Stack Selected",
            "topic": "Major Project",
            "decision": "FastAPI backend + React frontend chosen",
            "message_id": final_ground_truth["q2"],
            "participant": "Sneha Rao",
            "timestamp": id_lookup[final_ground_truth["q2"]]["timestamp"],
            "context_summary": "Selected FastAPI for fast async ML embeddings and React with Tailwind for modern UI.",
            "status": "Confirmed",
            "icon": "code"
        },
        {
            "id": "dec_03",
            "title": "Symposium Venue & Date Confirmed",
            "topic": "Innovate 2026",
            "decision": "Main Auditorium approved for September 18",
            "message_id": final_ground_truth["q3"],
            "participant": "Ananya Gupta",
            "timestamp": id_lookup[final_ground_truth["q3"]]["timestamp"],
            "context_summary": "Dean approved Main Auditorium over SAC Hall; official college circular issued.",
            "status": "Confirmed",
            "icon": "calendar"
        },
        {
            "id": "dec_04",
            "title": "Trip Budget Cap Fixed",
            "topic": "Trip Logistics",
            "decision": "Maximum expenditure limited to ₹8,000 per person",
            "message_id": final_ground_truth["q4"],
            "participant": "Priya Patel",
            "timestamp": id_lookup[final_ground_truth["q4"]]["timestamp"],
            "context_summary": "Agreed hotel ceiling at 2k/night to keep overall cost within student budget.",
            "status": "Confirmed",
            "icon": "wallet"
        }
    ]

    decisions_path = os.path.join(DATA_DIR, "decisions.json")
    with open(decisions_path, "w", encoding="utf-8") as f:
        json.dump(decisions_summary, f, indent=2, ensure_ascii=False)
    print(f"Saved canonical decisions summary to {decisions_path}")
    print("\nDataset generation completed successfully!")

if __name__ == "__main__":
    main()
