from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from datetime import datetime
from database import Base

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), index=True)
    analysis_type = Column(String(50), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Summary data
    total_sequences = Column(Integer)
    total_length = Column(Integer)
    average_length = Column(Float, nullable=True)
    average_gc_content = Column(Float, nullable=True)
    
    # Detailed results stored as JSON
    sequences = Column(JSON)
    nucleotide_composition = Column(JSON, nullable=True)
    
    # Additional metadata
    status = Column(String(50), default="completed")
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "analysis_type": self.analysis_type,
            "timestamp": self.timestamp.isoformat(),
            "total_sequences": self.total_sequences,
            "total_length": self.total_length,
            "average_length": self.average_length,
            "average_gc_content": self.average_gc_content,
            "sequences": self.sequences,
            "nucleotide_composition": self.nucleotide_composition,
            "status": self.status,
        }
