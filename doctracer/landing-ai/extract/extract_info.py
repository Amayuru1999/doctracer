from agentic_doc.parse import parse
from agentic_doc.utils import viz_parsed_document
from dotenv import load_dotenv
load_dotenv()
import os

api_key = os.getenv("VISION_AGENT_API_KEY")
if not api_key:
    raise ValueError("API key is not set. Please provide a valid API key.")

doc_path = "/Users/amayuruamarasinghe/Documents/University/7 Semester/Doctracer/doctracer/doctracer/landing-ai/data/2303-17_E_2022_10_26.pdf"
output_dir = "/Users/amayuruamarasinghe/Documents/University/7 Semester/Doctracer/doctracer/doctracer/landing-ai/output"

results = parse(doc_path)
parsed_doc = results[0]

images = viz_parsed_document(
    doc_path,
    parsed_doc,
    output_dir=output_dir
)