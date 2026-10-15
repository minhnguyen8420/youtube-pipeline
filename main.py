import logging
import pandas as pd

from utils.logger import setup_logging
from utils.io import load_json, export_dataframe_to_csv
from etl.extract import get_video_details, get_youtube_client, get_playlist_id, get_playlist_items, get_video_comments
from etl.load import load_dataframe_to_bigquery
from etl.transform import cast_columns_to_string, cast_columns_to_int

logger = logging.getLogger(__name__)

def main():
    """
    Main function to run the ETL process.
    """
    video_frames = []
    comment_frames = []
    video_table = "focal-grin-255308.YOUTUBE_DATA.video_details"
    comment_table = "focal-grin-255308.YOUTUBE_DATA.video_comments"
    setup_logging("INFO")
    logger.info("Starting the ETL process...")
    logger.info("Setting up YouTube API client...")
    youtube = get_youtube_client()
    logger.info("YouTube API client setup complete.")
    logger.info("Starting video details extraction...")
    channel_list = load_json("channels.json")
    if not channel_list:
        logger.warning("No channels found in channels.json. Nothing to extract.")
        return
    for channel in channel_list:
        channel_name = channel["channel_name"]
        channel_id = channel["channel_id"]
        playlist_list = get_playlist_id(youtube, channel_name, channel_id)
        if not playlist_list:
            logger.warning(f"No playlists found for channel '{channel_name}'. Skipping.")
            continue
        for playlist in playlist_list:
            playlist_name = playlist["playlist_name"]
            playlist_id = playlist["playlist_id"]
            video_ids = get_playlist_items(youtube, playlist_id)
            if not video_ids:
                logger.warning(f"No videos found in playlist '{playlist_name}' of channel '{channel_name}'. Skipping.")
                continue
            video_details = get_video_details(youtube, video_ids)
            df_playlist = pd.DataFrame(video_details)
            df_playlist["channel_name"] = channel_name
            df_playlist["playlist_name"] = playlist_name
            df_playlist["extraction_date"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            video_frames.append(df_playlist)
    if not video_frames:
        logger.warning("No video details extracted. Skipping CSV export.")
        return
    df_video_details = pd.concat(video_frames, ignore_index=True)
    video_string_columns = ["video_id", "title", "published_at", "channel_name", "playlist_name", "extraction_date"]
    df_video_details = cast_columns_to_string(df_video_details, video_string_columns)
    video_int_columns = ["view_count", "like_count", "comment_count"]   
    df_video_details = cast_columns_to_int(df_video_details, video_int_columns)
    logger.info("ETL process completed. Saving to BigQuery...")
    load_dataframe_to_bigquery(df_video_details, video_table)
    logger.info("End video details extraction.")
    logger.info("Starting video comments extraction...")
    video_list = df_video_details["video_id"].tolist()
    if not video_list:
        logger.warning("No video IDs found in the extracted data. Skipping individual video details extraction.")
        return
    else:
        for video in video_list:
            comments = get_video_comments(youtube, video)
            if comments:
                df_comments = pd.DataFrame(comments)
                df_comments["extraction_date"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                comment_frames.append(df_comments)
    if not comment_frames:
        logger.warning("No comments extracted. Skipping CSV export.")
        return
    df_video_comments = pd.concat(comment_frames, ignore_index=True)
    
    logger.info("Video comments extraction completed. Saving to BigQuery...")
    load_dataframe_to_bigquery(df_video_comments, comment_table)
    logger.info("End video comments extraction.")
    logger.info("ETL process completed successfully.")

if __name__ == "__main__":
    main()