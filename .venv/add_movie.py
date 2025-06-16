import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import datetime

class AddMovieWindow:
    def __init__(self, parent, add_movie_callback):
        self.parent = parent
        self.add_movie_callback = add_movie_callback

        self.window = tk.Toplevel(parent)
        self.window.title("添加影片")
        self.window.geometry("400x400")
        self.window.configure(bg="#1E1E1E")

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

        # 评分星级（初始5颗空星星）
        rating_frame = ttk.Frame(self.window, style="PosterFrame.TFrame")
        rating_frame.pack(pady=20, anchor=tk.W, padx=20)

        rating_label = ttk.Label(rating_frame, text="评分：", style="DetailText.TLabel")
        rating_label.pack(side=tk.LEFT)

        self.rating_widgets = []
        self.current_rating = 0

        for i in range(5):
            star_label = ttk.Label(rating_frame, image=self.STAR_EMPTY)
            star_label.image = self.STAR_EMPTY
            star_label.pack(side=tk.LEFT, padx=2)
            star_label.bind("<Button-1>", lambda event, idx=i: self.update_rating(idx + 1))
            self.rating_widgets.append(star_label)

        # 添加按钮
        add_btn = ttk.Button(self.window, text="添加", command=self.add_movie)
        add_btn.pack(pady=20)

    def update_rating(self, new_rating):
        # 更新星星显示
        for i, star in enumerate(self.rating_widgets):
            star.config(image=self.STAR_FILLED if i < new_rating else self.STAR_EMPTY)
            star.image = self.STAR_FILLED if i < new_rating else self.STAR_EMPTY
        self.current_rating = new_rating

    def add_movie(self):
        title = self.title_entry.get()
        stars = self.stars_entry.get()
        poster_path = self.poster_entry.get()
        download_link = self.download_entry.get()
        watch_link = self.watch_entry.get()
        rating = str(self.current_rating)
        update_date = datetime.datetime.now().strftime("%Y-%m-%d")

        if not title:
            messagebox.showerror("错误", "标题不能为空")
            return

        new_movie = {
            "title": title,
            "poster_path": poster_path,
            "stars": stars,
            "director": "",
            "type": "",
            "release_year": "",
            "region": "",
            "update_date": update_date,
            "rating": rating,
            "download_link": download_link,
            "watch_link": watch_link
        }

        self.add_movie_callback(new_movie)
        self.window.destroy()