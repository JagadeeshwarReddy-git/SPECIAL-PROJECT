
import os
import re

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import YOUTUBE_API_KEY


# ==========================================================
# SETTINGS
# ==========================================================

MAX_COMMENTS = 10_000
PAGE_SIZE = 100


# ==========================================================
# YOUTUBE API
# ==========================================================

class YouTubeAPI:

    def __init__(self):

        self.api_key = (
            YOUTUBE_API_KEY
            or os.getenv("YOUTUBE_API_KEY")
        )

        if not self.api_key:
            raise RuntimeError(
                "YouTube API key is missing. "
                "Set YOUTUBE_API_KEY in your .env file."
            )

        self.youtube = build(
            "youtube",
            "v3",
            developerKey=self.api_key,
        )

    # ======================================================
    # EXTRACT VIDEO ID
    # ======================================================

    @staticmethod
    def extract_video_id(url):

        if not url:
            return None

        url = str(url).strip()

        patterns = [
            r"(?:youtube\.com/watch\?v=)"
            r"([A-Za-z0-9_-]{11})",

            r"(?:youtu\.be/)"
            r"([A-Za-z0-9_-]{11})",

            r"(?:youtube\.com/shorts/)"
            r"([A-Za-z0-9_-]{11})",

            r"(?:youtube\.com/embed/)"
            r"([A-Za-z0-9_-]{11})",

            r"(?:youtube\.com/live/)"
            r"([A-Za-z0-9_-]{11})",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)

            if match:
                return match.group(1)

        # Accept a raw YouTube video ID.
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
            return url

        return None

    # ======================================================
    # GET VIDEO DETAILS
    # ======================================================

    def get_video_details(self, url):

        video_id = self.extract_video_id(url)

        if not video_id:
            return None

        try:
            response = (
                self.youtube
                .videos()
                .list(
                    part="snippet,statistics,contentDetails",
                    id=video_id,
                )
                .execute()
            )

        except HttpError as e:
            raise RuntimeError(
                "YouTube API error while fetching video details:\n"
                f"{e}"
            ) from e

        items = response.get("items", [])

        if not items:
            return None

        item = items[0]

        snippet = item.get("snippet", {})
        statistics = item.get("statistics", {})
        content_details = item.get("contentDetails", {})

        thumbnails = snippet.get("thumbnails", {})

        thumbnail = (
            thumbnails.get("high", {}).get("url")
            or thumbnails.get("medium", {}).get("url")
            or thumbnails.get("default", {}).get("url")
        )

        # NEW: Description and additional video context.
        description = snippet.get("description", "")

        tags = snippet.get("tags", [])

        return {
            "video_id": video_id,

            "title": snippet.get(
                "title",
                "Unknown Title",
            ),

            "description": description,

            "channel": snippet.get(
                "channelTitle",
                "Unknown Channel",
            ),

            "published": snippet.get(
                "publishedAt",
                "Unknown",
            ),

            "category_id": snippet.get(
                "categoryId",
                "",
            ),

            "tags": tags,

            "duration": content_details.get(
                "duration",
                "",
            ),

            "views": int(
                statistics.get("viewCount", 0)
            ),

            "likes": int(
                statistics.get("likeCount", 0)
            ),

            "comments": int(
                statistics.get("commentCount", 0)
            ),

            "thumbnail": thumbnail,
        }

    # ======================================================
    # GET COMMENTS
    # ======================================================

    def get_comments(
        self,
        video_id,
        max_comments=MAX_COMMENTS,
    ):
        """
        Fetch up to 10,000 top-level YouTube comments.

        Automatically follows nextPageToken until the requested
        number of comments is reached or no more pages remain.
        """

        if not video_id:
            raise ValueError(
                "A YouTube video ID is required."
            )

        try:
            max_comments = int(max_comments)
        except (TypeError, ValueError):
            max_comments = MAX_COMMENTS

        max_comments = max(
            1,
            min(max_comments, MAX_COMMENTS),
        )

        comments = []
        next_page_token = None

        # ==================================================
        # PAGINATION LOOP
        # ==================================================

        while len(comments) < max_comments:

            remaining = max_comments - len(comments)

            request_size = min(
                PAGE_SIZE,
                remaining,
            )

            try:
                response = (
                    self.youtube
                    .commentThreads()
                    .list(
                        part="snippet",
                        videoId=video_id,
                        maxResults=request_size,
                        pageToken=next_page_token,
                        textFormat="plainText",
                        order="relevance",
                    )
                    .execute()
                )

            except HttpError as e:

                error_text = str(e)

                if (
                    "commentsDisabled" in error_text
                    or "disabled comments" in error_text.lower()
                ):
                    raise RuntimeError(
                        "Comments are disabled for this video."
                    ) from e

                raise RuntimeError(
                    "YouTube API error while fetching comments:\n"
                    f"{e}"
                ) from e

            items = response.get("items", [])

            if not items:
                break

            # ==============================================
            # PROCESS CURRENT PAGE
            # ==============================================

            for item in items:

                try:
                    snippet = (
                        item["snippet"]
                        ["topLevelComment"]
                        ["snippet"]
                    )

                    comment = {
                        "author": snippet.get(
                            "authorDisplayName",
                            "Unknown",
                        ),

                        "text": snippet.get(
                            "textDisplay",
                            "",
                        ),

                        "likes": int(
                            snippet.get("likeCount", 0)
                        ),

                        "published": snippet.get(
                            "publishedAt",
                            "",
                        ),
                    }

                    comments.append(comment)

                except (
                    KeyError,
                    TypeError,
                    ValueError,
                ):
                    continue

                if len(comments) >= max_comments:
                    break

            # ==============================================
            # NEXT PAGE
            # ==============================================

            next_page_token = response.get("nextPageToken")

            if not next_page_token:
                break

        return comments[:max_comments]
