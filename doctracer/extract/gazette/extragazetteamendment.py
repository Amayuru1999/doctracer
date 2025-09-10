import json
from doctracer.extract.pdf_extractor import extract_text_from_pdfplumber
from doctracer.extract.gazette.gazette import BaseGazetteProcessor
from doctracer.prompt.catalog  import PromptCatalog
from doctracer.prompt.config   import SimpleMessageConfig
from doctracer.prompt.executor import PromptConfigChat, PromptExecutor
from doctracer.prompt.provider import ServiceProvider, AIModelProvider
import re


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
        prompt = PromptCatalog.get_prompt(
            PromptCatalog.CHANGES_AMENDMENT_EXTRACTION,
            text
        )
        return self.executor.execute_prompt(PromptConfigChat(prompt=prompt))
    
    @staticmethod
    def _clean_json_string(raw: str) -> str:
        return re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())

    def process_gazettes(self) -> str:
        text = extract_text_from_pdfplumber(self.pdf_path)

        raw_meta    = self._extract_metadata(text)
        raw_changes = self._extract_changes(text)

        # 👇 Add debug prints here
        # print("=== RAW METADATA ===")
        # print(raw_meta)
        # print("=== RAW CHANGES ===")
        # print(raw_changes)

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

