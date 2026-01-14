"""
NogicOS LLM Client - Claude API Integration
=====================================

封装 Anthropic Claude API 调用，支持：
1. Prompt Caching - 降Low成本，提HighDelayed
2. 流式Output - 实时Response
3. Tool Calling - Tool调用

参考:
- Anthropic SDK Python: https://github.com/anthropics/anthropic-sdk-python
- Prompt Caching: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching

Phase 5 Implement
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, AsyncIterator, Callable, Awaitable, TypeVar
import logging
import os
import json
import asyncio
import time

try:
    from anthropic import AsyncAnthropic, APIError, RateLimitError, APIConnectionError, APIStatusError
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    AsyncAnthropic = None
    APIError = Exception
    RateLimitError = Exception
    APIConnectionError = Exception
    APIStatusError = Exception

T = TypeVar('T')

from .types import (
    LLMResponse, ToolCall, Message, MessageRole, StopReason,
    ToolDefinition,
)

logger = logging.getLogger(__name__)


# ========== Config ==========

@dataclass
class LLMConfig:
    """
    LLM Config
    
    Supports different models and parameter configuration
    """
    # Model config
    model: str = "claude-sonnet-4-20250514"  # Default to latest Sonnet
    max_tokens: int = 4096
    temperature: float = 0.0  # Deterministic output, suitable for Agent
    
    # API Config
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: float = 120.0
    
    # Cache config
    enable_prompt_caching: bool = True
    cache_system_prompt: bool = True
    cache_tools: bool = True
    
    # Retry config
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_max_delay: float = 60.0  # Max backoff time
    retry_exponential_base: float = 2.0  # Exponential backoff base
    
    # Streaming config
    enable_streaming: bool = True
    fallback_to_non_streaming: bool = True  # Downgrade to non-streaming on failure
    
    def __post_init__(self):
        # Get API key from environment variable
        if self.api_key is None:
            self.api_key = os.environ.get("ANTHROPIC_API_KEY")


@dataclass
class CacheStats:
    """
    CacheStatistics
    
    跟踪 Prompt Caching Effect
    """
    total_calls: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    
    @property
    def cache_hit_rate(self) -> float:
        """Cache命Medium率"""
        total = self.cache_read_tokens + self.input_tokens
        if total == 0:
            return 0.0
        return self.cache_read_tokens / total
    
    @property
    def estimated_savings(self) -> float:
        """
        估算节省的成本比例
        
        CacheRead成本 = 10% 正常Input成本
        CacheWrite成本 = 125% 正常Input成本
        """
        normal_cost = self.input_tokens + self.cache_read_tokens
        cached_cost = self.input_tokens + self.cache_read_tokens * 0.1 + self.cache_write_tokens * 1.25
        if normal_cost == 0:
            return 0.0
        return 1 - (cached_cost / normal_cost)


# ========== Streaming Events ==========

@dataclass
class StreamEvent:
    """Streaming event"""
    type: str  # "text", "tool_call", "message_start", "message_end"
    text: Optional[str] = None
    tool_call: Optional[ToolCall] = None
    input_tokens: int = 0
    output_tokens: int = 0


# ========== LLM Client ==========

class LLMClient:
    """
    Claude LLM Client
    
    Wraps Anthropic API with support for:
    - Prompt Caching (reduces cost by up to 90%)
    - Streaming output
    - Tool Calling
    
    Usage example:
    ```python
    config = LLMConfig()
    client = LLMClient(config)
    await client.initialize()
    
    # Non-streaming call
    response = await client.generate(
        messages=[Message.user("Hello")],
        system_prompt="You are an AI assistant.",
        tools=[...]
    )
    
    # Streaming call
    async for event in client.stream(messages, system_prompt, tools):
        if event.type == "text":
            print(event.text, end="")
    ```
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM Client
        
        Args:
            config: LLM Config
        """
        self.config = config or LLMConfig()
        self._client: Optional[AsyncAnthropic] = None
        self._cache_stats = CacheStats()
        
        # System prompt cache (for Prompt Caching)
        self._cached_system_prompt: Optional[str] = None
        self._cached_tools: Optional[List[Dict[str, Any]]] = None
        
        self._initialized = False
    
    async def initialize(self):
        """InitializeClient"""
        if self._initialized:
            return
        
        if not HAS_ANTHROPIC:
            raise ImportError(
                "anthropic package not installed. "
                "Please run: pip install anthropic"
            )
        
        if not self.config.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set. "
                "Please set the environment variable or pass api_key in config."
            )
        
        self._client = AsyncAnthropic(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries,
        )
        
        self._initialized = True
        logger.info(f"LLMClient initialized with model={self.config.model}")
    
    def _prepare_system_content(self, system_prompt: str) -> List[Dict[str, Any]]:
        """
        Prepare system prompt content (with Prompt Caching support)
        
        Prompt Caching key points:
        - Use cache_control: {"type": "ephemeral"} to mark cacheable content
        - Cache TTL is 5 minutes, auto-refreshes on each use
        - Cache read cost is only 10% of normal cost
        """
        if not self.config.enable_prompt_caching or not self.config.cache_system_prompt:
            # Cache disabled
            return [{"type": "text", "text": system_prompt}]
        
        # Cache enabled
        return [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}  # Mark as cacheable
            }
        ]
    
    def _prepare_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare tool definitions (with Prompt Caching support)
        
        Tool definitions are typically large and stable, ideal for caching
        """
        if not tools:
            return []
        
        if not self.config.enable_prompt_caching or not self.config.cache_tools:
            return tools
        
        # Add cache_control to the last tool (Anthropic requires cache boundary at specific positions)
        cached_tools = [tool.copy() for tool in tools]
        if cached_tools:
            cached_tools[-1]["cache_control"] = {"type": "ephemeral"}
        
        return cached_tools
    
    def _prepare_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """
        Prepare message list - Phase 5 P0 Fix
        
        Convert Message objects to Claude API format, correctly handling:
        - Text messages
        - Image messages
        - Tool calls
        - Tool results (including screenshots)
        """
        result = []
        
        # Collect adjacent tool result messages (Claude requires them in a single user message)
        pending_tool_results = []
        
        for i, msg in enumerate(messages):
            # Handle tool result message - need to collect and merge
            if msg.role == MessageRole.TOOL and msg.tool_call_id:
                tool_result = self._format_tool_result_for_api(msg)
                pending_tool_results.append(tool_result)
                
                # Check if next message is also a tool result
                next_is_tool = (
                    i + 1 < len(messages) and 
                    messages[i + 1].role == MessageRole.TOOL
                )
                
                # If next is not a tool result, send collected results as a package
                if not next_is_tool and pending_tool_results:
                    result.append({
                        "role": "user",
                        "content": pending_tool_results,
                    })
                    pending_tool_results = []
                continue
            
            # Handle assistant message (may contain tool calls)
            if msg.role == MessageRole.ASSISTANT:
                api_msg = {"role": "assistant", "content": []}
                
                # Add text content
                if msg.content:
                    if isinstance(msg.content, str):
                        api_msg["content"].append({
                            "type": "text",
                            "text": msg.content,
                        })
                    elif isinstance(msg.content, list):
                        api_msg["content"].extend(msg.content)
                
                # Add tool calls
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        api_msg["content"].append({
                            "type": "tool_use",
                            "id": tc.id,
                            "name": tc.name,
                            "input": tc.arguments,
                        })
                
                # Ensure at least some content
                if not api_msg["content"]:
                    api_msg["content"] = [{"type": "text", "text": ""}]
                
                result.append(api_msg)
                continue
            
            # Handle user message
            if msg.role == MessageRole.USER:
                api_msg = {"role": "user"}
                
                if isinstance(msg.content, str):
                    # Check if content contains image markers
                    if "[SCREENSHOT:" in msg.content:
                        api_msg["content"] = self._parse_content_with_images(msg.content)
                    else:
                        api_msg["content"] = msg.content
                elif isinstance(msg.content, list):
                    api_msg["content"] = msg.content
                else:
                    api_msg["content"] = str(msg.content)
                
                result.append(api_msg)
                continue
            
            # Other message types
            api_msg = {
                "role": msg.role.value if msg.role != MessageRole.SYSTEM else "user",
                "content": msg.content if isinstance(msg.content, str) else str(msg.content),
            }
            result.append(api_msg)
        
        return result
    
    def _format_tool_result_for_api(self, msg: Message) -> Dict[str, Any]:
        """
        Format tool result for API - Phase 5 P0 Fix
        
        Handle text and image results
        """
        content = msg.content
        
        # If content is a list (structured content, may contain images)
        if isinstance(content, list):
            return {
                "type": "tool_result",
                "tool_use_id": msg.tool_call_id,
                "content": content,
            }
        
        # String content
        if isinstance(content, str):
            # Check if contains screenshot marker (legacy format compatibility)
            if "[SCREENSHOT:" in content:
                parts = content.split("[SCREENSHOT:")
                text_part = parts[0].strip()
                return {
                    "type": "tool_result",
                    "tool_use_id": msg.tool_call_id,
                    "content": text_part or "Screenshot captured",
                }
            
            return {
                "type": "tool_result",
                "tool_use_id": msg.tool_call_id,
                "content": content,
            }
        
        # Other types convert to JSON
        return {
            "type": "tool_result",
            "tool_use_id": msg.tool_call_id,
            "content": json.dumps(content) if content else "Success",
        }
    
    def _parse_content_with_images(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse content containing image markers - Phase 5 P0 Fix
        """
        result = []
        parts = content.split("[SCREENSHOT:")
        
        for i, part in enumerate(parts):
            if i == 0:
                # First part is pure text
                if part.strip():
                    result.append({"type": "text", "text": part.strip()})
            else:
                # Part containing screenshot marker
                if "]" in part:
                    # Text after screenshot marker
                    after_screenshot = part.split("]", 1)
                    if len(after_screenshot) > 1 and after_screenshot[1].strip():
                        result.append({"type": "text", "text": after_screenshot[1].strip()})
        
        return result if result else [{"type": "text", "text": content}]
    
    def _parse_response(self, response) -> LLMResponse:
        """
        Parse API Response
        
        Convert Anthropic API Response to LLMResponse
        """
        text_parts = []  # Collect all text blocks
        tool_calls = []
        
        for block in response.content:
            if block.type == "text":
                # Accumulate multiple text blocks (Claude may return multiple text blocks)
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=block.input,
                ))
        
        # Merge all text blocks
        content_text = "\n".join(text_parts) if text_parts else ""
        
        # Parse stop reason
        stop_reason_map = {
            "end_turn": StopReason.END_TURN,
            "tool_use": StopReason.TOOL_USE,
            "max_tokens": StopReason.MAX_TOKENS,
            "stop_sequence": StopReason.STOP_SEQUENCE,
        }
        stop_reason = stop_reason_map.get(response.stop_reason, StopReason.END_TURN)
        
        # UpdateCacheStatistics
        self._cache_stats.total_calls += 1
        self._cache_stats.input_tokens += response.usage.input_tokens
        self._cache_stats.output_tokens += response.usage.output_tokens
        
        # Prompt Caching Statistics
        if hasattr(response.usage, 'cache_read_input_tokens'):
            self._cache_stats.cache_read_tokens += response.usage.cache_read_input_tokens
        if hasattr(response.usage, 'cache_creation_input_tokens'):
            self._cache_stats.cache_write_tokens += response.usage.cache_creation_input_tokens
        
        return LLMResponse(
            content=content_text,
            stop_reason=stop_reason,
            tool_calls=tool_calls,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )
    
    def _calculate_retry_delay(self, attempt: int, error: Exception = None) -> float:
        """
        Calculate retry delay (exponential backoff)
        
        Args:
            attempt: Current retry attempt number (starting from 1)
            error: Exception object (may contain retry-after header)
            
        Returns:
            Delay in seconds
        """
        # Check for retry-after header
        if hasattr(error, 'response') and error.response:
            retry_after = error.response.headers.get('retry-after')
            if retry_after:
                try:
                    return min(float(retry_after), self.config.retry_max_delay)
                except ValueError:
                    pass
        
        # Exponential backoff: delay * base^attempt
        delay = self.config.retry_delay * (self.config.retry_exponential_base ** (attempt - 1))
        # Add jitter to avoid thundering herd
        import random
        jitter = random.uniform(0, delay * 0.1)
        return min(delay + jitter, self.config.retry_max_delay)
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Determine if error is retryable
        
        Args:
            error: Exception object
            
        Returns:
            Whether the error is retryable
        """
        # RateLimitError (429) - retryable
        if isinstance(error, RateLimitError):
            return True
        
        # ConnectionError - retryable
        if HAS_ANTHROPIC and isinstance(error, APIConnectionError):
            return True
        
        # 5xx Server error - retryable
        if HAS_ANTHROPIC and isinstance(error, APIStatusError):
            if hasattr(error, 'status_code') and 500 <= error.status_code < 600:
                return True
        
        # Network timeout - retryable
        if isinstance(error, (asyncio.TimeoutError, TimeoutError)):
            return True
        
        return False
    
    async def generate(
        self,
        messages: List[Message],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        """
        Generate response (non-streaming) - with retry logic
        
        Args:
            messages: Message history
            system_prompt: System prompt
            tools: Tool definitions list
            
        Returns:
            LLMResponse
        """
        if not self._initialized:
            await self.initialize()
        
        # Prepare request arguments
        system_content = self._prepare_system_content(system_prompt)
        api_messages = self._prepare_messages(messages)
        
        kwargs = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "system": system_content,
            "messages": api_messages,
        }
        
        # Add tools
        if tools:
            kwargs["tools"] = self._prepare_tools(tools)
        
        logger.debug(f"Calling Claude API: model={self.config.model}, messages={len(messages)}")
        
        last_error = None
        for attempt in range(1, self.config.max_retries + 1):
            try:
                response = await self._client.messages.create(**kwargs)
                return self._parse_response(response)
            
            except (RateLimitError, APIConnectionError, APIStatusError, asyncio.TimeoutError) as e:
                last_error = e
                
                if not self._is_retryable_error(e):
                    logger.error(f"Non-retryable API error: {e}")
                    raise
                
                if attempt >= self.config.max_retries:
                    logger.error(f"Max retries ({self.config.max_retries}) exceeded: {e}")
                    raise
                
                delay = self._calculate_retry_delay(attempt, e)
                logger.warning(
                    f"API error (attempt {attempt}/{self.config.max_retries}): {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)
            
            except APIError as e:
                logger.error(f"API error: {e}")
                raise
        
        # Should not reach here, but just in case
        raise last_error or RuntimeError("Unexpected error in generate")
    
    async def stream(
        self,
        messages: List[Message],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        on_text: Optional[Callable[[str], Awaitable[None]]] = None,
        on_tool_call: Optional[Callable[[ToolCall], Awaitable[None]]] = None,
    ) -> LLMResponse:
        """
        Stream response generation - with retry and fallback logic
        
        Supports real-time callbacks, suitable for frontend display
        Falls back to non-streaming on failure
        
        Args:
            messages: Message history
            system_prompt: System prompt
            tools: Tool definitions list
            on_text: Text callback (per token)
            on_tool_call: Tool call callback
            
        Returns:
            Final LLMResponse
        """
        if not self._initialized:
            await self.initialize()
        
        if not self.config.enable_streaming:
            # Use non-streaming directly
            return await self.generate(messages, system_prompt, tools)
        
        # Prepare request arguments
        system_content = self._prepare_system_content(system_prompt)
        api_messages = self._prepare_messages(messages)
        
        kwargs = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "system": system_content,
            "messages": api_messages,
        }
        
        if tools:
            kwargs["tools"] = self._prepare_tools(tools)
        
        logger.debug(f"Streaming from Claude API: model={self.config.model}")
        
        last_error = None
        for attempt in range(1, self.config.max_retries + 1):
            try:
                return await self._do_stream(kwargs, on_text, on_tool_call)
            
            except (RateLimitError, APIConnectionError, APIStatusError, asyncio.TimeoutError) as e:
                last_error = e
                
                if not self._is_retryable_error(e):
                    logger.error(f"Non-retryable streaming error: {e}")
                    break  # Try fallback
                
                if attempt >= self.config.max_retries:
                    logger.warning(f"Max streaming retries exceeded: {e}")
                    break  # Try fallback
                
                delay = self._calculate_retry_delay(attempt, e)
                logger.warning(
                    f"Streaming error (attempt {attempt}/{self.config.max_retries}): {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)
            
            except APIError as e:
                logger.error(f"Streaming API error: {e}")
                last_error = e
                break  # Try fallback
        
        # Streaming failed, try fallback to non-streaming
        if self.config.fallback_to_non_streaming:
            logger.warning("Streaming failed, falling back to non-streaming mode")
            
            # Notify caller to reset previous streaming output
            # Send special marker so frontend clears already displayed content
            # Use unique control sequence to avoid conflict with model output
            if on_text:
                try:
                    await on_text("\x00__NOGICOS_CTRL_STREAM_RESET__\x00")
                except Exception:
                    pass  # Ignore callback error
            
            try:
                response = await self.generate(messages, system_prompt, tools)
                # Mark as fallback response, caller can decide whether to reset UI
                response.is_fallback = True
                return response
            except Exception as fallback_error:
                logger.error(f"Fallback to non-streaming also failed: {fallback_error}")
                # Throw original streaming error
                raise last_error or fallback_error
        
        # No fallback, throw error directly
        raise last_error or RuntimeError("Streaming failed")
    
    async def _do_stream(
        self,
        kwargs: Dict[str, Any],
        on_text: Optional[Callable[[str], Awaitable[None]]] = None,
        on_tool_call: Optional[Callable[[ToolCall], Awaitable[None]]] = None,
    ) -> LLMResponse:
        """
        Execute streaming call - internal method
        
        Args:
            kwargs: API call arguments
            on_text: Text callback
            on_tool_call: Tool call callback
            
        Returns:
            LLMResponse
        """
        # Collect response content
        content_text = ""
        tool_calls = []
        current_tool_id = None
        current_tool_name = None
        current_tool_input = ""
        input_tokens = 0
        output_tokens = 0
        stop_reason = StopReason.END_TURN
        
        async with self._client.messages.stream(**kwargs) as stream:
            async for event in stream:
                if event.type == "message_start":
                    if hasattr(event.message, 'usage'):
                        input_tokens = event.message.usage.input_tokens
                
                elif event.type == "content_block_start":
                    if event.content_block.type == "tool_use":
                        current_tool_id = event.content_block.id
                        current_tool_name = event.content_block.name
                        current_tool_input = ""
                
                elif event.type == "content_block_delta":
                    if hasattr(event.delta, 'text'):
                        # Text delta
                        text = event.delta.text
                        content_text += text
                        if on_text:
                            await on_text(text)
                    
                    elif hasattr(event.delta, 'partial_json'):
                        # Tool input delta
                        current_tool_input += event.delta.partial_json
                
                elif event.type == "content_block_stop":
                    if current_tool_id and current_tool_name:
                        # Complete tool call
                        try:
                            tool_input = json.loads(current_tool_input) if current_tool_input else {}
                        except json.JSONDecodeError:
                            tool_input = {}
                        
                        tool_call = ToolCall(
                            id=current_tool_id,
                            name=current_tool_name,
                            arguments=tool_input,
                        )
                        tool_calls.append(tool_call)
                        
                        if on_tool_call:
                            await on_tool_call(tool_call)
                        
                        # Reset
                        current_tool_id = None
                        current_tool_name = None
                        current_tool_input = ""
                
                elif event.type == "message_delta":
                    if hasattr(event, 'delta') and hasattr(event.delta, 'stop_reason'):
                        stop_reason_map = {
                            "end_turn": StopReason.END_TURN,
                            "tool_use": StopReason.TOOL_USE,
                            "max_tokens": StopReason.MAX_TOKENS,
                            "stop_sequence": StopReason.STOP_SEQUENCE,
                        }
                        stop_reason = stop_reason_map.get(event.delta.stop_reason, StopReason.END_TURN)
                    
                    if hasattr(event, 'usage'):
                        output_tokens = event.usage.output_tokens
            
            # Get final message for complete usage stats
            final_message = await stream.get_final_message()
            
            # Update statistics
            self._cache_stats.total_calls += 1
            self._cache_stats.input_tokens += final_message.usage.input_tokens
            self._cache_stats.output_tokens += final_message.usage.output_tokens
            
            if hasattr(final_message.usage, 'cache_read_input_tokens'):
                self._cache_stats.cache_read_tokens += final_message.usage.cache_read_input_tokens
            if hasattr(final_message.usage, 'cache_creation_input_tokens'):
                self._cache_stats.cache_write_tokens += final_message.usage.cache_creation_input_tokens
        
        return LLMResponse(
            content=content_text,
            stop_reason=stop_reason,
            tool_calls=tool_calls,
            input_tokens=final_message.usage.input_tokens,
            output_tokens=final_message.usage.output_tokens,
        )
    
    def get_cache_stats(self) -> CacheStats:
        """Get cache statistics"""
        return self._cache_stats
    
    def reset_cache_stats(self):
        """Reset cache statistics"""
        self._cache_stats = CacheStats()
    
    async def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        
        Uses simple estimation (should use tiktoken in production)
        """
        # Rough estimate: 1 token ≈ 4 chars (English), 1 token ≈ 1.5 chars (Chinese)
        # Using conservative estimate here
        return len(text) // 3
    
    async def close(self):
        """Close client"""
        if self._client:
            await self._client.close()
            self._client = None
            self._initialized = False


# ========== Convenience Functions ==========

_default_client: Optional[LLMClient] = None


async def get_llm_client(config: Optional[LLMConfig] = None) -> LLMClient:
    """Get global LLM client singleton"""
    global _default_client
    
    if _default_client is None:
        _default_client = LLMClient(config)
        await _default_client.initialize()
    
    return _default_client


async def generate(
    messages: List[Message],
    system_prompt: str,
    tools: Optional[List[Dict[str, Any]]] = None,
) -> LLMResponse:
    """Convenience generation function"""
    client = await get_llm_client()
    return await client.generate(messages, system_prompt, tools)
