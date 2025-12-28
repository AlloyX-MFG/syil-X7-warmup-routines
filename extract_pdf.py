#!/usr/bin/env python3
"""
Extract PDF content to Markdown format.
This script extracts text from the Siemens Programming Guide PDF and saves it as markdown.
"""

import sys
import os

def extract_with_pypdf2():
    """Extract PDF using PyPDF2 library."""
    try:
        import PyPDF2

        pdf_path = "Siemens Programming Guide 828D.pdf"
        md_path = "Siemens_Programming_Guide_828D.md"

        print(f"Extracting PDF: {pdf_path}")
        print(f"Using PyPDF2 library...")

        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)

            print(f"Total pages: {total_pages}")

            with open(md_path, 'w', encoding='utf-8') as md_file:
                # Write header
                md_file.write("# Siemens Programming Guide 828D\n\n")
                md_file.write(f"*Extracted from PDF - {total_pages} pages*\n\n")
                md_file.write("---\n\n")

                # Extract text from each page
                for page_num in range(total_pages):
                    if (page_num + 1) % 10 == 0:
                        print(f"Processing page {page_num + 1}/{total_pages}...")

                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()

                    if text.strip():
                        md_file.write(f"## Page {page_num + 1}\n\n")
                        md_file.write(text)
                        md_file.write("\n\n---\n\n")

        print(f"[SUCCESS] Successfully extracted PDF to {md_path}")
        return True

    except ImportError:
        print("PyPDF2 not installed.")
        return False
    except Exception as e:
        print(f"Error with PyPDF2: {e}")
        return False

def extract_with_pdfplumber():
    """Extract PDF using pdfplumber library."""
    try:
        import pdfplumber

        pdf_path = "Siemens Programming Guide 828D.pdf"
        md_path = "Siemens_Programming_Guide_828D.md"

        print(f"Extracting PDF: {pdf_path}")
        print(f"Using pdfplumber library...")

        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"Total pages: {total_pages}")

            with open(md_path, 'w', encoding='utf-8') as md_file:
                # Write header
                md_file.write("# Siemens Programming Guide 828D\n\n")
                md_file.write(f"*Extracted from PDF - {total_pages} pages*\n\n")
                md_file.write("---\n\n")

                # Extract text from each page
                for page_num, page in enumerate(pdf.pages):
                    if (page_num + 1) % 10 == 0:
                        print(f"Processing page {page_num + 1}/{total_pages}...")

                    text = page.extract_text()

                    if text and text.strip():
                        md_file.write(f"## Page {page_num + 1}\n\n")
                        md_file.write(text)
                        md_file.write("\n\n---\n\n")

        print(f"[SUCCESS] Successfully extracted PDF to {md_path}")
        return True

    except ImportError:
        print("pdfplumber not installed.")
        return False
    except Exception as e:
        print(f"Error with pdfplumber: {e}")
        return False

def extract_with_pymupdf():
    """Extract PDF using PyMuPDF (fitz) library."""
    try:
        import fitz  # PyMuPDF

        pdf_path = "Siemens Programming Guide 828D.pdf"
        md_path = "Siemens_Programming_Guide_828D.md"

        print(f"Extracting PDF: {pdf_path}")
        print(f"Using PyMuPDF library...")

        pdf_document = fitz.open(pdf_path)
        total_pages = len(pdf_document)
        print(f"Total pages: {total_pages}")

        with open(md_path, 'w', encoding='utf-8') as md_file:
            # Write header
            md_file.write("# Siemens Programming Guide 828D\n\n")
            md_file.write(f"*Extracted from PDF - {total_pages} pages*\n\n")
            md_file.write("---\n\n")

            # Extract text from each page
            for page_num in range(total_pages):
                if (page_num + 1) % 10 == 0:
                    print(f"Processing page {page_num + 1}/{total_pages}...")

                page = pdf_document[page_num]
                text = page.get_text()

                if text.strip():
                    md_file.write(f"## Page {page_num + 1}\n\n")
                    md_file.write(text)
                    md_file.write("\n\n---\n\n")

        pdf_document.close()
        print(f"[SUCCESS] Successfully extracted PDF to {md_path}")
        return True

    except ImportError:
        print("PyMuPDF not installed.")
        return False
    except Exception as e:
        print(f"Error with PyMuPDF: {e}")
        return False

def main():
    """Try multiple PDF extraction libraries in order of preference."""
    print("=" * 60)
    print("PDF to Markdown Extractor")
    print("=" * 60)

    # Try libraries in order of preference
    methods = [
        ("PyMuPDF (fitz)", extract_with_pymupdf),
        ("pdfplumber", extract_with_pdfplumber),
        ("PyPDF2", extract_with_pypdf2),
    ]

    for method_name, method_func in methods:
        print(f"\nAttempting extraction with {method_name}...")
        if method_func():
            print("\n" + "=" * 60)
            print("SUCCESS!")
            print("=" * 60)
            return 0

    # If all methods failed
    print("\n" + "=" * 60)
    print("ERROR: No suitable PDF library found!")
    print("=" * 60)
    print("\nPlease install one of the following:")
    print("  pip install PyMuPDF")
    print("  pip install pdfplumber")
    print("  pip install PyPDF2")
    return 1

if __name__ == "__main__":
    sys.exit(main())
