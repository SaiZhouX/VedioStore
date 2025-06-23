import tkinter as tk
from tkinter import ttk, messagebox
import os
import json

# 电影数据存储文件
MOVIES_FILE = os.path.abspath("movies.json")  # 使用绝对路径


class AddMovieWindow:
    def __init__(self, parent, frame, add_movie_callback):
        self.parent = parent
        self.add_movie_callback = add_movie_callback
        self.current_level = 0  # 初始化评分为0

        self.window = frame
        # self.window.configure(bg="#1E1E1E")

        # 加载星星图片
        self.load_star_images()

        self.create_ui()

    def load_star_images(self):
        """加载星星图片，如果加载失败则使用文本替代"""
        try:
            STAR_EMPTY_PATH = os.path.join("posters", "star_empty.png")
            STAR_FILLED_PATH = os.path.join("posters", "star_filled.png")

            if os.path.exists(STAR_EMPTY_PATH) and os.path.exists(STAR_FILLED_PATH):
                from PIL import Image, ImageTk
                self.STAR_EMPTY = ImageTk.PhotoImage(Image.open(STAR_EMPTY_PATH).resize((20, 20)))
                self.STAR_FILLED = ImageTk.PhotoImage(Image.open(STAR_FILLED_PATH).resize((20, 20)))
                self.use_image_stars = True
            else:
                self.use_image_stars = False
        except Exception as e:
            print(f"加载星星图片失败: {e}")
            self.use_image_stars = False

    def create_ui(self):
        # 创建主框架，使用pack布局
        main_frame = ttk.Frame(self.window, style="PosterFrame.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 标题输入框
        title_label = ttk.Label(main_frame, text="标题：", style="DetailText.TLabel")
        title_label.pack(pady=(0, 5), anchor=tk.W)
        self.title_entry = ttk.Entry(main_frame, width=30)
        self.title_entry.pack(pady=(0, 10), anchor=tk.W)

        # 主演输入框
        stars_label = ttk.Label(main_frame, text="主演：", style="DetailText.TLabel")
        stars_label.pack(pady=(0, 5), anchor=tk.W)
        self.stars_entry = ttk.Entry(main_frame, width=30)
        self.stars_entry.pack(pady=(0, 10), anchor=tk.W)

        # 下载链接输入框
        download_label = ttk.Label(main_frame, text="下载链接：", style="DetailText.TLabel")
        download_label.pack(pady=(0, 5), anchor=tk.W)
        self.download_entry = ttk.Entry(main_frame, width=30)
        self.download_entry.pack(pady=(0, 10), anchor=tk.W)

        # 观看链接输入框
        watch_label = ttk.Label(main_frame, text="观看链接：", style="DetailText.TLabel")
        watch_label.pack(pady=(0, 5), anchor=tk.W)
        self.watch_entry = ttk.Entry(main_frame, width=30)
        self.watch_entry.pack(pady=(0, 10), anchor=tk.W)

        # 剧情简介输入框
        synopsis_label = ttk.Label(main_frame, text="剧情简介：", style="DetailText.TLabel")
        synopsis_label.pack(pady=(0, 5), anchor=tk.W)
        self.synopsis_entry = tk.Text(main_frame, width=30, height=5)
        self.synopsis_entry.pack(pady=(0, 10), anchor=tk.W)

        # 评分星级
        rating_frame = ttk.Frame(main_frame, style="PosterFrame.TFrame")
        rating_frame.pack(pady=(0, 10), anchor=tk.W)

        rating_label = ttk.Label(rating_frame, text="评分：", style="DetailText.TLabel")
        rating_label.pack(side=tk.LEFT)

        self.rating_widgets = []

        for i in range(5):
            if self.use_image_stars:
                # 使用图片星星
                star_label = ttk.Label(rating_frame, image=self.STAR_EMPTY)
                star_label.image = self.STAR_EMPTY
            else:
                # 使用文本星星
                star_label = ttk.Label(rating_frame, text="☆", foreground="#AAAAAA", font=("Helvetica", 14))

            star_label.pack(side=tk.LEFT, padx=2)
            star_label.bind("<Button-1>", lambda event, idx=i: self.update_level(idx + 1))
            self.rating_widgets.append(star_label)

        # 添加按钮
        add_btn = ttk.Button(main_frame, text="添加", command=self.add_movie)
        add_btn.pack(pady=(10, 0))

    def update_level(self, new_level):
        # 更新星星显示
        for i, star in enumerate(self.rating_widgets):
            if self.use_image_stars:
                star.config(image=self.STAR_FILLED if i < new_level else self.STAR_EMPTY)
                star.image = self.STAR_FILLED if i < new_level else self.STAR_EMPTY
            else:
                star.config(text="★" if i < new_level else "☆")

        self.current_level = new_level  # 更新评分值

    def add_movie(self):
        title = self.title_entry.get()
        stars = self.stars_entry.get()
        download_link = self.download_entry.get()
        watch_link = self.watch_entry.get()
        synopsis = self.synopsis_entry.get("1.0", tk.END).strip()
        level = str(self.current_level)  # 获取当前评分

        if not title:
            messagebox.showerror("错误", "标题不能为空")
            return

        # 自动生成海报路径，使用单斜杠
        poster_path = f"posters/{title}.jpg"

        new_movie = {
            "title": title,
            "poster_path": poster_path,
            "stars": stars,
            "director": "",
            "type": "",
            "region": "",
            "level": level,  # 保存评分
            "download_link": download_link,
            "watch_link": watch_link,
            "synopsis": synopsis
        }

        self.add_movie_callback(new_movie)
        # 关闭当前标签页
        index = self.parent.notebook.index(self.window)
        self.parent.notebook.forget(index)