import tkinter as tk
from tkinter import ttk, messagebox
import os
import json

# 电影数据存储文件
MOVIES_FILE = os.path.abspath("movies.json")  # 使用绝对路径

class AddMovieWindow:
    def __init__(self, parent, add_movie_callback):
        self.parent = parent
        self.add_movie_callback = add_movie_callback

        self.window = tk.Toplevel(parent)
        self.window.title("添加影片")
        self.window.geometry("400x500")
        self.window.configure(bg="#1E1E1E")

        self.create_ui()

    def create_ui(self):
        # 标题输入框
        title_label = ttk.Label(self.window, text="标题：", style="DetailText.TLabel")
        title_label.pack(pady=10, anchor=tk.W, padx=20)
        self.title_entry = ttk.Entry(self.window, width=30)
        self.title_entry.pack(pady=5, anchor=tk.W, padx=20)

        # 主演输入框
        stars_label = ttk.Label(self.window, text="主演：", style="DetailText.TLabel")
        stars_label.pack(pady=10, anchor=tk.W, padx=20)
        self.stars_entry = ttk.Entry(self.window, width=30)
        self.stars_entry.pack(pady=5, anchor=tk.W, padx=20)

        # 海报路径输入框
        poster_label = ttk.Label(self.window, text="海报路径：", style="DetailText.TLabel")
        poster_label.pack(pady=10, anchor=tk.W, padx=20)
        self.poster_entry = ttk.Entry(self.window, width=30)
        self.poster_entry.pack(pady=5, anchor=tk.W, padx=20)

        # 下载链接输入框
        download_label = ttk.Label(self.window, text="下载链接：", style="DetailText.TLabel")
        download_label.pack(pady=10, anchor=tk.W, padx=20)
        self.download_entry = ttk.Entry(self.window, width=30)
        self.download_entry.pack(pady=5, anchor=tk.W, padx=20)

        # 观看链接输入框
        watch_label = ttk.Label(self.window, text="观看链接：", style="DetailText.TLabel")
        watch_label.pack(pady=10, anchor=tk.W, padx=20)
        self.watch_entry = ttk.Entry(self.window, width=30)
        self.watch_entry.pack(pady=5, anchor=tk.W, padx=20)

        # 剧情简介输入框
        synopsis_label = ttk.Label(self.window, text="剧情简介：", style="DetailText.TLabel")
        synopsis_label.pack(pady=10, anchor=tk.W, padx=20)
        self.synopsis_entry = tk.Text(self.window, width=30, height=5)
        self.synopsis_entry.pack(pady=5, anchor=tk.W, padx=20)

        # 添加按钮
        add_btn = ttk.Button(self.window, text="添加", command=self.add_movie)
        add_btn.pack(pady=20)

    def add_movie(self):
        title = self.title_entry.get()
        stars = self.stars_entry.get()
        poster_path = self.poster_entry.get()
        download_link = self.download_entry.get()
        watch_link = self.watch_entry.get()
        synopsis = self.synopsis_entry.get("1.0", tk.END).strip()

        if not title:
            messagebox.showerror("错误", "标题不能为空")
            return

        new_movie = {
            "title": title,
            "poster_path": poster_path,
            "stars": stars,
            "director": "",
            "type": "",
            "region": "",
            "level": "0",
            "download_link": download_link,
            "watch_link": watch_link,
            "synopsis": synopsis
        }

        self.add_movie_callback(new_movie)
        self.window.destroy()