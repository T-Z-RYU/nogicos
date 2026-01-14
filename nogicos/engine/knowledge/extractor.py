# -*- coding: utf-8 -*-
"""
Memory Extractor - LLM-based memory extraction from conversations.

Based on LangMem's memory extraction pattern:
- Use Claude to extract structured memories from conversations
- Support for facts, preferences, events, relationships
- Conflict detection with existing memories
- Batch extraction for efficiency

Reference: https://github.com/langchain-ai/langmem
"""

import os
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger("nogicos.memory")


# Memory extraction prompt template
# NOTE: Double braces {{ }} are used to escape JSON examples from Python str.format()
EXTRACTION_PROMPT = """You are a memory extraction system. Your task is to analyze conversations and extract important information as structured memories.

## Instructions
1. Extract factual information about the user (preferences, habits, tools they use)
2. Note any explicit instructions or corrections from the user
3. Capture important events or actions that occurred
4. Identify relationships between entities

## Output Format
Return a JSON array of memories. Each memory should have:
- subject: Who or what the memory is about (usually "user" or a specific entity)
- predicate: The relationship or property (e.g., "prefers", "uses", "created", "works_at")
- object: The value or target
- type: One of "fact", "preference", "event", "relationship", "instruction"
- importance: "high" (explicit user statement/instruction), "medium" (inferred preference), "low" (incidental information)
- context: Optional brief context

## Examples
User: "I always organize my files by date, please do it that way"
Output: [{{"subject": "user", "predicate": "prefers", "object": "organizing files by date", "type": "instruction", "importance": "high"}}]

User: "I just finished the quarterly report"
Output: [{{"subject": "user", "predicate": "completed", "object": "quarterly report", "type": "event", "importance": "medium"}}]

## Conversation to Analyze
{conversation}

## Existing Memories (avoid duplicates)
{existing_memories}

## Output
Return ONLY a JSON array. If no new memories to extract, return [].
"""


class MemoryExtractor:
    """
    Extracts structured memories from conversations using Claude.
    
    Design principles:
    - Non-blocking: Extraction runs in background after task completion
    - Conflict-aware: Checks against existing memories to avoid duplicates
    - Importance scoring: Prioritizes explicit user statements
    """
    
    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        max_memories_per_extraction: int = 5,
    ):
        """
        Initialize memory extractor.
        
        Args:
            model: Claude model to use for extraction
            max_memories_per_extraction: Limit on memories per conversation
        """
        self.model = model
        self.max_memories_per_extraction = max_memories_per_extraction
        self._client = None
    
    def _get_client(self):
        """Lazy-load Anthropic client"""
        if self._client is None:
            try:
                import anthropic
                # Try api_keys.py first, then environment variable
                api_key = None
                try:
                    import api_keys
                    api_key = api_keys.ANTHROPIC_API_KEY
                except (ImportError, AttributeError):
                    api_key = os.environ.get("ANTHROPIC_API_KEY")
                
                if api_key:
                    self._client = anthropic.Anthropic(api_key=api_key)
                else:
                    logger.warning("[Extractor] ANTHROPIC_API_KEY not set")
            except ImportError:
                logger.warning("[Extractor] anthropic package not installed")
        return self._client
    
    async def extract_memories(
        self,
        messages: List[Dict[str, Any]],
        existing_memories: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract memories from a conversation.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            existing_memories: Optional list of existing memories to avoid duplicates
            
        Returns:
            List of extracted memory dicts
        """
        client = self._get_client()
        if client is None:
            logger.warning("[Extractor] No client available, skipping extraction")
            return []
        
        # Format conversation for prompt
        conversation_text = self._format_conversation(messages)
        
        # Format existing memories
        existing_text = self._format_existing_memories(existing_memories or [])
        
        # Build extraction prompt
        prompt = EXTRACTION_PROMPT.format(
            conversation=conversation_text,
            existing_memories=existing_text,
        )
        
        try:
            # Call Claude for extraction
            response = client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt,
                }],
            )
            
            # Parse response
            response_text = response.content[0].text.strip()
            memories = self._parse_extraction_response(response_text)
            
            # Limit and validate
            validated = []
            for mem in memories[:self.max_memories_per_extraction]:
                if self._validate_memory(mem):
                    validated.append(mem)
            
            logger.debug(f"[Extractor] Extracted {len(validated)} memories")
            return validated
            
        except Exception as e:
            logger.error(f"[Extractor] Extraction failed: {e}")
            return []
    
    def _format_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """Format messages for the extraction prompt"""
        lines = []
        for msg in messages[-10:]:  # Limit to last 10 messages
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            # Skip tool results and empty messages
            if not content or role == "tool":
                continue
            
            # Truncate very long messages
            if len(content) > 500:
                content = content[:500] + "..."
            
            role_label = "User" if role == "user" else "Assistant"
            lines.append(f"{role_label}: {content}")
        
        return "\n".join(lines) if lines else "(No conversation content)"
    
    def _format_existing_memories(self, memories: List[Dict[str, Any]]) -> str:
        """Format existing memories to avoid duplicates"""
        if not memories:
            return "(No existing memories)"
        
        lines = []
        for mem in memories[:10]:  # Limit to 10 most relevant
            subject = mem.get("subject", "")
            predicate = mem.get("predicate", "")
            obj = mem.get("object", "")
            lines.append(f"- {subject} {predicate} {obj}")
        
        return "\n".join(lines)
    
    def _parse_extraction_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into memory list"""
        # Try to extract JSON from response
        try:
            # Handle potential markdown code blocks
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end].strip()
            
            # Handle empty array response
            if response.strip() in ("[]", ""):
                return []
            
            # Parse JSON
            memories = json.loads(response)
            
            if isinstance(memories, list):
                # Filter to only valid dicts with required fields
                valid = []
                for m in memories:
                    if isinstance(m, dict) and all(k in m for k in ["subject", "predicate", "object"]):
                        valid.append(m)
                return valid
            elif isinstance(memories, dict):
                # Single memory returned as dict - validate it
                if all(k in memories for k in ["subject", "predicate", "object"]):
                    return [memories]
            
            return []
            
        except json.JSONDecodeError as e:
            logger.debug(f"[Extractor] Failed to parse response as JSON: {response[:100]}...")
            return []
        except Exception as e:
            logger.debug(f"[Extractor] Unexpected error parsing response: {e}")
            return []
    
    def _validate_memory(self, memory: Any) -> bool:
        """Validate a memory dict has required fields"""
        # Must be a dict
        if not isinstance(memory, dict):
            return False
        
        required = ["subject", "predicate", "object"]
        
        for field in required:
            if not memory.get(field):
                return False
        
        # Validate type
        valid_types = ["fact", "preference", "event", "relationship", "instruction"]
        if memory.get("type") and memory["type"] not in valid_types:
            memory["type"] = "fact"  # Default to fact
        
        # Validate importance
        valid_importance = ["high", "medium", "low"]
        if memory.get("importance") and memory["importance"] not in valid_importance:
            memory["importance"] = "medium"  # Default to medium
        
        return True


