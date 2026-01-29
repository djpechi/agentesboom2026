# /backend/app/services/rag_service.py

import os
from typing import List, Dict

# Path to knowledge base
KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge")

async def get_knowledge_context(filenames: List[str]) -> str:
    """
    Retrieves the content of specific knowledge files to inject into the prompt.
    For MVP, we simply read the full text files.
    """
    context_parts = []
    
    for filename in filenames:
        file_path = os.path.join(KNOWLEDGE_DIR, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    context_parts.append(f"--- DOCUMENT: {filename} ---\n{content}\n")
            except Exception as e:
                print(f"Error reading {filename}: {e}")
        else:
            print(f"Knowledge file not found: {file_path}")
            
    return "\n".join(context_parts)

async def get_available_documents() -> List[str]:
    """List available documents in the knowledge base"""
    if not os.path.exists(KNOWLEDGE_DIR):
        return []
    return [f for f in os.listdir(KNOWLEDGE_DIR) if f.endswith(".txt") or f.endswith(".pdf")]
