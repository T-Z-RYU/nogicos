# -*- coding: utf-8 -*-
"""
D2.3: Knowledge Store Tests

Tests for UserProfile, Trajectory, and KnowledgeStore.
"""

import pytest
import os
import tempfile
from engine.knowledge.models import UserProfile, Trajectory, LearnedSkill
from engine.knowledge.store import KnowledgeStore


class TestUserProfile:
    """Tests for UserProfile model"""
    
    def test_profile_creation(self):
        """Test creating a new profile"""
        profile = UserProfile(id="test")
        
        assert profile.id == "test"
        assert profile.frequent_folders == []
        assert profile.frequent_websites == []
    
    def test_add_frequent_folder(self):
        """Test adding frequent folders"""
        profile = UserProfile()
        
        profile.add_frequent_folder("/path/to/folder1")
        profile.add_frequent_folder("/path/to/folder2")
        profile.add_frequent_folder("/path/to/folder1")  # Duplicate
        
        assert len(profile.frequent_folders) == 2
        assert profile.frequent_folders[0] == "/path/to/folder1"  # Most recent
    
    def test_add_frequent_website(self):
        """Test adding frequent websites"""
        profile = UserProfile()
        
        profile.add_frequent_website("https://example.com/")
        profile.add_frequent_website("https://test.com")
        
        assert len(profile.frequent_websites) == 2
        assert "https://example.com" in profile.frequent_websites  # Normalized
    
    def test_context_for_prompt(self):
        """Test generating context for prompt"""
        profile = UserProfile()
        profile.add_frequent_folder("/home/user/Documents")
        profile.add_frequent_website("https://github.com")
        
        context = profile.get_context_for_prompt()
        
        assert "## User Context" in context
        assert "/home/user/Documents" in context
        assert "github.com" in context
    
    def test_serialization(self):
        """Test JSON serialization"""
        profile = UserProfile(id="test")
        profile.add_frequent_folder("/test")
        
        json_str = profile.to_json()
        restored = UserProfile.from_json(json_str)
        
        assert restored.id == profile.id
        assert restored.frequent_folders == profile.frequent_folders


class TestTrajectory:
    """Tests for Trajectory model"""
    
    def test_trajectory_creation(self):
        """Test creating a trajectory"""
        trajectory = Trajectory(
            id="test123",
            session_id="session1",
            task="Test task",
            success=True,
        )
        
        assert trajectory.id == "test123"
        assert trajectory.task == "Test task"
        assert trajectory.success is True
    
    def test_trajectory_serialization(self):
        """Test JSON serialization"""
        trajectory = Trajectory(
            task="Test task",
            tool_calls=[{"name": "test", "args": {}}],
        )
        
        json_str = trajectory.to_json()
        restored = Trajectory.from_json(json_str)
        
        assert restored.task == trajectory.task
        assert len(restored.tool_calls) == 1


class TestKnowledgeStore:
    """Tests for KnowledgeStore"""
    
    @pytest.fixture
    def store(self):
        """Create a temporary store for testing"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        store = KnowledgeStore(db_path=db_path)
        yield store
        
        # Cleanup
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_profile_persistence(self, store):
        """Test saving and loading profiles"""
        profile = UserProfile(id="test_user")
        profile.add_frequent_folder("/test/path")
        
        store.save_profile(profile)
        loaded = store.get_profile("test_user")
        
        assert loaded.id == "test_user"
        assert "/test/path" in loaded.frequent_folders
    
    def test_default_profile(self, store):
        """Test getting default profile"""
        profile = store.get_profile("new_user")
        
        assert profile.id == "new_user"
        assert profile.frequent_folders == []
    
    def test_trajectory_save(self, store):
        """Test saving trajectories"""
        trajectory = Trajectory(
            session_id="test_session",
            task="Test task",
            success=True,
        )
        
        traj_id = store.save_trajectory(trajectory)
        
        assert traj_id is not None
        assert len(traj_id) == 8
    
    def test_trajectory_search(self, store):
        """Test searching trajectories"""
        # Save some trajectories
        store.save_trajectory(Trajectory(
            session_id="s1",
            task="Search for files",
            success=True,
        ))
        store.save_trajectory(Trajectory(
            session_id="s1",
            task="Organize desktop",
            success=True,
        ))
        
        results = store.search_trajectories(query="files")
        
        assert len(results) >= 1
        assert "files" in results[0].task.lower()
    
    def test_stats(self, store):
        """Test getting store statistics"""
        store.save_trajectory(Trajectory(task="Test", success=True))
        store.save_trajectory(Trajectory(task="Test2", success=False))
        
        stats = store.get_stats()
        
        assert stats["trajectory_count"] == 2
        assert stats["success_count"] == 1
    
    def test_profile_update_from_execution(self, store):
        """Test updating profile from execution"""
        tool_calls = [
            {"name": "list_directory", "args": {"path": "/home/user/Documents"}, "success": True},
            {"name": "browser_navigate", "args": {"url": "https://example.com"}, "success": True},
        ]
        
        store.update_profile_from_execution("test", "List files", tool_calls)
        
        profile = store.get_profile("test")
        assert "/home/user/Documents" in profile.frequent_folders or "/home/user" in profile.frequent_folders

