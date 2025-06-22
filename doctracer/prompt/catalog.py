from enum import Enum

_METADATA_PROMPT_TEMPLATE: str = """
    You are an assistant tasked with extracting metadata from a government gazette document. Using the provided text, identify and return the following information in a compact JSON string:
    - Gazette ID
    - Gazette Published Date
    - Gazette Published by whom
    Ensure the JSON string is compact, without any additional formatting or escape characters.
    Don't include unnecessary backward slashes or forward slashes unless the data contains them. 
    Input Text:
    {gazette_text}
    Sample JSON Output:
    {{"Gazette ID":"2303/17","Gazette Published Date":"2022-10-26","Gazette Published by":"Authority"}}
    """
'''
_CHANGES_AMENDMENT_PROMPT_TEMPLATE: str = """
    You are an assistant tasked with extracting changes from a government gazette document. Based on the provided text, identify and list the following operation types along with their details:
    - RENAME
    - MERGE
    - MOVE
    - ADD
    - TERMINATE
    Provide the extracted data as a compact JSON string, without any additional formatting or escape characters.
    Don't include unnecessary backward slashes or forward slashes unless the data contains them.
    Input Text:
    {gazette_text}
    Sample JSON Output:
    {{"RENAME":[{{"Previous Name":"No. 03. Minister of Technology","New Name":"No. 03. Minister of Technology","Type":"minister","Date":"2022-10-26"}}],
    "MERGE":[{{"Previous Names":["Dept. A", "Dept. B"],"New Name":"Dept. AB","Type":"department merge","Date":"2022-10-26"}}],
    "MOVE":[{{"Previous Parent Name":"Ministry X","New Parent Name":"Ministry Y","Which Child is Moving":"Dept. Z","Type":"department","Date":"2022-10-26"}}],
    "ADD":[{{"Parent Name":"Ministry X","Child Name":"Dept. Z","Type":"department","Date":"2022-10-26"}}],
    "TERMINATE":[{{"Type":"minister","Date":"2022-10-26"}}]}}
    """
'''

'''
_CHANGES_AMENDMENT_PROMPT_TEMPLATE: str = """
    You are an assistant tasked with analyzing changes in a government gazette. Your job is to extract details of removals and additions **without making assumptions about movement or relationships**.

    Changes may appear in bullet points or be grouped under headings like "Column I", "Column II", "Column III". Identify removed and added items accurately even if they appear as numbered or bulleted list items.

    Return a JSON object with two main keys: "REMOVED" and "ADDED".

    Each section must include:
    - "Minister": the name of the minister being updated.
    - "Departments": list of departments removed from or added to that minister.
    - "Laws": list of laws removed from or added to that minister.
    - "Responsibilities": only for ADDED section; list of new responsibilities if mentioned.

    **DO NOT connect removed items to added items. Treat them independently.**

    Return only valid JSON. Do not wrap your output in markdown or triple backticks.

    Input Text:
    {gazette_text}

    Sample JSON Output:
    {{
    "REMOVED": {{
        "Minister": "Minister of Finance, Economic Stabilization and National Policies",
        "Departments": ["Sri Lanka Export Development Board"],
        "Laws": ["Export Development Act No. 40 of 1979"]
    }},
    "ADDED": {{
        "Minister": "Minister of Investment Promotion",
        "Departments": ["Sri Lanka Export Development Board"],
        "Laws": ["Export Development Act No. 40 of 1979"],
        "Responsibilities": ["Development of Colombo Port City Special Economic Zone"]
    }}
    }}
"""
'''
'''
_CHANGES_AMENDMENT_PROMPT_TEMPLATE: str = """
    You are an assistant tasked with analyzing changes in a government gazette. Your job is to extract details of removals and additions **without making assumptions about movement or relationships**.

    Changes may appear in bullet points or be grouped under headings like "Column I", "Column II", "Column III". Identify removed and added items accurately even if they appear as numbered or bulleted list items.

    Return a JSON object with two main keys: "REMOVED" and "ADDED".

    Each section must include:
    - "Minister": the name of the minister being updated.
    - "Departments": list of departments removed from or added to that minister.
        - If the gazette mentions removal of items by number only (e.g., “items 26, 50 and 51” in Column II), include those item numbers as strings in the "Departments" list.
    - "Laws": list of laws removed from or added to that minister.
    - "Responsibilities": only for the ADDED section; list of new responsibilities if mentioned.

    **DO NOT connect removed items to added items. Treat them independently.**

    Return only valid JSON. Do not wrap your output in markdown or triple backticks.

    Input Text:
    {gazette_text}

    Sample JSON Output:
    {{
    "REMOVED": {{
        "Minister": "Minister of Finance, Economic Stabilization and National Policies",
        "Departments": ["26", "50", "51"],
        "Laws": [
        "Sri Lanka Export Development Act No. 40 of 1979",
        "Greater Colombo Economic Commission Law No. 4 of 1978",
        "Colombo Port City Economic Commission Act, No. 11 of 2021"
        ]
    }},
    "ADDED": {{
        "Minister": "Minister of Investment Promotion",
        "Departments": ["Sri Lanka Export Development Board"],
        "Laws": ["Export Development Act No. 40 of 1979"],
        "Responsibilities": ["Development of Colombo Port City Special Economic Zone"]
  }}
}}
"""
'''


