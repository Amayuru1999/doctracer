import fitz  # PyMuPDF
import re
import json

def extract_ministry_data(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()

    ministries = []
    current_minister = None

    for line in text.split("\n"):
        line = line.strip()
        # Minister heading
        match = re.match(r"^\d+\.\s*minister of (.+)", line, re.IGNORECASE)
        if match:
            if current_minister:
                ministries.append(current_minister)
            current_minister = {
                "name": "Minister of " + match.group(1).strip(),
                "functions": [],
                "departments": [],
                "laws": []
            }
            continue

        if not current_minister:
            continue

        # Classify the line
        if "act" in line.lower() or "ordinance" in line.lower() or "law" in line.lower():
            current_minister["laws"].append(line)
        elif "department" in line.lower() or "board" in line.lower() or "authority" in line.lower() or "commission" in line.lower():
            current_minister["departments"].append(line)
        elif line:
            current_minister["functions"].append(line)

    if current_minister:
        ministries.append(current_minister)

    return ministries

def save_to_json(ministries, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ministries, f, indent=2)
