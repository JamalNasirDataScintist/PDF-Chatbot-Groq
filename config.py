"""
Configuration Settings for DocuMind AI
Powered by Groq — Lightning-Fast LLM Inference
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    # Flask Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'documind-groq-applab-2026')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))

    # Upload Settings
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB max file size

    # Groq AI Settings
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
    GROQ_MAX_TOKENS = int(os.getenv('GROQ_MAX_TOKENS', 1024))
    GROQ_TEMPERATURE = float(os.getenv('GROQ_TEMPERATURE', 0.3))

    # Embedding Model (runs locally — no API needed)
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')

    # RAG Settings
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 500))  # words per chunk
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 50))  # word overlap
    TOP_K_CHUNKS = int(os.getenv('TOP_K_CHUNKS', 4))  # chunks to retrieve
