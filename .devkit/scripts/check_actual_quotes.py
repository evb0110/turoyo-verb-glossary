#!/usr/bin/env python3
"""Check what quote characters are ACTUALLY in the DOCX"""

from docx import Document

doc = Document('.devkit/new-source-docx/3. h,ḥ,k.docx')

# Find the paragraph with ʕafu
for para in doc.paragraphs:
    text = para.text.strip()
    if 'ʕafu' in text and 'begnadigen' in text:
        print(f"Found paragraph:")
        print(f"{text}\n")

        print("All characters with codes:")
        for i, char in enumerate(text):
            code = ord(char)
            if code > 127 or char in ["'", '"', "`"]:
                print(f"  Pos {i:3}: '{char}' = U+{code:04X} ({code})")

        print(f"\nChecking for specific quote ranges:")
        print(f"  U+0027 (')  : {chr(0x0027) in text}")
        print(f"  U+2018 (')  : {chr(0x2018) in text}")
        print(f"  U+2019 (')  : {chr(0x2019) in text}")
        print(f"  U+02BB (ʻ)  : {chr(0x02BB) in text}")
        print(f"  U+02BC (ʼ)  : {chr(0x02BC) in text}")

        break
