# -*- coding: utf-8 -*-
import asyncio
import json
import os
import time
from typing import Any, TypeVar
import contextvars

import aioconsole
import anthropic
import dotenv
import openai
import PIL.Image
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionContentPartImageParam,
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)

from skillweaver.util.image_to_base64 import image_to_base64, image_to_data_url
from skillweaver.util.perfmon import monitor

#  sniffio  nest_asyncio 
#  nest_asyncio environmentsniffio asyncset
try:
    import sniffio
    # set sniffio variable asyncio environment
    sniffio.current_async_library_cvar.set("asyncio")
except (ImportError, AttributeError):
    pass

# import Google Generative AI (version)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

dotenv.load_dotenv()

Function = dict
NoArgs = object()

ResponseFormatT = TypeVar("ResponseFormatT")


def _is_claude_model(model_name: str) -> bool:
    """Check if this is a Claude model"""
    return "claude" in model_name.lower() or "opus" in model_name.lower()


def _is_gemini_model(model_name: str) -> bool:
    """Check if this is a Gemini model"""
    return "gemini" in model_name.lower()


def _sync_anthropic_call(api_key: str, model: str, request_params: dict):
    """Use sync client in separate thread to call Anthropic, avoid nest_asyncio + anyio conflict"""
    sync_client = anthropic.Anthropic(api_key=api_key)
    return sync_client.messages.create(**request_params)


async def completion_anthropic(
    client: anthropic.AsyncAnthropic,
    model: str,
    messages: list,
    json_mode=False,
    json_schema=None,
    tools: list[Function] = [],
    args: dict = None,
    key="general",
) -> Any:
    """Anthropic Claude completion function - uses sync client to avoid nest_asyncio conflict"""
    if args is None:
        args = {}
    
    tries = 5
    backoff = 4
    
    for i in range(tries):
        try:
            start_time = time.time()
            
            # convertmessageformat Anthropic format
            anthropic_messages = []
            system_message = ""
            
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "system":
                    system_message = content if isinstance(content, str) else str(content)
                    continue
                
                if isinstance(content, list):
                    # handle
                    anthropic_content = []
                    for item in content:
                        if item.get("type") == "text":
                            anthropic_content.append({"type": "text", "text": item.get("text", "")})
                        elif item.get("type") == "image_url":
                            # convertformat
                            url = item.get("image_url", {}).get("url", "")
                            if url.startswith("data:"):
                                # parse data URL
                                parts = url.split(";")
                                media_type = parts[0].split(":")[1] if ":" in parts[0] else "image/png"
                                data = url.split(",")[1] if "," in url else ""
                                anthropic_content.append({
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": data,
                                    }
                                })
                        elif item.get("type") == "image":
                            anthropic_content.append(item)
                    content = anthropic_content
                else:
                    content = content if isinstance(content, str) else str(content)
                
                anthropic_messages.append({
                    "role": role,
                    "content": content,
                })
            
            # add JSON  system message
            if json_mode or json_schema:
                json_instruction = "\n\nIMPORTANT: You MUST respond with valid JSON only. No markdown, no explanation, just pure JSON."
                if json_schema:
                    schema_str = json.dumps(json_schema.get("schema", json_schema), indent=2)
                    json_instruction += f"\n\nYour response must conform to this JSON schema:\n{schema_str}"
                system_message = (system_message or "") + json_instruction
            
            # requestparameter
            request_params = {
                "model": model,
                "max_tokens": 4096,
                "messages": anthropic_messages,
            }
            
            if system_message:
                request_params["system"] = system_message
            
            # runsyncclient nest_asyncio + anyio 
            import concurrent.futures
            import traceback
            
            # #region agent log - DEBUG Anthropic call
            debug_log_path = r"c:\Users\WIN\Desktop\Cursor Project\.cursor\debug.log"
            def log_debug_anthropic(msg, data=None):
                try:
                    import json
                    entry = {"location": "lm.py:anthropic_call", "message": msg, "data": data or {}, "timestamp": time.time(), "sessionId": "debug-session", "hypothesisId": "F-anthropic"}
                    with open(debug_log_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                except: pass
            # #endregion
            
            api_key = os.getenv("ANTHROPIC_API_KEY")
            
            def sync_anthropic_call_wrapper():
                try:
                    log_debug_anthropic("Creating Anthropic client", {"model": model})
                    return _sync_anthropic_call(api_key, model, request_params)
                except FileNotFoundError as e:
                    log_debug_anthropic("FileNotFoundError in anthropic call", {"error": str(e), "traceback": traceback.format_exc()})
                    raise
                except Exception as e:
                    log_debug_anthropic("Exception in anthropic call", {"error": str(e), "type": type(e).__name__, "traceback": traceback.format_exc()})
                    raise
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(sync_anthropic_call_wrapper)
                response = future.result(timeout=300)
            
            end_time = time.time()
            monitor.log_timing_event("lm/" + key, start_time, end_time)
            
            # extractresponse
            content = ""
            if response.content:
                for block in response.content:
                    if hasattr(block, 'text'):
                        content += block.text
            
            input_tokens = response.usage.input_tokens if response.usage else 0
            output_tokens = response.usage.output_tokens if response.usage else 0
            monitor.log_token_usage(key, "anthropic:" + model, input_tokens, output_tokens)
            
            if json_mode or json_schema:
                # extract JSON
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # extract
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0].strip()
                    return json.loads(content)
            
            return content
            
        except Exception as e:
            if i < tries - 1:
                await aioconsole.aprint(f"Anthropic error: {e}. Retrying...")
                await asyncio.sleep(backoff)
                backoff = min(30, backoff * 2)
            else:
                await aioconsole.aprint("Reached maximum number of tries. Raising.")
                raise


