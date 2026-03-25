# Construction of a dataset on Italian medicines

Course: Fundamentals of Programming and Data Management (Mod B)
University: Università degli Studi di Napoli Federico II
Authors: Hamayoon Baig (D03000190), Hussain Baig (D03000205)

---

## What this is

We scraped the AIFA (Italian Medicines Agency) website to build a structured dataset of Italian medicines from scratch. Starting from a list of 300+ AIC codes (the Italian drug identification numbers), we automated the download of each medicine's RCP document (Riassunto delle Caratteristiche del Prodotto), extracted specific clinical sections from the PDFs, assembled everything into an Excel file, normalized it into a SQLite database, and built a Power BI dashboard on top of it.

The whole thing is a data engineering pipeline: scraping, parsing, cleaning, storing, querying, and visualizing.

---

## Files

| File | What it is |
|------|------------|
| `download_all_pdfs.py` | Selenium script that searches the AIFA site by AIC code, downloads the RCP PDF for each medicine, and logs the ATC classification codes to a CSV |
| `extract_information.py` | PyMuPDF script that reads each downloaded PDF, extracts 10 specific clinical sections (4.1 through 4.9 plus 6.2), and saves everything to an Excel file |
| `Visualization_of_medicines.pbix` | Power BI dashboard with visualizations of active ingredients, therapeutic indications, and side effects |
| `Report_Hamayoon_Baig__D03000190_and_Hussain_Baig_D03000205.pdf` | Written project report |
| `README.md` | This file |

---

## How the pipeline works

### 1. Collecting the PDFs

`download_all_pdfs.py` reads a text file of AIC codes, prepends a leading zero (AIFA's search format), then uses Selenium with Chrome to:

- Open each medicine's page on `medicinali.aifa.gov.it`
- Scrape the ATC classification code from the detail page
- Trigger the PDF download
- Rename the downloaded file to `{AIC}.pdf`
- Log each AIC + ATC pair to `atc_codes.csv`

The script handles failures per-AIC and keeps going, so one bad page doesn't kill the whole run.

### 2. Extracting text from PDFs

`extract_information.py` loops through all downloaded PDFs using PyMuPDF (`fitz`). For each one it pulls the full text and uses regex to find these sections:

- 4.1 Therapeutic indications
- 4.2 Posology and method of administration
- 4.3 Contraindications
- 4.4 Special warnings and precautions for use
- 4.5 Interactions with other medicinal products
- 4.6 Fertility, pregnancy and lactation
- 4.7 Effects on ability to drive and use machines
- 4.8 Undesirable effects
- 4.9 Overdose
- 6.2 Incompatibilities

Each section's text runs from its heading to the start of the next numbered heading. If a section isn't found, it gets marked "Not found." Output is an Excel file with one row per medicine and one column per section.

### 3. Database and queries

The extracted data was loaded into SQLite using DB Browser, normalized into relational tables (`medicines`, `atc_classifications`, `contraindications`, `side_effects`) with foreign keys. Five analytical queries were written: medicine counts by ATC code, most frequent therapeutic indications, most common contraindications, medicines with the most side effects, and medicines grouped by equivalence class.

### 4. Visualization

A Power BI dashboard (`Visualization_of_medicines.pbix`) shows distribution of active ingredients, therapeutic indication frequencies, and side effect prevalence. You need Power BI Desktop to open the `.pbix` file.

---

## Difficulties we ran into

Some PDFs had inconsistent section formatting, which broke the regex extraction. The workaround was converting those to plain text first. A few documents had non-text-renderable content (scanned images instead of real text), which needed the same treatment. Power BI was new to us, so there was a learning curve there, but nothing that took too long to figure out.

---

## Tools

- Python 3 (Windows)
- Selenium + ChromeDriver for web scraping
- PyMuPDF (`fitz`) for PDF text extraction
- `pandas` for structuring the output
- `re` for regex-based section parsing
- `tqdm` for progress bars
- Power BI Desktop for the dashboard
- SQLite + DB Browser for the database

---

## Running the scripts

### download_all_pdfs.py

You'll need to edit three paths at the top of the file:

- `aic_file_path`: a text file with one AIC code per line
- `download_dir`: where the PDFs get saved
- `chromedriver_path`: path to your ChromeDriver executable

Then just run it. It opens a Chrome window and works through the list. Takes a while since there's a ~10 second wait per medicine (page load + download).

```bash
pip install selenium
python download_all_pdfs.py
```

### extract_information.py

Expects the PDFs to be in `~/Desktop/aifa_pdfs/`. Outputs an Excel file to the desktop.

```bash
pip install PyMuPDF pandas tqdm openpyxl
python extract_information.py
```

---

## License

Academic coursework.
