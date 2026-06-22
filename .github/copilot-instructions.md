# Bioinformatics Analysis Suite - Project Instructions

## Project Overview
A complete bioinformatics analysis platform with React frontend, FastAPI backend, SQLite database, and data visualization capabilities.

## ✅ Features Implemented

### 1. Results History & Storage (SQLite Database)
- Database schema with AnalysisResult model
- Automatic storage of all analysis results
- Timestamps for tracking when analyses were performed
- Full result retrieval with history endpoint

### 2. Results Export
- **CSV Export**: Tabular format for spreadsheet analysis
- **JSON Export**: Structured format for programmatic use
- **PDF Export**: Professional reports with summary and details
- Export endpoints for each format

### 3. File Preview
- `/api/preview` endpoint for previewing sequences
- Shows first 5 sequences with length and preview text
- Frontend preview component with detailed sequence view

### 4. Interactive Charts
- **GC Content Distribution**: Bar chart visualization
- **Nucleotide Composition**: Pie chart for A, T, G, C percentages
- **Sequence Length Distribution**: Bar chart of first 20 sequences
- Built with Recharts for React
- Responsive and interactive

### 5. Results Dashboard
- Tabbed interface (Upload, Results, History)
- Summary statistics cards with key metrics
- Multiple interactive charts
- Detailed sequence data display
- Export functionality buttons

### 6. AI Chatbot (Grok-powered)
- Real-time conversational AI assistant
- Context-aware responses using current analysis results
- Bioinformatics knowledge base integration
- Floating chat widget (bottom-right corner)
- Message history with timestamps
- Accessible from any tab
- Explains analysis results, concepts, and provides guidance

## Project Structure

### Backend Files
- `main.py` - FastAPI server with all endpoints
- `database.py` - SQLite database setup and configuration
- `models.py` - SQLAlchemy ORM models
- `export_utils.py` - CSV, JSON, and PDF export functions
- `chatbot_utils.py` - Grok API integration for AI chatbot
- `requirements.txt` - Python dependencies

### Frontend Files
- `App.js` - Complete React application with tabs, charts, preview
- `App.css` - Comprehensive styling for all components
- `Chatbot.js` - Floating chatbot component
- `package.json` - Dependencies including Recharts

## Running the Application

### Install All Dependencies
```bash
npm install
cd backend && pip install -r requirements.txt && cd ..
```

### Start Development Servers
```bash
npm run dev
```

This will run:
- Frontend on http://localhost:3000
- Backend on http://localhost:8000

### Manual Startup
Backend: `cd backend && python main.py`
Frontend: `cd frontend && npm start`

## API Endpoints

### Analysis Operations
- `POST /api/analyze/quality-control` - Run quality control analysis
- `POST /api/analyze/sequence` - Run sequence analysis

### Results Management
- `GET /api/history` - Get all past analyses
- `GET /api/result/{id}` - Get specific result
- `GET /api/export/{id}/csv|json|pdf` - Export result

### Chatbot
- `POST /api/chat` - Chat with Grok-powered bioinformatics assistant

### Utilities
- `POST /api/preview` - Preview file before analysis
- `GET /health` - Health check

## Available Analysis Types

1. **Quality Control**
   - GC content calculation
   - Sequence length analysis
   - Quality scores (for FASTQ)
   - Summary statistics

2. **Sequence Analysis**
   - Nucleotide composition (A, T, G, C, N)
   - Per-sequence composition
   - Overall statistics

## Technologies Stack

- **Frontend**: React 18, Recharts (charting), Axios
- **Backend**: FastAPI, Uvicorn, SQLAlchemy ORM
- **Database**: SQLite
- **Bioinformatics**: Biopython
- **Export**: ReportLab (PDF), CSV/JSON built-in
- **AI/LLM**: Grok API (xAI) for chatbot
- **HTTP**: httpx for async API calls

## Database Schema

### AnalysisResult Table
- id: Primary key
- filename: Name of uploaded file
- analysis_type: Type of analysis performed
- timestamp: When analysis was run
- total_sequences: Number of sequences
- total_length: Combined length of all sequences
- average_length: Average sequence length
- average_gc_content: Average GC content
- sequences: JSON array of sequence details
- nucleotide_composition: JSON nucleotide counts
- status: Analysis status

## Supported File Formats

- FASTA: `.fasta`, `.fa`
- FASTQ: `.fastq`, `.fq`

## Chatbot Setup

To use the AI chatbot feature, you need a Grok API key:

1. Get your API key at https://console.x.ai
2. Set environment variable before running the backend:
   ```bash
   export GROK_API_KEY="your-api-key-here"
   ```
3. Run the application normally
4. Click the 💬 button in the bottom-right corner to chat

The chatbot has context awareness of your current analysis results and can explain bioinformatics concepts.

## Future Enhancements

- Batch processing for multiple files
- User authentication and accounts
- Advanced analysis algorithms (alignment, variant calling)
- Data comparison tools
- Real-time progress updates
- Results sharing capability
- Chatbot conversation history storage
- Multi-language support
- Results caching for performance

