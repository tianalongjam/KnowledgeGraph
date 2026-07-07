import json
import os
import time
from urllib.request import Request, urlopen

HEADERS = {"User-Agent": "Tiana Longjam ltiana610@gmail.com"}

COMPANIES = {
    "microsoft": "0000789019",
    "ibm": "0000051143",
    "cisco": "0000858877",
    "broadcom": "0001730168",
    "salesforce": "0001108524",
}

FORMS_WANTED = {"8-K", "DEF 14A"}
START_DATE = "2015-01-01"  # adjust to whatever range you want to cover
RAW_DIR = "raw"


def fetch_json(url):
    req = Request(url, headers=HEADERS)
    with urlopen(req) as resp:
        return json.loads(resp.read())


def fetch_bytes(url):
    req = Request(url, headers=HEADERS)
    with urlopen(req) as resp:
        return resp.read()


def get_filings(cik):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    recent = fetch_json(url)["filings"]["recent"]
    filings = []
    for i in range(len(recent["form"])):
        if recent["form"][i] in FORMS_WANTED and recent["filingDate"][i] >= START_DATE:
            filings.append({
                "form": recent["form"][i],
                "date": recent["filingDate"][i],
                "accession": recent["accessionNumber"][i],
                "primary_doc": recent["primaryDocument"][i],
            })
    return filings


def download_filing(cik, filing, company_name):
    accession_nodash = filing["accession"].replace("-", "")
    cik_int = str(int(cik))
    url = (
        f"https://www.sec.gov/Archives/edgar/data/"
        f"{cik_int}/{accession_nodash}/{filing['primary_doc']}"
    )

    company_dir = os.path.join(RAW_DIR, company_name)
    os.makedirs(company_dir, exist_ok=True)

    form_label = filing["form"].replace(" ", "")
    filepath = os.path.join(company_dir, f"{filing['date']}_{form_label}.htm")

    if os.path.exists(filepath):
        return filepath

    with open(filepath, "wb") as f:
        f.write(fetch_bytes(url))
    return filepath


def main():
    for company_name, cik in COMPANIES.items():
        print(f"Fetching filings for {company_name}...")
        filings = get_filings(cik)
        print(f"  Found {len(filings)} 8-K/DEF 14A filings since {START_DATE}")
        for filing in filings:
            path = download_filing(cik, filing, company_name)
            print(f"    saved {path}")
            time.sleep(0.2)  # be polite to SEC's rate limit


if __name__ == "__main__":
    main()