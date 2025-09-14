from doctracer.extract import extract_text_from_docling

def test_extract_text_from_docling():
    pdf_path = "data/testdata/simple.pdf"
    text = extract_text_from_docling(pdf_path)
    assert text == "Hello Lanka Data Foundation"
