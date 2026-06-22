# Bioinformatics Analysis Suite

An integrated platform for computational genomics analysis with React frontend, FastAPI backend, and SQLite database for storing and visualizing analysis results.

## Project Structure

```
health-el/
├── frontend/              # React UI application
│   ├── public/           # Static files
│   ├── src/
│   │   ├── App.js        # Main application component
│   │   ├── App.css       # Application styles
│   │   └── index.js      # Entry point
│   └── package.json
├── backend/              # FastAPI server
│   ├── main.py           # API endpoints
│   ├── database.py       # Database configuration
│   ├── models.py         # SQLAlchemy models
│   ├── export_utils.py   # Export functionality
│   ├── requirements.txt  # Python dependencies
│   ├── data/             # SQLite database storage
│   └── uploads/          # Temporary file storage
└── package.json          # Root workspace configuration
```

## Features

### Backend (Python FastAPI)
- **Quality Control Analysis**: Analyze FASTA/FASTQ files for sequence quality metrics (GC content, sequence length, etc.)
- **Sequence Analysis**: Calculate nucleotide composition and sequence statistics
- **SQLite Database**: Store all analysis results with timestamps
- **Results History**: Retrieve and view past analyses
- **Export Functionality**: Export results in CSV, JSON, and PDF formats
- **File Preview**: Preview first sequences before analysis
- CORS enabled for frontend communication
- REST API endpoints for all operations

### Frontend (React)
- **Tabbed Interface**: Upload, Results Dashboard, and History tabs
- **File Upload & Preview**: Upload genomic data with preview functionality
- **Interactive Charts**:
  - GC Content Distribution (Bar chart)
  - Nucleotide Composition (Pie chart)
  - Sequence Length Distribution (Bar chart)
- **Results Dashboard**: Summary statistics and charts
- **Analysis History**: View all past analyses
- **Export Options**: Download results as CSV, JSON, or PDF
- **Responsive Design**: Works on desktop and mobile

## Technologies Used

- **Frontend**: React 18, Recharts (charting), Axios (API calls)
- **Backend**: FastAPI, Uvicorn, SQLAlchemy ORM
- **Database**: SQLite with SQLAlchemy
- **Bioinformatics**: Biopython
- **Export**: ReportLab (PDF generation), CSV/JSON built-in

## Quick Start

### Prerequisites
- Node.js (v14+) and npm
- Python 3.8+

### Installation

1. **Install all dependencies**
   ```bash
   npm install
   cd backend && pip install -r requirements.txt && cd ..
   ```

### Running the Application

**Development Mode** (runs both frontend and backend):
```bash
npm run dev
```

**Or run separately:**

Backend:
```bash
cd backend
python main.py
```

Frontend (in another terminal):
```bash
cd frontend
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## API Endpoints

### Health & Information
- `GET /` - API information
- `GET /health` - Server health status

### Analysis Endpoints
- `POST /api/analyze/quality-control` - Quality control analysis (upload FASTA/FASTQ file)
- `POST /api/analyze/sequence` - Sequence composition analysis (upload FASTA/FASTQ file)

### Results Management
- `GET /api/history` - Get all past analyses
- `GET /api/result/{result_id}` - Get specific analysis result
- `GET /api/export/{result_id}/{format}` - Export result (csv, json, pdf)

### File Operations
- `POST /api/preview` - Preview file sequences before analysis

## Example Analysis Output

```json
{
  "id": 1,
  "filename": "example.fasta",
  "analysis_type": "quality_control",
  "timestamp": "2024-01-15T10:30:00",
  "sequences": [
    {
      "id": "seq_001",
      "length": 150,
      "gc_content": 45.33
    }
  ],
  "summary": {
    "total_sequences": 10,
    "total_length": 1500,
    "average_length": 150,
    "average_gc_content": 45.33,
    "status": "completed"
  }
}
```

## Supported File Formats

- FASTA: `.fasta`, `.fa`
- FASTQ: `.fastq`, `.fq`

## Features Overview

### 1. Results History & Storage ✅
- SQLite database stores all analysis results
- Retrieve past analyses with timestamps
- Easy result lookup

### 2. Results Export ✅
- Export to CSV for spreadsheet analysis
- Export to JSON for programmatic use
- Export to PDF for reports

### 3. File Preview ✅
- Preview first 5 sequences before analysis
- Shows sequence length and preview text
- Validates file format early

### 4. Interactive Charts ✅
- GC Content Distribution visualization
- Nucleotide Composition pie charts
- Sequence Length Distribution graphs
- Responsive, interactive charts using Recharts

### 5. Results Dashboard ✅
- Summary statistics cards
- Interactive visualizations
- Detailed sequence data view
- Export options

## Bioinformatics AI Assistant (Chatbot)

The application includes an AI-powered chatbot powered by **Grok API** that provides real-time assistance with:
- Explaining bioinformatics concepts (GC content, nucleotide composition, FASTA/FASTQ formats)
- Interpreting your specific analysis results with context awareness
- Answering questions about genomic analysis
- Providing guidance on next steps

### Setting Up the Chatbot

1. **Get your Grok API Key**: Visit https://console.x.ai and create an API key
2. **Set environment variable** before running the backend:
   ```bash
   # Windows PowerShell
   $env:GROK_API_KEY = "your-api-key-here"
   
   # Windows Command Prompt
   set GROK_API_KEY=your-api-key-here
   
   # Linux/Mac
   export GROK_API_KEY="your-api-key-here"
   ```

3. **Run the application** as normal:
   ```bash
   npm run dev
   ```

4. **Use the chatbot**: Click the 💬 button in the bottom-right corner of the application

### Example Chatbot Questions
- "What does a 65% GC content mean?"
- "Why is my average sequence length 2500bp?"
- "How should I prepare FASTA files?"
- "What's the difference between FASTA and FASTQ?"
- "Can you explain my nucleotide composition results?"

The chatbot has access to your current analysis results and can provide context-specific explanations.

## Next Steps for Enhancement

- Batch processing for multiple files
- User authentication and accounts
- Advanced analysis types (alignment, variant calling)
- Data comparison tools
- More visualization options
- Rate limiting and usage analytics
- WebSocket support for real-time updates
- Chatbot conversation history storage

## License

MIT
