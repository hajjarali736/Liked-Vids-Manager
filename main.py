import tkinter as tk
from tkinter import messagebox
import requests
from io import BytesIO
from PIL import Image, ImageTk
from youtube_auth import authenticate_youtube  # Importing your authentication function

class YouTubeVideoManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Liked Videos Manager")

        # Initialize YouTube API
        self.youtube = authenticate_youtube()

        # Initialize liked videos and pagination variables
        self.liked_videos = []
        self.current_index = 0
        self.total_videos = 0
        self.next_page_token = None

        # GUI components
        self.video_title = tk.Label(root, text="", wraplength=400)
        self.video_title.pack(pady=20)

        self.thumbnail_label = tk.Label(root)
        self.thumbnail_label.pack(pady=10)

        self.keep_button = tk.Button(root, text="Keep Video", command=self.keep_video)
        self.keep_button.pack(side=tk.LEFT, padx=20)

        self.remove_button = tk.Button(root, text="Remove Video", command=self.remove_video)
        self.remove_button.pack(side=tk.RIGHT, padx=20)

        self.progress_label = tk.Label(root, text="")
        self.progress_label.pack(pady=10)

        # Fetch the first batch of videos
        self.load_next_batch()

    def fetch_liked_videos(self, page_token=None):
        request = self.youtube.videos().list(
            part="snippet,contentDetails",
            myRating="like",
            maxResults=50,
            pageToken=page_token
        )
        response = request.execute()
        videos = response.get("items", [])
        next_page_token = response.get("nextPageToken")
        return videos, next_page_token

    def load_next_batch(self):
        # Fetch videos and update pagination
        new_videos, self.next_page_token = self.fetch_liked_videos(self.next_page_token)
        if new_videos:
            self.liked_videos.extend(new_videos)
            self.total_videos += len(new_videos)
            self.current_index = 0  # Reset the index to start showing new videos
            self.show_video()  # Show the first video of the newly loaded batch
        else:
            self.video_title.config(text="No more liked videos found!")
            self.thumbnail_label.config(image="")
            self.keep_button.config(state=tk.DISABLED)
            self.remove_button.config(state=tk.DISABLED)

    def show_video(self):
        if self.current_index < self.total_videos:
            video = self.liked_videos[self.current_index]

            # Debugging line to check the structure of 'video'
            print(f"Current video structure: {video}")

            # Check if the video is a dictionary and contains expected keys
            if isinstance(video, dict) and 'snippet' in video:
                video_title = video['snippet']['title']
                video_thumbnail_url = video['snippet']['thumbnails']['default']['url']

                self.video_title.config(text=video_title)

                img_data = requests.get(video_thumbnail_url).content
                img = Image.open(BytesIO(img_data))
                self.thumbnail = ImageTk.PhotoImage(img)
                self.thumbnail_label.config(image=self.thumbnail)

                self.progress_label.config(text=f"{self.current_index + 1} / {self.total_videos} videos")
            else:
                print("Unexpected video structure or missing 'snippet'.")
        else:
            self.load_next_batch()  # Load next batch if the current index exceeds total videos

    def keep_video(self):
        self.current_index += 1
        self.show_video()

    def remove_video(self):
        video_id = self.liked_videos[self.current_index]['id']
        self.youtube.videos().rate(id=video_id, rating="none").execute()
        self.current_index += 1
        self.show_video()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeVideoManager(root)
    root.mainloop()
