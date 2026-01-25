# src/01_data_processing.py

import os
import fitz  # PyMuPDF
import re
import platform

def get_contracts_folder():
    """Finds the 'Capstone' folder on the user's Desktop."""
    home_dir = os.path.expanduser('~')
    desktop_name = 'Desktop'

    # Handle Windows "OneDrive" Desktops
    onedrive_desktop = os.path.join(home_dir, 'OneDrive', 'Desktop')
    local_desktop = os.path.join(home_dir, 'Desktop')

    if os.path.exists(os.path.join(onedrive_desktop, 'Capstone')):
        return os.path.join(onedrive_desktop, 'Capstone')
    elif os.path.exists(os.path.join(local_desktop, 'Capstone')):
        return os.path.join(local_desktop, 'Capstone')
    else:
        print(f"Error: Could not find 'Capstone' folder on your Desktop.")
        return None

def find_all_contract_paths():
    """
    Recursively finds all PDF paths in the Capstone folder.
    Returns a list of full file paths.
    """
    folder_path = get_contracts_folder()
    pdf_paths = []
    if folder_path:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                if filename.lower().endswith('.pdf'):
                    pdf_paths.append(os.path.join(dirpath, filename))
    return pdf_paths

def process_contract_pdf(pdf_path):
    """
    Opens a PDF and segments it into a list of "nodes" (clauses, sections).
    """
    print(f"\n--- Processing: {os.path.basename(pdf_path)} ---")

    # Define the regex patterns to identify different node types.
    patterns = [
        ("CLAUSE_NUM", re.compile(r'^\s*\d+\.\d+[\.\d]*\s+')),
        ("CLAUSE_SIMPLE_NUM", re.compile(r'^\s*\d+\.\s+')),
        ("SUB_CLAUSE_ALPHA", re.compile(r'^\s*\([a-z,i,v,x]+\)\s+')),
        ("SECTION_HEADER", re.compile(r'^\s*([A-Z]{4,}(\s[A-Z\d]+)*|ARTICLE\s[A-Z\d]+)')),
        ("DEF_HEADER", re.compile(r'^\s*[A-Z][a-zA-Z]+:')),
    ]

    doc = fitz.open(pdf_path)
    nodes = []

    for page in doc:
        text_blocks = page.get_text("blocks")

        for block in text_blocks:
            block_text = block[4].strip() # The 5th item (index 4) is the text

            if not block_text:
                continue 

            node_type = "TEXT" # Default type

            for n_type, pattern in patterns:
                match = pattern.match(block_text) 
                if match:
                    node_type = n_type
                    break 

            cleaned_content = re.sub(r'\s+', ' ', block_text).strip()

            if cleaned_content:
                nodes.append({
                    "type": node_type,
                    "content": cleaned_content
                })

    doc.close()
    print(f"Found {len(nodes)} nodes (clauses/paragraphs).")
    return nodes