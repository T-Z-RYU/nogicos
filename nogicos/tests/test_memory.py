# -*- coding: utf-8 -*-
"""
Tests for Long-term Memory System

Tests cover:
- Memory model creation and serialization
- Memory storage (add, list, delete)
- Semantic search (with and without embeddings)
- Memory extraction from conversations
- Background memory processing
"""

import os
import sys
import pytest
import asyncio
import tempfile
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from engine.knowledge.memory import (
    Memory, Episode, MemoryType, Importance, MemorySearchResult,
    format_memories_for_prompt, MEMORY_SQL_SCHEMA
)


class TestMemoryModel:
    """Tests for Memory and Episode models"""
    
    def test_memory_creation(self):
        """Test creating a basic memory"""
        memory = Memory(
            subject="user",
            predicate="prefers",
            object="dark mode",
            importance=Importance.HIGH,
        )
        
        assert memory.subject == "user"
        assert memory.predicate == "prefers"
        assert memory.object == "dark mode"
        assert memory.importance == Importance.HIGH
        assert memory.is_active == True
        assert memory.version == 1
    
    def test_memory_to_dict(self):
        """Test memory serialization"""
        memory = Memory(
            subject="user",
            predicate="works_at",
            object="Acme Corp",
            memory_type=MemoryType.FACT,
            importance=Importance.MEDIUM,
        )
        
        data = memory.to_dict()
        
        assert data["subject"] == "user"
        assert data["predicate"] == "works_at"
        assert data["object"] == "Acme Corp"
        assert data["memory_type"] == "fact"
        assert data["importance"] == "medium"
    
    def test_memory_from_dict(self):
        """Test memory deserialization"""
        data = {
            "id": "test123",
            "subject": "user",
            "predicate": "likes",
            "object": "Python",
            "memory_type": "preference",
            "importance": "high",
            "session_id": "session1",
        }
        
        memory = Memory.from_dict(data)
        
        assert memory.id == "test123"
        assert memory.subject == "user"
        assert memory.memory_type == MemoryType.PREFERENCE
        assert memory.importance == Importance.HIGH
    
    def test_memory_to_text(self):
        """Test natural language conversion"""
        memory = Memory(
            subject="user",
            predicate="prefers",
            object="organizing files by date",
        )
        
        text = memory.to_text()
        assert text == "user prefers organizing files by date"
    
    def test_memory_matches(self):
        """Test conflict detection"""
        m1 = Memory(subject="user", predicate="prefers", object="dark mode")
        m2 = Memory(subject="user", predicate="prefers", object="light mode")
        m3 = Memory(subject="user", predicate="uses", object="Python")
        
        assert m1.matches(m2) == True  # Same subject+predicate
        assert m1.matches(m3) == False  # Different predicate
    
    def test_episode_creation(self):
        """Test creating an episode"""
        episode = Episode(
            observation="User asked about binary trees",
            thoughts="Used family tree metaphor",
            action="Explained with visual example",
            result="User understood the concept",
            task="Explain binary trees",
            success=True,
        )
        
        assert episode.success == True
        assert "binary" in episode.observation.lower()


class TestFormatMemories:
    """Tests for memory formatting for prompts"""
    
    def test_format_empty(self):
        """Test formatting empty list"""
        result = format_memories_for_prompt([])
        assert result == ""
    
    def test_format_single_memory(self):
        """Test formatting a single memory"""
        memories = [
            Memory(
                subject="user",
                predicate="prefers",
                object="dark mode",
                memory_type=MemoryType.PREFERENCE,
                importance=Importance.HIGH,
            )
        ]
        
        result = format_memories_for_prompt(memories)
        
        assert "Long-term Memory" in result
        assert "User Preferences" in result
        assert "dark mode" in result
        assert "⭐" in result  # High importance marker
    
    def test_format_grouped_by_type(self):
        """Test memories are grouped by type"""
        memories = [
            Memory(subject="user", predicate="name", object="Alice", memory_type=MemoryType.FACT),
            Memory(subject="user", predicate="prefers", object="Python", memory_type=MemoryType.PREFERENCE),
            Memory(subject="user", predicate="created", object="report", memory_type=MemoryType.EVENT),
        ]
        
        result = format_memories_for_prompt(memories)
        
        assert "Known Facts" in result
        assert "User Preferences" in result
        assert "Past Events" in result


