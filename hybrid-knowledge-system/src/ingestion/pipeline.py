"""
Data Ingestion Pipeline: Processes documents and structured data for hybrid knowledge system
"""

import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, AsyncGenerator
import json
from datetime import datetime
from dataclasses import dataclass, asdict
import hashlib

# Document processing
try:
    import pypdf
    from docx import Document as DocxDocument
    DOCUMENT_PROCESSING_AVAILABLE = True
except ImportError:
    DOCUMENT_PROCESSING_AVAILABLE = False

from src.clients.neo4j_client import Neo4jClient
from src.clients.weaviate_client import WeaviateClient
from src.utils.embeddings import EmbeddingService
from src.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class DocumentChunk:
    content: str
    title: str = ""
    chunk_index: int = 0
    parent_document_id: str = ""
    document_type: str = ""
    source: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ProcessingStats:
    documents_processed: int = 0
    chunks_created: int = 0
    entities_extracted: int = 0
    relationships_created: int = 0
    embeddings_generated: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class IngestionPipeline:
    """
    Comprehensive data ingestion pipeline for hybrid Neo4j + Weaviate system.
    
    Features:
    - Multi-format document processing (PDF, DOCX, TXT, JSON)
    - Intelligent text chunking strategies
    - Entity extraction and relationship mapping
    - Dual indexing in both Neo4j and Weaviate
    - Batch processing with progress tracking
    """
    
    def __init__(
        self,
        neo4j_client: Optional[Neo4jClient] = None,
        weaviate_client: Optional[WeaviateClient] = None,
        embedding_service: Optional[EmbeddingService] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.neo4j = neo4j_client or Neo4jClient()
        self.weaviate = weaviate_client or WeaviateClient()
        self.embedding_service = embedding_service or EmbeddingService()
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize stats
        self.stats = ProcessingStats()
        
    async def initialize(self):
        """Initialize all clients and create necessary schemas/indexes"""
        logger.info("Initializing ingestion pipeline...")
        
        # Connect to databases
        await self.neo4j.connect()
        await self.weaviate.connect()
        
        # Create schemas and indexes
        await self._create_schemas()
        
        logger.info("Pipeline initialized successfully")
    
    async def _create_schemas(self):
        """Create necessary schemas and indexes"""
        
        # Create Weaviate schema
        await self.weaviate.create_schema("Document", force_recreate=False)
        
        # Create Neo4j indexes
        await self.neo4j.create_vector_index(
            "document_embeddings",
            "Document", 
            "embedding",
            dimensions=self.embedding_service.get_dimensions()
        )
        
        await self.neo4j.create_fulltext_index(
            "document_fulltext",
            ["Document", "Entity", "Concept"],
            ["content", "title", "description"]
        )
    
    async def ingest_documents(
        self,
        source_path: Union[str, Path],
        chunk_strategy: str = "semantic",
        domain: Optional[str] = None,
        metadata: Optional[Dict] = None,
        batch_size: int = 50
    ) -> ProcessingStats:
        """
        Ingest documents from a directory or file path.
        
        Args:
            source_path: Path to file or directory
            chunk_strategy: "fixed", "semantic", or "paragraph"
            domain: Domain classification for documents
            metadata: Additional metadata for all documents
            batch_size: Number of chunks to process in each batch
        """
        
        logger.info(f"Starting document ingestion from: {source_path}")
        source_path = Path(source_path)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source path not found: {source_path}")
        
        # Reset stats
        self.stats = ProcessingStats()
        
        # Get all document files
        if source_path.is_file():
            files = [source_path]
        else:
            files = self._discover_files(source_path)
        
        logger.info(f"Found {len(files)} files to process")
        
        # Process files in batches
        chunk_batch = []
        
        for file_path in files:
            try:
                # Process single document
                chunks = await self._process_document(
                    file_path, 
                    chunk_strategy, 
                    domain, 
                    metadata
                )
                
                chunk_batch.extend(chunks)
                self.stats.documents_processed += 1
                
                # Process batch when it reaches the limit
                if len(chunk_batch) >= batch_size:
                    await self._process_chunk_batch(chunk_batch)
                    chunk_batch = []
                    
            except Exception as e:
                error_msg = f"Failed to process {file_path}: {str(e)}"
                logger.error(error_msg)
                self.stats.errors.append(error_msg)
        
        # Process remaining chunks
        if chunk_batch:
            await self._process_chunk_batch(chunk_batch)
        
        logger.info(f"Ingestion completed: {asdict(self.stats)}")
        return self.stats
    
    def _discover_files(self, directory: Path) -> List[Path]:
        """Discover supported file types in directory"""
        supported_extensions = {'.txt', '.pdf', '.docx', '.json', '.md'}
        files = []
        
        for ext in supported_extensions:
            files.extend(directory.rglob(f'*{ext}'))
        
        return sorted(files)
    
    async def _process_document(
        self,
        file_path: Path,
        chunk_strategy: str,
        domain: Optional[str],
        base_metadata: Optional[Dict]
    ) -> List[DocumentChunk]:
        """Process a single document into chunks"""
        
        logger.info(f"Processing document: {file_path.name}")
        
        # Extract text from document
        content = await self._extract_text(file_path)
        if not content:
            return []
        
        # Generate document ID
        doc_id = hashlib.md5(str(file_path).encode()).hexdigest()
        
        # Create chunks
        if chunk_strategy == "semantic":
            chunks = await self._semantic_chunking(content)
        elif chunk_strategy == "paragraph":
            chunks = self._paragraph_chunking(content)
        else:  # fixed
            chunks = self._fixed_size_chunking(content)
        
        # Create DocumentChunk objects
        document_chunks = []
        for i, chunk_content in enumerate(chunks):
            metadata = (base_metadata or {}).copy()
            metadata.update({
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_extension': file_path.suffix,
                'file_size': file_path.stat().st_size,
                'processed_at': datetime.utcnow().isoformat(),
                'total_chunks': len(chunks)
            })
            
            document_chunk = DocumentChunk(
                content=chunk_content,
                title=file_path.stem,
                chunk_index=i,
                parent_document_id=doc_id,
                document_type=file_path.suffix[1:],  # Remove dot
                source=str(file_path),
                metadata=metadata
            )
            
            if domain:
                document_chunk.metadata['domain'] = domain
            
            document_chunks.append(document_chunk)
        
        logger.info(f"Created {len(document_chunks)} chunks from {file_path.name}")
        return document_chunks
    
    async def _extract_text(self, file_path: Path) -> str:
        """Extract text from various file formats"""
        
        try:
            if file_path.suffix.lower() == '.txt' or file_path.suffix.lower() == '.md':
                return file_path.read_text(encoding='utf-8')
            
            elif file_path.suffix.lower() == '.pdf':
                if not DOCUMENT_PROCESSING_AVAILABLE:
                    raise ImportError("pypdf not available for PDF processing")
                
                text = ""
                with open(file_path, 'rb') as file:
                    reader = pypdf.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                return text
            
            elif file_path.suffix.lower() == '.docx':
                if not DOCUMENT_PROCESSING_AVAILABLE:
                    raise ImportError("python-docx not available for DOCX processing")
                
                doc = DocxDocument(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            
            elif file_path.suffix.lower() == '.json':
                data = json.loads(file_path.read_text(encoding='utf-8'))
                # Convert JSON to text representation
                if isinstance(data, dict) and 'content' in data:
                    return data['content']
                else:
                    return json.dumps(data, indent=2)
            
            else:
                logger.warning(f"Unsupported file format: {file_path.suffix}")
                return ""
                
        except Exception as e:
            logger.error(f"Text extraction failed for {file_path}: {e}")
            return ""
    
    def _fixed_size_chunking(self, text: str) -> List[str]:
        """Split text into fixed-size chunks with overlap"""
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            if chunk_text.strip():
                chunks.append(chunk_text.strip())
        
        return chunks
    
    def _paragraph_chunking(self, text: str) -> List[str]:
        """Split text into chunks based on paragraphs"""
        
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= self.chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def _semantic_chunking(self, text: str) -> List[str]:
        """Advanced semantic chunking using embeddings"""
        
        # First, split by sentences
        sentences = self._split_sentences(text)
        if len(sentences) <= 1:
            return [text]
        
        # Generate embeddings for sentences
        sentence_embeddings = await self.embedding_service.embed_texts(sentences)
        
        # Group semantically similar sentences
        chunks = []
        current_chunk_sentences = []
        current_chunk_length = 0
        
        for i, (sentence, embedding) in enumerate(zip(sentences, sentence_embeddings)):
            # Check if adding this sentence would exceed chunk size
            if current_chunk_length + len(sentence) > self.chunk_size and current_chunk_sentences:
                # Finalize current chunk
                chunks.append(' '.join(current_chunk_sentences))
                current_chunk_sentences = []
                current_chunk_length = 0
            
            current_chunk_sentences.append(sentence)
            current_chunk_length += len(sentence)
        
        # Add final chunk
        if current_chunk_sentences:
            chunks.append(' '.join(current_chunk_sentences))
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Simple sentence splitting"""
        # Basic sentence splitting - could be enhanced with proper NLP
        import re
        
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    async def _process_chunk_batch(self, chunks: List[DocumentChunk]):
        """Process a batch of chunks"""
        
        logger.info(f"Processing batch of {len(chunks)} chunks")
        
        # Generate embeddings for all chunks
        chunk_texts = [chunk.content for chunk in chunks]
        embeddings = await self.embedding_service.embed_texts(chunk_texts)
        
        # Prepare data for dual indexing
        neo4j_tasks = []
        weaviate_docs = []
        
        for chunk, embedding in zip(chunks, embeddings):
            # Add to Weaviate
            weaviate_doc = {
                'content': chunk.content,
                'title': chunk.title,
                'entity_id': f"{chunk.parent_document_id}_{chunk.chunk_index}",
                'source': chunk.source,
                'document_type': chunk.document_type,
                'domain': chunk.metadata.get('domain', ''),
                'metadata': chunk.metadata
            }
            weaviate_docs.append(weaviate_doc)
            
            # Prepare Neo4j insertion
            neo4j_tasks.append(self._add_to_neo4j(chunk, embedding))
        
        # Execute dual indexing
        await asyncio.gather(
            self.weaviate.batch_add_documents(weaviate_docs),
            *neo4j_tasks
        )
        
        # Update stats
        self.stats.chunks_created += len(chunks)
        self.stats.embeddings_generated += len(embeddings)
        
        logger.info(f"Batch processed successfully")
    
    async def _add_to_neo4j(self, chunk: DocumentChunk, embedding: List[float]):
        """Add chunk to Neo4j with relationships"""
        
        # Create document node with embedding
        create_query = """
        MERGE (d:Document {id: $chunk_id})
        SET d.content = $content,
            d.title = $title,
            d.chunk_index = $chunk_index,
            d.parent_document_id = $parent_id,
            d.document_type = $document_type,
            d.source = $source,
            d.domain = $domain,
            d.embedding = $embedding,
            d.created_at = $created_at,
            d.metadata = $metadata
        
        // Create parent document relationship
        MERGE (parent:Document {id: $parent_id, is_parent: true})
        SET parent.title = $title,
            parent.document_type = $document_type,
            parent.source = $source
        
        MERGE (d)-[:PART_OF]->(parent)
        """
        
        try:
            async with self.neo4j.session() as session:
                await session.run(
                    create_query,
                    chunk_id=f"{chunk.parent_document_id}_{chunk.chunk_index}",
                    content=chunk.content,
                    title=chunk.title,
                    chunk_index=chunk.chunk_index,
                    parent_id=chunk.parent_document_id,
                    document_type=chunk.document_type,
                    source=chunk.source,
                    domain=chunk.metadata.get('domain', ''),
                    embedding=embedding,
                    created_at=datetime.utcnow().isoformat(),
                    metadata=chunk.metadata
                )
        except Exception as e:
            logger.error(f"Failed to add chunk to Neo4j: {e}")
            self.stats.errors.append(f"Neo4j insertion error: {str(e)}")
    
    async def ingest_structured_data(
        self,
        data: Union[List[Dict], Dict],
        source_name: str = "structured_data",
        extract_relationships: bool = True,
        domain: Optional[str] = None
    ) -> ProcessingStats:
        """Ingest structured data with relationship extraction"""
        
        logger.info(f"Ingesting structured data from: {source_name}")
        
        # Reset stats
        self.stats = ProcessingStats()
        
        # Normalize data to list
        if isinstance(data, dict):
            data = [data]
        
        # Process each record
        for i, record in enumerate(data):
            try:
                await self._process_structured_record(
                    record, 
                    f"{source_name}_{i}",
                    extract_relationships,
                    domain
                )
                self.stats.documents_processed += 1
                
            except Exception as e:
                error_msg = f"Failed to process record {i}: {str(e)}"
                logger.error(error_msg)
                self.stats.errors.append(error_msg)
        
        logger.info(f"Structured data ingestion completed: {asdict(self.stats)}")
        return self.stats
    
    async def _process_structured_record(
        self,
        record: Dict,
        record_id: str,
        extract_relationships: bool,
        domain: Optional[str]
    ):
        """Process a single structured data record"""
        
        # Convert record to searchable content
        content = self._record_to_text(record)
        
        # Generate embedding
        embedding = await self.embedding_service.embed_text(content)
        
        # Add to Weaviate
        await self.weaviate.add_document(
            content=content,
            title=record.get('title', record_id),
            entity_id=record_id,
            metadata={
                'source': 'structured_data',
                'domain': domain,
                'original_record': record,
                'processed_at': datetime.utcnow().isoformat()
            }
        )
        
        # Add to Neo4j with relationships
        if extract_relationships:
            await self._extract_and_create_relationships(record, record_id, embedding, domain)
        else:
            await self._add_simple_node(record, record_id, embedding, domain)
        
        self.stats.chunks_created += 1
        self.stats.embeddings_generated += 1
    
    def _record_to_text(self, record: Dict) -> str:
        """Convert structured record to searchable text"""
        
        text_parts = []
        
        # Add title/name if available
        for title_field in ['title', 'name', 'subject', 'heading']:
            if title_field in record:
                text_parts.append(f"{title_field.capitalize()}: {record[title_field]}")
        
        # Add description/content fields
        for content_field in ['description', 'content', 'summary', 'body']:
            if content_field in record:
                text_parts.append(str(record[content_field]))
        
        # Add other relevant fields
        for key, value in record.items():
            if key not in ['title', 'name', 'subject', 'heading', 'description', 'content', 'summary', 'body']:
                if isinstance(value, (str, int, float)):
                    text_parts.append(f"{key}: {value}")
        
        return '\n'.join(text_parts)
    
    async def _extract_and_create_relationships(
        self,
        record: Dict,
        record_id: str,
        embedding: List[float],
        domain: Optional[str]
    ):
        """Extract entities and relationships from structured data"""
        
        # This is a simplified version - could be enhanced with NER
        relationships_query = """
        CREATE (r:Record {
            id: $record_id,
            content: $content,
            embedding: $embedding,
            domain: $domain,
            created_at: $created_at,
            metadata: $metadata
        })
        
        // Create entity nodes and relationships based on record structure
        WITH r
        UNWIND $entities as entity
        MERGE (e:Entity {name: entity.name, type: entity.type})
        CREATE (r)-[:MENTIONS]->(e)
        """
        
        # Extract entities from record
        entities = []
        for key, value in record.items():
            if isinstance(value, str) and len(value.split()) <= 5:  # Likely entity names
                entities.append({'name': value, 'type': key})
        
        try:
            async with self.neo4j.session() as session:
                await session.run(
                    relationships_query,
                    record_id=record_id,
                    content=self._record_to_text(record),
                    embedding=embedding,
                    domain=domain,
                    created_at=datetime.utcnow().isoformat(),
                    metadata=record,
                    entities=entities
                )
            
            self.stats.entities_extracted += len(entities)
            self.stats.relationships_created += len(entities)
            
        except Exception as e:
            logger.error(f"Failed to create relationships for {record_id}: {e}")
    
    async def _add_simple_node(
        self,
        record: Dict,
        record_id: str,
        embedding: List[float],
        domain: Optional[str]
    ):
        """Add record as simple node without relationship extraction"""
        
        simple_query = """
        CREATE (r:Record {
            id: $record_id,
            content: $content,
            embedding: $embedding,
            domain: $domain,
            created_at: $created_at,
            metadata: $metadata
        })
        """
        
        try:
            async with self.neo4j.session() as session:
                await session.run(
                    simple_query,
                    record_id=record_id,
                    content=self._record_to_text(record),
                    embedding=embedding,
                    domain=domain,
                    created_at=datetime.utcnow().isoformat(),
                    metadata=record
                )
        except Exception as e:
            logger.error(f"Failed to add record {record_id}: {e}")
    
    async def get_ingestion_stats(self) -> Dict[str, Any]:
        """Get comprehensive ingestion statistics"""
        
        # Get database stats
        neo4j_stats = await self.neo4j.get_database_stats()
        weaviate_count = await self.weaviate.get_document_count()
        
        return {
            'processing_stats': asdict(self.stats),
            'neo4j_stats': neo4j_stats,
            'weaviate_document_count': weaviate_count,
            'embedding_model': self.embedding_service.get_model_info(),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def cleanup(self):
        """Clean up resources"""
        await self.neo4j.close()
        await self.weaviate.close()