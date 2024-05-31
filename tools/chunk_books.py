import os
import re
import tiktoken

section_headings_with_subsections = [
    "WHAT ARE YOUR CORE VALUES?",
    "WHAT IS YOUR CORE FOCUS?",
    "WHAT IS YOUR MARKETING STRATEGY?",
    "WHAT IS YOUR THREE-YEAR PICTURE?",
    "WHAT IS YOUR ONE-YEAR PLAN?",
    "WHAT ARE YOUR ISSUES?",
    "THE ISSUES SOLVING TRACK",
    "THE EOS QUARTERLY MEETING PULSE",
    "THE EOS ANNUAL MEETING PULSE",
    "THE LEVEL 10 WEEKLY MEETING AGENDA",
    "DISCOVERIES, POTHOLES, AND DELAYS ON THE GRAND JOURNEY"
]

subsection_headings = [
    "STEP 1",
    "STEP 2",
    "STEP 3",
    "STEP 4",
    "HOW TO DETERMINE YOUR CORE FOCUS",
    "YOUR TARGET MARKET",
    "YOUR THREE UNIQUES",
    "YOUR PROVEN PROCESS",
    "YOUR GUARANTEE",
    "PAINT THE THREE-YEAR PICTURE",
    "HOW TO CREATE YOUR ONE-YEAR PLAN",
    "HOW TO IDENTIFY YOUR ISSUES",
    "STEP 1: IDENTIFY",
    "STEP 2: DISCUSS",
    "STEP 3: SOLVE",
    "Segue",
    "Review Previous Quarter",
    "You have one of three options with incomplete Rocks:",
    "Review the V/TO",
    "Establish Next Quarter’s Rocks",
    "Tackle Key Issues",
    "Next Steps",
    "Conclude",
    "Segue",
    "Review Previous Year",
    "Team Health Building",
    "SWOT/Issues List",
    "V/TO (Through One-Year Plan)",
    "Segue",
    "Scorecard",
    "Rock Review",
    "Customer/Employee Headlines",
    "To-Do List",
    "IDS",
    "Conclude",
    "ROLLING OUT EOS TO YOUR COMPANY",
    "YOU CAN ONLY MOVE AT YOUR OWN SPEED",
    "WHY IT WORKS",
    "THE “CLICK\"",
    "YOU HAVE TO DO THE WORK",
    "STAY COMMITTED TO THE 90-DAY WORLD",
    "YOU WILL HIT THE CEILING AGAIN",
    "BIGGER ISN’T ALWAYS BETTER",
    "COMPARTMENTALIZING",
    "SAME-PAGE MEETINGS",
    "TAKE A CLARITY BREAK",
    "SHINY STUFF",
    "THE ROAD TO HANA"
]


def chunk_book(book_name: str) -> None:
    book_dir = os.path.join("books", book_name)
    book_content_file = f"{os.path.join(book_dir, book_name)}-content.txt"

    with open(book_content_file, "r") as book:
        chunks = book.read().split("\n\n")

        section_number = 0
        subsection_number = 0

        for chunk in chunks:
            chunk_lines = [line.strip() for line in chunk.splitlines() if not re.match(r"%%.+%%", line)]

            heading = chunk_lines[0]

            chapter_regex = re.compile(r"(CHAPTER) (\d+)")
            appendix_regex = re.compile(r"(APPENDIX) ([ABC]):")

            if heading == "INTRODUCTION":
                chunk_level = "chapter"
                chapter_name = "intro"
            elif chapter_regex.match(heading):
                chunk_level = "chapter"
                chapter_number = int(chapter_regex.search(heading).group(2))
                chapter_name = f"chapter{chapter_number}"
                section_number = 0
            elif appendix_regex.match(heading):
                chunk_level = "chapter"
                appendix_letter = appendix_regex.search(heading).group(2)
                chapter_name = f"appendix{appendix_letter}"
            elif book_name == "traction" and heading in subsection_headings:
                chunk_level = "subsection"
                subsection_number += 1
                subsection_name = f"subsection{subsection_number}"
            else:
                chunk_level = "section"
                section_number += 1
                section_name = f"section{section_number}"
                subsection_number = 0

            chapter_dir = os.path.join(book_dir, "chunks", chapter_name)

            if chunk_level == "chapter":
                os.makedirs(chapter_dir, exist_ok=True)
                chunk_file = os.path.join(chapter_dir, chapter_name)
            elif chunk_level == "section":
                if book_name == "traction" and heading in section_headings_with_subsections:
                    section_dir = os.path.join(chapter_dir, section_name)
                    os.makedirs(section_dir, exist_ok=True)
                    chunk_file = os.path.join(section_dir, section_name)
                else:
                    chunk_file = os.path.join(chapter_dir, section_name)
            elif chunk_level == "subsection":
                chunk_file = os.path.join(chapter_dir, section_name, subsection_name)
            else:
                raise Exception("Invalid chunk level")

            with open(f"{chunk_file}.txt", "w+") as outfile:
                enc = tiktoken.get_encoding("cl100k_base")
                chunk_text = "\n".join(chunk_lines)
                encoding = enc.encode(chunk_text)

                if len(encoding) > 8191:
                    raise Exception(f"Chunk is too long for Embedder: {chunk_text}")

                outfile.write(chunk_text)

if __name__ == "__main__":
    chunk_book("get-a-grip")
    chunk_book("traction")
    chunk_book("wth-is-eos")