class TestMemoryStore:
    """Tests for SemanticMemoryStore"""
    
    @pytest.fixture
    def temp_store(self):
        """Create a temporary memory store for testing"""
        from engine.knowledge.store import SemanticMemoryStore
        
        # Use temp file for database
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        
        store = SemanticMemoryStore(db_path=path)
        yield store
        
        # Cleanup
        try:
            os.unlink(path)
        except:
            pass
    
    @pytest.mark.asyncio
    async def test_add_memory(self, temp_store):
        """Test adding a memory"""
        memory_id = await temp_store.add_memory(
            subject="user",
            predicate="prefers",
            obj="dark mode",
            session_id="test_session",
            importance="high",
        )
        
        assert memory_id is not None
        assert len(memory_id) == 8  # UUID prefix
    
    @pytest.mark.asyncio
    async def test_get_memory(self, temp_store):
        """Test retrieving a memory"""
        memory_id = await temp_store.add_memory(
            subject="user",
            predicate="uses",
            obj="Python",
            session_id="test_session",
        )
        
        memory = temp_store.get_memory(memory_id)
        
        assert memory is not None
        assert memory["subject"] == "user"
        assert memory["predicate"] == "uses"
        assert memory["object"] == "Python"
    
    @pytest.mark.asyncio
    async def test_list_memories(self, temp_store):
        """Test listing memories"""
        # Add multiple memories
        await temp_store.add_memory(
            subject="user", predicate="prefers", obj="dark mode",
            session_id="test_session", importance="high"
        )
        await temp_store.add_memory(
            subject="user", predicate="uses", obj="VS Code",
            session_id="test_session", importance="medium"
        )
        await temp_store.add_memory(
            subject="user", predicate="likes", obj="Python",
            session_id="other_session", importance="low"
        )
        
        # List for test_session only
        memories = temp_store.list_memories(session_id="test_session")
        
        assert len(memories) == 2
        # Should be sorted by importance (high first)
        assert memories[0]["importance"] == "high"
    
    @pytest.mark.asyncio
    async def test_conflict_resolution(self, temp_store):
        """Test that conflicting memories supersede old ones"""
        # Add initial memory
        id1 = await temp_store.add_memory(
            subject="user",
            predicate="prefers",
            obj="light mode",
            session_id="test_session",
        )
        
        # Add conflicting memory (same subject + predicate)
        id2 = await temp_store.add_memory(
            subject="user",
            predicate="prefers",
            obj="dark mode",  # Updated preference
            session_id="test_session",
        )
        
        # Check first memory is now inactive
        m1 = temp_store.get_memory(id1)
        m2 = temp_store.get_memory(id2)
        
        assert m1["is_active"] == 0  # Superseded
        assert m2["is_active"] == 1  # Active
        
        # List should only return active memory
        memories = temp_store.list_memories(session_id="test_session")
        assert len(memories) == 1
        assert memories[0]["object"] == "dark mode"
    
    @pytest.mark.asyncio
    async def test_delete_memory(self, temp_store):
        """Test soft deleting a memory"""
        memory_id = await temp_store.add_memory(
            subject="user",
            predicate="test",
            obj="delete_me",
            session_id="test_session",
        )
        
        # Delete
        deleted = temp_store.delete_memory(memory_id)
        assert deleted == True
        
        # Memory should be inactive
        memory = temp_store.get_memory(memory_id)
        assert memory["is_active"] == 0
        
        # Should not appear in list
        memories = temp_store.list_memories(session_id="test_session")
        assert len(memories) == 0
    
    @pytest.mark.asyncio
    async def test_keyword_search(self, temp_store):
        """Test keyword-based search (fallback when no embeddings)"""
        # Add memories
        await temp_store.add_memory(
            subject="user", predicate="prefers", obj="dark mode",
            session_id="test_session"
        )
        await temp_store.add_memory(
            subject="user", predicate="uses", obj="Python programming",
            session_id="test_session"
        )
        
        # Search for "dark"
        results = await temp_store.search_memories(
            query="dark theme",
            session_id="test_session",
        )
        
        # Should find the dark mode memory via keyword match
        assert len(results) >= 1
    
    def test_get_stats(self, temp_store):
        """Test getting store statistics"""
        stats = temp_store.get_stats()
        
        assert "active_memories" in stats
        assert "total_memories" in stats
        assert "embeddings" in stats
        assert "db_path" in stats


