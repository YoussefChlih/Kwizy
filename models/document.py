"""
Document Models
"""

from models.database import db, TimestampMixin
import uuid


class Document(db.Model, TimestampMixin):
    """Document model for uploaded files"""
    __tablename__ = 'documents'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(20))
    file_size = db.Column(db.Integer)
    
    # Content metadata
    text_content = db.Column(db.Text)
    text_length = db.Column(db.Integer)
    language = db.Column(db.String(10), default='auto')
    detected_language = db.Column(db.String(10))
    
    # Extracted metadata
    title = db.Column(db.String(500))
    author = db.Column(db.String(200))
    page_count = db.Column(db.Integer)
    
    # Auto-generated content
    summary = db.Column(db.Text)
    key_concepts = db.Column(db.JSON)  # List of extracted concepts
    
    # Owner
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(36))  # For anonymous users
    
    # Relationships
    chunks = db.relationship('DocumentChunk', backref='document', lazy='dynamic', cascade='all, delete-orphan')
    quizzes = db.relationship('Quiz', secondary='quiz_documents', back_populates='documents')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'text_length': self.text_length,
            'language': self.detected_language or self.language,
            'title': self.title,
            'author': self.author,
            'page_count': self.page_count,
            'summary': self.summary,
            'key_concepts': self.key_concepts,
            'chunk_count': self.chunks.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DocumentChunk(db.Model, TimestampMixin):
    """Document chunk for RAG system"""
    __tablename__ = 'document_chunks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id'), nullable=False)
    
    # Content
    text = db.Column(db.Text, nullable=False)
    char_count = db.Column(db.Integer)
    chunk_index = db.Column(db.Integer)
    
    # Metadata
    page_number = db.Column(db.Integer)
    section_title = db.Column(db.String(500))
    
    # Embedding (stored as JSON for flexibility)
    embedding = db.Column(db.JSON)
    embedding_model = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'text': self.text,
            'char_count': self.char_count,
            'chunk_index': self.chunk_index,
            'page_number': self.page_number,
            'section_title': self.section_title
        }


# Association table for quiz-document many-to-many relationship
quiz_documents = db.Table('quiz_documents',
    db.Column('quiz_id', db.String(36), db.ForeignKey('quizzes.id'), primary_key=True),
    db.Column('document_id', db.String(36), db.ForeignKey('documents.id'), primary_key=True)
)
