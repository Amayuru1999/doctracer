from enum import Enum

_METADATA_PROMPT_TEMPLATE: str = """
    You are an assistant tasked with extracting metadata from a government gazette document. Using the provided text, identify and return the following information in a compact JSON string:
    - gazette_no
    - published_date
    - published_by
    - gazette_type
    - language
    - pdf_url (Use the year and month from the published_date. For months 1-9, use a single-digit month in the pdf_url path. Also, use the gazette_no. For months 1-9, if the gazette_no. contains single-digit after "/", use double-digits to create pdf_url. For example, for published_date '2020-04-22' and gazette_no '2277/2, the pdf_url should be: 'https://documents.gov.lk/view/extra-gazettes/2020/4/2277-02_E.pdf')
    - amends (gazette_no, published_date, pdf_url)

    After extracting this metadata, if an Amends PDF URL is present, trigger a recursive extraction step to:
    - Download and extract text from the amended gazette PDF
    - Extract its metadata and changes using this same prompt suite
    - Link the amended gazette data back to the current gazette metadata

    Ensure the JSON string is compact, without any additional formatting or escape characters.
    Don't include unnecessary backward slashes or forward slashes unless the data contains them. 

    Input Text:
    {gazette_text}

    Sample JSON Output:
    {{
        "gazette_no": "1905/4",
        "published_date": "2015-03-09",
        "published_by": "Authority",
        "gazette_type": "Extraordinary",
        "language": "English",
        "pdf_url": "https://documents.gov.lk/view/extra-gazettes/2015/3/1905-04_E.pdf",
        "amends": {{
            "gazette_no": "1897/15",
            "published_date": "2015-01-18",
            "pdf_url": "https://documents.gov.lk/view/extra-gazettes/2015/1/1897-15_E.pdf"
        }}
    }}
"""

_CHANGES_AMENDMENT_PROMPT_TEMPLATE: str = """
    You are an assistant tasked with extracting changes from a government gazette document. Based on the provided text, identify and list the following operation types along with their details:
    - addition 
    - substitution
    - omission

    Use natural labels such as "Previous Name", "Clause ID", etc. Ensure the JSON is compact and free of unnecessary escape characters or formatting.

    Followings are include in each change (as applicable)
    - clause_id
    - heading_no
    - heading
    - column_no
    - adding_after
    - new_items/new acts (if column_no is 3 give "new_acts". otherwise use "new_items")
    - items_out/acts_out (if column_no is 3 give "acts_out". otherwise use "items_out")
    - items_in/acts_in (if column_no is 3 give "acts_in". otherwise use "items_in")
    - omitted_items/omitted_acts (if column_no is 3 give "omitted_acts". otherwise use "omitted_items")

    Input Text:
    {gazette_text}

    Sample JSON Output:
    {{
        "addition": [{{"clause_id":"1b", "heading_no": "No. 04", "heading":"Minister of Public Order, Disaster Management & Christian Affairs","column_no":"Column 2","adding_after":"item 8","new_items":["9. Department of Registration of Persons"]}}],
        "substitution": [{{"clause_id":"1b", "heading_no": "No. 04", "heading":"Minister of Public Order, Disaster Management & Christian Affairs", "column_no":"Column 1","items_out":["item 18", "item 19"],"items_in":["18. Registration of Persons", "19. All other subjects that come under the purview of Institutions listed in Column 2", "20. Supervision of the Institutions listed in Column 2"]}}],
        "omission": [{{"clause_id":"2c", "heading_no": "No. 05", "heading":"Minister of Home Affairs & Fisheries", "column_no":"Column 3","omitted_acts":"Registration of Persons Act, No. 32 of 1968"}}],
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

