import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import json
from movie_detail import MovieDetailWindow
from movie_add import AddMovieWindow
from movie_edit import EditMovieWindow

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
        self.root.minsize(800, 900)  # 进一步增加最小高度

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
        self.use_image_stars = self.load_star_images()

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

        # 分页相关变量
        self.current_page = 1
        self.movies_per_page = 0  # 动态计算
        self.posters_frame_width = 0  # 海报区域宽度
        self._load_pending = False  # 防止重复加载

        # 创建 Notebook 用于管理标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 主页面框架
        self.main_frame = ttk.Frame(self.notebook, style="PostersFrame.TFrame")
        self.notebook.add(self.main_frame, text="主页面")

        # 界面组件
        self.create_ui()

        # 绑定窗口大小变化事件
        self.root.bind("<Configure>", self.on_window_resize)

        # 窗口首次显示后加载海报
        self.root.after(100, self.load_posters)

    def load_star_images(self):
        """加载星星图片，如果加载失败则使用文本替代"""
        try:
            STAR_EMPTY_PATH = os.path.join("posters", "star_empty.png")
            STAR_FILLED_PATH = os.path.join("posters", "star_filled.png")

            if os.path.exists(STAR_EMPTY_PATH) and os.path.exists(STAR_FILLED_PATH):
                self.STAR_EMPTY = ImageTk.PhotoImage(Image.open(STAR_EMPTY_PATH).resize((20, 20)))
                self.STAR_FILLED = ImageTk.PhotoImage(Image.open(STAR_FILLED_PATH).resize((20, 20)))
                return True
            else:
                return False
        except Exception as e:
            print(f"加载星星图片失败: {e}")
            return False

    def create_ui(self):
        # 顶部操作栏 - 添加影片按钮和搜索框
        top_bar = ttk.Frame(self.main_frame, style="SearchFrame.TFrame")
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

        # 海报墙框架 - 使用Canvas实现滚动
        self.canvas_frame = ttk.Frame(self.main_frame, style="PostersFrame.TFrame")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 0))

        # 创建Canvas和垂直滚动条
        self.canvas = tk.Canvas(self.canvas_frame, bg="#1E1E1E", highlightthickness=0)

        # 修改：隐藏滚动条但保留功能
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # 隐藏滚动条
        # self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建海报内容框架
        self.posters_frame = ttk.Frame(self.canvas, style="PostersFrame.TFrame")
        self.posters_window = self.canvas.create_window((0, 0), window=self.posters_frame, anchor="nw")

        # 绑定事件处理滚动和调整大小
        self.posters_frame.bind("<Configure>", self.on_posters_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # 绑定鼠标滚轮事件
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # 底部导航栏 - 分页控制
        self.bottom_nav = ttk.Frame(self.main_frame, style="SearchFrame.TFrame")
        self.bottom_nav.pack(fill=tk.X, padx=20, pady=30)  # 进一步增加底部边距

        # 上一页按钮
        self.prev_btn = ttk.Button(self.bottom_nav, text="上一页", command=self.prev_page)
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        # 页码标签
        self.page_label = ttk.Label(self.bottom_nav, text="第 1 页", style="TitleLabel.TLabel")
        self.page_label.pack(side=tk.LEFT, padx=20)

        # 下一页按钮
        self.next_btn = ttk.Button(self.bottom_nav, text="下一页", command=self.next_page)
        self.next_btn.pack(side=tk.LEFT, padx=5)

    def on_window_resize(self, event):
        """窗口大小变化时重新计算每行显示的海报数量并刷新"""
        # 防止重复调用
        if event and event.widget == self.root:
            # 延迟执行，避免频繁刷新
            self.root.after(100, self._delayed_load_posters)

    def on_canvas_configure(self, event):
        """当Canvas大小变化时，调整内部窗口宽度"""
        # 仅在宽度变化时调整
        if hasattr(self, 'posters_window'):
            self.canvas.itemconfig(self.posters_window, width=event.width)

            # 延迟执行，避免频繁刷新
            self.root.after(100, self._delayed_load_posters)

    def _delayed_load_posters(self):
        """延迟加载海报，避免频繁调用"""
        # 防止在窗口调整过程中多次调用
        if not hasattr(self, '_load_pending') or not self._load_pending:
            self._load_pending = True
            self.calculate_movies_per_page()
            self.load_posters()
            self._load_pending = False

    def calculate_movies_per_page(self):
        """计算每页可显示的电影数量，固定为3行"""
        # 获取Canvas实际宽度
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 0:
            canvas_width = 1000  # 默认宽度，防止计算错误

        # 计算每行可显示的海报数量（海报宽度180 + 左右边距各5）
        cols = max(1, canvas_width // 190)  # 至少显示1列

        # 固定行数为3
        rows = 3

        # 计算每页显示的电影数量
        self.movies_per_page = rows * cols

    def on_posters_frame_configure(self, event):
        """当海报框架大小变化时，更新Canvas的滚动区域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # 更新Canvas内部窗口宽度
        self.canvas.itemconfig(self.posters_window, width=event.width)

    def on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        if self.canvas_frame.winfo_containing(event.x_root, event.y_root) == self.canvas:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def load_posters(self):
        """根据当前页和每页显示数量加载海报"""
        # 获取Canvas的可用宽度
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 0:
            canvas_width = 1000  # 默认宽度，防止计算错误

        # 计算每页可显示的电影数量
        self.calculate_movies_per_page()

        # 确保每页显示的电影数量至少为1
        if self.movies_per_page <= 0:
            self.movies_per_page = 1

        # 获取当前页的电影数据
        start_idx = (self.current_page - 1) * self.movies_per_page
        end_idx = start_idx + self.movies_per_page
        current_movies = self.movies_data[start_idx:end_idx]

        # 清空现有内容
        for widget in self.posters_frame.winfo_children():
            widget.destroy()

        # 创建一个列表来存储所有海报图片的引用，防止被垃圾回收
        self.poster_images = []

        # 计算总页数
        total_pages = max(1, (len(self.movies_data) + self.movies_per_page - 1) // self.movies_per_page)

        # 更新分页控制
        self.update_pagination(total_pages)

        # 重新加载当前页的电影海报
        if not current_movies:
            # 如果当前页没有电影，显示提示信息
            no_movies_label = ttk.Label(
                self.posters_frame,
                text="没有找到电影",
                style="TitleLabel.TLabel"
            )
            no_movies_label.grid(row=0, column=0, padx=20, pady=20)
            return

        # 确保每行至少有1列
        cols = max(1, canvas_width // 190)  # 每行显示的海报数量

        for index, movie in enumerate(current_movies):
            row = index // cols
            col = index % cols

            # 使用统一的加载海报函数，确保所有海报尺寸一致
            poster_photo = self.load_poster_image(movie["poster_path"])

            if poster_photo:
                # 创建固定大小的海报框架
                poster_frame = ttk.Frame(self.posters_frame, style="PosterFrame.TFrame", width=180, height=260)  # 进一步增加高度
                poster_frame.grid(row=row, column=col, padx=5, pady=5)
                poster_frame.grid_propagate(False)  # 防止框架根据内容调整大小

                # 创建海报容器
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

                # 创建标题标签 - 调整wraplength为海报宽度
                title_label = ttk.Label(title_container, text=movie["title"],
                                        style="TitleLabel.TLabel", wraplength=180)  # 设置为海报宽度
                title_label.pack(fill=tk.BOTH, expand=True)

                # 主演信息容器
                stars_container = ttk.Frame(poster_frame, style="PosterFrame.TFrame", height=30)
                stars_container.pack(side=tk.TOP, fill=tk.X, pady=2)  # 增加边距
                stars_container.pack_propagate(False)  # 防止容器根据内容调整大小

                # 主演信息标签
                stars_text = movie.get("stars", "")
                stars_label = ttk.Label(stars_container,
                                        text=stars_text if len(stars_text) <= 15 else stars_text[:15] + "...",
                                        style="StarsLabel.TLabel", wraplength=180)  # 设置为海报宽度
                stars_label.pack(fill=tk.BOTH, expand=True)

                # 显示评分星级
                level = int(float(movie["level"])) if movie["level"] else 0
                stars_frame = ttk.Frame(poster_frame, style="PosterFrame.TFrame")
                stars_frame.pack(side=tk.TOP, pady=5, anchor=tk.W)  # 增加边距

                # 存储星星组件引用，用于后续更新
                movie["star_widgets"] = []
                for i in range(5):
                    if self.use_image_stars:
                        # 使用图片星星
                        star_label = ttk.Label(stars_frame, image=self.STAR_FILLED if i < level else self.STAR_EMPTY)
                        star_label.image = self.STAR_FILLED if i < level else self.STAR_EMPTY
                    else:
                        # 使用文本星星
                        star_label = ttk.Label(stars_frame, text="★" if i < level else "☆",
                                               foreground="#FFD700" if i < level else "#AAAAAA",
                                               font=("Helvetica", 14))
                    # 添加星星之间的间距
                    star_label.pack(side=tk.LEFT, padx=2)
                    movie["star_widgets"].append(star_label)

                # 绑定点击事件
                poster_frame.bind("<Button-1>", lambda event, m=movie: self.show_movie_detail(m))
                poster_label.bind("<Button-1>", lambda event, m=movie: self.show_movie_detail(m))
                title_label.bind("<Button-1>", lambda event, m=movie: self.show_movie_detail(m))
                stars_label.bind("<Button-1>", lambda event, m=movie: self.show_movie_detail(m))

    def load_poster_image(self, poster_path):
        """加载并统一调整海报尺寸的辅助函数"""
        try:
            # 检查海报路径是否存在，如果不存在则使用默认海报
            if not poster_path or not os.path.exists(poster_path):
                if os.path.exists(DEFAULT_POSTER):
                    poster_path = DEFAULT_POSTER
                else:
                    # 创建默认海报
                    img = Image.new('RGB', (120, 180), color=(50, 50, 50))
                    img.save(DEFAULT_POSTER)
                    poster_path = DEFAULT_POSTER

            # 打开图片
            img = Image.open(poster_path).convert('RGB')

            # 目标尺寸 - 海报宽度
            target_width = 180
            target_height = 120

            # 调整图片大小并居中
            img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)

            # 创建背景
            final_img = Image.new('RGB', (target_width, target_height), color=(50, 50, 50))

            # 居中放置图片
            position = ((target_width - img.width) // 2, (target_height - img.height) // 2)
            final_img.paste(img, position)

            photo = ImageTk.PhotoImage(final_img)

            # 保存图片引用，防止被垃圾回收
            self.poster_images.append(photo)
            return photo

        except Exception as e:
            print(f"Error loading poster {poster_path}: {e}")
            return None

    def update_pagination(self, total_pages):
        """更新分页控制"""
        # 更新页码标签
        self.page_label.config(text=f"第 {self.current_page} 页，共 {total_pages} 页")

        # 启用/禁用上一页按钮
        if self.current_page <= 1:
            self.prev_btn.config(state=tk.DISABLED)
        else:
            self.prev_btn.config(state=tk.NORMAL)

        # 启用/禁用下一页按钮
        if self.current_page >= total_pages:
            self.next_btn.config(state=tk.DISABLED)
        else:
            self.next_btn.config(state=tk.NORMAL)

    def prev_page(self):
        """显示上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_posters()

    def next_page(self):
        """显示下一页"""
        total_pages = (len(self.movies_data) + self.movies_per_page - 1) // self.movies_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self.load_posters()

    def search_movies(self):
        """搜索电影"""
        keyword = self.search_entry.get().lower()
        filtered = [m for m in self.movies_data
                    if keyword in m["title"].lower() or
                    keyword in m["stars"].lower() or
                    keyword in m["director"].lower()]

        # 重置分页状态
        self.current_page = 1
        self.movies_data = filtered
        self.load_posters()

    def show_movie_detail(self, movie):
        """显示电影详情"""
        detail_frame = ttk.Frame(self.notebook)
        MovieDetailWindow(self, detail_frame, movie, self.update_level, self.save_movies_data)
        self.notebook.add(detail_frame, text=movie["title"])
        self.notebook.select(detail_frame)

    def update_level(self, movie, new_level):
        """更新电影评分"""
        # 更新电影数据
        movie["level"] = str(new_level)

        # 更新首页星星显示
        if "star_widgets" in movie:
            for i, star in enumerate(movie["star_widgets"]):
                if self.use_image_stars:
                    star.config(image=self.STAR_FILLED if i < new_level else self.STAR_EMPTY)
                    star.image = self.STAR_FILLED if i < new_level else self.STAR_EMPTY
                else:
                    star.config(text="★" if i < new_level else "☆",
                                foreground="#FFD700" if i < new_level else "#AAAAAA")

        # 保存更新后的电影数据到文件
        self.save_movies_data()

        messagebox.showinfo("提示", f"已将《{movie['title']}》的评分更新为{new_level}星")

    def show_add_movie_window(self):
        """显示添加电影窗口"""
        add_frame = ttk.Frame(self.notebook)
        AddMovieWindow(self, add_frame, self.add_movie)
        self.notebook.add(add_frame, text="添加影片")
        self.notebook.select(add_frame)

    def add_movie(self, new_movie):
        """添加新电影"""
        self.movies_data.append(new_movie)

        # 重置分页状态
        self.current_page = 1
        self.load_posters()

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

        # 重置分页状态
        self.current_page = 1

        # 重新加载海报
        self.load_posters()

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
    style.configure("StarsLabel.TLabel", background="#1E1E1E", foreground="#AAAAAA", font=("Helvetica", 9))
    style.configure("InfoFrame.TFrame", background="#1E1E1E")
    style.configure("DetailTitle.TLabel", background="#1E1E1E", foreground="white")
    style.configure("DetailText.TLabel", background="#1E1E1E", foreground="white")
    style.configure("BtnFrame.TFrame", background="#1E1E1E")
    style.configure("TButton", background="#333333", foreground="white", borderwidth=0, focuscolor="#333333")
    style.map("TButton", background=[("active", "#444444")])

    app = MovieLibraryApp(root)
    root.mainloop()