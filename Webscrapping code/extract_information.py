import os
import re
import fitz  # PyMuPDF
import pandas as pd
from tqdm import tqdm

# --- CONFIGURATION ---
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
pdf_folder = os.path.join(desktop_path, "aifa_pdfs")
output_file = os.path.join(desktop_path, "estratti_aifa_all_available.xlsx")

# --- Sections to extract ---
sections_to_extract = [
    "4.1 Therapeutic indications",
    "4.2 Posology and method of administration",
    "4.3 Contraindications",
    "4.4 Special warnings and precautions for use",
    "4.5 Interactions with other medicinal products",
    "4.6 Fertility, pregnancy and lactation",
    "4.7 Effects on ability to drive and use machines",
    "4.8 Undesirable effects",
    "4.9 Overdose",
    "6.2 Incompatibilities"
]

# Precompile regex for section headings
section_regex = re.compile(r"(4\.1|4\.2|4\.3|4\.4|4\.5|4\.6|4\.7|4\.8|4\.9|6\.2)\s+([^\n]+)", re.IGNORECASE)

# --- Function to extract section text ---
def extract_sections_from_text(text):
    matches = list(section_regex.finditer(text))
    section_dict = {}

    for i, match in enumerate(matches):
        section_num = match.group(1)
        section_title = match.group(2).strip()
        section_key = f"{section_num} {section_title}"
        section_key_clean = next((s for s in sections_to_extract if s.lower().startswith(section_num)), None)
        if not section_key_clean:
            continue
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section_text = text[start:end].strip()
        section_dict[section_key_clean] = section_text

    # Add missing sections as "Not found"
    for s in sections_to_extract:
        if s not in section_dict:
            section_dict[s] = "Not found"

    return section_dict

# --- Process all PDFs ---
data = []
pdf_files = sorted(f for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf"))

for filename in tqdm(pdf_files, desc="Processing PDFs"):
    aic = filename.replace(".pdf", "")
    pdf_path = os.path.join(pdf_folder, filename)
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()

        extracted = extract_sections_from_text(full_text)
        extracted["AIC"] = aic
        data.append(extracted)

    except Exception as e:
        print(f"Error processing {filename}: {e}")

# --- Save to Excel ---
df = pd.DataFrame(data)
df = df[["AIC"] + sections_to_extract]  # Column order
df.to_excel(output_file, index=False)

print(f"\n✅ Extraction complete. File saved to:\n{output_file}")
