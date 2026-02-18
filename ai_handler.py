"""
AI Handler Module
Routes voice commands to Groq or OpenRouter with automatic fallback.
Parses JSON responses and handles errors gracefully.
"""

import json
import re
from groq import Groq as GroqClient
from openai import OpenAI
import config

# System prompt for AI backend
SYSTEM_PROMPT = """You are Jarvis, a voice assistant. You receive a transcribed voice command.
Return ONLY valid JSON, no markdown, no explanation.
Available actions:

web_search(query)         → search the web, summarize result in 1-2 sentences
watch_youtube(query)      → open YouTube video search results for given query
open_app(name)            → open application by name
create_file(name,content) → create file in sandbox workspace only
read_file(name)           → read file from sandbox workspace
run_command(cmd)          → shell command, ONLY from allowlist: [ls, pwd, git, echo, python, pip, open]
clipboard_read()
clipboard_write(text)
system_info(metric)       → metric is one of: time, battery, disk
respond(text)             → just answer verbally/visually, no other action

Response format:
{"action": "action_name", "params": {...}, "answer": "short human-readable result or confirmation, max 2 sentences"}"""


def ask_ai(prompt: str) -> dict:
    """
    Send a prompt to the AI backend (Groq or OpenRouter).
    Automatically retries with fallback backend on error.
    Returns parsed JSON response.
    
    Args:
        prompt: User command/question to send to AI
        
    Returns:
        Parsed JSON dict with keys: action, params, answer
        On error, returns safe fallback response
    """
    
    # Try primary backend first
    primary_backend = config.AI_BACKEND
    backends = [primary_backend]
    
    # Add fallback backend
    fallback = "openrouter" if primary_backend == "groq" else "groq"
    backends.append(fallback)
    
    for backend in backends:
        try:
            if backend == "groq":
                response = _call_groq(prompt)
            else:
                response = _call_openrouter(prompt)
            
            print(f"[DEBUG] Raw response from {backend}: {response[:200] if len(response) > 200 else response}")
            
            # Parse JSON with improved handling
            parsed = _parse_json_response(response, prompt)
            
            # Validate required fields
            if "action" not in parsed or "params" not in parsed or "answer" not in parsed:
                raise ValueError("Missing required fields in parsed response")
            
            return parsed
        
        except json.JSONDecodeError as e:
            print(f"JSON parse error from {backend}: {e}")
            continue
        except ValueError as e:
            print(f"Validation error from {backend}: {e}")
            continue
        except Exception as e:
            print(f"Error with {backend} backend: {e}")
            continue
    
    # All backends failed, return safe fallback
    print("All AI backends failed, returning fallback response")
    return {
        "action": "respond",
        "params": {},
        "answer": "I encountered an error. Please try again."
    }


def _parse_json_response(response_text: str, prompt: str) -> dict:
    """
    Parse JSON from AI response with robustness to various formats.
    Extracts JSON from markdown code blocks if needed.
    Provides sensible defaults for missing fields.
    
    Args:
        response_text: Raw response from AI
        prompt: Original user prompt (for fallback inference)
        
    Returns:
        Parsed dict with action, params, answer
    """
    # Try to extract JSON from markdown code blocks first
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if json_match:
        response_text = json_match.group(1)
    
    # Try to parse as JSON
    try:
        parsed = json.loads(response_text)
        if isinstance(parsed, dict):
            # Ensure all required fields exist
            if "action" not in parsed:
                parsed["action"] = "respond"
            if "params" not in parsed:
                parsed["params"] = {}
            if "answer" not in parsed:
                parsed["answer"] = "Done"
            return parsed
    except json.JSONDecodeError:
        pass
    
    # Fallback: try to infer action from response content
    response_lower = response_text.lower()
    
    # Detect YouTube intent
    if any(word in response_lower for word in ["youtube", "watch", "video", "let's watch", "let me watch"]):
        # Extract search query from prompt
        query = re.sub(r"^(let's|let me)?\s*(watch|find|search for)", "", prompt, flags=re.IGNORECASE).strip()
        return {
            "action": "watch_youtube",
            "params": {"query": query or prompt},
            "answer": f"Opening YouTube for {query or prompt}"
        }
    
    # Detect web search intent
    if any(word in response_lower for word in ["search", "google", "find", "look up", "web"]):
        query = re.sub(r"^(search|find|look up)", "", prompt, flags=re.IGNORECASE).strip()
        return {
            "action": "web_search",
            "params": {"query": query or prompt},
            "answer": f"Searching for {query or prompt}"
        }
    
    # Default: respond
    return {
        "action": "respond",
        "params": {},
        "answer": response_text[:200]  # Return first 200 chars as answer
    }


def _call_groq(prompt: str) -> str:
    """
    Call Groq API.
    
    Args:
        prompt: User prompt
        
    Returns:
        AI response text
        
    Raises:
        Exception: On API error
    """
    if not config.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not configured")
    
    client = GroqClient(api_key=config.GROQ_API_KEY)
    
    message = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    return message.choices[0].message.content



def _call_openrouter(prompt: str) -> str:
    """
    Call OpenRouter API via OpenAI client.
    
    Args:
        prompt: User prompt
        
    Returns:
        AI response text
        
    Raises:
        Exception: On API error
    """
    if not config.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not configured")
    
    client = OpenAI(
        api_key=config.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        default_headers={"HTTP-Referer": "jarvis-assistant"}
    )
    
    message = client.chat.completions.create(
        model=config.OPENROUTER_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    return message.choices[0].message.content