async def completion_gemini(
    model: str,
    messages: list,
    json_mode=False,
    json_schema=None,
    tools: list[Function] = [],
    args: dict = None,
    key="general",
) -> Any:
    """Google Gemini completion function - based on latest docs"""
    if not GEMINI_AVAILABLE:
        raise ImportError("google-generativeai is not installed. Run: pip install google-generativeai")
    
    if args is None:
        args = {}
    
    tries = 5
    backoff = 4
    
    for i in range(tries):
        try:
            start_time = time.time()
            
            # config Gemini
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not set")
            genai.configure(api_key=api_key)
            
            # createmodel
            gemini_model = genai.GenerativeModel(model)
            
            # convertmessageformat
            prompt_parts = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if isinstance(content, list):
                    for item in content:
                        if item.get("type") == "text":
                            text = item.get("text", "")
                            if role == "system":
                                prompt_parts.insert(0, f"System instruction: {text}\n\n")
                            else:
                                prompt_parts.append(text)
                        elif item.get("type") == "image_url":
                            # Gemini handle
                            url = item.get("image_url", {}).get("url", "")
                            if url.startswith("data:"):
                                import base64
                                data = url.split(",")[1] if "," in url else ""
                                image_bytes = base64.b64decode(data)
                                # Gemini  Part object
                                prompt_parts.append({
                                    "mime_type": "image/png",
                                    "data": image_bytes
                                })
                else:
                    if role == "system":
                        prompt_parts.insert(0, f"System instruction: {content}\n\n")
                    else:
                        prompt_parts.append(str(content))
            
            # add JSON 
            if json_mode or json_schema:
                json_instruction = "\n\nIMPORTANT: Respond with valid JSON only. No markdown, no explanation."
                if json_schema:
                    schema_str = json.dumps(json_schema.get("schema", json_schema), indent=2)
                    json_instruction += f"\n\nJSON Schema:\n{schema_str}"
                prompt_parts.append(json_instruction)
            
            # merge
            if all(isinstance(p, str) for p in prompt_parts):
                prompt = "\n".join(prompt_parts)
                response = await asyncio.to_thread(
                    gemini_model.generate_content, prompt
                )
            else:
                response = await asyncio.to_thread(
                    gemini_model.generate_content, prompt_parts
                )
            
            end_time = time.time()
            monitor.log_timing_event("lm/" + key, start_time, end_time)
            
            content = response.text if response.text else ""
            
            # Token 
            try:
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    input_tokens = response.usage_metadata.prompt_token_count or 0
                    output_tokens = response.usage_metadata.candidates_token_count or 0
                    monitor.log_token_usage(key, "gemini:" + model, input_tokens, output_tokens)
            except:
                pass
            
            if json_mode or json_schema:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0].strip()
                    return json.loads(content)
            
            return content
            
        except Exception as e:
            if i < tries - 1:
                await aioconsole.aprint(f"Gemini error: {e}. Retrying...")
                await asyncio.sleep(backoff)
                backoff = min(30, backoff * 2)
            else:
                await aioconsole.aprint("Reached maximum number of tries. Raising.")
                raise


