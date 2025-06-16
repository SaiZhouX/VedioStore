import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import json
from movie_detail import MovieDetailWindow

# 电影数据存储文件
MOVIES_FILE = os.path.abspath("movies.json")  # 使用绝对路径
# 默认海报路径
DEFAULT_POSTER = os.path.abspath("posters/default.png")  # 使用绝对路径


class MovieLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("影片库")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1E1E1E")

        # 创建海报目录
        os.makedirs("posters", exist_ok=True)

        # 检查默认海报是否存在，不存在则创建
        if not os.path.exists(DEFAULT_POSTER):
            try:
                img = Image.new('RGB', (120, 180), color=(50, 50, 50))
                img.save(DEFAULT_POSTER)
            except Exception as e:
                print(f"无法创建默认海报: {e}")

        # 加载星星图片
        STAR_EMPTY_PATH = os.path.join("posters", "star_empty.png")
        STAR_FILLED_PATH = os.path.join("posters", "star_filled.png")

        if os.path.exists(STAR_EMPTY_PATH) and os.path.exists(STAR_FILLED_PATH):
            self.STAR_EMPTY = ImageTk.PhotoImage(Image.open(STAR_EMPTY_PATH).resize((20, 20)))
            self.STAR_FILLED = ImageTk.PhotoImage(Image.open(STAR_FILLED_PATH).resize((20, 20)))
        else:
            messagebox.showerror("错误", "星星图片文件不存在，请检查路径。")

        # 尝试从文件中读取电影数据
        try:
            with open(MOVIES_FILE, "r", encoding="utf-8") as f:
                self.movies_data = json.load(f)
        except FileNotFoundError:
            # 如果文件不存在，使用默认数据
            self.movies_data = [
                {
                    "title": "铁血战士：杀戮之王",
                    "poster_path": "posters/predator.jpg",
                    "stars": "迈克尔·比恩, 道格·科克尔",
                    "director": "丹·特拉亨伯格",
                    "type": "首推",
                    "region": "美国",
                    "level": "7.1",
                    "download_link": "",
                    "watch_link": ""
                },
                {
                    "title": "哪吒之魔童闹海",
                    "poster_path": "posters/nezha.jpg",
                    "stars": "吕艳婷, 囧森瑟夫",
                    "director": "饺子",
                    "type": "动画",
                    "region": "中国",
                    "level": "8.6",
                    "download_link": "",
                    "watch_link": ""
                }
            ]

        # 界面组件
        self.create_ui()

    def create_ui(self):
        # 顶部操作栏 - 添加影片按钮和搜索框
        top_bar = ttk.Frame(self.root, style="SearchFrame.TFrame")
        top_bar.pack(pady=10, fill=tk.X, padx=20)

        # 添加影片按钮
        add_movie_btn = ttk.Button(top_bar, text="添加影片", command=self.show_add_movie_window)
        add_movie_btn.pack(side=tk.RIGHT, padx=5)

        # 搜索栏
        search_frame = ttk.Frame(top_bar, style="SearchFrame.TFrame")
        search_frame.pack(side=tk.RIGHT, padx=5)

        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        self.search_btn = ttk.Button(search_frame, text="搜索", command=self.search_movies)
        self.search_btn.pack(side=tk.LEFT, padx=5)

        # 海报墙框架
        self.posters_frame = ttk.Frame(self.root, style="PostersFrame.TFrame")
        self.posters_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 加载海报
        self.load_posters(self.movies_data)

    def load_posters(self, movies):
        # 清空现有内容
        for widget in self.posters_frame.winfo_children():
            widget.destroy()

        # 创建一个列表来存储所有海报图片的引用，防止被垃圾回收
        self.poster_images = []

        # 重新加载所有电影海报
        cols = 7
        for index, movie in enumerate(movies):
            row = index // cols
            col = index % cols

            # 使用统一的加载海报函数，确保所有海报尺寸一致
            poster_photo = self.load_poster_image(movie["poster_path"])

            if poster_photo:
                # 创建固定大小的海报框架
                poster_frame = ttk.Frame(self.posters_frame, style="PosterFrame.TFrame", width=300, height=130)  # 增加高度以容纳主演信息
                poster_frame.grid(row=row, column=col, padx=5, pady=5)
                poster_frame.grid_propagate(False)  # 防止框架根据内容调整大小

                # 创建海报容器，使用pack布局确保顶部对齐
                image_container = ttk.Frame(poster_frame, style="PosterFrame.TFrame")
                image_container.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

                # 创建海报标签
                poster_label = ttk.Label(image_container, image=poster_photo)
                poster_label.image = poster_photo
                poster_label.pack()

                # 创建标题容器，使用固定高度并允许文本溢出
                title_container = ttk.Frame(poster_frame, style="PosterFrame.TFrame", height=40)
                title_container.pack(side=tk.TOP, fill=tk.X, pady=2)
                title_container.pack_propagate(False)  # 防止容器根据内容调整大小

                # 创建标题标签
                title_label = ttk.Label(title_container, text=movie["title"],
                                        style="TitleLabel.TLabel", wraplength=120)
                title_label.pack(fill=tk.BOTH, expand=True)

                # 新增：主演信息容器
                stars_container = ttk.Frame(poster_frame, style="PosterFrame.TFrame", height=30)
                stars_container.pack(side=tk.TOP, fill=tk.X, pady=1)
                stars_container.pack_propagate(False)  # 防止容器根据内容调整大小

                # 新增：主演信息标签
                stars_text = movie.get("stars", "")
                stars_label = ttk.Label(stars_container, text=stars_text if len(stars_text) <= 15 else stars_text[:15] + "...",
                                       style="StarsLabel.TLabel", wraplength=120)
                stars_label.pack(fill=tk.BOTH, expand=True)

                # 显示评分星级
                level = int(float(movie["level"])) if movie["level"] else 0
                stars_frame = ttk.Frame(poster_frame, style="PosterFrame.TFrame")
                # 修改这里，使用 pack 方法左对齐
                stars_frame.pack(side=tk.TOP, pady=2, anchor=tk.W)

                # 存储星星组件引用，用于后续更新
                movie["star_widgets"] = []
                for i in range(5):
                    star_label = ttk.Label(stars_frame,
                                           image=self.STAR_FILLED if i < level else self.STAR_EMPTY)
                    star_label.image = self.STAR_FILLED if i < level else self.STAR_EMPTY
                    star_label.pack(side=tk.LEFT)
                    movie["star_widgets"].append(star_label)

                # 绑定点击事件
                poster_frame.bind("<Button-1>", lambda event, m=movie: self.show_movie_detail(m))
                poster_label.bind("<Button-1>", lambda event, m=movie: self.show_movie_detail(m))
                title_label.bind("<Button-1>", lambda event, m=movie: self.show_movie_detail(m))
                stars_label.bind("<Button-1>", lambda event, m=movie: self.show_movie_detail(m))  # 新增：为主演信息添加点击事件

    def load_poster_image(self, poster_path):
        """加载并统一调整海报尺寸的辅助函数"""
        try:
            # 检查海报路径是否存在，如果不存在则使用默认海报
            if not poster_path or not os.path.exists(poster_path):
                if os.path.exists(DEFAULT_POSTER):
                    poster_path = DEFAULT_POSTER
                else:
                    print("默认海报也不存在!")
                    return None

            # 打开图片
            img = Image.open(poster_path).convert('RGB')

            # 目标尺寸
            target_width = 250
            target_height = 120

            # 计算宽高比
            aspect_ratio = img.width / img.height

            # 计算等比例缩小后的尺寸
            if img.width > target_width or img.height > target_height:
                if img.width / target_width > img.height / target_height:
                    new_width = target_width
                    new_height = int(new_width / aspect_ratio)
                else:
                    new_height = target_height
                    new_width = int(new_height * aspect_ratio)
            else:
                new_width = img.width
                new_height = img.height

            # 调整图片大小
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 创建一个空白的目标大小的图片
            final_img = Image.new('RGB', (target_width, target_height), color=(50, 50, 50))

            # 计算居中位置
            x_offset = (target_width - new_width) // 2
            y_offset = (target_height - new_height) // 2

            # 将调整后的图片粘贴到空白图片上
            final_img.paste(resized_img, (x_offset, y_offset))

            photo = ImageTk.PhotoImage(final_img)

            # 保存图片引用，防止被垃圾回收
            self.poster_images.append(photo)
            return photo

        except Exception as e:
            print(f"Error loading poster {poster_path}: {e}")
            # 如果加载出错，尝试加载默认海报
            try:
                img = Image.open(DEFAULT_POSTER).convert('RGB')

                # 目标尺寸
                target_width = 120
                target_height = 180

                # 计算宽高比
                aspect_ratio = img.width / img.height

                # 计算等比例缩小后的尺寸
                if img.width > target_width or img.height > target_height:
                    if img.width / target_width > img.height / target_height:
                        new_width = target_width
                        new_height = int(new_width / aspect_ratio)
                    else:
                        new_height = target_height
                        new_width = int(new_height * aspect_ratio)
                else:
                    new_width = img.width
                    new_height = img.height

                # 调整图片大小
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # 创建一个空白的目标大小的图片
                final_img = Image.new('RGB', (target_width, target_height), color=(50, 50, 50))

                # 计算居中位置
                x_offset = (target_width - new_width) // 2
                y_offset = (target_height - new_height) // 2

                # 将调整后的图片粘贴到空白图片上
                final_img.paste(resized_img, (x_offset, y_offset))

                photo = ImageTk.PhotoImage(final_img)
                self.poster_images.append(photo)
                return photo
            except Exception as e2:
                print(f"Error loading default poster: {e2}")
                return None

    def search_movies(self):
        keyword = self.search_entry.get().lower()
        filtered = [m for m in self.movies_data
                    if keyword in m["title"].lower() or
                    keyword in m["stars"].lower() or
                    keyword in m["director"].lower()]
        self.load_posters(filtered)

    def show_movie_detail(self, movie):
        # 修改这里，将 self 作为第一个参数传递
        MovieDetailWindow(self, movie, self.update_level, self.save_movies_data)

    def update_level(self, movie, new_level):
        # 更新电影数据
        movie["level"] = str(new_level)

        # 更新首页星星显示
        if "star_widgets" in movie:
            for i, star in enumerate(movie["star_widgets"]):
                star.config(image=self.STAR_FILLED if i < new_level else self.STAR_EMPTY)
                star.image = self.STAR_FILLED if i < new_level else self.STAR_EMPTY

        # 保存更新后的电影数据到文件
        self.save_movies_data()

        messagebox.showinfo("提示", f"已将《{movie['title']}》的评分更新为{new_level}星")

    def show_add_movie_window(self):
        # 延迟导入以避免循环依赖
        from add_movie import AddMovieWindow
        AddMovieWindow(self.root, self.add_movie)

    def add_movie(self, new_movie):
        self.movies_data.append(new_movie)
        self.load_posters(self.movies_data)
        messagebox.showinfo("提示", "影片添加成功")
        print(f"添加新电影: {new_movie['title']}")

        # 确保保存电影数据
        save_success = self.save_movies_data()
        if save_success:
            print(f"电影数据已成功保存到 {MOVIES_FILE}")
        else:
            print(f"保存电影数据失败: {MOVIES_FILE}")

    def save_movies_data(self):
        """保存电影数据到JSON文件，返回保存是否成功"""
        # 移除临时的 star_widgets 键
        for movie in self.movies_data:
            movie.pop("star_widgets", None)

        # 确保存储目录存在
        directory = os.path.dirname(MOVIES_FILE)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"创建目录: {directory}")
            except Exception as e:
                error_info = f"无法创建目录: {directory}\n"
                error_info += f"错误: {str(e)}\n"
                error_info += f"当前工作目录: {os.getcwd()}"
                print(error_info)
                messagebox.showerror("错误", error_info)
                return False

        # 尝试将电影数据保存到 JSON 文件
        try:
            with open(MOVIES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.movies_data, f, ensure_ascii=False, indent=4)
            print(f"电影数据已成功保存到 {MOVIES_FILE}")

            # 验证保存的文件是否可读
            try:
                with open(MOVIES_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                print(f"验证成功: 保存的文件包含 {len(data)} 部电影")
                return True
            except Exception as e:
                print(f"验证失败: 保存的文件无法读取: {e}")
                return False

        except Exception as e:
            # 提供更详细的错误信息
            error_info = f"保存电影数据失败: {str(e)}\n"
            error_info += f"错误类型: {type(e).__name__}\n"
            error_info += f"当前工作目录: {os.getcwd()}\n"
            error_info += f"尝试保存的文件路径: {MOVIES_FILE}\n"
            error_info += f"文件所在目录是否存在: {os.path.exists(directory)}\n"
            error_info += f"目录权限: {oct(os.stat(directory).st_mode & 0o777)}"

            print(error_info)
            messagebox.showerror("错误", error_info)
            return False

    # 其他方法保持不变
    def play_movie(self, movie):
        messagebox.showinfo("提示", f"即将播放 {movie['title']}")

    def follow_movie(self, movie):
        messagebox.showinfo("提示", f"已关注 {movie['title']}")

    def choose_subtitle(self, subtitle):
        messagebox.showinfo("提示", f"已选择字幕：{subtitle}")

    def delete_movie(self, movie):
        # 从电影数据列表中删除该电影
        self.movies_data = [m for m in self.movies_data if m != movie]
        # 重新加载海报
        self.load_posters(self.movies_data)
        # 保存更新后的电影数据到文件
        self.save_movies_data()
        messagebox.showinfo("提示", f"已删除《{movie['title']}》")


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use("clam")

    # 配置深色风格
    style.configure("SearchFrame.TFrame", background="#1E1E1E")
    style.configure("PostersFrame.TFrame", background="#1E1E1E")
    style.configure("PosterFrame.TFrame", background="#1E1E1E")
    style.configure("TitleLabel.TLabel", background="#1E1E1E", foreground="white", font=("Helvetica", 10, "bold"))
    style.configure("StarsLabel.TLabel", background="#1E1E1E", foreground="#AAAAAA", font=("Helvetica", 9))  # 新增：主演信息样式
    style.configure("InfoFrame.TFrame", background="#1E1E1E")
    style.configure("DetailTitle.TLabel", background="#1E1E1E", foreground="white")
    style.configure("DetailText.TLabel", background="#1E1E1E", foreground="white")
    style.configure("BtnFrame.TFrame", background="#1E1E1E")
    style.configure("TButton", background="#333333", foreground="white", borderwidth=0, focuscolor="#333333")
    style.map("TButton", background=[("active", "#444444")])

    app = MovieLibraryApp(root)
    root.mainloop()