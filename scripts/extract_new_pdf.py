import pypdf
from pathlib import Path

pdf_path = "SPP Руководство пользователя_5.3.pdf"
output_path = "pdf_5.3_content.txt"

def extract():
    print(f"Extracting from {pdf_path}...")
    try:
        reader = pypdf.PdfReader(pdf_path)
        with open(output_path, "w", encoding="utf-8") as f:
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                f.write(f"--- Page {i+1} ---\n")
                f.write(text)
                f.write("\n\n")
        print("Extraction complete.")
    except Exception as e:
        print(f"Error extracting PDF: {e}")

if __name__ == "__main__":
    extract()
