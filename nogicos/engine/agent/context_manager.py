"""
NogicOS Context Manager - UpDown文压缩Policy
========================================

smart管理 LLM UpDown文，支持：
1. Token 预算管理
2. 历史Message压缩（Usage Haiku）
3. 截Graph管理（保留最近 N 张）
4. ImportantInfo保留Policy

参考:
- Claude Context Window Management
- LangGraph Message History Compression

Phase 5b Implement
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, TYPE_CHECKING
import logging
import base64
import json

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False
    tiktoken = None

from .types import Message, MessageRole

if TYPE_CHECKING:
    from .llm_client import LLMClient

logger = logging.getLogger(__name__)


# ========== Token Budget ==========

@dataclass
class TokenBudget:
    """
    Token budget configuration
    
    Manages input/output token limits and cost estimation
    """
    # Token limits
    max_input_tokens: int = 180000      # Claude max input
    max_output_tokens: int = 8192       # Output limit
    
    # Thresholds
    warning_threshold: float = 0.75      # Warning at 75%
    compression_threshold: float = 0.80  # Trigger compression at 80%
    emergency_threshold: float = 0.95    # Emergency handling at 95%
    
    # Screenshot management
    max_screenshots: int = 3             # Keep last N screenshots
    # Screenshot token budget estimate (for reserving space)
    # Actual counting uses dynamic estimate: (width * height) / 750 * 1.2
    # This value is for space reservation, should be slightly above average
    screenshot_tokens_estimate: int = 3500  # 1920x1080 is actually ~3000-3500
    
    # Reserved space
    system_prompt_reserve: int = 5000    # System prompt reserve
    tool_definitions_reserve: int = 3000 # Tool definitions reserve
    response_reserve: int = 4096         # Response reserve space
    
    @property
    def available_for_history(self) -> int:
        """Tokens available for message history"""
        return (
            self.max_input_tokens 
            - self.system_prompt_reserve 
            - self.tool_definitions_reserve 
            - self.response_reserve
            - (self.max_screenshots * self.screenshot_tokens_estimate)
        )
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate API call cost (USD)
        
        Based on Claude 3.5 Sonnet pricing:
        - Input: $3 / 1M tokens
        - Output: $15 / 1M tokens
        """
        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0
        return input_cost + output_cost


# ========== Token Counter ==========

