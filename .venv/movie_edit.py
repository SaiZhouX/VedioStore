import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import datetime


class EditMovieWindow:
    def __init__(self, parent, frame, movie, update_movie_callback):
        self.parent = parent
        self.movie = movie
        self.update_movie_callback = update_movie_callback
        self.current_level = int(float(movie["level"])) if movie["level"] else 0  # 初始化评分

        self.window = frame
        # self.window.configure(bg="#1E1E1E")

        # 加载星星图片
        STAR_EMPTY_PATH = os.path.join("posters", "star_empty.png")
        STAR_FILLED_PATH = os.path.join("posters", "star_filled.png")

        if os.path.exists(STAR_EMPTY_PATH) and os.path.exists(STAR_FILLED_PATH):
            self.STAR_EMPTY = ImageTk.PhotoImage(Image.open(STAR_EMPTY_PATH).resize((20, 20)))
            self.STAR_FILLED = ImageTk.PhotoImage(Image.open(STAR_FILLED_PATH).resize((20, 20)))
        else:
            messagebox.showerror("错误", "星星图片文件不存在，请检查路径。")

        self.create_ui()

    def create_ui(self):
        # 标题输入框
        title_label = ttk.Label(self.window, text="标题：", style="DetailText.TLabel")
        title_label.pack(pady=10, anchor=tk.W, padx=20)
        self.title_entry = ttk.Entry(self.window, width=30)
        self.title_entry.insert(0, self.movie["title"])
        self.title_entry.pack(pady=5, anchor=tk.W, padx=20)

        # 主演输入框
        stars_label = ttk.Label(self.window, text="主演：", style="DetailText.TLabel")
        stars_label.pack(pady=10, anchor=tk.W, padx=20)
        self.stars_entry = ttk.Entry(self.window, width=30)
        self.stars_entry.insert(0, self.movie["stars"])
        self.stars_entry.pack(pady=5, anchor=tk.W, padx=20)

        # 海报路径输入框
        poster_label = ttk.Label(self.window, text="海报路径：", style="DetailText.TLabel")
        poster_label.pack(pady=10, anchor=tk.W, padx=20)
        self.poster_entry = ttk.Entry(self.window, width=30)
        self.poster_entry.insert(0, self.movie["poster_path"])
        self.poster_entry.pack(pady=5, anchor=tk.W, padx=20)

        # 下载链接输入框
        download_label = ttk.Label(self.window, text="下载链接：", style="DetailText.TLabel")
        download_label.pack(pady=10, anchor=tk.W, padx=20)
        self.download_entry = ttk.Entry(self.window, width=30)
        self.download_entry.insert(0, self.movie["download_link"])
        self.download_entry.pack(pady=5, anchor=tk.W, padx=20)

        # 观看链接输入框
        watch_label = ttk.Label(self.window, text="观看链接：", style="DetailText.TLabel")
        watch_label.pack(pady=10, anchor=tk.W, padx=20)
        self.watch_entry = ttk.Entry(self.window, width=30)
        self.watch_entry.insert(0, self.movie["watch_link"])
        self.watch_entry.pack(pady=5, anchor=tk.W, padx=20)

        # 剧情简介输入框
        synopsis_label = ttk.Label(self.window, text="剧情简介：", style="DetailText.TLabel")
        synopsis_label.pack(pady=10, anchor=tk.W, padx=20)
        self.synopsis_entry = tk.Text(self.window, width=30, height=5)
        self.synopsis_entry.insert("1.0", self.movie.get("synopsis", ""))
        self.synopsis_entry.pack(pady=5, anchor=tk.W, padx=20)

        # 评分星级（初始显示当前评分）
        rating_frame = ttk.Frame(self.window, style="PosterFrame.TFrame")
        rating_frame.pack(pady=20, anchor=tk.W, padx=20)

        rating_label = ttk.Label(rating_frame, text="评分：", style="DetailText.TLabel")
        rating_label.pack(side=tk.LEFT)

        self.rating_widgets = []
        current_level = self.current_level  # 使用初始化的值

        for i in range(5):
            star_label = ttk.Label(rating_frame,
                                   image=self.STAR_FILLED if i < current_level else self.STAR_EMPTY)
            star_label.image = self.STAR_FILLED if i < current_level else self.STAR_EMPTY
            star_label.pack(side=tk.LEFT, padx=2)
            star_label.bind("<Button-1>", lambda event, idx=i: self.update_level(idx + 1))
            self.rating_widgets.append(star_label)

        # 修改按钮
        edit_btn = ttk.Button(self.window, text="修改", command=self.edit_movie)
        edit_btn.pack(pady=20)

    def update_level(self, new_level):
        # 更新星星显示
        for i, star in enumerate(self.rating_widgets):
            star.config(image=self.STAR_FILLED if i < new_level else self.STAR_EMPTY)
            star.image = self.STAR_FILLED if i < new_level else self.STAR_EMPTY
        self.current_level = new_level  # 更新评分值

    def edit_movie(self):
        title = self.title_entry.get()
        stars = self.stars_entry.get()
        poster_path = self.poster_entry.get()
        download_link = self.download_entry.get()
        watch_link = self.watch_entry.get()
        level = str(self.current_level)  # 使用已初始化的评分值
        synopsis = self.synopsis_entry.get("1.0", tk.END).strip()

        if not title:
            messagebox.showerror("错误", "标题不能为空")
            return

        updated_movie = {
            "title": title,
            "poster_path": poster_path,
            "stars": stars,
            "director": self.movie["director"],
            "type": self.movie["type"],
            "region": self.movie["region"],
            "level": level,
            "download_link": download_link,
            "watch_link": watch_link,
            "synopsis": synopsis  # 添加剧情简介
        }

        self.update_movie_callback(updated_movie)
        # 关闭当前标签页
        index = self.parent.notebook.index(self.window)
        self.parent.notebook.forget(index)