class BackgroundMemoryProcessor:
    """
    Processes memory extraction in the background without blocking responses.
    
    Usage:
        processor = BackgroundMemoryProcessor(memory_store)
        processor.schedule_extraction(messages, session_id)
    """
    
    def __init__(
        self,
        memory_store,
        extractor: Optional[MemoryExtractor] = None,
    ):
        """
        Initialize background processor.
        
        Args:
            memory_store: SemanticMemoryStore instance
            extractor: Optional MemoryExtractor (creates default if None)
        """
        self.memory_store = memory_store
        self.extractor = extractor or MemoryExtractor()
        self._pending_tasks: List[asyncio.Task] = []
    
    def schedule_extraction(
        self,
        messages: List[Dict[str, Any]],
        session_id: str,
        source_task: Optional[str] = None,
    ):
        """
        Schedule background memory extraction.
        
        Args:
            messages: Conversation messages
            session_id: Session ID for memory scoping
            source_task: Optional task description for context
        """
        task = asyncio.create_task(
            self._extract_and_save(messages, session_id, source_task)
        )
        self._pending_tasks.append(task)
        
        # Clean up completed tasks
        self._pending_tasks = [t for t in self._pending_tasks if not t.done()]
    
    async def _extract_and_save(
        self,
        messages: List[Dict[str, Any]],
        session_id: str,
        source_task: Optional[str] = None,
    ):
        """Extract memories and save to store"""
        try:
            # Get existing memories for context
            existing = self.memory_store.list_memories(
                session_id=session_id,
                limit=10,
            )
            
            # Extract new memories
            extracted = await self.extractor.extract_memories(
                messages=messages,
                existing_memories=existing,
            )
            
            # Save each extracted memory (with defensive checks)
            saved_count = 0
            for mem in extracted:
                # Skip non-dict items (defensive)
                if not isinstance(mem, dict):
                    logger.debug(f"[Memory] Skipping non-dict item: {type(mem)}")
                    continue
                
                # Ensure required fields exist
                subject = mem.get("subject")
                predicate = mem.get("predicate")
                obj = mem.get("object")
                
                if not all([subject, predicate, obj]):
                    logger.debug(f"[Memory] Skipping incomplete memory: {mem}")
                    continue
                
                await self.memory_store.add_memory(
                    subject=subject,
                    predicate=predicate,
                    obj=obj,
                    session_id=session_id,
                    memory_type=mem.get("type", "fact"),
                    importance=mem.get("importance", "medium"),
                    context=mem.get("context"),
                    source_task=source_task,
                )
                saved_count += 1
            
            if saved_count > 0:
                logger.info(f"[Memory] Saved {saved_count} memories for session {session_id}")
                
        except Exception as e:
            logger.error(f"[Memory] Background extraction failed: {e}")
    
    async def wait_pending(self, timeout: float = 5.0):
        """Wait for pending extraction tasks to complete"""
        if self._pending_tasks:
            await asyncio.wait(
                self._pending_tasks,
                timeout=timeout,
                return_when=asyncio.ALL_COMPLETED,
            )


# Convenience function for one-shot extraction
async def extract_memories_from_conversation(
    messages: List[Dict[str, Any]],
    existing_memories: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    One-shot memory extraction from a conversation.
    
    Args:
        messages: Conversation messages
        existing_memories: Optional existing memories
        
    Returns:
        List of extracted memory dicts
    """
    extractor = MemoryExtractor()
    return await extractor.extract_memories(messages, existing_memories)

