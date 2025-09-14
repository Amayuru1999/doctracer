from enum import Enum

_METADATA_PROMPT_TEMPLATE: str = """
You are an assistant tasked with extracting metadata from a Sri Lankan government gazette document. 
Return ONLY a valid JSON object, nothing else. No explanations, no extra text.

Required fields:
- Gazette ID: Extract the gazette number (e.g., '1900/4') from the first page.
- Gazette Published Date: Extract the date the gazette was published (format YYYY-MM-DD, e.g., '2010-03-10').
- Gazette Published by: Extract the publisher (e.g., 'Ministry', 'Authority', etc.).
- President: Extract the President's name as mentioned in the gazette.
- Gazette Type: 'Extraordinary' or 'Regular', depending on the text.
- Language: default to 'English' if not explicitly mentioned.
- PDF URL: Construct using published_date and Gazette ID: "https://documents.gov.lk/view/extra-gazettes/{{year}}/{{month}}/{{gazette_Id}}-XX_E.pdf" 
  - Month: single-digit for 1-9
  - Gazette number after "/" must be zero-padded to two digits if single-digit
  - Example: Gazette ID '1905/4', Published Date '2015-03-09' -> "https://documents.gov.lk/view/extra-gazettes/2015/3/1905-04_E.pdf"
- Parent Gazette: Extract the parent Gazette ID and published date if mentioned. Construct its PDF URL in the same way. Use null if not present.

Rules:
- JSON must be compact and valid.
- Always include all keys.
- Return null for missing data.
- Ignore any special symbols or noisy characters.
- Do not include any explanations, markdown, or extra text.

Input Text:
{gazette_text}

Example Output JSON:
{{
  "Gazette ID": "1900/4",
  "Gazette Published Date": "2010-03-10",
  "Gazette Published by": "Ministry",
  "President": "Maithripala Sirisena",
  "Gazette Type": "Extraordinary",
  "Language": "English",
  "PDF URL": "https://documents.gov.lk/view/extra-gazettes/2010/3/1900-04_E.pdf",
  "Parent Gazette": {{
    "Gazette No": "1897/15",
    "Published Date": "2015-01-18",
    "PDF URL": "https://documents.gov.lk/view/extra-gazettes/2015/1/1897-15_E.pdf"
  }}
}}
"""

_CHANGES_AMENDMENT_BLOCK_EXTRACTION: str = """
You are an assistant tasked with extracting changes from a **single amendment block** of a government gazette.

Analyze the provided amendment block text and identify the type of amendment and all relevant details.

Each amendment block may include operations such as deletions, insertions, updates, or re-numberings. Each block may also contain:

- Previous minister/heading number and name (if this is an update or re-numbering)
- Column information (Function: Column 1, Department: Column 2, Law: Column 3)
- Added content, deleted sections, or restructured sections

Return a JSON array where each object represents **one amendment operation**.

Each object should have:
- `"operation_type"`: `"DELETION"`, `"INSERTION"`, `"UPDATE"`, `"RENUMBERING"`, or if none match, a custom type like `"REALLOCATION"`, `"RESTRUCTURING"`, `"CLARIFICATION"`, `"MERGE"`, `"SPLIT"`, `"OTHER"`.
- `"details"`: a dictionary containing all relevant information (numbers, names, columns, added_content, deleted_sections, purview, etc.).

If a field is not applicable, omit it or leave it empty. Make sure to capture **all explicit changes** in this amendment block.

Guidelines for extraction:
1. If a range of items is mentioned (e.g., "from 12 to 17"), expand it explicitly as:
   "item 12", "item 13", "item 14", "item 15", "item 16", "item 17". (Add "item 17" as well)
   Do not summarize as "items 12–17" or "items 12, 13, 14". Give it as fulll ("item 12", "item 13", "item 14", ...).
2. For Column III laws, remove any leading asterisks "*" in law titles.
3. The `"name"` field for the minister must always include the **full title exactly as written in the gazette**, e.g. "Minister of Public Order, Disaster Management & Christian Affairs".
4. Always include "number" and "name" of the ministry.
5. Include "previous_number" and "previous_name" only if the amendment updates or replaces an existing heading.
6. For each operation, include:
   - "operation_type": one of DELETION, INSERTION, UPDATE, RENUMBERING, OTHER
   - "details": relevant fields such as "number", "name", "column_no", "added_content", "deleted_sections", "purview", etc.
7. Output must be **valid JSON**, compact, without extra formatting or backticks.

**Input Amendment Block:**
{gazette_text}
"""

