from enum import Enum

_METADATA_PROMPT_TEMPLATE: str = """
    You are an assistant tasked with extracting metadata from a government gazette document. Using the provided text, identify and return the following information in a compact JSON string:
    - Gazette ID
    - Gazette Published Date
    - Gazette Published by
    - President (You can see clearly the president name by calling president tag in first page of the gazette)
    - Gazette Type
    - Language (If the language is not explicitly mentioned, default to "English")
    - PDF URL (Use the year and month from the published_date. For months 1-9, use a single-digit month in the pdf_url path. Also, use the gazette_no. For months 1-9, if the gazette_no. contains single-digit after "/", use double-digits to create pdf_url. For example, for published_date '2020-04-22' and gazette_no '2277/2, the pdf_url should be: 'https://documents.gov.lk/view/extra-gazettes/2020/4/2277-02_E.pdf')
    - Parent Gazette (Gazette ID, Gazette Published Date, PDF URL)

    Ensure the JSON string is compact, without any additional formatting or escape characters.
    Don't include unnecessary backward slashes or forward slashes unless the data contains them. 
    Input Text:
    {gazette_text}
    Sample JSON Output:
    {{
      "Gazette ID":"2303/17",
      "Gazette Published Date":"2022-10-26",
      "Gazette Published by":"Authority",
      "President":"Maithripala Sirisena", 
      "Gazette Type":"Extraordinary", 
      "Language":"English", 
      "PDF URL":"https://documents.gov.lk/view/extra-gazettes/2022/10/2303-17_E.pdf", 
      "Parent Gazette": {{
        "Gazette ID":"1897/15",
        "Gazette Published Date":"2015-01-18",
        "PDF URL":"https://documents.gov.lk/view/extra-gazettes/2015/1/1897-15_E.pdf"
      }}
    }}
    """

