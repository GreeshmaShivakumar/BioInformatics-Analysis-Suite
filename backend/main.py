from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
import shutil
import os
from pathlib import Path
from Bio import SeqIO
import json
from datetime import datetime
from sqlalchemy.orm import Session
from database import init_db, get_db, engine
from models import AnalysisResult, Base
from export_utils import export_to_csv, export_to_json, export_to_pdf
from chatbot_utils import chat_with_grok
from advanced_analysis import (
    get_quality_scores, get_base_frequency_heatmap, find_orfs,
    translate_dna_to_protein, get_dinucleotide_frequency, find_repeats,
    multiple_sequence_alignment, blast_local_search
)
from pydantic import BaseModel
from typing import Optional, Dict, Any

app = FastAPI(
    title="Bioinformatics Analysis Suite API",
    description="API for computational genomics analysis",
    version="0.1.0"
)

# Add CORS middleware
allow_origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://bio-analysis-frontend.onrender.com",
    "https://bio-analysis-backend.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/")
def read_root():
    return {
        "message": "Bioinformatics Analysis Suite API",
        "version": "0.1.0",
        "endpoints": [
            "/api/analyze/quality-control",
            "/api/analyze/sequence",
            "/health"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/preview")
async def preview_file(file: UploadFile = File(...)):
    """
    Preview the first few sequences from a file
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        preview_data = {
            "filename": file.filename,
            "sequences": []
        }
        
        try:
            for i, record in enumerate(SeqIO.parse(file_path, "fasta")):
                if i >= 5:  # Show first 5 sequences
                    break
                preview_data["sequences"].append({
                    "id": record.id,
                    "length": len(record.seq),
                    "preview": str(record.seq)[:100] + "..." if len(record.seq) > 100 else str(record.seq)
                })
        except:
            for i, record in enumerate(SeqIO.parse(file_path, "fastq")):
                if i >= 5:
                    break
                preview_data["sequences"].append({
                    "id": record.id,
                    "length": len(record.seq),
                    "preview": str(record.seq)[:100] + "..." if len(record.seq) > 100 else str(record.seq)
                })
        
        preview_data["total_found"] = len(preview_data["sequences"])
        os.remove(file_path)
        return preview_data
        
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")

@app.get("/api/history")
async def get_history(db: Session = Depends(get_db)):
    """
    Get all analysis results history
    """
    results = db.query(AnalysisResult).order_by(AnalysisResult.timestamp.desc()).all()
    return [result.to_dict() for result in results]

@app.get("/api/result/{result_id}")
async def get_result(result_id: int, db: Session = Depends(get_db)):
    """
    Get a specific analysis result
    """
    result = db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result.to_dict()

@app.get("/api/export/{result_id}/{format}")
async def export_result(result_id: int, format: str, db: Session = Depends(get_db)):
    """
    Export analysis result in different formats (csv, json, pdf)
    """
    result = db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    result_data = result.to_dict()
    
    if format.lower() == "csv":
        content = export_to_csv(result_data)
        return StreamingResponse(
            iter([content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=analysis_{result_id}.csv"}
        )
    elif format.lower() == "json":
        content = export_to_json(result_data)
        return StreamingResponse(
            iter([content]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=analysis_{result_id}.json"}
        )
    elif format.lower() == "pdf":
        pdf_buffer = export_to_pdf(result_data)
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=analysis_{result_id}.pdf"}
        )
    else:
        raise HTTPException(status_code=400, detail="Format must be csv, json, or pdf")


@app.post("/api/analyze/quality-control")
async def quality_control_analysis(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Perform quality control analysis on genomic data.
    Supports FASTA and FASTQ files.
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Analyze sequences
        results = {
            "filename": file.filename,
            "analysis_type": "quality_control",
            "timestamp": datetime.now().isoformat(),
            "sequences": [],
            "summary": {}
        }
        
        sequence_count = 0
        total_length = 0
        gc_content_sum = 0
        
        try:
            for record in SeqIO.parse(file_path, "fasta"):
                seq_str = str(record.seq).upper()
                gc_count = seq_str.count('G') + seq_str.count('C')
                gc_percentage = (gc_count / len(seq_str) * 100) if len(seq_str) > 0 else 0
                
                results["sequences"].append({
                    "id": record.id,
                    "length": len(record.seq),
                    "gc_content": round(gc_percentage, 2)
                })
                
                sequence_count += 1
                total_length += len(record.seq)
                gc_content_sum += gc_percentage
        except:
            for record in SeqIO.parse(file_path, "fastq"):
                seq_str = str(record.seq).upper()
                gc_count = seq_str.count('G') + seq_str.count('C')
                gc_percentage = (gc_count / len(seq_str) * 100) if len(seq_str) > 0 else 0
                
                results["sequences"].append({
                    "id": record.id,
                    "length": len(record.seq),
                    "gc_content": round(gc_percentage, 2),
                    "quality_score": round(sum(record.letter_annotations.get("phred_quality", [])) / len(record.seq)) if "phred_quality" in record.letter_annotations else None
                })
                
                sequence_count += 1
                total_length += len(record.seq)
                gc_content_sum += gc_percentage
        
        # Calculate summary statistics
        results["summary"] = {
            "total_sequences": sequence_count,
            "total_length": total_length,
            "average_length": round(total_length / sequence_count) if sequence_count > 0 else 0,
            "average_gc_content": round(gc_content_sum / sequence_count, 2) if sequence_count > 0 else 0,
            "status": "completed"
        }
        
        # Store in database
        db_result = AnalysisResult(
            filename=file.filename,
            analysis_type="quality_control",
            total_sequences=sequence_count,
            total_length=total_length,
            average_length=results["summary"]["average_length"],
            average_gc_content=results["summary"]["average_gc_content"],
            sequences=results["sequences"],
            status="completed"
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        
        results["id"] = db_result.id
        
        # Cleanup
        os.remove(file_path)
        
        return results
        
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/analyze/sequence")
async def sequence_analysis(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Perform sequence analysis on genomic data.
    Analyzes nucleotide composition and other metrics.
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        results = {
            "filename": file.filename,
            "analysis_type": "sequence_analysis",
            "timestamp": datetime.now().isoformat(),
            "sequences": [],
            "summary": {}
        }
        
        nucleotide_counts = {"A": 0, "T": 0, "G": 0, "C": 0, "N": 0}
        total_sequences = 0
        
        try:
            for record in SeqIO.parse(file_path, "fasta"):
                seq_str = str(record.seq).upper()
                
                seq_nucleotides = {"A": 0, "T": 0, "G": 0, "C": 0, "N": 0}
                for nuc in seq_str:
                    if nuc in nucleotide_counts:
                        nucleotide_counts[nuc] += 1
                        seq_nucleotides[nuc] += 1
                
                results["sequences"].append({
                    "id": record.id,
                    "length": len(record.seq),
                    "composition": seq_nucleotides
                })
                total_sequences += 1
        except:
            for record in SeqIO.parse(file_path, "fastq"):
                seq_str = str(record.seq).upper()
                
                seq_nucleotides = {"A": 0, "T": 0, "G": 0, "C": 0, "N": 0}
                for nuc in seq_str:
                    if nuc in nucleotide_counts:
                        nucleotide_counts[nuc] += 1
                        seq_nucleotides[nuc] += 1
                
                results["sequences"].append({
                    "id": record.id,
                    "length": len(record.seq),
                    "composition": seq_nucleotides
                })
                total_sequences += 1
        
        results["summary"] = {
            "total_sequences": total_sequences,
            "nucleotide_composition": nucleotide_counts,
            "status": "completed"
        }
        
        # Store in database
        db_result = AnalysisResult(
            filename=file.filename,
            analysis_type="sequence_analysis",
            total_sequences=total_sequences,
            total_length=sum(nucleotide_counts.values()),
            sequences=results["sequences"],
            nucleotide_composition=nucleotide_counts,
            status="completed"
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        
        results["id"] = db_result.id
        
        os.remove(file_path)
        
        return results
        
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/analyze/quality-scores")
async def quality_score_analysis(file: UploadFile = File(...)):
    """
    Analyze quality scores from FASTQ file
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        quality_data = get_quality_scores(file_path)
        os.remove(file_path)
        
        return {
            "filename": file.filename,
            "analysis_type": "quality_scores",
            "timestamp": datetime.now().isoformat(),
            "data": quality_data
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Quality analysis failed: {str(e)}")


@app.post("/api/analyze/base-frequency")
async def base_frequency_analysis(file: UploadFile = File(...)):
    """
    Generate base frequency heatmap
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        heatmap_data = get_base_frequency_heatmap(file_path)
        os.remove(file_path)
        
        return {
            "filename": file.filename,
            "analysis_type": "base_frequency",
            "timestamp": datetime.now().isoformat(),
            "data": heatmap_data
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Base frequency analysis failed: {str(e)}")


@app.post("/api/analyze/orfs")
async def orf_analysis(file: UploadFile = File(...), min_length: int = 100):
    """
    Find Open Reading Frames
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        orfs_data = find_orfs(file_path, min_length)
        os.remove(file_path)
        
        return {
            "filename": file.filename,
            "analysis_type": "orfs",
            "timestamp": datetime.now().isoformat(),
            "data": orfs_data
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"ORF analysis failed: {str(e)}")


@app.post("/api/analyze/translation")
async def translation_analysis(file: UploadFile = File(...)):
    """
    Translate DNA sequences to protein
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        protein_data = translate_dna_to_protein(file_path)
        os.remove(file_path)
        
        return {
            "filename": file.filename,
            "analysis_type": "translation",
            "timestamp": datetime.now().isoformat(),
            "data": protein_data
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Translation analysis failed: {str(e)}")


@app.post("/api/analyze/dinucleotides")
async def dinucleotide_analysis(file: UploadFile = File(...)):
    """
    Analyze dinucleotide and trinucleotide frequencies
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        freq_data = get_dinucleotide_frequency(file_path)
        os.remove(file_path)
        
        return {
            "filename": file.filename,
            "analysis_type": "dinucleotides",
            "timestamp": datetime.now().isoformat(),
            "data": freq_data
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Dinucleotide analysis failed: {str(e)}")


@app.post("/api/analyze/repeats")
async def repeat_analysis(file: UploadFile = File(...), min_length: int = 10):
    """
    Find repetitive sequences
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        repeat_data = find_repeats(file_path, min_length)
        os.remove(file_path)
        
        return {
            "filename": file.filename,
            "analysis_type": "repeats",
            "timestamp": datetime.now().isoformat(),
            "data": repeat_data
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Repeat analysis failed: {str(e)}")


@app.post("/api/analyze/alignment")
async def alignment_analysis(file: UploadFile = File(...)):
    """
    Multiple sequence alignment
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        alignment_data = multiple_sequence_alignment(file_path)
        os.remove(file_path)
        
        return {
            "filename": file.filename,
            "analysis_type": "alignment",
            "timestamp": datetime.now().isoformat(),
            "data": alignment_data
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Alignment analysis failed: {str(e)}")


@app.get("/api/compare-results")
async def compare_results(result_ids: str, db: Session = Depends(get_db)):
    """
    Compare statistics across multiple analysis results
    """
    try:
        ids = [int(x.strip()) for x in result_ids.split(",")]
        results = []
        
        for rid in ids:
            result = db.query(AnalysisResult).filter(AnalysisResult.id == rid).first()
            if result:
                results.append(result.to_dict())
        
        if not results:
            raise HTTPException(status_code=404, detail="No results found")
        
        # Build comparison
        comparison = {
            "results": results,
            "comparison_stats": {
                "total_analyses": len(results),
                "average_sequences": sum(r.get("total_sequences", 0) for r in results) / len(results),
                "average_gc_content": sum(r.get("average_gc_content", 0) for r in results) / len(results),
                "total_length_combined": sum(r.get("total_length", 0) for r in results)
            }
        }
        
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")




class ChatMessage(BaseModel):
    message: str
    analysis_context: Optional[Dict[str, Any]] = None


@app.post("/api/chat")
async def chat(chat_msg: ChatMessage):
    """
    Chat with the bioinformatics assistant powered by Grok AI.
    Optionally provide recent analysis context for more informed responses.
    """
    try:
        response = await chat_with_grok(
            user_message=chat_msg.message,
            analysis_context=chat_msg.analysis_context
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
