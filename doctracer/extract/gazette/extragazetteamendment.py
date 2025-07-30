import json
from doctracer.extract.pdf_extractor import extract_text_from_pdfplumber
from doctracer.extract.gazette.gazette import BaseGazetteProcessor
from doctracer.prompt.catalog import PromptCatalog
from doctracer.prompt.config import SimpleMessageConfig
from doctracer.prompt.executor import PromptConfigChat, PromptExecutor
from doctracer.prompt.provider import ServiceProvider, AIModelProvider
import os


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
        raw_meta = self._extract_metadata(text)
        raw_changes = self._extract_changes(text)

        # Print out raw changes for debugging
        # print("Raw changes:", raw_changes)

        # 3. Check for non-empty raw_changes
        if not raw_changes.strip():
            print("Error: No valid changes returned.")
            return json.dumps({"error": "No valid changes returned"}, indent=2)

        # 4. Check if raw_changes contains valid JSON
        try:
            changes = json.loads(raw_changes)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return json.dumps({"error": f"Failed to parse changes: {e}"}, indent=2)

        # 5. Check if raw_meta contains valid JSON
        try:
            metadata = json.loads(raw_meta)
        except json.JSONDecodeError as e:
            print(f"Error decoding metadata: {e}")
            return json.dumps({"error": f"Failed to parse metadata: {e}"}, indent=2)

        # 6. Combine the results into one dictionary, ensure it's not empty
        output = {
            "metadata": metadata,
            "changes": changes
        }

        # 7. Only write to file if both metadata and changes are valid
        if metadata and changes:  # Ensure both are non-empty
            output_file_path = "output/amendment/2015/1905-04_E_new.json"
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

            # Writing the output to a file
            try:
                with open(output_file_path, 'w') as outfile:
                    json.dump(output, outfile, indent=2)
                print(f"Output successfully saved to {output_file_path}")
            except Exception as e:
                print(f"Error saving to file: {e}")
        else:
            print("No valid data to save, file not created.")

        # Return the output as a JSON string (optional)
        return json.dumps(output, indent=2)
