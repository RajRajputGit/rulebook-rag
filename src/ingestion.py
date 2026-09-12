import os
import glob
from typing import List, Dict, Any
import pymupdf  # PyMuPDF for PDF extraction

def parse_markdown_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Parses a markdown document into logical section-based chunks with source metadata.
    """
    chunks = []
    filename = os.path.basename(filepath)
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    lines = content.split("\n")
    current_chapter = "General Regulations"
    current_section = "Introduction"
    current_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## CHAPTER"):
            # Save previous chunk if non-empty
            if current_lines:
                text = "\n".join(current_lines).strip()
                if len(text) > 40:
                    chunks.append({
                        "source": filename,
                        "section": f"{current_chapter} - {current_section}",
                        "page": None,
                        "text": text
                    })
                current_lines = []
            current_chapter = stripped.lstrip("#").strip()
            current_section = "Overview"
        elif stripped.startswith("### Section"):
            if current_lines:
                text = "\n".join(current_lines).strip()
                if len(text) > 40:
                    chunks.append({
                        "source": filename,
                        "section": f"{current_chapter} - {current_section}",
                        "page": None,
                        "text": text
                    })
                current_lines = []
            current_section = stripped.lstrip("#").strip()
        else:
            current_lines.append(line)
            
    if current_lines:
        text = "\n".join(current_lines).strip()
        if len(text) > 40:
            chunks.append({
                "source": filename,
                "section": f"{current_chapter} - {current_section}",
                "page": None,
                "text": text
            })
            
    return chunks

def parse_pdf_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Parses a PDF document page by page into section chunks with page number metadata.
    """
    chunks = []
    filename = os.path.basename(filepath)
    
    doc = pymupdf.open(filepath)
    for page_idx in range(len(doc)):
        page_num = page_idx + 1
        page = doc[page_idx]
        text = page.get_text()
        
        # Split text by double newlines or section headers
        blocks = text.split("================================================================================")
        for block in blocks:
            cleaned = block.strip()
            if len(cleaned) < 30:
                continue
            
            # Extract section title if available
            lines = cleaned.split("\n")
            section_title = f"Page {page_num}"
            for line in lines:
                if line.strip().startswith("SECTION"):
                    section_title = line.strip()
                    break
                    
            chunks.append({
                "source": filename,
                "section": section_title,
                "page": page_num,
                "text": cleaned
            })
            
    doc.close()
    return chunks

def load_corpus(corpus_dir: str = "corpus") -> List[Dict[str, Any]]:
    """
    Loads and parses all Markdown and PDF documents in the corpus directory.
    """
    all_chunks = []
    
    md_files = glob.glob(os.path.join(corpus_dir, "*.md"))
    for md_path in md_files:
        chunks = parse_markdown_file(md_path)
        all_chunks.extend(chunks)
        
    pdf_files = glob.glob(os.path.join(corpus_dir, "*.pdf"))
    for pdf_path in pdf_files:
        chunks = parse_pdf_file(pdf_path)
        all_chunks.extend(chunks)
        
    print(f"Loaded total of {len(all_chunks)} chunks from corpus '{corpus_dir}'.")
    return all_chunks

if __name__ == "__main__":
    chunks = load_corpus("corpus")
    print(f"Sample chunk 1: {chunks[0]}")