class TestMemoryExtractor:
    """Tests for MemoryExtractor"""
    
    def test_format_conversation(self):
        """Test conversation formatting"""
        from engine.knowledge.extractor import MemoryExtractor
        
        extractor = MemoryExtractor()
        
        messages = [
            {"role": "user", "content": "I prefer dark mode"},
            {"role": "assistant", "content": "I'll remember that preference."},
            {"role": "user", "content": "Thanks!"},
        ]
        
        formatted = extractor._format_conversation(messages)
        
        assert "User: I prefer dark mode" in formatted
        assert "Assistant:" in formatted
    
    def test_validate_memory(self):
        """Test memory validation"""
        from engine.knowledge.extractor import MemoryExtractor
        
        extractor = MemoryExtractor()
        
        # Valid memory
        valid = {
            "subject": "user",
            "predicate": "prefers",
            "object": "dark mode",
        }
        assert extractor._validate_memory(valid) == True
        
        # Missing required field
        invalid = {
            "subject": "user",
            "predicate": "prefers",
        }
        assert extractor._validate_memory(invalid) == False
    
    def test_parse_extraction_response_json(self):
        """Test parsing JSON response"""
        from engine.knowledge.extractor import MemoryExtractor
        
        extractor = MemoryExtractor()
        
        response = '[{"subject": "user", "predicate": "prefers", "object": "dark mode"}]'
        memories = extractor._parse_extraction_response(response)
        
        assert len(memories) == 1
        assert memories[0]["subject"] == "user"
    
    def test_parse_extraction_response_markdown(self):
        """Test parsing markdown-wrapped JSON"""
        from engine.knowledge.extractor import MemoryExtractor
        
        extractor = MemoryExtractor()
        
        response = '''Here are the memories:
```json
[{"subject": "user", "predicate": "uses", "object": "Python"}]
```
'''
        memories = extractor._parse_extraction_response(response)
        
        assert len(memories) == 1
        assert memories[0]["object"] == "Python"


class TestSemanticSearch:
    """Tests for SemanticMemorySearch"""
    
    @pytest.fixture
    def temp_store_with_search(self):
        """Create store with search interface"""
        from engine.knowledge.store import SemanticMemoryStore
        from engine.knowledge.search import SemanticMemorySearch
        
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        
        store = SemanticMemoryStore(db_path=path)
        search = SemanticMemorySearch(store)
        
        yield store, search
        
        try:
            os.unlink(path)
        except:
            pass
    
    @pytest.mark.asyncio
    async def test_search_returns_scored_results(self, temp_store_with_search):
        """Test that search returns results with scores"""
        store, search = temp_store_with_search
        
        # Add a memory
        await store.add_memory(
            subject="user",
            predicate="prefers",
            obj="dark theme",
            session_id="test_session",
        )
        
        # Search
        results = await search.search(
            query="dark mode preference",
            session_id="test_session",
        )
        
        # Results should have scores
        for result in results:
            assert hasattr(result, "score")
            assert 0 <= result.score <= 1
    
    @pytest.mark.asyncio
    async def test_search_for_prompt(self, temp_store_with_search):
        """Test formatted search output"""
        store, search = temp_store_with_search
        
        await store.add_memory(
            subject="user",
            predicate="prefers",
            obj="Python",
            session_id="test_session",
            memory_type="preference",
        )
        
        result = await search.search_for_prompt(
            query="programming language",
            session_id="test_session",
        )
        
        # Should return formatted string
        assert isinstance(result, str)


# Run with: pytest tests/test_memory.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-x"])

