import os
import re
import tiktoken

def chunk_doc(doc_name: str) -> None:
    doc_dir = os.path.join("docs", doc_name)
    doc_content_path = f"{os.path.join(doc_dir, doc_name)}-content.txt"

    with open(doc_content_path, "r") as doc:
        chunks = doc.read().split("\n\n")

        is_chapter_headline = False
        section_number = 0

        for chunk in chunks:
            # TODO: (Later version?) Ask GPT-4 to describe the images and upload them to the index
            # tagged as images and can call with another function upon request, images stored in Firebase Storage
            chunk_lines = [line.strip() for line in chunk.splitlines() if not re.match(r"%%.+%%", line)]

            first_line = chunk_lines[0]

            chapter_regex = re.compile(r"(CHAPTER) (\d+)")
            appendix_regex = re.compile(r"(APPENDIX) ([ABC]):")

            if first_line == "INTRODUCTION":
                is_chapter_headline = True
                chapter_dir = "intro"
            elif chapter_regex.match(first_line):
                is_chapter_headline = True
                chapter_number = int(chapter_regex.search(first_line).group(2))
                chapter_dir = f"chapter{chapter_number}"
                section_number = 0
            elif appendix_regex.match(first_line):
                is_chapter_headline = True
                appendix_letter = appendix_regex.search(first_line).group(2)
                chapter_dir = f"appendix{appendix_letter}"
            else:
                is_chapter_headline = False
                section_number += 1

            chapter_dir_path = os.path.join(doc_dir, "chunks", chapter_dir)

            if is_chapter_headline:
                os.makedirs(chapter_dir_path, exist_ok=True)
                chunk_path = os.path.join(chapter_dir_path, chapter_dir)
            else:
                chunk_path = os.path.join(chapter_dir_path, f"section{section_number}")
            
            # TODO: Possibly get a synopsis of each chunk from GPT-4

            with open(f"{chunk_path}.txt", "w+") as outfile:
                enc = tiktoken.get_encoding("cl100k_base")
                chunk_text = "\n".join(chunk_lines)
                encoding = enc.encode(chunk_text)

                if len(encoding) > 8191:
                    raise Exception(f"Chunk is too long for Embedder: {chunk_text}")

                outfile.write(chunk_text)

get_a_grip_outline = """
    INTRODUCTION
    CHAPTER 1 THE INCIDENT
        HOPE
    CHAPTER 2 FIT
        CONTEXT
    CHAPTER 3 FOCUS
        ACCOUNTABILITY RIGHT STRUCTURE
        RIGHT PEOPLE IN THE RIGHT SEATS
        LASER FOCUS
        THE PULSE
        DATA
    CHAPTER 4 VISION PART 1
        DISCIPLINE
        TRANSITION TO VISION
        SWEET SPOT
        THE GOAL
    CHAPTER 5 VISION PART 2
        LAYING THE FOUNDATION
        VISION AND PLAN
        MAKING IT REAL
    CHAPTER 6 BIG MOVES
        NINETY-DAY WORLD
        QUARTERLY ROCKS
        RESOLUTION
        MOMENTUM
        QUARTERLY PULSING
    CHAPTER 7 THE ANNUAL
        TEAM HEALTH
        ORGANIZATIONAL CHECKUP
        DAY TWO
    CHAPTER 8 TRACTION
"""
    