class TokenCounter:
    """
    Token counter
    
    Uses tiktoken for accurate counting, falls back to estimation
    """
    
    def __init__(self):
        self._encoder = None
        if HAS_TIKTOKEN:
            try:
                # Claude uses cl100k_base encoding (similar to GPT-4)
                self._encoder = tiktoken.get_encoding("cl100k_base")
            except Exception:
                pass
    
    def count(self, text: str) -> int:
        """Count tokens in text"""
        if self._encoder:
            return len(self._encoder.encode(text))
        else:
            # Use improved estimation when tiktoken unavailable
            return self._estimate_tokens(text)
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Improved token estimation (used when tiktoken unavailable)
        
        Rules:
        - English/numbers/punctuation: ~4 chars/token
        - Chinese/Japanese/Korean: ~1.5 chars/token (CJK chars take more tokens)
        - Mixed text weighted by proportion
        """
        if not text:
            return 0
        
        # Count CJK characters
        cjk_count = 0
        for char in text:
            # CJK unified ideographs range
            if '\u4e00' <= char <= '\u9fff':  # Chinese
                cjk_count += 1
            elif '\u3040' <= char <= '\u30ff':  # Japanese hiragana/katakana
                cjk_count += 1
            elif '\uac00' <= char <= '\ud7af':  # Korean
                cjk_count += 1
        
        non_cjk_count = len(text) - cjk_count
        
        # CJK ~1.5 chars/token, non-CJK ~4 chars/token
        cjk_tokens = cjk_count / 1.5
        non_cjk_tokens = non_cjk_count / 4
        
        # Add 10% safety margin
        return int((cjk_tokens + non_cjk_tokens) * 1.1)
    
    def count_message(self, message: Message) -> int:
        """Count tokens in a message"""
        tokens = 4  # Message overhead
        
        if isinstance(message.content, str):
            tokens += self.count(message.content)
        elif isinstance(message.content, list):
            tokens += self._count_content_list(message.content)
        
        if message.tool_calls:
            for tc in message.tool_calls:
                tokens += self.count(tc.name)
                tokens += self.count(json.dumps(tc.arguments))
        
        return tokens
    
    def _count_content_list(self, content_list: List[Any]) -> int:
        """
        Recursively count tokens in content list
        
        Handles text, image, tool_result types, supports nested content
        """
        tokens = 0
        
        for item in content_list:
            if isinstance(item, str):
                tokens += self.count(item)
            elif isinstance(item, dict):
                item_type = item.get("type", "")
                
                if item_type == "text":
                    tokens += self.count(item.get("text", ""))
                    
                elif item_type == "image":
                    tokens += self._estimate_image_tokens(item)
                    
                elif item_type == "tool_result":
                    # tool_result content can be string or list (with images)
                    content = item.get("content", "")
                    if isinstance(content, str):
                        tokens += self.count(content)
                    elif isinstance(content, list):
                        # Recursively handle nested content (may contain images)
                        tokens += self._count_content_list(content)
                    elif isinstance(content, dict):
                        # Single content block
                        tokens += self._count_content_list([content])
                        
                elif item_type == "tool_use":
                    tokens += self.count(item.get("name", ""))
                    tokens += self.count(json.dumps(item.get("input", {})))
                    
                else:
                    # Unknown type, use JSON estimation
                    tokens += self.count(json.dumps(item))
        
        return tokens
    
    def count_messages(self, messages: List[Message]) -> int:
        """Count total tokens in message list"""
        return sum(self.count_message(m) for m in messages)
    
    def _estimate_image_tokens(self, image_item: Dict[str, Any]) -> int:
        """
        Dynamically estimate image token count
        
        Based on Anthropic docs:
        - Base formula: (width * height) / 750
        - Minimum: ~1000 tokens
        - 1920x1080 ≈ 2765 tokens, but actual may be higher
        
        Args:
            image_item: Image content dict, may contain size info
            
        Returns:
            Estimated token count
        """
        # Try to extract size from image data
        width, height = 1920, 1080  # Default Full HD
        
        # Check for size info
        source = image_item.get("source", {})
        if isinstance(source, dict):
            # Check for explicit dimensions
            if "width" in source and "height" in source:
                width = source.get("width", width)
                height = source.get("height", height)
            
            # Try to infer size from base64 data
            data = source.get("data", "")
            if data and len(data) > 100:
                # Rough estimate based on base64 data size
                # PNG/JPEG have different compression, use conservative estimate
                data_size = len(data) * 3 / 4  # Size after base64 decode
                
                # Assume 8-bit color depth, 3 channels, 50% compression
                # pixels ≈ data_size / (3 * 0.5) = data_size * 0.67
                estimated_pixels = data_size * 0.67
                
                # Assume 16:9 aspect ratio
                estimated_height = int((estimated_pixels / (16/9)) ** 0.5)
                estimated_width = int(estimated_height * 16 / 9)
                
                if estimated_width > 100 and estimated_height > 100:
                    width = min(estimated_width, 4096)  # Limit max size
                    height = min(estimated_height, 4096)
        
        # Calculate token count
        # Anthropic formula: (width * height) / 750
        # Add 20% safety margin
        raw_tokens = (width * height) / 750
        tokens_with_margin = int(raw_tokens * 1.2)
        
        # Minimum 1500 tokens (conservative)
        return max(tokens_with_margin, 1500)


# ========== Context Compressor ==========

@dataclass
class CompressionResult:
    """Compression result"""
    messages: List[Message]
    original_tokens: int
    compressed_tokens: int
    removed_count: int
    summary_added: bool
    
    @property
    def compression_ratio(self) -> float:
        """Compression ratio"""
        if self.original_tokens == 0:
            return 0.0
        return 1 - (self.compressed_tokens / self.original_tokens)


class ContextCompressor:
    """
    Context compressor
    
    Strategy:
    1. Preserve system messages
    2. Preserve recent N messages
    3. Use Haiku to summarize history messages
    4. Preserve key messages with screenshots
    """
    
    # [P1 Fix] Class-level Haiku client to avoid repeated creation
    _haiku_client: Optional["LLMClient"] = None
    _haiku_initialized: bool = False
    
    def __init__(
        self,
        llm_client: Optional["LLMClient"] = None,
        use_haiku_summary: bool = True,
    ):
        """
        Initialize compressor
        
        Args:
            llm_client: LLM client (for generating summaries)
            use_haiku_summary: Whether to use Haiku for summaries
        """
        self._llm_client = llm_client
        self._use_haiku_summary = use_haiku_summary
        self._counter = TokenCounter()
    
    async def compress(
        self,
        messages: List[Message],
        budget: TokenBudget,
        preserve_recent: int = 6,
    ) -> CompressionResult:
        """
        Compress message history
        
        Args:
            messages: Message list
            budget: Token budget
            preserve_recent: Keep recent N messages
            
        Returns:
            CompressionResult
        """
        original_tokens = self._counter.count_messages(messages)
        
        # Check if compression needed
        if original_tokens <= budget.available_for_history:
            return CompressionResult(
                messages=messages,
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                removed_count=0,
                summary_added=False,
            )
        
        logger.info(f"Compressing context: {original_tokens} tokens -> target {budget.available_for_history}")
        
        # Split messages
        recent_messages = messages[-preserve_recent:] if len(messages) > preserve_recent else messages
        old_messages = messages[:-preserve_recent] if len(messages) > preserve_recent else []
        
        # If no old messages, return directly
        if not old_messages:
            return CompressionResult(
                messages=recent_messages,
                original_tokens=original_tokens,
                compressed_tokens=self._counter.count_messages(recent_messages),
                removed_count=0,
                summary_added=False,
            )
        
        # Generate summary
        summary = await self._summarize_history(old_messages)
        
        # Build new message list
        compressed_messages = []
        
        # Add summary message
        if summary:
            summary_msg = Message.system(f"[Previous conversation summary]\n{summary}")
            compressed_messages.append(summary_msg)
        
        # Add recent messages
        compressed_messages.extend(recent_messages)
        
        compressed_tokens = self._counter.count_messages(compressed_messages)
        
        return CompressionResult(
            messages=compressed_messages,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            removed_count=len(old_messages),
            summary_added=bool(summary),
        )
    
    async def _summarize_history(self, messages: List[Message]) -> str:
        """
        Use Haiku to summarize history messages - P1 Fix: reuse client
        
        Args:
            messages: Messages to summarize
            
        Returns:
            Summary text
        """
        if not self._use_haiku_summary:
            return self._extract_key_info(messages)
        
        # Build summary prompt
        history_text = self._format_messages_for_summary(messages)
        
        summary_prompt = f"""Summarize this conversation history concisely, preserving:
