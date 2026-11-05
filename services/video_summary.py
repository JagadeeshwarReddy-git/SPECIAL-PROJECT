
import ollama

from youtube_transcript_api import YouTubeTranscriptApi

MODEL = "llama3.2"


def fetch_video_transcript(video_id):
    """
    Retrieve available captions/transcript for a YouTube video.
    Returns transcript text, or None if unavailable.
    """

    if not video_id:
        return None

    try:
        api = YouTubeTranscriptApi()

        transcript = api.fetch(
            video_id,
            languages=["en", "en-US", "en-GB", "hi"],
        )

        snippets = getattr(transcript, "snippets", [])
        transcript_text = " ".join(
            snippet.text.strip()
            for snippet in snippets
            if getattr(snippet, "text", "").strip()
        )

        return transcript_text or None

    except Exception:
        # Captions may be disabled, unavailable, or inaccessible.
        return None


def generate_video_summary(
    title,
    description="",
    transcript=None,
):
    """
    Generate a video-focused explanation with Ollama.
    The model receives video metadata and, when available,
    the actual transcript. Comments are never used.
    """

    title = (title or "").strip()
    description = (description or "").strip()
    transcript = (transcript or "").strip()

    if not title and not description and not transcript:
        return {
            "summary": (
                "There is not enough video information to "
                "generate a reliable explanation."
            ),
            "source": "No video information available",
        }

    if transcript:
        # Limit prompt size for local model processing.
        transcript_for_prompt = transcript[:24000]

        prompt = f"""
You are a helpful video-content analyst.

Explain the actual content of this YouTube video using the
transcript supplied below. Do NOT analyze audience comments.
No comments have been provided.

VIDEO TITLE:
{title}

VIDEO DESCRIPTION:
{description[:5000]}

VIDEO TRANSCRIPT:
{transcript_for_prompt}

Write a useful, well-organized report with these sections:

## 1. What is this video about?
Explain the main subject in clear, simple language.

## 2. Detailed explanation
Explain the main ideas, concepts, events, or steps discussed.
Organize them logically so someone who has not watched the
video can understand its content.

## 3. Important topics and concepts
List the important topics covered and briefly explain each.

## 4. Useful information and key takeaways
Give practical lessons, facts, methods, or recommendations
actually supported by the transcript.

## 5. Who would benefit from this video?
Identify the likely audience based on the content.

## 6. Conclusion
Summarize the video's main message.

Rules:
- Base factual claims on the supplied transcript.
- Do not invent information, examples, statistics, or claims.
- Do not summarize comments or describe audience sentiment.
- If the transcript is incomplete or unclear, say so.
- If the title or description conflicts with the transcript,
  prioritize the transcript and mention the uncertainty.
- Write a meaningful explanation, not just a few generic bullets.
"""

        source = "Video transcript"

    else:
        # Never pretend metadata is a full transcript.
        prompt = f"""
You are a careful YouTube video information analyst.

A transcript was not available. Explain only what can reasonably
be inferred from the metadata below. Do not pretend that you
watched the video or know details that are not provided.

VIDEO TITLE:
{title}

VIDEO DESCRIPTION:
{description[:5000] or "No description available."}

Provide these sections:

## 1. What the video appears to be about?
Explain what the title and description indicate.

## 2. Information available
Summarize the actual information present in the description.

## 3. Potentially useful points
Mention only points supported by the available metadata.

## 4. Limitations
Clearly state that a transcript was unavailable and that the
full video content could not be verified.

Rules:
- Do not invent the video's content.
- Do not analyze audience comments.
- Do not claim that you watched the video.
"""

        source = "Video title and description only"

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You explain video content accurately. "
                        "Never invent facts or claim to have watched "
                        "a video when only metadata is available."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        summary = response["message"]["content"].strip()

        return {
            "summary": summary,
            "source": source,
        }

    except Exception as exc:
        error = str(exc).lower()

        if "connection" in error:
            message = (
                "Ollama is not running. Start Ollama and try again."
            )
        elif "not found" in error:
            message = (
                f"Model '{MODEL}' was not found. "
                f"Run: ollama pull {MODEL}"
            )
        else:
            message = f"Could not generate the video explanation: {exc}"

        return {
            "summary": message,
            "source": source,
        }