traction_outline = """
    INTRODUCTION
    CHAPTER 1 THE ENTREPRENEURIAL OPERATING SYSTEM
        VISION
        PEOPLE
        DATA
        ISSUES
        PROCESS
        TRACTION
        ORGANIZATIONAL CHECKUP
    CHAPTER 2 LETTING GO OF THE VINE
        BUILDING A TRUE LEADERSHIP TEAM
        HITTING THE CEILING IS INEVITABLE
        SIMPLIFY
        DELEGATE
        PREDICT
        SYSTEMIZE
        STRUCTURE
        YOU CAN ONLY RUN YOUR BUSINESS ON ONE OPERATING SYSTEM
        YOU MUST BE OPEN-MINDED GROWTH-ORIENTED, AND VULNERABLE
    CHAPTER 3 THE VISION COMPONENT: DO THEY SEE WHAT YOU ARE SAYING?
        ANSWERING THE EIGHT QUESTIONS
        WHAT ARE YOUR CORE VALUES?
            STEP 1
            STEP 2
            STEP 3
            STEP 4
        WHAT IS YOUR CORE FOCUS?
            HOW TO DETERMINE YOUR CORE FOCUS
        WHAT IS YOUR 10-YEAR TARGET?
        WHAT IS YOUR MARKETING STRATEGY?
            YOUR TARGET MARKET
            YOUR THREE UNIQUES
            YOUR PROVEN PROCESS
            YOUR GUARANTEE
        WHAT IS YOUR THREE-YEAR PICTURE?
            PAINT THE THREE-YEAR PICTURE
        WHAT IS YOUR ONE-YEAR PLAN?
            HOW TO CREATE YOUR ONE-YEAR PLAN
        WHAT ARE YOUR QUARTERLY ROCKS?
        WHAT ARE YOUR ISSUES?
            HOW TO IDENTIFY YOUR ISSUES
        SHARED BY ALL
    CHAPTER 4 THE PEOPLE COMPONENT: SURROUND YOURSELF WITH GOOD PEOPLE
        RIGHT PERSON, WRONG SEAT
        WRONG PERSON, RIGHT SEAT
        RIGHT PEOPLE
        THE THREE-STRIKE RULE
        RIGHT SEATS
        THE ACCOUNTABILITY CHART
        INTEGRATORS
        VISIONARIES
        YOUR LEADERSHIP TEAM
        ONE NAME, TWO SEATS
        DELEGATE AND ELEVATE
        EVOLUTION
        SCALABILITY
        TERMINATIONS
        36 HOURS OF PAIN
        THE THREE QUESTIONS TO ASK
    CHAPTER 5 THE DATA COMPONENT: SAFETY IN NUMBERS
        SCORECARD
        THREE SCORECARD RULES OF THUMB
        MEASURABLES
    CHAPTER 6 THE ISSUES COMPONENT: DECIDE!
        THE ISSUES LIST
        THE ISSUES SOLVING TRACK
            STEP 1: IDENTIFY
            STEP 2: DISCUSS
            STEP 3: SOLVE
        THE 10 COMMANDMENTS OF SOLVING ISSUES
        THE PERSONAL ISSUES SOLVING SESSION
    CHAPTER 7 THE PROCESS COMPONENT: FINDING YOUR WAY
        DOCUMENTING YOUR CORE PROCESSES
        DOCUMENT EACH OF THE CORE PROCESSES
        THE HR PROCESS
        PACKAGE IT
        FOLLOWED BY ALL
        "FOLLOWED BY ALL" ACTION STEPS
    CHAPTER 8 THE TRACTION COMPONENT: FROM LUFTMENSCH TO ACTION!
        BEFORE TRACTION
        AFTER TRACTION
        ROCKS
        ROCK TRAPS AND PITFALLS
        MEETING PULSE
        THE EOS QUARTERLY MEETING PULSE
            Segue
            Review Previous Quarter
            You have one of three options with incomplete Rocks:
            Review the V/TO
            Establish Next Quarter's Rocks
            Tackle Key Issues
            Next Steps
            Conclude
        THE EOS ANNUAL MEETING PULSE
            Segue
            Review Previous Year
            Team Health Building
            SWOT/Issues List
            V/TO (Through One-Year Plan)
        THE ANNUAL PLANNING AGENDA: DAY TWO
        THE BUILDUP
        THE WEEKLY MEETING PULSE
        ALWAYS A LEVEL 10 MEETING
        THE EOS WEEKLY MEETING PULSE
            Segue
            Scorecard
            Rock Review
            Customer/Employee Headlines
            To-Do List
            IDS
            Conclude
            THE FIVE POINTS OF THE WEEKLY MEETING PULSE
            THE WEEKLY MEETING ROLLOUT
            MEETING PULSE ACTIONS
    CHAPTER 9 PUTTING IT ALL TOGETHER: THE GRAND JOURNEY
        ORGANIZATIONAL CHECKUP
        DISCOVERIES, POTHOLES, AND DELAYS ON THE GRAND JOURNEY
            ROLLING OUT EOS TO YOUR COMPANY
            YOU CAN ONLY MOVE AT YOUR OWN SPEED
            WHY IT WORKS
            THE "CLICK"
            YOU HAVE TO DO THE WORK
            STAY COMMITTED TO THE 90-DAY WORLD
            YOU WILL HIT THE CEILING AGAIN
            BIGGER ISN'T ALWAYS BETTER
            COMPARTMENTALIZING
            SAME-PAGE MEEETINGS
            TAKE A CLARITY BREAK
            SHINY STUFF
            THE ROAD TO HANA
    CHAPTER 10 Getting STARTED
        ACCOUNTABILITY CHART (WHICH INCLUDES PEOPLE ANALYZER AND GWC) 
        ROCKS
        MEETING PULSE (WHICH INCLUDES IDS, LEVEL 10 MEETING, QUARTERLIES, AND ANNUALS) 
        SCORECARD
        V/TO (WHICH INCLUDES CORE VALUES, CORE FOCUS, 10-YEAR TARGET, MARKETING STRATEGY, THREEYEAR PICTURE, AND ONE-YEAR PLAN) 
        THE EOS FOUNDATIONAL TOOLS 
        THREE-STEP PROCESS DOCUMENTER 
        EVERYONE HAS A NUMBER 
        ONGOING IMPLEMENTATION AND REINFORCEMENT
"""

