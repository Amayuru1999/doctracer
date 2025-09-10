import json
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
            # print("❌ JSON decode failed. Raw response was:\n", raw_json)
            raise e


    
    def _extract_changes(self, text: str) -> dict:
        return self._extract_changes_from_text(text)

    def process_gazettes(self) -> str:
        # Default metadata
        meta = {
            "Gazette ID": "1970/01",
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
            gazette_id=meta.get("Gazette ID", ""),
            published_date=meta.get("Gazette Published Date", "1970-01-01"),
            published_by=meta.get("Gazette Published By", "Authority"),
            president=meta.get("President", ""),
            gazette_type=meta.get("Gazette Type", "Extraordinary"),
            language=meta.get("Language", "English"),
            pdf_url=meta.get("PDF URL", ""),
            ministers=ministers
        )

        return gazette.model_dump_json(indent=2)
