#!/usr/bin/env python3
"""Quick test of AI response handling."""

import ai_handler
import config

print(f"Testing with {config.AI_BACKEND} backend...\n")

# Test YouTube command
prompt = "let's watch lebron highlights"
print(f"Testing prompt: '{prompt}'")
result = ai_handler.ask_ai(prompt)
print(f"Result: {result}\n")

# Test web search command
prompt2 = "search for python tutorials"
print(f"Testing prompt: '{prompt2}'")
result2 = ai_handler.ask_ai(prompt2)
print(f"Result: {result2}\n")

# Test generic command
prompt3 = "what time is it"
print(f"Testing prompt: '{prompt3}'")
result3 = ai_handler.ask_ai(prompt3)
print(f"Result: {result3}\n")
