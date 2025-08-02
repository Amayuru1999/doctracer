from agentic_doc.parse import parse
from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.getenv("VISION_AGENT_API_KEY")
if not api_key:
    raise ValueError("API key is not set. Please provide a valid API key.")

pdf_path = "/Users/amayuruamarasinghe/Documents/University/7 Semester/Doctracer/doctracer/doctracer/landing-ai/data/2303-17_E_2022_10_26.pdf"
result = parse(pdf_path)

markdown_content = result[0].markdown
chunks = result[0].chunks

print("### Extracted Markdown ###\n")
print(markdown_content)

# Save markdown to a file
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)  # Create folder if it doesn't exist

output_md_file = os.path.join(output_dir, "extracted_result.md")
with open(output_md_file, "w", encoding="utf-8") as f:
    f.write(markdown_content)

print(f"\n✅ Markdown has been saved to {output_md_file}")

