import webbrowser
import tkinter as tk
from tkinter import messagebox
import requests
from io import BytesIO
from PIL import Image, ImageTk
from youtube_auth import authenticate_youtube  # Importing your authentication function
import aiohttp
import asyncio


def get_total_liked_videos(youtube):
    playlist_id = "LL"  # "LL" is the playlist ID for liked videos
    total_liked_videos = 0
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,  # Max allowed per request
            pageToken=next_page_token
        )
        response = request.execute()

        total_liked_videos += len(response.get("items", []))
        next_page_token = response.get("nextPageToken")

        # If there are no more pages, break the loop
        if not next_page_token:
            break

    return total_liked_videos



class YouTubeVideoManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Liked Videos Manager")
        self.root.geometry("800x600")
        self.root.configure(bg="#181818")



        # Initialize YouTube API
        self.youtube = authenticate_youtube()

        # Initialize liked videos and pagination variables
        self.liked_videos = []
        self.current_index = 0
        self.total_videos = 0
        self.next_page_token = None

        # GUI components
        self.video_title = tk.Label(root, text="", wraplength=400, bg="#181818", fg="#FFFFFF", font=("Helvetica", 14))
        self.video_title.pack(pady=20)

        self.thumbnail_label = tk.Label(root, bg="#181818")
        self.thumbnail_label.pack(pady=10)

        # Button creation with hover effect
        self.create_buttons(root)

        self.progress_label = tk.Label(root, text="", bg="#181818", fg="#FFFFFF", font=("Helvetica", 12))
        self.progress_label.pack(pady=10)

        # Fetch the first batch of videos
        self.load_next_batch()


    def create_buttons(self, root):
        button_color = "#3A3A3A"
        hover_color = "#C70000"  # Red color for hover effect

        # Keep Video Button
        self.keep_button = tk.Button(root, text="Keep Video", fg="#FFFFFF", bg=button_color, font=("Helvetica", 12), command=self.keep_video)
        self.keep_button.pack(side=tk.LEFT, padx=20)
        self.setup_button_hover_effect(self.keep_button, button_color, hover_color)

        # Remove Video Button
        self.remove_button = tk.Button(root, text="Remove Video", fg="#FFFFFF", bg=button_color, font=("Helvetica", 12), command=self.remove_video)
        self.remove_button.pack(side=tk.RIGHT, padx=20)
        self.setup_button_hover_effect(self.remove_button, button_color, hover_color)

        # Open Video Button
        self.open_video_button = tk.Button(root, text="Open Video", fg="#FFFFFF", bg=button_color, font=("Helvetica", 12), command=self.open_video)
        self.open_video_button.pack(pady=10)
        self.setup_button_hover_effect(self.open_video_button, button_color, hover_color)

    def setup_button_hover_effect(self, button, normal_color, hover_color):
        button.bind("<Enter>", lambda e: button.config(bg=hover_color))
        button.bind("<Leave>", lambda e: button.config(bg=normal_color))
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

    def show_loading(self):
        self.progress_label.config(text="Loading videos...")

    def hide_loading(self):
        self.progress_label.config(text="")


    def load_next_batch(self):
        # Fetch videos and update pagination
        self.show_loading()
        new_videos, self.next_page_token = self.fetch_liked_videos(self.next_page_token)
        if new_videos:
            self.liked_videos = new_videos
            self.total_videos = len(new_videos)
            self.current_index = 0  # Reset the index to start showing new videos
            self.show_video()  # Show the first video of the newly loaded batch
        else:
            self.video_title.config(text="No more liked videos found!")
            self.thumbnail_label.config(image="")
            self.keep_button.config(state=tk.DISABLED)
            self.remove_button.config(state=tk.DISABLED)

        self.hide_loading()

    def show_video(self):
        if self.current_index < self.total_videos:
            video = self.liked_videos[self.current_index]

            if isinstance(video, dict) and 'snippet' in video:
                video_title = video['snippet']['title']
                video_thumbnail_url = video['snippet']['thumbnails']['default']['url']

                self.video_title.config(text=video_title)

                img_data = requests.get(video_thumbnail_url).content
                img = Image.open(BytesIO(img_data))
                img = img.resize((336, 252), Image.LANCZOS)  # Resize to match the label size
                self.thumbnail = ImageTk.PhotoImage(img)
                self.thumbnail_label.config(image=self.thumbnail)

            else:
                print("Unexpected video structure or missing 'snippet'.")
        else:
            self.load_next_batch()  # Load next batch if the current index exceeds total videos

    def open_video(self):
        if self.current_index < self.total_videos:
            video_id = self.liked_videos[self.current_index]['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            webbrowser.open(video_url)

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
    # print(get_total_liked_videos(app.youtube))
    root.mainloop()
