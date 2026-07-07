import os

RAW_DIR = "raw"
DISCARD_DIR = "discarded"

# one or more acquisition-target keywords per company — only 8-Ks
# mentioning one of these are kept
KEYWORDS = {
    "microsoft": ["activision", "nuance", "linkedin"],
    "ibm": ["red hat", "hashicorp"],
    "cisco": ["splunk", "acacia"],
    "broadcom": ["vmware", "ca technologies", "symantec"],
    "salesforce": ["slack", "tableau", "mulesoft"],
}
for company, keywords in KEYWORDS.items():
    company_dir = os.path.join(RAW_DIR, company)
    if not os.path.isdir(company_dir):
        continue

    for filename in os.listdir(company_dir):
        filepath = os.path.join(company_dir, filename)

        # always keep DEF 14A filings, no keyword check needed
        if "DEF14A" in filename:
            continue

        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().lower()

        if any(keyword.lower() in content for keyword in keywords):
            continue  # match found, keep it in place

        discard_company_dir = os.path.join(DISCARD_DIR, company)
        os.makedirs(discard_company_dir, exist_ok=True)
        os.rename(filepath, os.path.join(discard_company_dir, filename))
        print(f"moved {filepath} -> {discard_company_dir} (no keyword match)")