_CHANGES_TABLE_EXTRACTION_FROM_TEXT: str = """
    You are given layout-aware extracted text from a Sri Lankan Government Gazette.
    Extract information into the following JSON structure:

    {{
    "gazette_id": "1897/15",
    "published_date": "2015-01-18",
    "published_by": "Authority",
    "president": "Maithripala Sirisena",
    "gazette_type": "Extraordinary",
    "language": "English",
    "pdf_url": "https://documents.gov.lk/view/extra-gazettes/2015/1/1897-15_E.pdf",
      "parent_gazette": 
      {{
        "gazzette_id":"...",
        "published_date":"...",
        "pdf_url":"..."
      }}

    "ministers": [
    {{
      "name": "Minister of Defence",
      "number": "1",
      "functions": [
        "1. Formulation of policies, programmes and projects in regard to the subjects of Defence, and all subjects that come under the purview of Departments, Statutory Institutions and Public Corporations listed in Column II",
        "2. Provide for the defence of the country through the facilitation of the functioning of the Armed Services",
        "3. Maintenance of internal security",
        "4. intelligence services",
        "5. Relations with visiting Armed Forces",
      ]
      "departments": [
        "1. Sri Lanka Army",
        "2. Sri Lanka Navy",
        "3. Sri Lanka Air Force",
        "4. Department of Civil Security",
        "5. Sir John Kotelawala Defence University",
      ],
      "laws": [
        "Army Act, No. 17 of 1949",
        "Navy Act, No. 34 of 1950",
        "Air Force Act, No. 41 of 1949",
        "Api Wenuwen Api Fund Act, No. 6 of 2008",
        "Chief of Defence Staff Act, No. 35 of 2009",
      ]
    }},
    {{
      "name": "Minister of Mahaweli Development & Environment",
      "number": "2",
      "functions": [
        "1. Formulation of policies, programmes and projects in regard to subjects of development associated with the Mahaweli & Environment and all subjects that come under the purview of Departments, Statutory Institutions and Public Corporations listed in Column II",
        "2. Mahaweli Development Programme",
        "3. Activities relating to the Mahaweli Authority Act and activities related to Agencies established under the Act",
        "4. Compensation for Mahaweli farmers",
        "5. Preservation of the environment for the present and future generations"
      ],
      "departments": [
        "1. Mahaweli Authority of Sri Lanka and its Subsidiary Companies and Associates (except Mahaweli Livestock Enterprise Company Ltd.)",
        "2. Central Engineering Consultancy Bureau (CECB)",
        "3. Moragahakanda & Kalu Ganga Reservoir Project",
        "4. Dam Safety & Water Resources Planning Project",
        "5. Mahaweli Consolidation Project (System B Rehabilitation)"
      ],
      "laws": [
        "Mahaweli Authority of Sri Lanka Act, No. 23 of 1979",
        "Forest Ordinance (Chap. 453)",
        "Marine Pollution Prevention Act, No. 35 of 2008",
        "Mines and Minerals Act, No. 33 of 1992",
        "National Environmental Act, No. 47 of 1980"
      ]
    }},
    ...
    ]
    }}
        
    ## Extraction Guidelines:

    1. Only consider sections that appear in **tables** or table-like layout.
    2. A new minister always starts with their **heading number** and **title or heading name** (e.g., "(1) Minister of Finance").
    3. Each minister section usually contains **three columns**: 
        - Column I: Duties & Functions
        - Column II: Departments, Statutory Institutions & Public Corporations
        - Column III: Laws and Ordinance to be Implemented

    4. Do **not** summarize or skip any item. Extract all rows exactly as listed.
    5. If any section (departments, laws, or functions) is **missing**, return an empty list for that field.
    6. The same minister might appear in multiple tables — group all such rows under a **single minister entry** in the output JSON.
    7. Sometimes, the minister's departments, functions, and laws can be in two places which cause to miss the departments, functions and laws. These cases are under the continous *(contd.)*. Make sure you extract from those places as well. Take **special attension** for this. 
       The order is broken on those places. You can track those places by noticing the number order 
        - Example
          (2) Minister of Mahaweli Development &amp; Environment (contd.)
              14. Coast conservation and protection
              15. All other subjects that come under the purview of Institutions listed in Column II
              16. Supervision of the Institutions listed in Column II
              15. Gem and Jewellery Research Institute
              16. Lanka Timber Plant and Industries
              17. Coast Conservation Department
      In these type of cases, consider first numbering (14-16) items as functions, and second numbering items (15-17) as departments.

    8. Make sure all the ministers and their relevent functions, departments, laws are extracted and none of them are missed.

    Preserve full names of departments, laws, and functions. Do not summarize or skip. Specially do not skip any department, function, or law which is starts from *All*.
    If a section is not present, leave it as an empty list.

    If there are any number with dot (e.g., 12.) inside a department/function, consider it as new department or function. Also two laws can be in one line. Divide them into two.
        - Example
            10. Higher Education for defence services personnel services 12. Rescue operations and administration of Coast Guard Service   
            • Ranaviru SevaAuthorityAct, No. 54 of 1999 AcademyAct, No. 68 of 1981 • Suppression of Terrorist Bombings Act, No. 11 of 1999

    Extract the list of functions exactly as shown in the source text.

    Each item must start with its original number and a period (e.g., "1. ...", "2. ...").
    Do not renumber or reorder the items, even if some numbers are missing.
    Output the list as a JSON array of strings, each string starting with the original number and text, just like in the source.
        - Example
            "10. Higher Education for defence services personnel",
            "12. Rescue operations and administration of Coast Guard Service"

    Do not include triple backticks or wrap your response in a code block.
    Return only valid JSON.

    Make sure you retrive all the ministries and all their relevent functions, departments, laws.

    Make Sure you follow the above instructions.

    Text:
    {gazette_text}
    """