'''
_CHANGES_AMENDMENT_PROMPT_TEMPLATE: str = """
You are an assistant tasked with extracting changes from a government gazette document.
Analyze the provided text to identify different types of amendments and extract their details.
Focus on identifying explicit operations like "By deleting", "By insertion of the following new Heading", "is as follows" (indicating an update/redefinition), and "By re-numbering".

Return a JSON array where each object represents a single amendment operation.

Each object in the array should have an "operation_type" key, and a "details" key.
The "operation_type" can be one of the following: "DELETION", "INSERTION", "UPDATE", "RENUMBERING".

Here are the details to extract for each operation type:

1.  For "DELETION" operations:
    -   "heading_number": The number of the heading being deleted (e.g., "No. 3.0").
    -   "heading_name": The name of the Minister or State Minister heading being deleted (e.g., "Minister of Finance").
    -   "deleted_sections": A list of the specific sub-sections explicitly mentioned as being deleted (e.g., ["Purview", "Subjects & Functions"]). If the entire heading is deleted and sub-sections aren't individually listed, state "All associated sections".

2.  For "INSERTION" operations:
    -   "heading_number": The number of the new heading (e.g., "3.0").
    -   "heading_name": The name of the new Minister or State Minister heading (e.g., "Minister of Economic Policies & Plan Implementation").
    -   "purview": (Optional) The text of the "Purview" section, if present.
    -   "subjects_and_functions": (Optional) A list of strings, each representing a subject or function.
    -   "special_priorities": (Optional) A list of strings, each representing a special priority.
    -   "related_institutional_and_legal_framework": (Optional) An object containing:
        -   "departments_and_institutions": A list of strings, each representing a department or institution.
        -   "laws_and_ordinances": A list of strings, each representing a law or ordinance.

3.  For "UPDATE" operations (indicated by "is as follows" for an existing heading or a specific section under a heading):
    -   "heading_number": The number of the heading being updated (e.g., "No. 5.1").
    -   "heading_name": The name of the Minister or State Minister heading being updated.
    -   "updated_content": An object containing the new or updated content. This can include:
        -   "purview": (Optional) The new text of the "Purview" section.
        -   "subjects_and_functions": (Optional) A list of new or updated subjects/functions.
        -   "special_priorities": (Optional) A list of new or updated special priorities.
        -   "related_institutional_and_legal_framework": (Optional) An object with new departments/institutions and laws/ordinances.
        -   If only a specific sub-section is updated (e.g., "04. Related Institutional and Legal Framework" under a Minister), explicitly mention that sub-section.

4.  For "RENUMBERING" operations:
    -   "previous_number": The original heading number.
    -   "new_number": The new heading number.
    -   "heading_name": The name of the Minister or State Minister whose heading is re-numbered.

Ensure the JSON output is compact, without any additional formatting or escape characters like triple backticks.
If a section is not applicable or not found for a specific operation, omit it or use an empty list/object.

Input Text:
{gazette_text}

Sample JSON Output (illustrative, not exhaustive for all cases):
[
  {{
    "operation_type": "DELETION",
    "details": {{
      "heading_number": "No. 3.0",
      "heading_name": "Minister of Finance",
      "deleted_sections": ["Purview", "Subjects & Functions"]
    }}
  }},
  {{
    "operation_type": "INSERTION",
    "details": {{
      "heading_number": "3.0",
      "heading_name": "Minister of Economic Policies & Plan Implementation",
      "purview": "Planning and implementation of relevant policies...",
      "subjects_and_functions": ["Formulating policies...", "Facilitating of carrying out relevant development activities..."],
      "special_priorities": ["Formulation and implementation of national development programmes..."],
      "related_institutional_and_legal_framework": {{
        "departments_and_institutions": ["National Planning Department", "Department of Census and Statistics"],
        "laws_and_ordinances": ["Census Ordinance (Chapter 143)", "Institute of Policy Studies of Sri Lanka Act No. 53 of 1988"]
      }}
    }}
  }},
  {{
    "operation_type": "UPDATE",
    "details": {{
      "heading_number": "No. 5.1",
      "heading_name": "State Minister of Urban Development, Waste Disposal and Community Cleanliness",
      "updated_content": {{
        "subjects_and_functions": ["Assisting in the formulation of policies...", "Implementing projects under the National Budget..."],
        "special_priorities": ["Socially empowering urban labour force...", "Coordinating the provision of long term credit facilities..."],
        "related_institutional_and_legal_framework": {{
          "departments_and_institutions": ["Urban Development Authority", "Urban Settlement Development Authority"],
          "laws_and_ordinances": ["Urban Development Authority Act, No. 41 of 1978"]
        }}
      }}
    }}
  }},
  {{
    "operation_type": "RENUMBERING",
    "details": {{
      "previous_number": "3.1",
      "new_number": "6.1",
      "heading_name": "State Minister of Money and Capital Market and State Enterprise Reforms"
    }}
  }}
]
"""

'''

