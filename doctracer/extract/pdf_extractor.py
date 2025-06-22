# from pdf2image import convert_from_path
# import pdfplumber
# from io import BytesIO


# # Function to extract text from the PDF
# def extract_text_from_pdfplumber(pdf_path):
#     with pdfplumber.open(pdf_path) as pdf:
#         return "\n".join(page.extract_text() for page in pdf.pages)
from pathlib import Path
import json
import time
import logging

from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions

logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)

def extract_text_from_pdfplumber(pdf_path, output_dir="output"):
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True

    doc_converter = DocumentConverter(
        allowed_formats=[InputFormat.PDF],
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        },
    )

    start_time = time.time()
    result = doc_converter.convert(pdf_path)
    _log.info(f"Document converted in {time.time() - start_time:.2f} seconds.")

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    base_name = result.input.file.stem

    md_path = out_dir / f"{base_name}.md"
    txt_path = out_dir / f"{base_name}.txt"
    json_path = out_dir / f"{base_name}.json"

    md_path.write_text(result.document.export_to_markdown(), encoding="utf-8")
    txt_path.write_text(result.document.export_to_text(), encoding="utf-8")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result.document.export_to_dict(), f, indent=2)

    return txt_path.read_text(encoding="utf-8")

