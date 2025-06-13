from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_community.document_loaders import PyPDFLoader
import os
from typing import List, Dict
import json
from datetime import datetime

import shutil
import time

class RAGService:
    def __init__(self):
        # Initialize the embedding model
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vector_store = None
        self.documents = []
        self.current_document_metadata = {}

    
    ## NOT Working as expected to review later
    def cleanup_vector_store(self):
        """Clean up the vector store and its files"""
        import shutil, os, time
        from chromadb import PersistentClient

        # Dereference vector store
        self.vector_store = None

        # Try to reset the Chroma DB client
        try:
            client = PersistentClient(persist_directory="./chroma_db")
            client.reset()  # This clears collections and releases locks
            print("Chroma client reset successfully.")
        except Exception as e:
            print(f"Warning: Error resetting Chroma client: {e}")

        # Retry deletion
        for i in range(5):
            try:
                if os.path.exists("./chroma_db"):
                    shutil.rmtree("./chroma_db")
                    print("Deleted chroma_db folder.")
                    break
            except Exception as e:
                print(f"Warning: Attempt {i+1} - Error deleting chroma_db: {str(e)}")
                time.sleep(1)


    def process_pdf(self, pdf_path: str) -> None:
        """Process a PDF file and create vector embeddings"""
        # Load PDF
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()

        # Generate a unique collection name based on timestamp
        collection_name = f"pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Clean up existing vector store
        self.cleanup_vector_store()
        
        # Create metadata
        self.current_document_metadata = {
            'filename': os.path.basename(pdf_path),
            'processed_date': datetime.now().isoformat(),
            'total_pages': len(pages),
            'total_chunks': 0,
            'chunk_size': self.text_splitter._chunk_size,
            'chunk_overlap': self.text_splitter._chunk_overlap,
            'collection_name': collection_name
        }
        
        # Split text into chunks
        self.documents = self.text_splitter.split_documents(pages)
        self.current_document_metadata['total_chunks'] = len(self.documents)
        
        try:
            # Create vector store with unique collection name
            self.vector_store = Chroma.from_documents(
                documents=self.documents,
                embedding=self.embeddings,
                collection_name=collection_name,
                persist_directory="./chroma_db"
            )
            
            # Save metadata
            self.save_metadata(self.current_document_metadata)
        except Exception as e:
            # If there's an error, clean up and re-raise
            self.cleanup_vector_store()
            raise Exception(f"Error creating vector store: {str(e)}")

    def process_text(self, text: str) -> None:
        """Process raw text and create vector embeddings"""
        # Create metadata
        self.current_document_metadata = {
            'processed_date': datetime.now().isoformat(),
            'total_chunks': 0,
            'chunk_size': self.text_splitter._chunk_size,
            'chunk_overlap': self.text_splitter._chunk_overlap
        }
        
        # Split text into chunks
        self.documents = self.text_splitter.split_text(text)
        self.current_document_metadata['total_chunks'] = len(self.documents)
        
        # Create vector store
        self.vector_store = Chroma.from_texts(
            texts=self.documents,
            embedding=self.embeddings,
            persist_directory="./chroma_db"
        )
        
        # Save metadata
        self.save_metadata(self.current_document_metadata)

    def get_relevant_chunks(self, query: str, k: int = 3) -> List[str]:
        """Retrieve the most relevant text chunks for a given query"""
        if not self.vector_store:
            raise ValueError("No documents have been processed yet")
        
        # Search for relevant chunks
        docs = self.vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]

    def get_context_for_question(self, question_type: str, num_questions: int) -> List[str]:
        """Get relevant context for generating questions"""
        if not self.vector_store:
            raise ValueError("No documents have been processed yet")
        
        # Create a query based on question type
        if question_type == "open":
            query = "Find sections that contain detailed explanations or definitions"
        else:  # yes/no questions
            query = "Find sections that contain factual statements or clear assertions"
        
        # Get relevant chunks
        chunks = self.get_relevant_chunks(query, k=num_questions)
        return chunks

    def save_metadata(self, metadata: Dict) -> None:
        """Save metadata about the processed document"""
        os.makedirs("./metadata", exist_ok=True)
        metadata_file = "./metadata/document_metadata.json"
        
        # Load existing metadata if it exists
        existing_metadata = {}
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, "r") as f:
                    existing_metadata = json.load(f)
            except json.JSONDecodeError:
                existing_metadata = {}
        
        # Update metadata
        if not isinstance(existing_metadata, list):
            existing_metadata = []
        
        existing_metadata.append(metadata)
        
        # Save updated metadata
        with open(metadata_file, "w") as f:
            json.dump(existing_metadata, f, indent=2)

    def load_metadata(self) -> List[Dict]:
        """Load metadata about all processed documents"""
        try:
            with open("./metadata/document_metadata.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def get_document_stats(self) -> Dict:
        """Get statistics about the current document"""
        if not self.current_document_metadata:
            return {}
        
        return {
            'total_chunks': self.current_document_metadata.get('total_chunks', 0),
            'chunk_size': self.current_document_metadata.get('chunk_size', 0),
            'chunk_overlap': self.current_document_metadata.get('chunk_overlap', 0),
            'processed_date': self.current_document_metadata.get('processed_date', '')
        } 