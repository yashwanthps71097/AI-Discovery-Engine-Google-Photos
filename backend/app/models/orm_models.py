import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Float, Integer, 
    Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    channel_name = Column(String(100), nullable=False) # e.g., 'Reddit', 'PlayStore'
    base_url = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    last_scraped_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    raw_posts = relationship("RawPost", back_populates="source", cascade="all, delete-orphan")

class RawPost(Base):
    __tablename__ = "raw_posts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_id = Column(String(36), ForeignKey("data_sources.id"), nullable=True)
    source_channel = Column(String(100), nullable=False)
    raw_text = Column(Text, nullable=False)
    canonical_url = Column(String(1000), nullable=False)
    post_author = Column(String(200), nullable=True)
    post_created_at = Column(DateTime, nullable=True)
    deduplication_hash = Column(String(64), unique=True, index=True, nullable=False)
    relevance_score = Column(Float, default=0.0)
    processing_status = Column(String(50), default="PENDING_EXTRACTION") # PENDING, PROCESSED, REJECTED
    created_at = Column(DateTime, default=datetime.utcnow)

    source = relationship("DataSource", back_populates="raw_posts")
    evidence = relationship("ExtractedEvidence", back_populates="raw_post", uselist=False, cascade="all, delete-orphan")

class ExtractedEvidence(Base):
    __tablename__ = "extracted_evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    raw_post_id = Column(String(36), ForeignKey("raw_posts.id"), nullable=False)
    scenario_type = Column(String(100), nullable=False, index=True)
    scenario_custom_description = Column(String(500), nullable=True)
    
    # Stored as JSON arrays
    remembered_clues = Column(JSON, nullable=False, default=list)
    forgotten_metadata = Column(JSON, nullable=False, default=list)
    search_behaviors = Column(JSON, nullable=False, default=list)
    
    failure_point = Column(String(150), nullable=False, index=True)
    workarounds = Column(JSON, nullable=False, default=list)
    user_outcome = Column(String(100), nullable=False, index=True)
    
    # Layer 1 raw grounding preservation
    verbatim_quote = Column(Text, nullable=False)
    canonical_url = Column(String(1000), nullable=False)
    source_channel = Column(String(100), nullable=False)
    post_date = Column(String(100), nullable=True)
    
    # AI audit
    ai_confidence_score = Column(Float, default=1.0)
    ai_interpretation_notes = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    raw_post = relationship("RawPost", back_populates="evidence")
    clusters = relationship("ClusterEvidenceJunction", back_populates="evidence")

class ProblemCluster(Base):
    __tablename__ = "problem_clusters"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cluster_id = Column(String(100), unique=True, index=True, nullable=False)
    problem_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    frequency = Column(Integer, default=0)
    frequency_percentage = Column(Float, default=0.0)
    severity_indicators = Column(String(255), nullable=False)
    retrieval_impact = Column(String(255), nullable=False)
    common_user_behavior = Column(JSON, default=list)
    common_workaround = Column(JSON, default=list)
    sources_present = Column(JSON, default=list)
    potential_opportunity_area = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    evidence_items = relationship("ClusterEvidenceJunction", back_populates="cluster")
    opportunity_areas = relationship("OpportunityArea", back_populates="cluster")

class ClusterEvidenceJunction(Base):
    __tablename__ = "cluster_evidence_junction"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cluster_id = Column(String(36), ForeignKey("problem_clusters.id"), nullable=False)
    evidence_id = Column(String(36), ForeignKey("extracted_evidence.id"), nullable=False)
    distance_to_centroid = Column(Float, default=0.0)

    cluster = relationship("ProblemCluster", back_populates="evidence_items")
    evidence = relationship("ExtractedEvidence", back_populates="clusters")

class OpportunityArea(Base):
    __tablename__ = "opportunity_areas"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cluster_id = Column(String(36), ForeignKey("problem_clusters.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    evidence_volume = Column(Integer, default=0)
    severity_level = Column(String(50), default="Medium")
    validation_hypothesis = Column(Text, nullable=False)
    primary_research_questions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    cluster = relationship("ProblemCluster", back_populates="opportunity_areas")
