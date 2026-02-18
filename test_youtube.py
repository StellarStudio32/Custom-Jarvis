#!/usr/bin/env python3
"""Test YouTube module directly."""

from actions import youtube

print("Testing: watch_youtube('lebron highlights')\n")
result = youtube.watch_youtube('lebron highlights')
print(f"\n✓ Test result: {result}")
