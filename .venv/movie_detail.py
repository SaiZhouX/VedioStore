import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os


class MovieDetailWindow:
    def __init__(self, parent, frame, movie, update_level_callback, save_data_callback):
        self.parent = parent
        self.movie = movie
        self.update_level_callback = update_level_callback
        self.save_data_callback = save_data_callback

        self.window = frame
        # self.window.configure(bg="#1E1E1E")

        # 创建主框架
        main_frame = ttk.Frame(self.window, style="InfoFrame.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建Canvas来显示图片
        self.canvas = tk.Canvas(main_frame, width=800, height=538, bg="#1E1E1E", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW, pady=(0, 20))

        # 按钮框架
        btn_frame = ttk.Frame(main_frame, style="BtnFrame.TFrame")
        btn_frame.grid(row=1, column=0, sticky=tk.W, pady=(0, 20))

        ttk.Button(btn_frame, text="播放", command=self.play_movie).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="修改信息", command=self.show_edit_movie_window).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="删除", command=self.delete_movie).pack(side=tk.LEFT)

        # 信息框架
        info_frame = ttk.Frame(main_frame, style="InfoFrame.TFrame")
        info_frame.grid(row=2, column=0, sticky=tk.W)

        # 标题
        title_label = ttk.Label(info_frame, text=f"{self.movie['title']}",
                                style="DetailTitle.TLabel", font=("Helvetica", 18, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 10))

        # 电影信息
        fields = ["stars", "download_link", "watch_link"]
        labels = ["主演", "下载链接", "观看链接"]

        for field, label_text in zip(fields, labels):
            text = self.movie.get(field, "")
            label = ttk.Label(info_frame, text=f"{label_text}：{text}", style="DetailText.TLabel")
            label.pack(anchor=tk.W, pady=5)

        # 评分星级
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

        # 剧情简介
        synopsis = self.movie.get("synopsis", "")
        synopsis_label = ttk.Label(info_frame, text=f"剧情简介：{synopsis}", style="DetailText.TLabel", wraplength=700)
        synopsis_label.pack(anchor=tk.W, pady=20)

        # 加载并显示图片
        self.load_poster()

    def load_poster(self):
        poster_path = self.movie["poster_path"]
        if not poster_path or not os.path.exists(poster_path):
            poster_path = "posters/default.png"

        try:
            img = Image.open(poster_path)
            # 调整海报尺寸为固定的800x538
            img = img.resize((800, 538), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)

            # 在Canvas上显示图片
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        except Exception as e:
            print(f"Error loading poster: {e}")
            # 如果加载失败，显示错误信息
            self.canvas.create_text(400, 269, text="无法加载海报", fill="white", font=("Helvetica", 14))

    def update_level(self, new_level):
        for i, star in enumerate(self.rating_widgets):
            star.config(image=self.parent.STAR_FILLED if i < new_level else self.parent.STAR_EMPTY)
            star.image = self.parent.STAR_FILLED if i < new_level else self.parent.STAR_EMPTY

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
            # 关闭当前标签页
            index = self.parent.notebook.index(self.window)
            self.parent.notebook.forget(index)

    def show_edit_movie_window(self):
        edit_frame = ttk.Frame(self.parent.notebook)
        from movie_edit import EditMovieWindow
        EditMovieWindow(self.parent, edit_frame, self.movie, self.update_movie)
        self.parent.notebook.add(edit_frame, text=f"修改 {self.movie['title']}")
        self.parent.notebook.select(edit_frame)

    def update_movie(self, updated_movie):
        index = next((i for i, m in enumerate(self.parent.movies_data) if m["title"] == self.movie["title"]), None)
        if index is not None:
            self.parent.movies_data[index] = updated_movie
            self.parent.load_posters()
            self.save_data_callback()
            messagebox.showinfo("提示", "影片信息更新成功")
            # 关闭当前标签页
            index = self.parent.notebook.index(self.window)
            self.parent.notebook.forget(index)