wth_is_eos_outline = """
    INTRODUCTION 
    CHAPTER 1 WHAT THE HECK IS EOS?
        WHY EOS?
        EOS AND YOUR LEADERSHIP TEAM
        EOS AND YOU
    CHAPTER 2 How Does EOS Work? (The EOS Model) 
        THE VISION COMPONENT
        THE PEOPLE COMPONENT
        THE DATA COMPONENT
        THE ISSUES COMPONENT
        THE PROCESS COMPONENT
        THE TRACTION COMPONENT
        CHAPTER SUMMARY
        Questions to Ask Your Manager
    CHAPTER 3 Do You See What They Are Saying? (The Vision/Traction Organizer) 
        QUESTION 1: WHAT ARE YOUR CORE VALUES?
        QUESTION 2: WHAT IS YOUR CORE FOCUS?
        QUESTION 3: WHAT IS YOUR 10-YEAR TARGET?
        QUESTION 4: WHAT IS YOUR MARKETING STRATEGY?
        QUESTION 5: WHAT IS YOUR 3-YEAR PICTURE?
        QUESTION 6: WHAT IS YOUR 1-YEAR PLAN?
        QUESTION 7: WHAT ARE YOUR ROCKS?
        QUESTION 8: WHAT ARE YOUR COMPANY'S ISSUES?
        CHAPTER SUMMARY
        Questions to Ask Your Manager
    CHAPTER 4 WHO'S DOING WHAT? (THE ACCOUNTABILITY CHART)
        THE NEED FOR STRUCTURE
        THE ACCOUNTABILITY CHART
        SCALABILITY
        EVOLUTION
        COMMUNICATION
        CHAPTER SUMMARY
        Questions to Ask Your Manager
    CHAPTER 5 WHAT IS MOST IMPORTANT RIGHT NOW? (ROCKS)
        THE 90-DAY WORLD
        YOUR ROCKS
        SMART
        REVIEWING ROCKS WEEKLY
        ROCKS VS. MEASURABLES
        ROCK COMPLETION
        CHAPTER SUMMARY
        Questions to Ask Your Manager
    CHAPTER 6 WHY DO WE HAVE TO HAVE MEETINGS? (THE WEEKLY MEETING PULSE)
        END PROCRASTINATION
        WEEKLY MEETING PULSE
        LEVEL 10 MEETINGS
        THE LEVEL 10 MEETING AGENDA
        SEGUE (GOOD NEWS)
        SCORECARD
        ROCK REVIEW
        CUSTOMER/EMPLOYEE HEADLINES
        TO-DOS
        IDS (IDENTIFY, DISCUSS, SOLVE)
        Who, Who, 1-Sentence
        Tangent Alert
        CONCLUDE
        CHAPTER SUMMARY
        Questions to Ask Your Manager
    CHAPTER 7 WHAT'S MY NUMBER? (SCORECARD & MEASURABLES)
        DESIGNING THE SCORECARD
        WHAT GETS MEASURED GETS DONE
        EVERYONE HAVING A NUMBER
        CHAPTER SUMMARY
        Questions to Ask Your Manager
    CHAPTER 8 HOW AM I DOING? (PEOPLE ANALYZER)
        STEP 1
        STEP 2
        STEP 3
        WRONG FIT-DON'T PANIC
        THE QUARTERLY CONVERSATION
        CHAPTER SUMMARY
        Questions to Ask Your Manager
    CHAPTER 9 WHAT DO I DO NEXT? (CONCLUSION)
        ORGANIZATIONAL CHECKUP
        THE EOS ORGANIZATIONAL CHECKUP™
        EOS AND YOU
    APPENDIX A: YOUR ROLE
    APPENDIX B: QUESTIONS TO ASK YOUR MANAGER
    APPENDIX C: EOS TERMS
"""

if __name__ == "__main__":
    chunk_doc("get-a-grip")
    # chunk_doc("traction")
    chunk_doc("wth-is-eos")
