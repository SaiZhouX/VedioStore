import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os


class MovieDetailWindow:
    def __init__(self, parent, movie, update_level_callback, save_data_callback):
        self.parent = parent
        self.movie = movie
        self.update_level_callback = update_level_callback
        self.save_data_callback = save_data_callback

        self.window = tk.Toplevel(parent.root)
        self.window.title(movie["title"])
        # 增加窗口高度，确保内容能完整显示
        self.window.geometry("800x800")
        self.window.configure(bg="#1E1E1E")

        # 创建主框架，用于控制整体布局
        main_frame = ttk.Frame(self.window, style="InfoFrame.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.create_ui(main_frame)

    def create_ui(self, parent_frame):
        # 海报
        poster_path = self.movie["poster_path"]
        if not poster_path or not os.path.exists(poster_path):
            poster_path = "posters/default.png"

        # 打开海报图片
        img = Image.open(poster_path)

        # 计算调整后的高度，保持宽高比
        width = 800
        aspect_ratio = img.height / img.width
        height = int(width * aspect_ratio)

        # 调整海报尺寸
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)

        # 使用grid布局，确保与其他元素左对齐
        poster_label = ttk.Label(parent_frame, image=photo)
        poster_label.image = photo
        poster_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 20))

        # 按钮框架，放到海报和文字中间，与海报左对齐
        btn_frame = ttk.Frame(parent_frame, style="BtnFrame.TFrame")
        btn_frame.grid(row=1, column=0, sticky=tk.W, pady=(0, 20))

        ttk.Button(btn_frame, text="播放", command=self.play_movie).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="修改信息", command=self.show_edit_movie_window).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="删除", command=self.delete_movie).pack(side=tk.LEFT)

        # 信息框架，与海报左对齐
        info_frame = ttk.Frame(parent_frame, style="InfoFrame.TFrame")
        info_frame.grid(row=2, column=0, sticky=tk.W)

        # 标题和评分，左对齐
        title_label = ttk.Label(info_frame, text=f"{self.movie['title']}",
                                style="DetailTitle.TLabel", font=("Helvetica", 18, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 10))

        # 电影信息，左对齐
        fields = ["stars", "download_link", "watch_link"]
        labels = ["主演", "下载链接", "观看链接"]

        for field, label_text in zip(fields, labels):
            text = self.movie.get(field, "")
            label = ttk.Label(info_frame, text=f"{label_text}：{text}", style="DetailText.TLabel")
            label.pack(anchor=tk.W, pady=5)

        # 评分星级，左对齐
        rating_frame = ttk.Frame(info_frame, style="PosterFrame.TFrame")
        rating_frame.pack(anchor=tk.W, pady=20)

        rating_label = ttk.Label(rating_frame, text="评分：", style="DetailText.TLabel")
        rating_label.pack(side=tk.LEFT)

        current_level = int(float(self.movie["level"])) if self.movie["level"] else 0
        self.rating_widgets = []

        for i in range(5):
            star_label = ttk.Label(rating_frame,
                                   image=self.parent.STAR_FILLED if i < current_level else self.parent.STAR_EMPTY)
            star_label.image = self.parent.STAR_FILLED if i < current_level else self.parent.STAR_EMPTY
            star_label.pack(side=tk.LEFT, padx=2)
            star_label.bind("<Button-1>", lambda event, idx=i: self.update_level(idx + 1))
            self.rating_widgets.append(star_label)

        # 剧情简介，左对齐
        synopsis = self.movie.get("synopsis", "")
        synopsis_label = ttk.Label(info_frame, text=f"剧情简介：{synopsis}", style="DetailText.TLabel", wraplength=700)
        synopsis_label.pack(anchor=tk.W, pady=20)

    def update_level(self, new_level):
        # 更新详细页面星星显示
        for i, star in enumerate(self.rating_widgets):
            star.config(image=self.parent.STAR_FILLED if i < new_level else self.parent.STAR_EMPTY)
            star.image = self.parent.STAR_FILLED if i < new_level else self.parent.STAR_EMPTY

        # 调用主窗口的评分更新方法
        self.update_level_callback(self.movie, new_level)

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
        from movie_edit import EditMovieWindow
        EditMovieWindow(self.window, self.movie, self.update_movie)

    def update_movie(self, updated_movie):
        index = next((i for i, m in enumerate(self.parent.movies_data) if m["title"] == self.movie["title"]), None)
        if index is not None:
            self.parent.movies_data[index] = updated_movie
            self.parent.load_posters(self.parent.movies_data)
            self.save_data_callback()
            messagebox.showinfo("提示", "影片信息更新成功")
            self.window.destroy()