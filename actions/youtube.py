"""
YouTube video search action - opens YouTube with search query.
Plays the top result directly instead of showing search results.
"""

import webbrowser
import subprocess
import json


def watch_youtube(query: str) -> bool:
    """
    Search YouTube and open the top video result.
    
    Args:
        query: Video search query (e.g., "lebron highlights")
    
    Returns:
        bool: True if opened successfully
    """
    try:
        video_id = _get_top_video(query)
        if not video_id:
            # Fallback to search results if we can't find a video
            import urllib.parse
            search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            webbrowser.open(search_url)
            print(f"✓ YouTube: Opening search for '{query}'")
            return True
        
        # Open the top video directly
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        webbrowser.open(video_url)
        print(f"✓ YouTube: Playing top result for '{query}'")
        return True
    except Exception as e:
        print(f"✗ YouTube error: {e}")
        return False


def _get_top_video(query: str) -> str:
    """
    Get the video ID of the top YouTube search result using yt-dlp.
    
    Args:
        query: Search query
        
    Returns:
        Video ID string, or empty string if not found
    """
    try:
        # Use yt-dlp to search YouTube (no API key required)
<<<<<<< HEAD
<<<<<<< HEAD
        # --dump-single-json returns one JSON object containing 'entries'
        cmd = [
            "yt-dlp",
            "--dump-single-json",
            "--no-warnings",
            f"ytsearch1:{query}"
        ]

=======
=======
        # --dump-single-json returns one JSON object containing 'entries'
>>>>>>> bf68d16 (Youtube search works)
        cmd = [
            "yt-dlp",
            "--dump-single-json",
            "--no-warnings",
            f"ytsearch1:{query}"
        ]
<<<<<<< HEAD
        
>>>>>>> 4245f98 (Jarvis up & running)
=======

>>>>>>> bf68d16 (Youtube search works)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
<<<<<<< HEAD
<<<<<<< HEAD
            timeout=10
        )

        if result.returncode != 0 or not result.stdout:
            # try fallback: parse first JSON object per line
            out = result.stdout or ""
            for line in out.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        if "id" in obj:
                            return obj.get("id", "")
                        if "entries" in obj and obj.get("entries"):
                            return obj["entries"][0].get("id", "")
                except Exception:
                    continue
            return ""

        # Parse single JSON output
        data = json.loads(result.stdout)
        entries = data.get("entries") or []
        if entries:
            # entries may be list of dicts or list of video entries
            first = entries[0]
            if isinstance(first, dict) and "id" in first:
                return first.get("id", "")
        
        # As a last resort, if the JSON itself is a single video object
        if isinstance(data, dict) and "id" in data:
            return data.get("id", "")

=======
            timeout=5
=======
            timeout=10
>>>>>>> bf68d16 (Youtube search works)
        )

        if result.returncode != 0 or not result.stdout:
            # try fallback: parse first JSON object per line
            out = result.stdout or ""
            for line in out.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        if "id" in obj:
                            return obj.get("id", "")
                        if "entries" in obj and obj.get("entries"):
                            return obj["entries"][0].get("id", "")
                except Exception:
                    continue
            return ""

        # Parse single JSON output
        data = json.loads(result.stdout)
        entries = data.get("entries") or []
        if entries:
            # entries may be list of dicts or list of video entries
            first = entries[0]
            if isinstance(first, dict) and "id" in first:
                return first.get("id", "")
        
<<<<<<< HEAD
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            entries = data.get("entries", [])
            if entries:
                return entries[0].get("id", "")
        
>>>>>>> 4245f98 (Jarvis up & running)
=======
        # As a last resort, if the JSON itself is a single video object
        if isinstance(data, dict) and "id" in data:
            return data.get("id", "")

>>>>>>> bf68d16 (Youtube search works)
        return ""
    except Exception:
        return ""