def _sync_openai_call(
    model: str,
    messages: list,
    response_format: dict,
    tools: list,
    args: dict,
) -> ChatCompletion:
    """Use sync client in separate thread to call OpenAI, avoid nest_asyncio + anyio conflict"""
    sync_client = openai.OpenAI()
    return sync_client.chat.completions.create(
        model=model,
        messages=messages,
        response_format=response_format,
        **(
            {
                "tools": tools,
                "tool_choice": "required",
                "parallel_tool_calls": False,
            }
            if len(tools) > 0
            else {}
        ),
        **args,
    )


async def completion_openai(
    client: openai.AsyncAzureOpenAI | openai.AsyncOpenAI,
    model: str,
    messages: list[ChatCompletionMessageParam],
    json_mode=False,
    json_schema=None,
    tools: list[Function] = [],
    args: dict = NoArgs,  # type: ignore
    key="general",
) -> Any:
    if args is NoArgs:
        args = {}
    else:
        args = {**args}

    tries = 5
    backoff = 4
    for i in range(tries):
        try:
            start_time = time.time()

            if json_mode:
                response_format = {"type": "json_object"}
            elif json_schema:
                response_format = {
                    "type": "json_schema",
                    "json_schema": json_schema,
                }
            else:
                response_format = {"type": "text"}

            # runsyncclient nest_asyncio + anyio 
            import concurrent.futures
            import traceback
            
            # #region agent log - DEBUG OpenAI call
            debug_log_path = r"c:\Users\WIN\Desktop\Cursor Project\.cursor\debug.log"
            def log_debug(msg, data=None):
                try:
                    import json
                    entry = {"location": "lm.py:sync_openai_call", "message": msg, "data": data or {}, "timestamp": time.time(), "sessionId": "debug-session", "hypothesisId": "F-openai"}
                    with open(debug_log_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                except: pass
            # #endregion
            
            def sync_openai_call():
                try:
                    log_debug("Creating OpenAI client")
                    sync_client = openai.OpenAI()
                    log_debug("Client created, calling API", {"model": model})
                    result = sync_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        response_format=response_format,
                        **(
                            {
                                "tools": tools,
                                "tool_choice": "required",
                                "parallel_tool_calls": False,
                            }
                            if len(tools) > 0
                            else {}
                        ),
                        **args,
                    )
                    log_debug("API call succeeded")
                    return result
                except FileNotFoundError as e:
                    log_debug("FileNotFoundError in sync_openai_call", {"error": str(e), "traceback": traceback.format_exc()})
                    raise
                except Exception as e:
                    log_debug("Exception in sync_openai_call", {"error": str(e), "type": type(e).__name__, "traceback": traceback.format_exc()})
                    raise
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(sync_openai_call)
                response: ChatCompletion = future.result(timeout=300)

            end_time = time.time()
            monitor.log_timing_event("lm/" + key, start_time, end_time)
            assert response.usage
            msg = response.choices[0].message
            cmpl_tokens = response.usage.completion_tokens  # type: ignore
            prompt_tokens = response.usage.prompt_tokens  # type: ignore

            monitor.log_token_usage(key, "openai:" + model, prompt_tokens, cmpl_tokens)

            if len(tools) > 0:
                fn_names = [t["name"] for t in tools]
                assert (
                    msg.tool_calls is not None and len(msg.tool_calls) > 0
                ), "Tool list provided, but no tool call was made."

                assert (
                    msg.tool_calls[0].function.name in fn_names
                ), f"Unexpected tool name: {msg.tool_calls[0].function.name}"

                try:
                    arguments = json.loads(msg.tool_calls[0].function.arguments)
                except json.JSONDecodeError:
                    print("JSONDecodeError. Function call arguments:")
                    print(msg.tool_calls[0].function.arguments)
                    raise

                return {
                    "name": msg.tool_calls[0].function.name,
                    "arguments": arguments,
                }

            if msg.content is None:
                await aioconsole.aprint("msg.content was None. msg:", msg)

            assert msg.content is not None

            if json_mode or json_schema is not None:
                return json.loads(msg.content)
            else:
                return msg.content
        except Exception as e:
            if "JSON" in str(type(e)).upper():
                await aioconsole.aprint("JSON error:")
                await aioconsole.aprint("Content:", msg.content)
                await aioconsole.aprint(e)

            if i < tries - 1:
                await aioconsole.aprint(f"Error: {e}. Retrying...")
                await asyncio.sleep(backoff)
                backoff = min(30, backoff * 2)
            else:
                await aioconsole.aprint("Reached maximum number of tries. Raising.")
                raise