_CHANGES_AMENDMENT_PROMPT_TEMPLATE: str = """
You are an assistant tasked with extracting changes from a government gazette document.
Analyze the provided text to identify different types of amendments and extract their details.
Focus on identifying explicit operations like "By deleting", "By insertion of the following new Heading", "is as follows" (indicating an update/redefinition), and "By re-numbering".

Return a JSON array where each object represents a single amendment operation.

Each object in the array should have an "operation_type" key, and a "details" key.
The "operation_type" can be one of the following: "DELETION", "INSERTION", "UPDATE", "RENUMBERING".

Here are the details to extract for each operation type:

1.  For "DELETION" operations:
    -   "heading_number": The number of the heading being deleted (e.g., "No. 3.0").
    -   "heading_name": The name of the Minister or State Minister heading being deleted (e.g., "Minister of Finance").
    -   "deleted_sections": A list of the specific sub-sections explicitly mentioned as being deleted (e.g., ["Purview", "Subjects & Functions"]). If the entire heading is deleted and sub-sections aren't individually listed, state "All associated sections".

2.  For "INSERTION" operations:
    -   "heading_number": The number of the new heading (e.g., "3.0").
    -   "heading_name": The name of the new Minister or State Minister heading (e.g., "Minister of Economic Policies & Plan Implementation").
    -   "purview": (Optional) The text of the "Purview" section, if present.
    -   "subjects_and_functions": (Optional) A list of strings, each representing a subject or function.
    -   "special_priorities": (Optional) A list of strings, each representing a special priority.
    -   "related_institutional_and_legal_framework": (Optional) An object containing:
        -   "departments_and_institutions": A list of strings, each representing a department or institution.
        -   "laws_and_ordinances": A list of strings, each representing a law or ordinance.

3.  For "UPDATE" operations (indicated by "is as follows" for an existing heading or a specific section under a heading):
    -   "heading_number": The number of the heading being updated (e.g., "No. 5.1").
    -   "heading_name": The name of the Minister or State Minister heading being updated.
    -   "updated_content": An object containing the new or updated content. This can include:
        -   "purview": (Optional) The new text of the "Purview" section.
        -   "subjects_and_functions": (Optional) A list of new or updated subjects/functions.
        -   "special_priorities": (Optional) A list of new or updated special priorities.
        -   "related_institutional_and_legal_framework": (Optional) An object with new departments/institutions and laws/ordinances.
        -   If only a specific sub-section is updated (e.g., "04. Related Institutional and Legal Framework" under a Minister), explicitly mention that sub-section.

4.  For "RENUMBERING" operations:
    -   "previous_number": The original heading number.
    -   "new_number": The new heading number.
    -   "heading_name": The name of the Minister or State Minister whose heading is re-numbered.

Ensure the JSON output is compact, without any additional formatting or escape characters like triple backticks.
If a section is not applicable or not found for a specific operation, omit it or use an empty list/object.

---

Example Change Text:
(2) “By insertion of the following new Heading and “01. Purview, 02. Subjects and Functions, 03. Special Priorities and
04. Related Institutional and Legal Framework” under thereof after the Heading No. “2.1 State Minister of Digital
Technology and Enterprise Development” in that notification;
3.0 Minister of Economic Policies & Plan Implementation
01. Purview
Planning and implementation of relevant policies, in order to accelerate economic development and social progress based on the National Policy Statement: “Vistas of Prosperity and Splendour”.
02. Subjects and Functions
1. Formulating policies in relation to the subject of economic policies and plan implementation...
2. Facilitating of carrying out relevant development activities...
03. Special Priorities
1. Formulation and implementation of national development programmes and projects...
2. Co-ordination of State, Private and Co-operative sectors...
04. Related Institutional and Legal Framework
Departments and Institutions:
- National Planning Department
- Department of Census and Statistics
Laws and Ordinances:
- Census Ordinance (Chapter 143)
- Institute of Policy Studies of Sri Lanka Act No. 53 of 1988

Expected JSON:
[
  {{
    "operation_type": "INSERTION",
    "details": {{
      "heading_number": "3.0",
      "heading_name": "Minister of Economic Policies & Plan Implementation",
      "purview": "Planning and implementation of relevant policies, in order to accelerate economic development and social progress based on the National Policy Statement: “Vistas of Prosperity and Splendour”.",
      "subjects_and_functions": [
        "Formulating policies in relation to the subject of economic policies and plan implementation...",
        "Facilitating of carrying out relevant development activities...",
        "Monitoring and reviewing the cost of living...",
        "Implementing people-centric development activities..."
      ],
      "special_priorities": [
        "Formulation and implementation of national development programmes and projects...",
        "Co-ordination of State, Private and Co-operative sectors...",
        "Implementation of rural and regional economic development policies..."
      ],
      "related_institutional_and_legal_framework": {{
        "departments_and_institutions": [
          "National Planning Department",
          "Department of Census and Statistics",
          "Institute of Policy Studies",
          "Sustainable Development Council",
          "Office of Comptroller General"
        ],
        "laws_and_ordinances": [
          "Census Ordinance (Chapter 143)",
          "Institute of Policy Studies of Sri Lanka Act No. 53 of 1988",
          "The Sustainable Development Act No. 19 of 2017"
        ]
      }}
    }}
  }}
]

Now apply the same logic to the remaining content and return the full JSON array of changes from the gazette text.

Input Gazette Text:
{gazette_text}
"""



