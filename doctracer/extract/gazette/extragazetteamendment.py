# import json
# from doctracer.extract.pdf_extractor import extract_text_from_docling
# from doctracer.extract.gazette.gazette import BaseGazetteProcessor
# from doctracer.prompt.catalog  import PromptCatalog
# from doctracer.prompt.config   import SimpleMessageConfig
# from doctracer.prompt.executor import PromptConfigChat, PromptExecutor
# from doctracer.prompt.provider import ServiceProvider, AIModelProvider
# import re

# class ExtraGazetteAmendmentProcessor(BaseGazetteProcessor):

#     def _initialize_executor(self) -> PromptExecutor:
#         return PromptExecutor(
#             ServiceProvider.OPENAI,
#             AIModelProvider.GPT_4O_MINI,
#             SimpleMessageConfig()
#         )

#     def _extract_metadata(self, text: str) -> str:
#         prompt = PromptCatalog.get_prompt(
#             PromptCatalog.METADATA_EXTRACTION,
#             text
#         )
#         return self.executor.execute_prompt(PromptConfigChat(prompt=prompt))

#     def _extract_changes(self, text: str) -> dict:
#         prompt = PromptCatalog.get_prompt(
#             PromptCatalog.CHANGES_AMENDMENT_EXTRACTION,
#             text
#         )
#         raw = self.executor.execute_prompt(PromptConfigChat(prompt=prompt))
#         clean = self._clean_json_string(raw)
#         try:
#             return json.loads(clean)
#         except json.JSONDecodeError:
#             print(f"❌ Block output is not valid JSON! Block text:\n{text[:100]}...")
#             return {}

#     @staticmethod
#     def _clean_json_string(raw: str) -> str:
#         return re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())

#     def _split_into_blocks(self, text: str) -> list:
#         # Split on the marker inserted by pdf_extractor.py
#         blocks = re.split(r"=== CHANGE \d+ ===\n", text)
#         return [b.strip() for b in blocks if b.strip()]

#     def process_gazettes(self) -> str:
#         text = extract_text_from_docling(self.pdf_path)

#         raw_meta = self._extract_metadata(text)
#         try:
#             metadata = json.loads(raw_meta)
#         except json.JSONDecodeError:
#             print("⚠️ Metadata is not valid JSON!")
#             metadata = {}

#         # Split text into amendment blocks
#         blocks = self._split_into_blocks(text)
#         changes = []
#         for block in blocks:
#             change = self._extract_changes(block)
#             if change:
#                 # If the LLM returns a list, extend; else, append
#                 if isinstance(change, list):
#                     changes.extend(change)
#                 else:
#                     changes.append(change)

#         output = {
#             "metadata": metadata,
#             "changes": changes
#         }
#         return json.dumps(output, indent=2)
    
import json
from pydoc import text
from doctracer.extract.pdf_extractor import extract_text_from_pdfplumber
from doctracer.extract.pdf_extractor import extract_text_from_docling
from doctracer.extract.gazette.gazette import BaseGazetteProcessor
from doctracer.prompt.catalog  import PromptCatalog
from doctracer.prompt.config   import SimpleMessageConfig
from doctracer.prompt.executor import PromptConfigChat, PromptExecutor
from doctracer.prompt.provider import ServiceProvider, AIModelProvider
import re

def split_amendment_blocks(docling_text: str):
    """Split the gazette text into amendment blocks based on - (1), - (2), ..."""
    blocks = re.split(r"(?=\n-\s\(\d+\))", docling_text)
    return [b.strip() for b in blocks if b.strip()]

class ExtraGazetteAmendmentProcessor(BaseGazetteProcessor):

    def _initialize_executor(self) -> PromptExecutor:
        return PromptExecutor(
            ServiceProvider.OPENAI,
            AIModelProvider.GPT_4O_MINI,
            SimpleMessageConfig()
        )

    def _extract_metadata(self, text: str) -> str:
        prompt = PromptCatalog.get_prompt(
            PromptCatalog.METADATA_EXTRACTION,
            text
        )
        return self.executor.execute_prompt(PromptConfigChat(prompt=prompt))
    
    def _extract_changes(self, text: str) -> str:
        # 1️⃣ Split the full docling text into amendment blocks
        blocks = split_amendment_blocks(text)

        all_results = []

        # 2️⃣ Process each block separately using the same prompt template
        for block in blocks:
            prompt = PromptCatalog.get_prompt(
                PromptCatalog.CHANGES_AMENDMENT_BLOCK_EXTRACTION,
                gazette_text=block
            )
            raw_result = self.executor.execute_prompt(PromptConfigChat(prompt=prompt))

            # 3️⃣ Clean JSON string and parse
            try:
                clean_result = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_result.strip())
                block_json = json.loads(clean_result)
                all_results.extend(block_json if isinstance(block_json, list) else [block_json])
            except json.JSONDecodeError:
                print("❌ Failed to parse JSON for a block!")
                continue

        # 4️⃣ Return combined JSON of all blocks
        return json.dumps(all_results, ensure_ascii=False)

    @staticmethod
    def _clean_json_string(raw: str) -> str:
        return re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())

    def process_gazettes(self) -> str:

        plumber_text = extract_text_from_pdfplumber(self.pdf_path)
        docling_text = extract_text_from_docling(self.pdf_path)

        raw_meta    = self._extract_metadata(plumber_text)
        raw_changes = self._extract_changes(docling_text)

        # 👇 Optional: safely parse JSON with fallback
        try:
            metadata = json.loads(raw_meta)
        except json.JSONDecodeError:
            print("⚠️ Metadata is not valid JSON!")
            metadata = {}

        try:
            clean_changes = self._clean_json_string(raw_changes)
            changes = json.loads(clean_changes)
        except json.JSONDecodeError:
            print("❌ Changes output is not valid JSON!")
            print("❗ This is likely a prompt issue.")
            changes = {}

        output = {
            "metadata": metadata,
            "changes":  changes
        }
        return json.dumps(output, indent=2)