def create_tool_description(tool: ChatCompletionToolParam):
    name = tool["function"]["name"]
    args_str = ", ".join(
        tool["function"]["parameters"].keys()
        if "parameters" in tool["function"]
        else []
    )

    string = f"Function: {name}({args_str})\n\n"

    if "description" in tool["function"]:
        string += "Description:\n" + tool["function"]["description"] + "\n\n"

    if "parameters" in tool["function"]:
        params: dict = tool["function"]["parameters"]["properties"]  # type: ignore

        string += "Parameters:\n"
        for parameter_name, parameter in params.items():
            string += f"- {parameter_name}"

            if "description" in parameter:
                string += ": " + parameter["description"]

            string += "\n"

        string += "\n\n"

    return string


def _get_client(model_name: str):
    """Get the correct client based on model name"""
    # Claude model
    if _is_claude_model(model_name):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set for Claude model")
        return anthropic.AsyncAnthropic(api_key=api_key)
    
    # Gemini model - return Noneconfig
    if _is_gemini_model(model_name):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")
        return None
    
    # OpenAI modeldefault-  aiohttp  httpx/anyio  nest_asyncio 
    try:
        from openai import DefaultAioHttpClient
        http_client = DefaultAioHttpClient()
    except ImportError:
        #  aiohttp defaultclient
        http_client = None
    
    if os.getenv("AZURE_OPENAI", "0") == "1":
        endpoint = os.getenv(f"AZURE_OPENAI_{model_name.replace('-', '_')}_ENDPOINT")
        api_key = os.getenv(f"AZURE_OPENAI_{model_name.replace('-', '_')}_API_KEY")

        assert (
            endpoint is not None and api_key is not None
        ), f"AZURE_OPENAI_*_ENDPOINT and AZURE_OPENAI_*_API_KEY are not set for the model '{model_name}'"

        api_version = endpoint.split("=")[-1]

        return openai.AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
            http_client=http_client,
        )
    else:
        return openai.AsyncOpenAI(http_client=http_client)


class LM:
    def __init__(
        self,
        model: str,
        max_concurrency=10,
        default_kwargs=None,
    ):
        self.model = model
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.client = _get_client(model)
        self.default_kwargs = default_kwargs or {}
        
        # modelclass
        self._is_claude = _is_claude_model(model)
        self._is_gemini = _is_gemini_model(model)

    def is_openai(self) -> bool:
        return isinstance(self.client, (openai.AsyncAzureOpenAI, openai.AsyncOpenAI))

    def is_anthropic(self) -> bool:
        return isinstance(self.client, anthropic.AsyncAnthropic)
    
    def is_gemini(self) -> bool:
        return self._is_gemini

    def image_url_content_piece(
        self, image: PIL.Image.Image
    ) -> ChatCompletionContentPartImageParam:
        if self.is_anthropic():
            return {
                "type": "image",  # type: ignore
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": image_to_base64(image),
                },
            }
        else:
            # OpenAI  Gemini format
            return {
                "type": "image_url",
                "image_url": {"url": image_to_data_url(image), "detail": "high"},
            }

    async def __call__(
        self,
        messages: list[ChatCompletionMessageParam],
        json_mode=False,
        json_schema=None,
        tools: list[Function] = [],
        key="general",
        **kwargs,
    ) -> Any:
        async with self.semaphore:
            if self.is_anthropic():
                return await completion_anthropic(
                    self.client,
                    self.model,
                    messages,
                    json_mode,
                    json_schema,
                    tools,
                    args={**self.default_kwargs, **kwargs},
                    key=key,
                )
            elif self.is_gemini():
                return await completion_gemini(
                    self.model,
                    messages,
                    json_mode,
                    json_schema,
                    tools,
                    args={**self.default_kwargs, **kwargs},
                    key=key,
                )
            elif self.is_openai():
                return await completion_openai(
                    self.client,
                    self.model,
                    messages,
                    json_mode,
                    json_schema,
                    tools,
                    args={**self.default_kwargs, **kwargs},
                    key=key,
                )
            else:
                raise ValueError(f"Unknown model type for: {self.model}")

    async def json(
        self,
        messages: list[ChatCompletionMessageParam],
        response_model: type[ResponseFormatT],
        **kwargs,
    ) -> ResponseFormatT:
        if self.is_openai():
            result = await self.client.beta.chat.completions.parse(
                messages=messages,
                model=self.model,
                response_format=response_model,
            )
            parsed = result.choices[0].message.parsed
            assert parsed is not None
            return parsed
        else:
            #  OpenAI model JSON mode
            result = await self(messages, json_mode=True, **kwargs)
            return result