1. Key actions taken and their results
2. Important information discovered
3. Current progress towards the goal
4. Any errors or issues encountered

Keep the summary under 500 words.

Conversation history:
{history_text}"""
        
        try:
            # [P1 Fix] Reuse Haiku client
            haiku_client = await self._get_haiku_client()
            if not haiku_client:
                return self._extract_key_info(messages)
            
            response = await haiku_client.generate(
                messages=[Message.user(summary_prompt)],
                system_prompt="You are a concise summarizer. Extract key information only.",
            )
            
            return response.content
            
        except Exception as e:
            logger.warning(f"Failed to generate summary with Haiku: {e}")
            return self._extract_key_info(messages)
    
    @classmethod
    async def _get_haiku_client(cls) -> Optional["LLMClient"]:
        """
        Get or create Haiku client singleton - P1 Fix
        
        Reuse client to avoid resource leaks
        """
        if cls._haiku_initialized:
            return cls._haiku_client
        
        try:
            from .llm_client import LLMClient, LLMConfig
            
            haiku_config = LLMConfig(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                enable_prompt_caching=False,  # Summary doesn't need caching
                enable_streaming=False,  # Summary doesn't need streaming
            )
            cls._haiku_client = LLMClient(haiku_config)
            await cls._haiku_client.initialize()
            cls._haiku_initialized = True
            
            logger.info("Haiku client initialized for context compression")
            return cls._haiku_client
            
        except Exception as e:
            logger.warning(f"Failed to initialize Haiku client: {e}")
            cls._haiku_initialized = True  # Mark as attempted, avoid retrying
            return None
    
    def _format_messages_for_summary(self, messages: List[Message]) -> str:
        """Format messages for summary"""
        lines = []
        for msg in messages:
            role = msg.role.value.upper()
            if isinstance(msg.content, str):
                # Truncate overly long content
                content = msg.content[:500] + "..." if len(msg.content) > 500 else msg.content
                lines.append(f"[{role}]: {content}")
            elif isinstance(msg.content, list):
                # Handle complex content
                for item in msg.content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        content = item.get("text", "")[:500]
                        lines.append(f"[{role}]: {content}")
        
        return "\n".join(lines)
    
    def _extract_key_info(self, messages: List[Message]) -> str:
        """
        Extract key info from messages (without using LLM)
        
        Args:
            messages: Message list
            
        Returns:
            Key info summary
        """
        key_info = []
        
        for msg in messages:
            # Extract tool call results
            if msg.role == MessageRole.TOOL:
                if isinstance(msg.content, str):
                    # Keep only success/failure status
                    if "error" in msg.content.lower():
                        key_info.append(f"Tool error: {msg.content[:100]}")
                    elif "success" in msg.content.lower():
                        key_info.append(f"Tool success: {msg.name}")
            
            # Extract assistant's key actions
            elif msg.role == MessageRole.ASSISTANT and msg.tool_calls:
                for tc in msg.tool_calls:
                    key_info.append(f"Action: {tc.name}")
        
        if not key_info:
            return "Previous actions taken but details summarized for brevity."
        
        return "Previous actions: " + "; ".join(key_info[:10])


# ========== Context Manager ==========

class ContextManager:
    """
    Context manager
    
    Comprehensive LLM context management:
    - Token budget monitoring
    - Auto compression trigger
    - Screenshot management
    - Status reporting
    """
    
    def __init__(
        self,
        budget: Optional[TokenBudget] = None,
        llm_client: Optional["LLMClient"] = None,
    ):
        """
        Initialize context manager
        
        Args:
            budget: Token budget config
            llm_client: LLM client (for compression)
        """
        self.budget = budget or TokenBudget()
        self._counter = TokenCounter()
        self._compressor = ContextCompressor(llm_client)
        
        # Screenshot tracking
        self._screenshot_count = 0
    
    def count_tokens(self, messages: List[Message]) -> int:
        """Count tokens in messages"""
        return self._counter.count_messages(messages)
    
    def get_usage_ratio(self, messages: List[Message]) -> float:
        """Get token usage ratio"""
        tokens = self.count_tokens(messages)
        return tokens / self.budget.available_for_history
    
    def should_warn(self, messages: List[Message]) -> bool:
        """Whether to show warning"""
        return self.get_usage_ratio(messages) >= self.budget.warning_threshold
    
    def should_compress(self, messages: List[Message]) -> bool:
        """Whether to compress"""
        return self.get_usage_ratio(messages) >= self.budget.compression_threshold
    
    def is_emergency(self, messages: List[Message]) -> bool:
        """Whether in emergency state"""
        return self.get_usage_ratio(messages) >= self.budget.emergency_threshold
    
    async def maybe_compress(
        self,
        messages: List[Message],
        force: bool = False,
    ) -> List[Message]:
        """
        Compress messages as needed
        
        Args:
            messages: Message list
            force: Force compression
            
        Returns:
            Possibly compressed message list
        """
        if not force and not self.should_compress(messages):
            return messages
        
        result = await self._compressor.compress(messages, self.budget)
        
        if result.compression_ratio > 0:
            logger.info(
                f"Compressed context: {result.original_tokens} -> {result.compressed_tokens} tokens "
                f"({result.compression_ratio:.1%} reduction, {result.removed_count} messages removed)"
            )
        
        return result.messages
    
    def manage_screenshots(
        self,
        messages: List[Message],
    ) -> List[Message]:
        """
        Manage screenshot count
        
        Keep last N screenshots, remove old ones
        
        Args:
            messages: Message list
            
        Returns:
            Processed message list
        """
        max_screenshots = self.budget.max_screenshots
        screenshot_indices = []
        
        # Find all message positions containing screenshots
        for i, msg in enumerate(messages):
            if self._has_screenshot(msg):
                screenshot_indices.append(i)
        
        # If screenshot count exceeds limit, remove old ones
        if len(screenshot_indices) > max_screenshots:
            indices_to_remove = screenshot_indices[:-max_screenshots]
            
            # Create new message list, replace old screenshots
            new_messages = []
            for i, msg in enumerate(messages):
                if i in indices_to_remove:
                    # Replace with placeholder message
                    new_messages.append(
                        Message(
                            role=msg.role,
                            content="[Screenshot removed to save context space]",
                        )
                    )
                else:
                    new_messages.append(msg)
            
            logger.debug(f"Removed {len(indices_to_remove)} old screenshots")
            return new_messages
        
        return messages
    
    def _has_screenshot(self, message: Message) -> bool:
        """Check if message contains screenshot"""
        if isinstance(message.content, list):
            for item in message.content:
                if isinstance(item, dict):
                    if item.get("type") == "image":
                        return True
                    if item.get("type") == "tool_result" and item.get("content", {}).get("type") == "image":
                        return True
        return False
    
    def get_status(self, messages: List[Message]) -> Dict[str, Any]:
        """
        Get context status report
        
        Returns:
            Status info dictionary
        """
        tokens = self.count_tokens(messages)
        usage_ratio = self.get_usage_ratio(messages)
        
        return {
            "current_tokens": tokens,
            "max_tokens": self.budget.available_for_history,
            "usage_ratio": usage_ratio,
            "usage_percent": f"{usage_ratio:.1%}",
            "status": (
                "emergency" if self.is_emergency(messages)
                else "warning" if self.should_warn(messages)
                else "normal"
            ),
            "should_compress": self.should_compress(messages),
            "message_count": len(messages),
            "estimated_cost": self.budget.estimate_cost(tokens, 0),
        }


# ========== Convenience Functions ==========

_default_manager: Optional[ContextManager] = None


def get_context_manager(budget: Optional[TokenBudget] = None) -> ContextManager:
    """Get global context manager"""
    global _default_manager
    
    if _default_manager is None:
        _default_manager = ContextManager(budget)
    
    return _default_manager
