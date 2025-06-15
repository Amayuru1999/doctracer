import json
from doctracer.extract.pdf_extractor import extract_text_from_pdfplumber
from doctracer.extract.gazette.gazette import BaseGazetteProcessor
from doctracer.prompt.catalog  import PromptCatalog
from doctracer.prompt.config   import SimpleMessageConfig
from doctracer.prompt.executor import PromptConfigChat, PromptExecutor
from doctracer.prompt.provider import ServiceProvider, AIModelProvider


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

    def process_gazettes(self) -> str:
        # 1. Read PDF text
        text = extract_text_from_pdfplumber(self.pdf_path)

        # 2. Call the LLM twice
        raw_meta    = self._extract_metadata(text)
        raw_changes = self._extract_changes(text)

        # 3. Parse into Python objects
        metadata = json.loads(raw_meta)
        changes  = json.loads(raw_changes)

        # 4. Combine and return as one JSON string
        output = {
            "metadata": metadata,
            "changes":  changes
        }
        return json.dumps(output, indent=2)
