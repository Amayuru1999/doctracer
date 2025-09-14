import re
import json
from doctracer.extract.pdf_extractor import extract_text_from_pdfplumber
from doctracer.extract.pdf_extractor import extract_text_from_docling
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
        """Run the LLM to extract ministers, functions, departments, and laws from a text block."""
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
    
    def _split_minister_blocks(self, docling_text: str) -> list[str]:
        """
        Split the docling text into blocks per minister.
        Each block starts with '## (X) Minister ...'.
        """
        pattern = r"(##\s*\(\d+\)\s*Minister[^\n]*)"
        matches = list(re.finditer(pattern, docling_text))

        if not matches:
            return [docling_text]  # fallback

        blocks = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(docling_text)
            blocks.append(docling_text[start:end].strip())
        return blocks
    
    def _extract_changes(self, text: str) -> dict:
        return self._extract_changes_from_text(text)

    def process_gazettes(self) -> str:
        
        # Step 1: Extract text from PDF
        plumber_text = extract_text_from_pdfplumber(self.pdf_path)
        docling_text = extract_text_from_docling(self.pdf_path)

        # Step 2: Extract metadata
        try:
            meta = self._extract_metadata(plumber_text)
        except Exception:
            pass  # Fallback to defaults

        # Step 3: Split docling text into minister blocks
        minister_blocks = self._split_minister_blocks(docling_text)

        # Step 4: Iteratively extract each block
        all_ministers = []
        for block in minister_blocks:
            try:
                result = self._extract_changes_from_text(block)
                if "ministers" in result:
                    all_ministers.extend(result["ministers"])
            except Exception as e:
                print(f"⚠️ Skipping block due to error: {e}")
                continue

        # Step 5: Merge duplicate ministers (by number)
        merged_ministers = {}
        for m in all_ministers:
            key = m.get("number") or m.get("name")
            if key not in merged_ministers:
                merged_ministers[key] = m
            else:
                for field in ["functions", "departments", "laws"]:
                    merged_ministers[key][field].extend(m.get(field, []))

        ministers_list = [MinisterEntry(**m) for m in merged_ministers.values()]

        # table_data = self._extract_changes_from_text(docling_text)

        # # Parse ministers list
        # ministers = [MinisterEntry(**m) for m in table_data.get("ministers", [])]

        # Step 6: Build final GazetteData object
        gazette = GazetteData(
            gazette_id=meta.get("Gazette ID", ""),
            published_date=meta.get("Gazette Published Date", "1970-01-01"),
            published_by=meta.get("Gazette Published By", "Authority"),
            president=meta.get("President", ""),
            gazette_type=meta.get("Gazette Type", "Extraordinary"),
            language=meta.get("Language", "English"),
            pdf_url=meta.get("PDF URL", ""),
            ministers=ministers_list
        )

        return gazette.model_dump_json(indent=2)