_CHANGES_AMENDMENT_PROMPT_TEMPLATE: str = """
    You are an assistant tasked with extracting changes from a government gazette document.
    Analyze the provided text to identify different types of amendments and extract their details.

    The document is structured using amendment blocks. Each amendment begins with a marker like:
    - (1)
    - (2)
    - (3)

    These indicate individual, self-contained changes. Each block represents **one distinct amendment** such as a deletion, insertion, update, or re-numbering.

    Focus on identifying explicit operations like "By deleting", "By insertion of the following new Heading", "is as follows" (indicating an update/redefinition), and "By re-numbering".

    Return a JSON array where each object represents a single amendment operation.

    Each object in the array should have an "operation_type" key, and a "details" key.
    The "operation_type" can be one of the following: "DELETION", "INSERTION", "UPDATE", "RENUMBERING".

    Here are the details to extract for each operation type:

    1.  For "DELETION" operations:
        -   "number": The number of the heading being deleted (e.g., "No. 3").
        -   "name": The name of the Minister or State Minister heading being deleted (e.g., "Minister of Finance").
        -   "column_no": The number of the column of the department/function/law. If it is function => Column 1, Department => Column 2, Law => Column 3 (e.g., "2").
        -   "deleted_sections": A list of deleted functions, departments and lows.
                - If the deleted_sections is a function or department it mention the item number only. Then include that item number/s. (e.g., "item 18, item 19")
                - If the deleted_sections is a law it mention the law. Then include that law/s. (e.g., "Tax Appeals Commission Act, No. 23 of 2008")

    2.  For "INSERTION" operations:
        -   "number": The number of the new heading (e.g., "3").
        -   "name": The name of the new Minister or State Minister heading (e.g., "Minister of Economic Policies & Plan Implementation").
        -   "column_no": The number of the column of the department/function/law. If it is function => Column 1, Department => Column 2, Law => Column 3 (e.g., "2").
        -   "purview": (Optional) The text of the "Purview" section, if present.
        -   "added_content": A list of strings of added department, function or law.
                  - If the added_content is a function or department it mention the item number and name. Then include the item number/s name/s. (e.g., "18. Registration of Persons", "19. All other subjects that come under the purview of Institutions listed in Column II")
                  - If the added_content is a law it mention the law. Then include that law/s. (e.g., "Tax Appeals Commission Act, No. 23 of 2008")

    3.  For "UPDATE" operations (indicated by "is as follows" for an existing heading or a specific section under a heading):
        -   "previous_number": The original heading number being updated 
        -   "previous_name": The original name of the Minister or State Minister before the update 
        -   "number": The number of the heading being updated (e.g., "No. 5.1").
        -   "name": The name of the Minister or State Minister heading being updated.
        -   "column_no": The number of the column of the department/function/law. If it is function => Column 1, Department => Column 2, Law => Column 3 (e.g., "2").
        -   "added_content": An object containing the new or updated content. This can include:
                - If the added_content is a function or department it mention the item number and name. Then include the item number/s name/s. (e.g., "18. Registration of Persons", "19. All other subjects that come under the purview of Institutions listed in Column II")
                - If the added_content is a law it mention the law. Then include that law/s. (e.g., "Tax Appeals Commission Act, No. 23 of 2008")
        -   "deleted_sections": A list of deleted functions, departments and lows.
                - If the deleted_sections is a function or department it mention the item number only. Then include that item number/s. (e.g., "item 18, item 19")
                - If the deleted_sections is a law it mention the law. Then include that law/s. (e.g., "Tax Appeals Commission Act, No. 23 of 2008")

    4.  For "RENUMBERING" operations:
        -   "previous_number": The original heading number.
        -   "new_number": The new heading number.
        -   "name": The name of the Minister or State Minister whose heading is re-numbered.
        -   "column_no": The number of the column of the department/function/law. If it is function => Column 1, Department => Column 2, Law => Column 3 (e.g., "2").
        
    5.  If a change does not clearly match any of the above categories (DELETION, INSERTION, UPDATE, RENUMBERING),
        use an appropriate custom "operation_type" that best fits the nature of the change. This could be something like:
        - "REALLOCATION"
        - "RESTRUCTURING"
        - "CLARIFICATION"
        - "MERGE"
        - "SPLIT"
        - "OTHER"

        In such cases:
        - Provide a descriptive name as "operation_type"
        - Still use a "details" dictionary to describe what is happening as specifically as possible
        - Include any fields that are extractable, such as involved minister names, affected laws, or textual edits

        This ensures no change is skipped even if it doesn't perfectly match the predefined categories.


    Ensure the JSON output is compact, without any additional formatting or escape characters like triple backticks.
    If a section is not applicable or not found for a specific operation, omit it or use an empty list/object.

    ---

    Example Change Text:
    - (2) 'By insertion of the following new Heading and '01. Purview, 02. Subjects and Functions, 03. Special Priorities and 04. Related Institutional and Legal Framework' under thereof after the Heading No. '2.1 State Minister of Digital Technology and Enterprise Development' in that notification;

## 3 Minister of Economic Policies &amp; Plan Implementation

## 01. Purview

Planning and implementation of relevant policies, in order to accelerate economic development and social progress based on the National Policy Statement: 'Vistas of Prosperity and Splendour'.

## 02. Subjects and Functions

- 1. Formulating policies in relation to the subject of economic policies and plan implementation  in conformity , with the prescribed Laws, Acts and Ordinances, implementation of projects under the national budget, state Investment and National Development Programme, and formulating, implementing, monitoring and evaluating policies, programmes and projects, related to subjects and functions under below-mentioned State Corporations and Statutory Institutions for 'economic policies &amp; plan implementation' based on the  national  policies  implemented by the government, and in accordance with the policy statement 'Vistas of Prosperity and Splendour'.
- 2. Facilitating of carrying out relevant development activities while coordinating all ministries with the Presidential Task Force for Economic Revival and Poverty Alleviation and the Presidential Task Force for transform Sri Lanka into a Green Socio economy with Sustainable Solutions for Climate Changes.
- 3. Coordinating with the Presidential Task Force for Gama Samaga Pilisandara Rural Development.
- 4. Monitoring and reviewing the cost of living and the flow of goods and services among the community of consumer, making periodic requests to the Cabinet Committee on Cost of Living to ensure that consumers as well as local producers and suppliers to receive goods and services at the reasonable prices.
- 5. Implementing people-centric development activities by coordinating the development activities of District and Divisional Development Committees and Provincial Councils.

## 03. Special  Priorities

- 1. Formulation and implementation of national development programmes and projects to achieve the sustainable  development goals in accordance with the Policy Statement; 'Vistas of Prosperity and Splendour'
- 2. Formulation of national policies
- 3. Co-ordination of State, Private and Co-operative sectors for facilitating the private sector participation in economic development
- 4. Implementation of rural and regional economic development policies and strategies.
- 5. Co-ordination of all Ministries and other relevant institutions for directing the infrastructure development, investment promotion, regulation of organic fertilizer  production  and  other  Government  flagship development programmes towards the expected goals.
- 6. Take necessary measures to consolidate International Banks, funds and local Banks to uplift the rural and regional economy while strengthening grass root level network of service delivery network.

## 04. Related Institutional and Legal Framework

| Departments, Statutory Institutions and Public Corporations                                                                                                                                                                                                                                                                                                                       | Laws and Ordinance to be Implemented                                                                                                                                                                                                                                                                                                                                                                                                              |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1. National Planning Department 2. Department of Census and Statistics 3. Institute of Policy Studies 4. Sustainable Development Council 5. Office of Comptroller General 6. Department of Valuation 7. Sri LankaAccounting and Auditing Standard Monitoring Board 8. Public Utilities Commission of Sri Lanka 9. Welfare Benefits Board 10. Public Service Mutual Provident Fund | • Census Ordinance (Chapter 143) • Institute of Policy Studies of Sri Lanka Act No. 53 of 1988 • The Sustainable Development Act No. 19 of 2017 • Sri Lanka Accounting and Auditing Standards Act, No. 15 of 1995 • Public Utilities Commission of Sri Lanka Act, No. 35 of 2002 • Welfare Benefits Act, No. 24 of 2002 • Public Service Mutual Provident Association Ordinance, No. 5 of 1891 • Strategic Development Project Act No. 14 of 2008 |


    Expected JSON:
    [
      {{
        "operation_type": "INSERTION",
        "details": {{
          "number": "3",
          "name": "Minister of Economic Policies & Plan Implementation",
          "column_no": "2",
          "purview": "Planning and implementation of relevant policies, in order to accelerate economic development and social progress based on the National Policy Statement: 'Vistas of Prosperity and Splendour'.",
          "added_content": [
              "9. Department of Registration of Persons",
              "18. Registration of Persons",
            ]
          }}
        }}
      }}
    ]

    Example Change Text:
    - (5) '01.  Purview,  02.  Subjects  and  Functions,  03.  Special  Priorities  and  04.  Related    Institutional  and Legal Framework'  under the Heading 'No. 3 Minister of Finance'  of  the  said  Notification  is  as follows;

## 6 Minister of Finance

## 01. Purview

Responsibilities in relation to macro-economic policies, annual budget and Appropriation Acts, public financial management, local and foreign savings and investments, public debts, banking, finance and insurance activities,  international  financial  cooperation  and  directing  social  security  and  economic development activities.

## 02. Subjects and Functions

Providing policy guidance to relevant State Ministries, and formulating policies in relation to the subject of Finance  in conformity with the prescribed Laws, Acts and Ordinances, implementation of projects , under the national budget, state Investment and National Development Programme, and formulating, implementing, monitoring and evaluating policies, programmes and projects, related to subjects and functions under below-mentioned Departments, State Corporations and Statutory Institutions for the creation of a 'People Centric Economy' based on the national policies implemented by the government, and in line with the policy statement 'Vistas of Prosperity and Splendour'.

## 03. Special Priorities

- 1. Establishing a sustained, high economic growth rate that distributes benefits to all, covers all provinces, and minimizes income disparities
- 2. Reducing unemployment giving priority to low income earners and increasing per capita income
- 3. Ensuring price stability by maintaining annual average inflation rate at a low level
- 4. Reducing uncertainties in public revenue policies by reducing budget deficit and public debt
- 5. Expanding financial resources and economic needs by maintaining loan interest rate at a lower level
- 6. Stabilizing the interest rates, financial and balance of payment policies in order to ensure that the exchange value of the rupee is maintained at a stable level.

- 7. Introducing measures to promote domestic production, empower low-income earners and incentivize investments
- 8. Expanding the business environment for the domestic business community in a manner that would provide benefits to general public.
- 9. Strengthening public enterprises.
- 10. Strengthening the institutional structure required for the efficient management of state revenue and expenditure

## 04.   Related Institutional and Legal Framework

| Departments, Statutory Institutions and Public Corporations                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Laws and Ordinance to be Implemented                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1. TreasuryAffairs i. General Treasury ii. Department of Fiscal Policy iii. Department of National Budget iv. Department of Management Services v. Department of External Resources vi. Department of Public Finance vii. Department of Treasury Operations viii. Department of Public Accounts i x. Department of Trade and Investment Policies x. Department of Information Technology Management xi. Department of LegalAffairs xii. Department of ManagementAuditing xiii. Department of Development Finance 2. Government Revenue Management Affairs i. Department of Inland Revenue ii. Sri Lanka Customs iii. Department of Excise iv. National Lotteries Board v. Development Lotteries Board vi. Import and Export Control Department 3. Bank Financial and Capital Market Policies and Regulatory Affairs i. Central Bank of Sri Lanka ii. All State Banks, Financial, Insurance and their subsidiaries and related institutions iii. Sri Lanka Insurance Board iv. Sri Lanka Insurance Corporation and its subsidiaries and affiliated companies v. Credit Information Bureau vi. Department of Registrar Companies | • Appropriation Acts • Customs Ordinance, No. 17 of 1956 • Foreign Loans Act, No. 29 of 1957 • Debits Tax Act, No. 12 of 2007 • Betting and Gaming Levy Act, No. 40 of 1998 • Economic Service Charge Act, No. 13 of 2006 • Excise Ordinance (Chapter 52) • Finance Leasing Act, No. 56 of 2000 • Financial Transactions Reporting Act, No. 6 of 2006 • Public Fiscal Management (Responsibility) Act, No. 3 of 2003 • Inland Revenue Act, No. 10 of 2006 • Regulation of Insurance Industry Act, No. 43 of 2000 • Lady Lochore Fund Act, No. 38 of 1951 • Local Treasury Bills Ordinance, No. 38 of 1923 • Nation Building Tax Act, No. 9 of 2009 • Business Names Act, No 07 of 1987 • Companies Act No. 07 of 2007 • Trade Marks Act No. 30 of 1964 • Cheetus Ordinance No 61 of 1935 • Public Contract Act No. 03 0f 1987 • Prevention of Money Laundering Act, No. 5 of 2006 • Import and Export (Control) Act, No. 1 of 1969 • Stamp Duty (Special Provisions) Act, No. 12 of 2006 • Stamps Duty Act, No. 43 of 1982 • Value Added Tax Act, No. 14 of 2002 • Finance Act, No. 38 of 1971 • Environment Conservation Levy Act, No. 26 of 2008 • Tax Appeals Commission Act, No. 23 of 2008 • Development Lotteries Board Act, No. 20 of 1997 • Sri Lanka Export Credit Insurance Act, No. 15 of 1978 • Monetary Law Act No. 58 of 1949 |

| Departments, Statutory Institutions and Public Corporations                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Laws and Ordinance to be Implemented                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| vii. Security and Exchange Commission of Sri Lanka viii. Sri Lanka Export Credit Insurance 4. Provision of Funds i. Lady Lochore Fund ii. Strike, Riot, Civil Commotion and Terrorism Fund iii. National Insurance Trust Fund iv. Employees'Trust Fund v. ShramaVasana Fund vi. National Health Development Fund vii. Kidney Fund viii. Tea Shakthi Fund ix. Kapruka Fund x. Public Service Pensioners' Trust Fund xi. Buddha Sasana Fund xii. Buddhist Renaissance Fund xiii. Skills Development Fund Ltd. xiv. Local Loans and Development Fund xv. Inventors' Fund xvi. Thurusaviya Fund xvii. Central Cultural Fund \ 5. Institutions to be liquidated orGLYPH<31> amalgamatedwithotherInstitutions i. Department of Telecommunications ii. Wildlife Trust iii. Sri Lanka Media Training Institute iv. Internal Trade Department v. Pulse Crops, Grain Research and Production Authority vi. Janatha Fertilizer Enterprises Ltd vii. Protection of Children National Trust Fund | • National Savings Bank Act, No. 30 of 1971 • People's Bank Act, No. 29 of 1961 • Bank of Ceylon Ordinance No. 53 of 1938 • Banking Act, No. 30 of 1988 • Recovery of loans by Banks (Special Provisions) Act, No. 4 of 1990 • Securities and Exchange Commission of Sri Lanka Act, No. 36 of 1987 • National Insurance Trust Fund Act, No. 28 of 2006·Employees' Trust Fund (Special Provisions) Act (No. 19 of 1993) • Employees Trust Fund Act, No. 46 of 1980 • Excise (Special Provisions) Act, No. 13 of 1989 • Registered Stock and Securities Ordinance No. 07 of 1937 • Payment and Settlement Systems Act, No. 28 of 2005 • Finance Business Act, No. 42 of 2011 • Foreign Exchange Act, No. 12 of 2017 • Insurance Corporation Act, No. 02 of 1961 • Shrama Vasana Fund Act No. 12 of 1998 • Tea Shakthi Fund Act, No. 47 of 2000 • Kapruka Fund Act, No. 31 of 2005 • Central Cultural Fund Act No. 57 of 1980 • Local loans and Development FundAct No. 22 of 1916 • Thurusaviya Fund Act, No. 23 of 2000 • Credit Information Bureau of Sri Lanka Act, No. 18 of 1990 • Rehabilitation of the Visually Handicapped Trust Fund Act No. 9 of 1992 |


expected output for this:
[
  {{
    "operation_type": "UPDATE",
    "details": {{
      "previous_number": "3",
      "previous_name": "Minister of Finance",
      "number": "6",
      "name": "Minister of Finance",
      "column_no": "4",
      "updated_content": {{
        "purview": "Responsibilities in relation to macro-economic policies, annual budget and Appropriation Acts, public financial management, local and foreign savings and investments, public debts, banking, finance and insurance activities, international financial cooperation and directing social security and economic development activities.",
        "added_content": [
            "18. Registration of Persons",
            "19. All other subjects that come under the purview of Institutions listed in Column II",
            "20. Supervision of the Institutions listed in Column II"
        ],
        "deleted_sections": [
          "item 18 and item 19"
        ],
        }}
      }}
    }}
  }}
]

    as above two example for a particular change , make sure that you extract everything related to that. 
    Also make sure that if there is previous minter number and name, include those as well, so then it clearly can see what is the change

    Now apply the same logic to each amendment block in the gazette text.

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

        {{
            "ministers": 
            [
                {{
                    "name": "Minister of Defence",
                    "number": "1",
                    "functions": [
                        "1. Ensure national security",
                        "2. Coordinate armed forces",
                        "3. Develop defense policies"
                    ],
                    "departments": [
                        "1. Office of the Chief of Defence Staff",
                        "2. Sri Lanka Army",
                        "3. Sri Lanka Navy"
                    ],
                    "laws": [
                        "National Security Act No. 45 of 2003",
                        "Military Ordinance No. 12 of 1945"
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
            ]
        }}

        Don't add any extra text such as ```json so that i can directly save the response to a json file.
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

    Do not consider about number order of the function or department. Just put the exact number which is infront of function or department. 
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
    CHANGES_AMENDMENT_EXTRACTION = "changes_amendment_extraction"
    CHANGES_TABLE_EXTRACTION = "changes_table_extraction"
    CHANGES_TABLE_EXTRACTION_FROM_TEXT = "changes_table_extraction_from_text"  # ✅ New prompt type

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
            # No gazette_text needed
            return _CHANGES_TABLE_PROMPT_TEMPLATE

        elif prompt_type == PromptCatalog.CHANGES_TABLE_EXTRACTION_FROM_TEXT:  # ✅ New case
            if gazette_text is None:
                raise ValueError("The 'gazette_text' parameter is required for CHANGES_TABLE_EXTRACTION_FROM_TEXT.")
            return _CHANGES_TABLE_EXTRACTION_FROM_TEXT.format(gazette_text=gazette_text)

        else:
            raise ValueError(f"Unsupported prompt type: {prompt_type}")
