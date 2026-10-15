"""Module for extracting data from YouTube API."""

import logging
from utils.logger import setup_logging

import os
from dotenv import load_dotenv

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

def get_youtube_client():
    """
    Returns a YouTube API client using the API key from environment variables.
    """

    try:
        load_dotenv()
        YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
        logger.info("Creating YouTube API client...")
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        logger.info("YouTube API client created successfully.")
        return youtube
    except HttpError as e:
        logger.error(f"An HTTP error occurred: {e}")
        return None
    except Exception as e:
        logger.error(f"An error occurred while creating YouTube API client: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None

def get_playlist_id(youtube, channel_name, channel_id):
    """
    Fetches all playlist IDs for a given channel, following pagination.

    Args:
        youtube: YouTube API client.
        channel_name (str): The name of the YouTube channel.
        channel_id (str): The ID of the YouTube channel.
    """
    try:
        playlist = []
        logger.info(f"Fetching playlists for channel: {channel_name}")
        request = youtube.playlists().list(
            part="snippet,contentDetails",
            channelId=channel_id,
            maxResults=50  # API maximum per page
        )
        while request is not None:
            response = request.execute()
            for item in response["items"]:
                playlist.append({
                    "playlist_id": item["id"],
                    "playlist_name": item["snippet"]["title"]
                })
            request = youtube.playlists().list_next(request, response)
        logger.info("Playlists fetched successfully.")
        logger.info(f"Total playlists fetched for channel {channel_name}: {len(playlist)}")
        return playlist
    except HttpError as e:
        logger.error(f"An HTTP error occurred: {e}")
        return None
    except Exception as e:
        logger.error(f"An error occurred while fetching playlists: {e}")
        return None

def get_playlist_items(youtube, playlist_id):
    """
    Fetches all video IDs from a given playlist, following pagination.

    Args:
        youtube: YouTube API client.
        playlist_id (str): The ID of the YouTube playlist.
    """
    try:
        playlist_item_ids = []
        logger.info(f"Fetching items for playlist ID: {playlist_id}")
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50  # API maximum per page
        )
        while request is not None:
            response = request.execute()
            for item in response["items"]:
                playlist_item_ids.append(item["contentDetails"]["videoId"])
            request = youtube.playlistItems().list_next(request, response)
        logger.info("Playlist items fetched successfully.")
        logger.info(f"Total items fetched for playlist {playlist_id}: {len(playlist_item_ids)}")
        return playlist_item_ids
    except HttpError as e:
        logger.error(f"An HTTP error occurred: {e}")
        return None
    except Exception as e:
        logger.error(f"An error occurred while fetching playlist items: {e}")
        return None

def get_video_details(youtube, video_ids):
    """
    Fetches details for given video IDs.

    Args:
        youtube: YouTube API client.
        video_ids (list): List of YouTube video IDs.
    """
    try:
        video_details = []
        logger.info(f"Fetching details for {len(video_ids)} videos")
        # API accepts at most 50 IDs per request
        for i in range(0, len(video_ids), 50):
            request = youtube.videos().list(
                part="snippet,statistics",
                id=",".join(video_ids[i:i + 50])
            )
            response = request.execute()
            for video in response["items"]:
                video_details.append({
                    "video_id": video["id"],
                    "title": video["snippet"]["title"],
                    "published_at": video["snippet"]["publishedAt"],
                    "view_count": video["statistics"].get("viewCount", 0),
                    "like_count": video["statistics"].get("likeCount", 0),
                    "comment_count": video["statistics"].get("commentCount", 0),
                })
        logger.info("Video details fetched successfully.")
        return video_details
    except HttpError as e:
        logger.error(f"An HTTP error occurred: {e}")
        return None
    except Exception as e:
        logger.error(f"An error occurred while fetching video details: {e}")
        return None

def get_video_comments(youtube, video_id, max_comments: int | None = None):
    """
    Fetches top-level comments for a given video ID, following pagination
    until all comments are retrieved.

    Args:
        youtube: YouTube API client.
        video_id (str): The ID of the YouTube video.
        max_comments (int | None): Optional cap on the number of comments to fetch.
            Default is None (fetch all).
    """
    try:
        comments = []
        logger.info(f"Fetching comments for video ID: {video_id}")
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100  # API maximum per page
        )
        while request is not None:
            response = request.execute()
            for item in response["items"]:
                comment = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "comment_id": item["id"],
                    "video_id": video_id,
                    "author": comment["authorDisplayName"],
                    "text_display": comment["textDisplay"],
                    "text_original": comment["textOriginal"],
                    "published_at": comment["publishedAt"],
                    "updated_at": comment["updatedAt"],
                    "like_count": comment.get("likeCount", 0),
                })
            if max_comments is not None and len(comments) >= max_comments:
                comments = comments[:max_comments]
                break
            request = youtube.commentThreads().list_next(request, response)
        logger.info(f"Total comments fetched for video {video_id}: {len(comments)}")
        return comments
    except HttpError as e:
        logger.error(f"An HTTP error occurred: {e}")
        return None
    except Exception as e:
        logger.error(f"An error occurred while fetching comments: {e}")
        return None