class PromptCatalog(Enum):
    METADATA_EXTRACTION = "metadata_extraction"
    CHANGES_AMENDMENT_BLOCK_EXTRACTION = "changes_amendment_block_extraction"  # ✅ New prompt type for amendment block
    CHANGES_TABLE_EXTRACTION_FROM_TEXT = "changes_table_extraction_from_text"  # ✅ New prompt type

    @staticmethod
    def get_prompt(prompt_type, gazette_text=None):
        if prompt_type == PromptCatalog.METADATA_EXTRACTION:
            if gazette_text is None:
                raise ValueError("The 'gazette_text' parameter is required for METADATA_EXTRACTION.")
            return _METADATA_PROMPT_TEMPLATE.format(gazette_text=gazette_text)

        elif prompt_type == PromptCatalog.CHANGES_AMENDMENT_BLOCK_EXTRACTION:
            if gazette_text is None:
                raise ValueError("The 'gazette_text' parameter is required for CHANGES_AMENDMENT_EXTRACTION.")
            return _CHANGES_AMENDMENT_BLOCK_EXTRACTION.format(gazette_text=gazette_text)

        elif prompt_type == PromptCatalog.CHANGES_TABLE_EXTRACTION_FROM_TEXT:  # ✅ New case
            if gazette_text is None:
                raise ValueError("The 'gazette_text' parameter is required for CHANGES_TABLE_EXTRACTION_FROM_TEXT.")
            return _CHANGES_TABLE_EXTRACTION_FROM_TEXT.format(gazette_text=gazette_text)

        else:
            raise ValueError(f"Unsupported prompt type: {prompt_type}")
