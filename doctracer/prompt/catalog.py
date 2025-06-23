from enum import Enum

_METADATA_PROMPT_TEMPLATE: str = """
    You are an assistant tasked with extracting metadata from a government gazette document. Using the provided text, identify and return the following information in a compact JSON string:
    - Gazette No
    - Published Date
    - Published By
    - Gazette Type
    - Language
    - PDF URL (Use the year and month from the Published Date. For months 1-9, use a single-digit month in the URL path. Also, use the Gazette No. For months 1-9, if the Gazette No. contains single-digit after "/", use double-digits to create PDF URL. For example, for Published Date '2020-04-22' and Gazette No '2277/2, the PDF URL should be: 'https://documents.gov.lk/view/extra-gazettes/2020/4/2277-02_E.pdf')
    - Amends (Gazette No, Published Date, PDF URL)

    After extracting this metadata, if an Amends PDF URL is present, trigger a recursive extraction step to:
    - Download and extract text from the amended gazette PDF
    - Extract its metadata and changes using this same prompt suite
    - Link the amended gazette data back to the current gazette metadata

    Ensure the JSON string is compact, without any additional formatting or escape characters.
    Don't include unnecessary backward slashes or forward slashes unless the data contains them. 

    Input Text:
    {gazette_text}

    Sample JSON Output:
    {{"Gazette No":"2303/17","Published Date":"2022-10-26","Published By":"Authority","Gazette Type":"Extraordinary","Language":"English","PDF URL":"https://documents.gov.lk/view/extra-gazettes/2022/10/2303-17_E.pdf","Amends":{{"Gazette No":"2276/24","Published Date":"2021-06-19", "PDF URL":"https://documents.gov.lk/view/extra-gazettes/2021/6/2276-24_E.pdf"}}}}
"""

_CHANGES_AMENDMENT_PROMPT_TEMPLATE: str = """
    You are an assistant tasked with extracting changes from a government gazette document. Based on the provided text, identify and list the following operation types along with their details:
    - RENAME (Add only if the Previous Name and New Name are difference)
    - MERGE
    - MOVE
    - ADD
    - TERMINATE

    For each change, include the following (as applicable):
    - Type
    - Previous Name
    - New Name
    - Parent Name
    - Previous Parent Name
    - New Parent Name
    - New Entity
    - Effective Date
    - Clause ID (if present)
    - Reason (if mentioned or implied)

    Use natural labels such as "Previous Name", "Clause ID", etc. Ensure the JSON is compact and free of unnecessary escape characters or formatting.

    Input Text:
    {gazette_text}

    Sample JSON Output:
    {{
        "RENAME": [{{"Type":"Minister","Previous Name":"No. 03. Minister of Technology","New Name":"No. 03. Minister of Science","Effective Date":"2022-10-26","Clause ID":"8.2","Reason":"Updated title"}}],
        "MERGE": [{{"Type":"Department merge", "Previous Names":["Dept. A", "Dept. B"],"New Name":"Dept. AB","Effective Date":"2022-10-26"}}],
        "MOVE": [{{"Type":"Department", "Previous Parent Name":"Ministry X","New Parent Name":"Ministry Y","Which Child is Moving":"Dept. Z","Effective Date":"2022-10-26"}}],
        "ADD": [{{"Type":"Minister","Parent Name":"Minister X","New Entity":"Ministry Y","Effective Date":"2022-10-26","Clause ID":"8.4","Reason":"To address needs"}}],
        "TERMINATE": [{{"Type":"minister","Date":"2022-10-26"}}]
    }}
"""

_CHANGES_TABLE_PROMPT_TEMPLATE: str = """
    You are an assistant tasked with extracting metadata from a government gazette document images. Using the provided images, identify and return the following information in a compact JSON string:
    - gazette_id
    - published_date
    - published_by
    - gazette_type
    - language
    - pdf_url (Use the year and month from the published_date. For months 1-9, use a single-digit month in the url path. Also, use the gazette_id For months 1-9, if the gazette_id contains single-digit after "/", use double-digits to create pdf_url. For example, for published_date '2020-04-22' and gazette_id '2277/2, the pdf_url should be: 'https://documents.gov.lk/view/extra-gazettes/2020/4/2277-02_E.pdf')
    - amends (Gazette No, Published Date, PDF URL)

    After extracting this metadata, you should find what are the ministers found in the image? There will always be at least one minister. Use this information to find the minister(s):
    - The minister begins with a number (example 1. Minister of Defence)
    - The minister is in the format "Minister of ..."
    - The minister is in bold
    - The minister is not found inside any table or columns

    Also retrieve lists of the 'subjects and functions', 'departments, statutory institutions and public corporations' and 'laws, acts and ordinances to be implemented' in this image for each minister identified. If there are none in either column leave the list empty for that column.

    Aggregate all pages into a single JSON result.

    Return the information as a JSON object, for example:

    {
        "gazette_id": "2303/17",
        "published_date": "2022-10-26",
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

