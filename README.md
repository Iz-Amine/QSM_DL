# QCM Generator

A Flask-based application that generates questions (QCM) from PDF documents using AI. The application uses RAG (Retrieval-Augmented Generation) to create contextually relevant questions from uploaded documents.

## Features

- PDF document upload and processing
- Generation of open-ended and yes/no questions
- Vector-based document storage for efficient retrieval
- RESTful API endpoints for integration
- Web interface for easy interaction

## Recent Changes

### Vector Store Management
- Implemented unique collection names for each PDF upload using timestamps
- Added proper error handling for vector store operations
- Improved collection cleanup process
- Added metadata tracking for vector store collections

### Project Structure
- Added `.gitignore` to exclude:
  - `uploads/` directory (for PDF files)
  - `chroma_db/` directory (for vector store)
  - `metadata/` directory (for document metadata)
  - `.env` file (for environment variables)

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys and configuration

4. Run the application:
```bash
python app.py
```

## API Endpoints

- `POST /upload`: Upload and process PDF files
- `POST /generate`: Generate questions from text
- `POST /api/generate`: API endpoint for question generation
- `GET /api/documentation`: API documentation

## Project Structure

```
.
├── app.py              # Main Flask application
├── requirements.txt    # Project dependencies
├── service/           # Core services
│   ├── llm_gimi.py    # LLM integration
│   └── rag_service.py # RAG implementation
├── templates/         # HTML templates
├── uploads/          # PDF upload directory
├── chroma_db/        # Vector store database
└── metadata/         # Document metadata
```

## Environment Variables

Create a `.env` file with the following variables:
```
GOOGLE_API_KEY=your_api_key_here
```

## Notes

- Each PDF upload creates a unique vector store collection
- Vector stores are automatically cleaned up when new documents are processed
- Document metadata is tracked for each processed file
- The system uses the all-MiniLM-L6-v2 model for embeddings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 