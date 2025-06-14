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

## Project Setup and Running Instructions

## Prerequisites
- Python 3.9 or higher
- pip (Python package installer)
- Docker (optional, for containerized deployment)

## Setting up Virtual Environment

1. Create a virtual environment:
```bash
# Windows
python -m venv venv

# Activate the virtual environment
# Windows
.\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up GEMINI_API_KEY:
```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# Linux/Mac
export GEMINI_API_KEY=your_api_key_here
```

4. Run the application:
```bash
python app.py
```

## Running with Docker

1. Build the Docker image:
```bash
docker build -t your-app-name .
```

2. Run the container with GEMINI_API_KEY:
```bash
# Windows PowerShell
docker run -p 5000:5000 -e GEMINI_API_KEY=your_api_key_here your-app-name

# Windows Command Prompt
docker run -p 5000:5000 -e "GEMINI_API_KEY=your_api_key_here" your-app-name
```

## Environment Variables
The following environment variables are required:
- `GEMINI_API_KEY`: Your Google Gemini API key

## Notes
- Make sure to replace `your_api_key_here` with your actual Gemini API key
- Never commit your API key to version control
- For development, you can create a `.env` file in the project root with your environment variables

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