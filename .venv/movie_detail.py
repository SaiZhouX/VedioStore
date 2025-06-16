import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os


class MovieDetailWindow:
    def __init__(self, parent, movie, update_rating_callback, save_data_callback):
        self.parent = parent
        self.movie = movie
        self.update_rating_callback = update_rating_callback
        self.save_data_callback = save_data_callback

        self.window = tk.Toplevel(parent.root)
        self.window.title(movie["title"])
        self.window.geometry("800x600")
        self.window.configure(bg="#1E1E1E")

        self.create_ui()

    def create_ui(self):
        # 海报
        poster_path = self.movie["poster_path"]
        if not poster_path or not os.path.exists(poster_path):
            poster_path = "posters/default.png"

        img = Image.open(poster_path).resize((200, 300), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        poster_label = ttk.Label(self.window, image=photo)
        poster_label.image = photo
        poster_label.pack(pady=20)

        # 信息框架
        info_frame = ttk.Frame(self.window, style="InfoFrame.TFrame")
        info_frame.pack(pady=20, fill=tk.X)

        # 标题和评分
        title_label = ttk.Label(info_frame, text=f"{self.movie['title']}  [{self.movie.get('rating', '')}分]",
                                style="DetailTitle.TLabel", font=("Helvetica", 18, "bold"))
        title_label.pack(pady=10, anchor=tk.CENTER)

        # 电影信息
        fields = ["stars", "update_date", "download_link", "watch_link"]
        labels = ["主演", "更新", "下载链接", "观看链接"]

        for field, label_text in zip(fields, labels):
            text = self.movie.get(field, "")
            label = ttk.Label(info_frame, text=f"{label_text}：{text}", style="DetailText.TLabel")
            label.pack(pady=5, anchor=tk.CENTER)

        # 新增评分星级（初始5颗空星星）
        rating_frame = ttk.Frame(info_frame, style="PosterFrame.TFrame")
        rating_frame.pack(pady=20, anchor=tk.CENTER)

        rating_label = ttk.Label(rating_frame, text="评分：", style="DetailText.TLabel")
        rating_label.pack(side=tk.LEFT)

        current_rating = int(float(self.movie["rating"])) if self.movie["rating"] else 0
        self.rating_widgets = []

        for i in range(5):
            star_label = ttk.Label(rating_frame,
                                   image=self.parent.STAR_FILLED if i < current_rating else self.parent.STAR_EMPTY)
            star_label.image = self.parent.STAR_FILLED if i < current_rating else self.parent.STAR_EMPTY
            star_label.pack(side=tk.LEFT, padx=2)
            star_label.bind("<Button-1>", lambda event, idx=i: self.update_rating(idx + 1))
            self.rating_widgets.append(star_label)

        # 按钮框架
        btn_frame = ttk.Frame(self.window, style="BtnFrame.TFrame")
        btn_frame.pack(pady=20, fill=tk.X)

        ttk.Button(btn_frame, text="播放", command=self.play_movie).pack(side=tk.LEFT, padx=10)
        # 新增修改按钮
        ttk.Button(btn_frame, text="修改信息", command=self.show_edit_movie_window).pack(side=tk.LEFT, padx=10)
        # 新增删除按钮
        ttk.Button(btn_frame, text="删除", command=self.delete_movie).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="HD英语中学", command=lambda: self.choose_subtitle("HD英语中学")).pack(side=tk.LEFT,
                                                                                                          padx=10)

    def update_rating(self, new_rating):
        # 更新详细页面星星显示
        for i, star in enumerate(self.rating_widgets):
            star.config(image=self.parent.STAR_FILLED if i < new_rating else self.parent.STAR_EMPTY)
            star.image = self.parent.STAR_FILLED if i < new_rating else self.parent.STAR_EMPTY

        # 调用主窗口的评分更新方法
        self.update_rating_callback(self.movie, new_rating)

    def play_movie(self):
        messagebox.showinfo("提示", f"即将播放 {self.movie['title']}")

    def follow_movie(self):
        messagebox.showinfo("提示", f"已关注 {self.movie['title']}")

    def choose_subtitle(self, subtitle):
        messagebox.showinfo("提示", f"已选择字幕：{subtitle}")

    def delete_movie(self):
        # 弹出二次确认窗口
        confirm = messagebox.askyesno("确认删除", f"确定要删除《{self.movie['title']}》吗？")
        if confirm:
            # 调用主窗口的删除方法
            self.parent.delete_movie(self.movie)
            self.window.destroy()

    def show_edit_movie_window(self):
        from edit_movie import EditMovieWindow
        EditMovieWindow(self.window, self.movie, self.update_movie)

    def update_movie(self, updated_movie):
        index = next((i for i, m in enumerate(self.parent.movies_data) if m["title"] == self.movie["title"]), None)
        if index is not None:
            self.parent.movies_data[index] = updated_movie
            self.parent.load_posters(self.parent.movies_data)
            self.save_data_callback()
            messagebox.showinfo("提示", "影片信息更新成功")
            self.window.destroy()
