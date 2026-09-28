"""
Intelligent Chatbot Service — Groq AI + RAG
Uses Retrieval Augmented Generation for accurate, context-aware answers

Architecture:
1. Document chunks are embedded using sentence-transformers
2. User questions are matched to relevant chunks via cosine similarity
3. Top-K chunks + question sent to Groq AI (llama-3.3-70b-versatile)
4. Groq returns intelligent, natural language answer
"""

import logging
from typing import Dict, List, Optional
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from groq import Groq
from config import Config

logger = logging.getLogger(__name__)


class Chatbot:
    """
    AI Chatbot using RAG (Retrieval Augmented Generation)
    
    Combines semantic search with Groq's lightning-fast LLM inference
    for intelligent document Q&A
    """

    SYSTEM_PROMPT = """You are DocuMind AI, an intelligent document assistant.

Your role:
- Answer questions based ONLY on the provided document context
- Be clear, accurate, and helpful
- Use bullet points or numbered lists when appropriate
- If the answer is not in the context, say "I couldn't find that information in the document"
- Reference specific details from the document when possible

Keep answers concise but complete."""

    def __init__(self):
        logger.info("Initializing Chatbot with Groq AI...")

        # Load local embedding model (no API needed)
        self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
        logger.info(f"✓ Embedding model loaded: {Config.EMBEDDING_MODEL}")

        # Document storage
        self.chunks: List[str] = []
        self.embeddings: List[torch.Tensor] = []
        self.metadata: List[Dict] = []

        # Groq client
        self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL
        self.max_tokens = Config.GROQ_MAX_TOKENS
        self.temperature = Config.GROQ_TEMPERATURE
        self.top_k = Config.TOP_K_CHUNKS

        logger.info(f"✓ Groq AI initialized: {self.model}")
        logger.info("✓ Chatbot ready!")

    def add_document(self, text: str, filename: str) -> str:
        """
        Process and index a document into the knowledge base
        
        Steps:
        1. Split text into overlapping chunks
        2. Generate embeddings for each chunk
        3. Store chunks + embeddings + metadata
        
        Args:
            text: Extracted document text
            filename: Original filename
            
        Returns:
            Document ID
        """
        logger.info(f"Indexing document: {filename}")
        
        # Split into chunks
        chunks = self._chunk_text(text)
        doc_id = f"doc_{len(self.metadata)}"

        # Generate embeddings for all chunks (batch processing for speed)
        embeddings = self.embedding_model.encode(chunks, convert_to_tensor=True)

        # Store everything
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            self.chunks.append(chunk)
            self.embeddings.append(emb)
            self.metadata.append({
                'doc_id': doc_id,
                'filename': filename,
                'chunk_index': i,
                'total_chunks': len(chunks)
            })

        logger.info(f"✓ Indexed {len(chunks)} chunks from '{filename}'")
        return doc_id

    def get_answer(self, question: str) -> Dict:
        """
        Generate AI answer using RAG pipeline
        
        Pipeline:
        1. Retrieve relevant chunks via semantic search
        2. Build context from top-K chunks
        3. Query Groq AI with context + question
        4. Return answer + sources + confidence
        
        Args:
            question: User's question
            
        Returns:
            Dict with answer, sources, confidence
        """
        # Step 1: Retrieve relevant chunks
        relevant_chunks = self._retrieve(question)

        if not relevant_chunks:
            return {
                'answer': "I couldn't find relevant information in the uploaded documents.",
                'sources': [],
                'confidence': 'low'
            }

        # Step 2: Build context
        context = self._build_context(relevant_chunks)

        # Step 3: Query Groq AI
        answer = self._query_groq(question, context)

        # Step 4: Build source references
        sources = [
            {
                'filename': chunk['metadata']['filename'],
                'chunk': chunk['metadata']['chunk_index'] + 1,
                'snippet': chunk['text'][:120] + '...' if len(chunk['text']) > 120 else chunk['text'],
                'relevance': round(chunk['score'] * 100, 1)
            }
            for chunk in relevant_chunks
        ]

        return {
            'answer': answer,
            'sources': sources,
            'confidence': self._calculate_confidence(relevant_chunks)
        }

    def _retrieve(self, question: str) -> List[Dict]:
        """
        Retrieve most relevant document chunks using semantic search
        
        Uses cosine similarity between question embedding and chunk embeddings
        """
        # Encode question
        q_embedding = self.embedding_model.encode(question, convert_to_tensor=True)

        # Calculate similarity scores
        scores = []
        for i, chunk_embedding in enumerate(self.embeddings):
            similarity = torch.cosine_similarity(
                q_embedding.unsqueeze(0),
                chunk_embedding.unsqueeze(0)
            ).item()
            scores.append((i, similarity))

        # Sort by relevance
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get top-K chunks (filter out low-relevance)
        top_chunks = scores[:self.top_k]

        return [
            {
                'text': self.chunks[idx],
                'metadata': self.metadata[idx],
                'score': score
            }
            for idx, score in top_chunks if score > 0.2
        ]

    def _build_context(self, chunks: List[Dict]) -> str:
        """Build clean context string from retrieved chunks"""
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i} - {chunk['metadata']['filename']}]\n{chunk['text']}"
            )
        return "\n\n---\n\n".join(context_parts)

    def _query_groq(self, question: str, context: str) -> str:
        """
        Send question + context to Groq AI and get answer
        
        Uses llama-3.3-70b-versatile for lightning-fast, high-quality responses
        """
        if not Config.GROQ_API_KEY:
            return "⚠️ Groq API key not configured. Please add GROQ_API_KEY to your .env file."

        try:
            # Build prompt
            user_message = f"""Based on the following document context, answer the question.

DOCUMENT CONTEXT:
{context}

QUESTION: {question}

Please provide a clear, accurate answer based only on the context above."""

            # Call Groq API
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            answer = chat_completion.choices[0].message.content.strip()
            logger.info("✓ Groq AI response received")
            return answer

        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            if "api_key" in str(e).lower():
                return "⚠️ Invalid Groq API key. Please check your .env file."
            elif "rate" in str(e).lower():
                return "⚠️ Rate limit reached. Please wait a moment and try again."
            return f"⚠️ Error generating answer: {str(e)}"

    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks for better context coverage
        
        Uses word-based chunking with overlap to maintain context
        """
        words = text.split()
        chunks = []
        step = Config.CHUNK_SIZE - Config.CHUNK_OVERLAP

        for i in range(0, len(words), step):
            chunk = ' '.join(words[i:i + Config.CHUNK_SIZE])
            if chunk.strip():
                chunks.append(chunk)

        return chunks

    def _calculate_confidence(self, chunks: List[Dict]) -> str:
        """Calculate confidence level based on similarity scores"""
        if not chunks:
            return 'low'
        
        avg_score = np.mean([c['score'] for c in chunks])
        
        if avg_score > 0.65:
            return 'high'
        elif avg_score > 0.45:
            return 'medium'
        return 'low'

    def has_documents(self) -> bool:
        """Check if any documents are loaded in knowledge base"""
        return len(self.chunks) > 0

    def get_document_list(self) -> List[Dict]:
        """Get list of all unique documents in knowledge base"""
        seen = {}
        for meta in self.metadata:
            doc_id = meta['doc_id']
            if doc_id not in seen:
                seen[doc_id] = {
                    'id': doc_id,
                    'filename': meta['filename'],
                    'chunks': meta['total_chunks']
                }
        return list(seen.values())

    def clear_documents(self):
        """Clear all documents from knowledge base"""
        self.chunks.clear()
        self.embeddings.clear()
        self.metadata.clear()
        logger.info("Knowledge base cleared")
