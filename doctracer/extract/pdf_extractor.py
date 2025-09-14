from pathlib import Path
import time
import logging
import re
import pdfplumber
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions

logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)

def extract_text_from_pdfplumber(pdf_path: str) -> str:
    """
    Extract metadata text from only the first page of the PDF.
    """
    with pdfplumber.open(pdf_path) as pdf:
        if not pdf.pages:
            return ""
        page_text = pdf.pages[0].extract_text() or ""
    return page_text.strip()

def extract_text_from_docling(pdf_path, output_dir="docling_txt") -> str:
    """
    Docling-powered drop-in replacement for legacy extract_text_from_docling.
    Preserves the same return type: full text string.
    Improves layout and prep by splitting amendment blocks and rejoining clearly.
    """
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

    # Prepare file paths
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    base_name = result.input.file.stem

    # Save raw outputs
    # md_path = out_dir / f"{base_name}.md"
    txt_path = out_dir / f"{base_name}.txt"
    # json_path = out_dir / f"{base_name}.json"

    raw_text = result.document.export_to_text()
    # md_path.write_text(result.document.export_to_markdown(), encoding="utf-8")
    txt_path.write_text(raw_text, encoding="utf-8")
    # with open(json_path, "w", encoding="utf-8") as f:
    #     json.dump(result.document.export_to_dict(), f, indent=2)

    # Extract change blocks and rebuild clean structured text
    change_blocks = _split_change_blocks(raw_text)
    if not change_blocks:
        return raw_text  # fallback

    # Reconstruct full text with separation between change blocks
    structured_text = "\n\n".join(
        [f"=== CHANGE {num} ===\n{block}" for num, block in change_blocks]
    )

    return structured_text


def _split_change_blocks(doc_text: str):
    """
    Splits layout text into amendment change blocks using numbered markers (e.g., - (1), - (2)).
    Returns:
        List[Tuple[int, str]]: List of (change_number, change_text)
    """
    # Normalize whitespace to avoid paragraph joins breaking numbering
    clean_text = re.sub(r'\r?\n', ' ', doc_text)
    blocks = re.split(r'-\s+\((\d+)\)\s+', clean_text)

    results = []
    for i in range(1, len(blocks) - 1, 2):
        number = int(blocks[i])
        change_text = blocks[i + 1].strip()
        results.append((number, change_text))

    return results