_CHANGES_TABLE_PROMPT_TEMPLATE: str = """
        What are the ministers found in the image? There will always be at least one minister. Use this information to find the minister(s):
        - The minister begins with a number (example 1. Minister of Defence)
        - The minister is in the format "Minister of ..."
        - The minister is in bold
        - The minister is not found inside any table or columns

        Also retrieve lists of the 'subjects and functions', 'departments, statutory institutions and public corporations' and 'laws, acts and ordinances to be implemented' in this image for each minister identified. If there are none in either column leave the list empty for that column.

        Return the information as a JSON object, for example:

        {
            "ministers": 
            [
                {
                    "name": "Minister of Defence",
                    "functions": [
                        "Ensure national security",
                        "Coordinate armed forces",
                        "Develop defense policies"
                    ],
                    "departments": [
                        "Office of the Chief of Defence Staff",
                        "Sri Lanka Army",
                        "Sri Lanka Navy"
                    ],
                    "laws": [
                        "National Security Act No. 45 of 2003",
                        "Military Ordinance No. 12 of 1945"
                    ]
                },
            ]
        }

        Don't add any extra text such as ```json so that i can directly save the response to a json file.
    """
    

class PromptCatalog(Enum):
    METADATA_EXTRACTION = "metadata_extraction"
    CHANGES_AMENDMENT_EXTRACTION = "changes_amendment_extraction"
    CHANGES_TABLE_EXTRACTION = "changes_table_extraction"
    # Add more prompts as needed

    @staticmethod
    def get_prompt(prompt_type, gazette_text=None):
        if prompt_type == PromptCatalog.METADATA_EXTRACTION:
            if gazette_text is None:
                raise ValueError("The 'gazette_text' parameter is required for METADATA_EXTRACTION.")
            return _METADATA_PROMPT_TEMPLATE.format(gazette_text=gazette_text)
        
        elif prompt_type == PromptCatalog.CHANGES_AMENDMENT_EXTRACTION:
            if gazette_text is None:
                raise ValueError("The 'gazette_text' parameter is required for CHANGES_AMENDMENT_EXTRACTION.")
            return _CHANGES_AMENDMENT_PROMPT_TEMPLATE.format(gazette_text=gazette_text)
        elif prompt_type == PromptCatalog.CHANGES_TABLE_EXTRACTION:
            # No gazette_text needed for this prompt
            return _CHANGES_TABLE_PROMPT_TEMPLATE
        else:
            raise ValueError(f"Unsupported prompt type: {prompt_type}")

