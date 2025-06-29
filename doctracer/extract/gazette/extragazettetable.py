# import json
# import base64
# from pathlib import Path

# from doctracer.extract.pdf_extractor import extract_text_from_pdfplumber
# from doctracer.extract.gazette.gazette import BaseGazetteProcessor
# from doctracer.prompt.catalog import PromptCatalog
# from doctracer.prompt.config import SimpleMessageConfig
# from doctracer.prompt.executor import PromptConfigChat, PromptConfigImage, PromptExecutor
# from doctracer.prompt.provider import ServiceProvider, AIModelProvider
# from doctracer.models.gazette import GazetteData, MinisterEntry


# class ExtraGazetteTableProcessor(BaseGazetteProcessor):
#     def _initialize_executor(self) -> PromptExecutor:
#         return PromptExecutor(
#             ServiceProvider.OPENAI_VISION,
#             AIModelProvider.GPT_4O_MINI,
#             SimpleMessageConfig()
#         )

#     def _extract_metadata(self, text: str) -> dict:
#         """Run metadata prompt on extracted text (if available)."""
#         prompt = PromptCatalog.get_prompt(PromptCatalog.METADATA_EXTRACTION, text)
#         raw_meta = self.executor.execute_prompt(PromptConfigChat(prompt=prompt))
#         return json.loads(raw_meta)

#     def _extract_changes(self, image_path: str) -> dict:
#         """Run table extraction prompt on image content."""
#         prompt = PromptCatalog.get_prompt(PromptCatalog.CHANGES_TABLE_EXTRACTION)
#         image_b64 = self._encode_image(image_path)
#         raw_json = self.executor.execute_prompt(
#             PromptConfigImage(prompt=prompt, image=image_b64)
#         )
#         return json.loads(raw_json)

#     def _encode_image(self, image_path: str) -> str:
#         with open(image_path, "rb") as f:
#             return base64.b64encode(f.read()).decode("utf-8")

#     def process_gazettes(self) -> str:
#         # If input is an image, skip PDF text extraction
#         ext = Path(self.pdf_path).suffix.lower()
#         is_pdf = ext == ".pdf"

#         # Default metadata (fallback if PDF text extraction fails)
#         meta = {
#             "Gazette ID": "UNKNOWN",
#             "Gazette Published Date": "1970-01-01"  # valid fallback ISO date
#         }

#         if is_pdf:
#             try:
#                 text = extract_text_from_pdfplumber(self.pdf_path)
#                 meta = self._extract_metadata(text)
#             except Exception:
#                 pass  # Silently fall back

#         # Extract changes from image
#         table_data = self._extract_changes(self.pdf_path)

#         # Parse minister data
#         ministers = [MinisterEntry(**m) for m in table_data["ministers"]]

#         gazette = GazetteData(
#             gazette_id=meta["Gazette ID"],
#             published_date=meta["Gazette Published Date"],
#             ministers=ministers
#         )

#         # Return clean JSON
#         return gazette.model_dump_json(indent=2)



#######################

import json
from pathlib import Path

from doctracer.extract.pdf_extractor import extract_text_from_pdfplumber
from doctracer.extract.gazette.gazette import BaseGazetteProcessor
from doctracer.prompt.catalog import PromptCatalog
from doctracer.prompt.config import SimpleMessageConfig
from doctracer.prompt.executor import PromptConfigChat, PromptExecutor
from doctracer.prompt.provider import ServiceProvider, AIModelProvider
from doctracer.models.gazette import GazetteData, MinisterEntry


class ExtraGazetteTableProcessor(BaseGazetteProcessor):
    def _initialize_executor(self) -> PromptExecutor:
        return PromptExecutor(
            ServiceProvider.OPENAI,
            AIModelProvider.GPT_4O_MINI,
            SimpleMessageConfig()
        )

    def _extract_metadata(self, text: str) -> dict:
        """Run metadata prompt on extracted text (if available)."""
        prompt = PromptCatalog.get_prompt(PromptCatalog.METADATA_EXTRACTION, text)
        raw_meta = self.executor.execute_prompt(PromptConfigChat(prompt=prompt))
        return json.loads(raw_meta)

    def _extract_changes_from_text(self, text: str) -> dict:
        prompt = PromptCatalog.get_prompt(PromptCatalog.CHANGES_TABLE_EXTRACTION_FROM_TEXT, text)

        raw_json = self.executor.execute_prompt(PromptConfigChat(prompt=prompt))

        # 🔧 Fix: remove markdown-style ```json or ``` wrappers if present
        if raw_json.strip().startswith("```"):
            raw_json = raw_json.strip().strip("```json").strip("```").strip()

        if not raw_json.strip():
            raise ValueError("LLM returned empty response for table extraction")

        try:
            return json.loads(raw_json)
        except json.JSONDecodeError as e:
            print("❌ JSON decode failed. Raw response was:\n", raw_json)
            raise e


    
    def _extract_changes(self, text: str) -> dict:
        return self._extract_changes_from_text(text)

    def process_gazettes(self) -> str:
        # Default metadata
        meta = {
            "Gazette ID": "UNKNOWN",
            "Gazette Published Date": "1970-01-01"
        }

        # Extract layout-aware text using Docling
        text = extract_text_from_pdfplumber(self.pdf_path)

        # Extract metadata and changes from text
        try:
            meta = self._extract_metadata(text)
        except Exception:
            pass  # Fallback to defaults

        table_data = self._extract_changes_from_text(text)

        # Parse ministers list
        ministers = [MinisterEntry(**m) for m in table_data.get("ministers", [])]

        gazette = GazetteData(
            gazette_id=meta.get("Gazette ID", "UNKNOWN"),
            published_date=meta.get("Gazette Published Date", "1970-01-01"),
            ministers=ministers
        )

        return gazette.model_dump_json(indent=2)
