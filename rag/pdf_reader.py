from pypdf import PdfReader
import re

PDF_PATH = "knowledge base/services.pdf"

pdf = PdfReader(PDF_PATH)

full_text = ""

for page in pdf.pages:
    text = page.extract_text()

    if text:
        full_text += text + "\n"

full_text = re.sub(r"\n+", "\n", full_text)
full_text = full_text.strip()

print("Total characters:", len(full_text))

chunks = []

sections = re.split(
    r"\n(?=(?:FAQ\s+\d+|Trademark Registration|Trademark Hearing|Trademark Objection|Trademark Renewal|International Trademark Registration|Well-Known Trademark Services|Copyright Registration|Design Registration|Patent Registration|IP Monitoring & Journaling|Legal Services|Geographical Indication|Good Manufacturing Practices|ISO 9001|ISO 13485|ISO 14001|ISO 22000|ISO 45001|ISO 27001|FSSAI License & Registration|APEDA Registration|BIS Certification|Spice Board Certification|Barcode Registration|IEC Registration|MSME|Domain Registration|Logo Design|Brand Development|Custom Websites|CopyHart))",
    full_text,
    flags=re.IGNORECASE
)

for section in sections:
    section = section.strip()

    if len(section) > 100:
        chunks.append(section)

faq_pattern = re.compile(
    r"FAQ\s+\d+.*?(?=FAQ\s+\d+|\Z)",
    re.IGNORECASE | re.DOTALL
)

faqs = faq_pattern.findall(full_text)

for faq in faqs:
    faq = faq.strip()

    if len(faq) > 100:
        chunks.append(faq)

final_chunks = []
seen = set()

for chunk in chunks:
    normalized = re.sub(r"\s+", " ", chunk).strip().lower()

    if normalized not in seen:
        final_chunks.append(chunk)
        seen.add(normalized)

chunks = final_chunks

print("Total chunks:", len(chunks))

for i, chunk in enumerate(chunks):
    print("\n")
    print("=" * 60)
    print("CHUNK:", i)
    print("=" * 60)
    print(chunk[:500])