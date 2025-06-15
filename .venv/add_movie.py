import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from PIL import Image, ImageTk  # 新增导入


class AddMovieWindow:
    def __init__(self, parent, add_movie_callback):
        self.parent = parent
        self.add_movie_callback = add_movie_callback

        self.window = tk.Toplevel(parent)
        self.window.title("添加影片")
        self.window.geometry("450x300")
        self.window.configure(bg="#1E1E1E")

        # 独立加载星星图片资源
        self.load_star_images()

        self.create_ui()

    def load_star_images(self):
        """加载星星图片资源"""
        STAR_EMPTY_PATH = os.path.join("posters", "star_empty.png")
        STAR_FILLED_PATH = os.path.join("posters", "star_filled.png")

        if os.path.exists(STAR_EMPTY_PATH) and os.path.exists(STAR_FILLED_PATH):
            self.STAR_EMPTY = ImageTk.PhotoImage(Image.open(STAR_EMPTY_PATH).resize((20, 20)))
            self.STAR_FILLED = ImageTk.PhotoImage(Image.open(STAR_FILLED_PATH).resize((20, 20)))
        else:
            messagebox.showerror("错误", "星星图片文件不存在，请检查路径。")

    def create_ui(self):
        # 输入字段 - 仅保留必要字段
        fields = ["title", "poster_path", "download_link", "watch_link"]
        labels = ["电影名称", "海报路径", "下载链接", "观看链接"]
        self.entries = {}

        for field, label_text in zip(fields, labels):
            frame = ttk.Frame(self.window, style="PosterFrame.TFrame")
            frame.pack(fill=tk.X, padx=20, pady=5)

            ttk.Label(frame, text=f"{label_text}：", style="DetailText.TLabel").pack(side=tk.LEFT, padx=5)

            if field == "poster_path":
                # 海报路径输入框和浏览按钮
                path_frame = ttk.Frame(frame)
                path_frame.pack(fill=tk.X, expand=True)

                entry = ttk.Entry(path_frame)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                self.entries[field] = entry

                browse_btn = ttk.Button(path_frame, text="浏览", command=lambda e=entry: self.browse_poster(e))
                browse_btn.pack(side=tk.LEFT, padx=5)
            else:
                entry = ttk.Entry(frame)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                self.entries[field] = entry

        # 评分星级选择（初始5颗空星星）
        rating_frame = ttk.Frame(self.window, style="PosterFrame.TFrame")
        rating_frame.pack(fill=tk.X, padx=20, pady=5)

        ttk.Label(rating_frame, text="评价星级：", style="DetailText.TLabel").pack(side=tk.LEFT, padx=5)

        self.rating_widgets = []
        self.selected_rating = tk.IntVar(value=0)  # 初始值为0（全空）

        # 确保星星图像已加载
        if not hasattr(self, 'STAR_EMPTY') or not hasattr(self, 'STAR_FILLED'):
            messagebox.showerror("错误", "星星图片资源未加载，请检查路径")
            return

        for i in range(5):
            star_label = ttk.Label(rating_frame, image=self.STAR_EMPTY)
            star_label.image = self.STAR_EMPTY
            star_label.pack(side=tk.LEFT)
            star_label.bind("<Button-1>", lambda event, idx=i: self.set_add_rating(idx + 1))
            self.rating_widgets.append(star_label)

        # 确认按钮
        ttk.Button(self.window, text="确认", command=self.confirm_add).pack(pady=20)

    def browse_poster(self, entry_widget):
        """打开文件浏览器选择海报图片"""
        file_path = filedialog.askopenfilename(
            title="选择海报图片",
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)

    def set_add_rating(self, num):
        """设置评分星级"""
        self.selected_rating.set(num)
        for i, star in enumerate(self.rating_widgets):
            star.config(image=self.STAR_FILLED if i < num else self.STAR_EMPTY)
            star.image = self.STAR_FILLED if i < num else self.STAR_EMPTY

    def confirm_add(self):
        """确认添加电影"""
        title = self.entries["title"].get().strip()
        poster_path = self.entries["poster_path"].get().strip()

        if not title or self.selected_rating.get() == 0:
            messagebox.showerror("错误", "电影名称和评价星级不能为空")
            return

        # 如果没有提供海报路径，使用默认海报
        if not poster_path:
            poster_path = "posters/default.png"
        # 检查海报文件是否存在
        elif not os.path.exists(poster_path):
            messagebox.showwarning("警告", f"海报文件不存在: {poster_path}\n将使用默认海报")
            poster_path = "posters/default.png"

        new_movie = {
            "title": title,
            "poster_path": poster_path,
            "stars": "",  # 空值，已移除输入字段
            "director": "",  # 空值，已移除输入字段
            "type": "",  # 空值，已移除输入字段
            "release_year": "",  # 空值，已移除输入字段
            "region": "",  # 空值，已移除输入字段
            "update_date": "",  # 可自动设置为当前日期
            "rating": str(self.selected_rating.get()),
            "download_link": self.entries["download_link"].get(),
            "watch_link": self.entries["watch_link"].get()
        }

        # 调用主窗口的添加电影方法
        self.add_movie_callback(new_movie)

        # 关闭窗口
        self.window.destroy()