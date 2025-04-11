import wcocr
import os
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, font, ttk
from PIL import Image, ImageTk, ImageGrab
import pyautogui
import time
import pyperclip
import json
from datetime import datetime
from find_wechat_path import find_wechat_path, find_wechatocr_exe

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("微信OCR截图识别工具")
        self.root.geometry("900x700")
        
        # 初始化变量
        self.image_path = tk.StringVar()
        self.screenshot_mode = False
        self.screenshot_canvas = None
        self.screenshot_window = None
        self.screenshot_rect = None
        self.screenshot_start = None
        
        # 默认字体设置
        self.current_font_family = "微软雅黑"
        self.current_font_size = 11
        
        # 历史记录相关
        self.history_file = "ocr_history.json"
        self.history_data = self.load_history()
        
        # 创建图片保存目录
        self.image_dir = "ocr_images"
        os.makedirs(self.image_dir, exist_ok=True)
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        # 主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 按钮区域 - 使用Frame作为容器并居中
        button_container = tk.Frame(main_frame)
        button_container.pack(fill=tk.X, pady=10)
        
        # 在容器内部再创建一个Frame用于放置按钮，并居中
        button_frame = tk.Frame(button_container)
        button_frame.pack()  # 默认居中
        
        # 功能按钮 - 现在会居中显示
        buttons = [
            ("载入图片", self.load_image, None),
            ("屏幕截图", self.start_screenshot_mode, "#4CAF50"),
            ("全局识别", self.start_global_ocr, None),
            ("历史记录", self.show_history, "#9C27B0")
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                button_frame, 
                text=text, 
                command=command,
                width=10  # 统一按钮宽度
            )
            if color:
                btn.config(bg=color, fg="white")
            btn.pack(side=tk.LEFT, padx=5, ipadx=5, ipady=3)

        # 图片显示区域
        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="white")
        h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.config(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)

    def start_screenshot_mode(self):
        """进入区域截图模式"""
        try:
            self.screenshot_mode = True
            self.status_var.set("截图模式: 请选择屏幕区域 (按住鼠标左键拖动, ESC键取消)")
            self.root.withdraw()
            time.sleep(0.3)  # 等待窗口隐藏
            
            # 创建全屏透明窗口
            self.screenshot_window = tk.Toplevel()
            self.screenshot_window.attributes('-fullscreen', True)
            self.screenshot_window.attributes('-alpha', 0.2)
            self.screenshot_window.attributes('-topmost', True)
            self.screenshot_window.configure(bg='black')
            
            # 添加Canvas用于绘制选择框
            self.screenshot_canvas = tk.Canvas(self.screenshot_window, bg='black', highlightthickness=0)
            self.screenshot_canvas.pack(fill=tk.BOTH, expand=True)
            
            # 绑定鼠标事件
            self.screenshot_window.bind("<Button-1>", self.on_screenshot_start)
            self.screenshot_window.bind("<B1-Motion>", self.on_screenshot_drag)
            self.screenshot_window.bind("<ButtonRelease-1>", self.on_screenshot_end)
            
            # 绑定ESC键退出事件
            self.screenshot_window.bind("<Escape>", lambda e: self.cancel_screenshot())
            
            # 窗口关闭事件
            self.screenshot_window.protocol("WM_DELETE_WINDOW", self.cancel_screenshot)
            
            # 确保窗口获得焦点
            self.screenshot_window.focus_force()
            
        except Exception as e:
            messagebox.showerror("错误", f"无法进入截图模式: {str(e)}")
            self.root.deiconify()

    def on_screenshot_start(self, event):
        """截图开始事件"""
        self.screenshot_start = (event.x_root, event.y_root)
        self.screenshot_rect = None

    def on_screenshot_drag(self, event):
        """截图拖动事件"""
        if hasattr(self, 'screenshot_start') and self.screenshot_start:
            if self.screenshot_rect:
                self.screenshot_canvas.delete(self.screenshot_rect)
            x1, y1 = self.screenshot_start
            x2, y2 = event.x_root, event.y_root
            # 转换为相对于Canvas的坐标
            canvas_x1 = x1 - self.screenshot_window.winfo_rootx()
            canvas_y1 = y1 - self.screenshot_window.winfo_rooty()
            canvas_x2 = x2 - self.screenshot_window.winfo_rootx()
            canvas_y2 = y2 - self.screenshot_window.winfo_rooty()
            self.screenshot_rect = self.screenshot_canvas.create_rectangle(
                canvas_x1, canvas_y1, canvas_x2, canvas_y2, 
                outline='red', width=2, fill='white')

    def on_screenshot_end(self, event):
        """截图结束事件"""
        if hasattr(self, 'screenshot_start') and self.screenshot_start and self.screenshot_rect:
            x1, y1 = self.screenshot_start
            x2, y2 = event.x_root, event.y_root
            
            # 确保坐标是左上到右下
            x1, x2 = sorted([x1, x2])
            y1, y2 = sorted([y1, y2])
            
            # 截取屏幕区域
            try:
                screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_filename = f"screenshot_{timestamp}.png"
                image_path = os.path.join(self.image_dir, image_filename)
                screenshot.save(image_path)
                
                # 恢复主窗口
                if self.screenshot_window:
                    self.screenshot_window.destroy()
                    self.screenshot_window = None
                self.root.deiconify()
                
                # 加载截图
                self.image_path.set(image_path)
                self.display_image(image_path)
                self.status_var.set(f"已截取区域: {x1},{y1} 到 {x2},{y2}")
                
            except Exception as e:
                messagebox.showerror("错误", f"截图失败: {str(e)}")
            finally:
                self.cleanup_screenshot()

    def cancel_screenshot(self, event=None):
        """取消截图"""
        self.cleanup_screenshot()
        self.status_var.set("截图已取消")

    def cleanup_screenshot(self):
        """清理截图资源"""
        self.screenshot_mode = False
        if hasattr(self, 'screenshot_window') and self.screenshot_window:
            self.screenshot_window.destroy()
            self.screenshot_window = None
        self.root.deiconify()

    def wechat_ocr(self, image_path):
        """调用微信OCR进行识别"""
        try:
            wcocr.init(find_wechatocr_exe(), find_wechat_path())
            result = wcocr.ocr(image_path)
            ocr_text = "\n".join([temp['text'] for temp in result['ocr_response']])
            
            # 添加到历史记录
            self.add_to_history(image_path, ocr_text)
            
            self.show_message(ocr_text=ocr_text)
        except Exception as e:
            messagebox.showerror("OCR错误", f"识别失败: {str(e)}")

    def show_message(self, ocr_text=None):
        """显示识别结果"""
        window = tk.Toplevel(self.root)
        window.title("识别结果")
        window.geometry("700x500")
        window.minsize(500, 400)  # 设置最小尺寸
        
        # 配置行列权重
        window.grid_rowconfigure(0, weight=1)
        window.grid_columnconfigure(0, weight=1)
        
        # 主框架
        main_frame = tk.Frame(window)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # 文本区域
        text_area = scrolledtext.ScrolledText(
            main_frame, 
            wrap=tk.WORD, 
            font=(self.current_font_family, self.current_font_size)
        )
        text_area.grid(row=0, column=0, sticky="nsew")
        
        if ocr_text:
            text_area.insert(tk.END, ocr_text)
            text_area.config(state=tk.DISABLED)

        # 创建右键菜单
        context_menu = tk.Menu(window, tearoff=0)
        context_menu.add_command(label="复制", command=lambda: self.copy_to_clipboard(text_area))
        context_menu.add_command(label="全选", command=lambda: text_area.tag_add(tk.SEL, "1.0", tk.END))
        
        # 绑定右键事件
        text_area.bind("<Button-3>", lambda e: context_menu.post(e.x_root, e.y_root))

        # 底部按钮框架
        bottom_frame = tk.Frame(window)
        bottom_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        # 左侧按钮组
        left_button_frame = tk.Frame(bottom_frame)
        left_button_frame.pack(side=tk.LEFT)

        # 导出文本按钮
        tk.Button(left_button_frame, text="导出文本", 
                 command=lambda: self.export_text(ocr_text),
                 bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)

        # 字体设置按钮
        tk.Button(left_button_frame, text="字体设置",
                 command=lambda: self.font_settings(window, text_area),
                 bg="#FF9800", fg="white").pack(side=tk.LEFT, padx=5)

        # 右侧按钮组
        right_button_frame = tk.Frame(bottom_frame)
        right_button_frame.pack(side=tk.RIGHT)

        # 一键复制按钮
        copy_btn = tk.Button(right_button_frame, 
                           text="一键复制", 
                           command=lambda: self.copy_to_clipboard(text_area),
                           bg="#2196F3", 
                           fg="white",
                           padx=15,
                           pady=5,
                           font=("微软雅黑", 10, "bold"))
        copy_btn.pack(side=tk.RIGHT, padx=5)

    def font_settings(self, parent_window, text_widget):
        """字体设置对话框"""
        font_window = tk.Toplevel(parent_window)
        font_window.title("字体设置")
        font_window.geometry("300x200")
        
        # 字体选择
        tk.Label(font_window, text="字体:").pack(pady=(10,0))
        font_family_var = tk.StringVar(value=self.current_font_family)
        font_family_menu = tk.OptionMenu(font_window, font_family_var, 
                                        "微软雅黑", "宋体", "黑体", "楷体", "Arial", "Times New Roman")
        font_family_menu.pack()
        
        # 字号选择
        tk.Label(font_window, text="字号:").pack(pady=(10,0))
        font_size_var = tk.IntVar(value=self.current_font_size)
        tk.Spinbox(font_window, from_=8, to=36, textvariable=font_size_var).pack()
        
        # 应用按钮
        def apply_font():
            new_size = font_size_var.get()
            self.current_font_family = font_family_var.get()
            self.current_font_size = new_size
            text_widget.config(font=(self.current_font_family, self.current_font_size))
            
            # 如果字体较大，自动调整窗口大小
            if new_size > 14:
                parent_window.geometry("800x600")
            
            font_window.destroy()
        
        tk.Button(font_window, text="应用", command=apply_font, 
                 bg="#4CAF50", fg="white").pack(pady=10)

    def copy_to_clipboard(self, text_widget):
        """复制文本到剪贴板"""
        try:
            # 获取选中文本，如果没有选中则获取全部文本
            selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST) if text_widget.tag_ranges(tk.SEL) else text_widget.get("1.0", tk.END)
            pyperclip.copy(selected_text.strip())
            self.status_var.set("文本已复制到剪贴板")
            # 显示复制成功的提示（短暂显示）
            self.root.after(2000, lambda: self.status_var.set("就绪"))
        except Exception as e:
            messagebox.showerror("复制失败", f"无法复制文本: {str(e)}")

    def export_text(self, text_content):
        """导出识别结果"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="保存识别结果"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                messagebox.showinfo("导出成功", f"文本已保存到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("导出失败", f"无法保存文件: {str(e)}")

    def load_image(self):
        """加载图片文件"""
        file_path = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if file_path:
            # 复制图片到图片目录
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = os.path.splitext(file_path)[1]
            new_filename = f"image_{timestamp}{ext}"
            new_path = os.path.join(self.image_dir, new_filename)
            
            try:
                # 复制文件
                with open(file_path, 'rb') as f_src:
                    with open(new_path, 'wb') as f_dst:
                        f_dst.write(f_src.read())
                
                self.image_path.set(new_path)
                self.display_image(new_path)
            except Exception as e:
                messagebox.showerror("错误", f"无法复制图片: {str(e)}")
                self.image_path.set(file_path)
                self.display_image(file_path)

    def display_image(self, file_path):
        """显示图片"""
        try:
            image = Image.open(file_path)
            photo = ImageTk.PhotoImage(image)

            self.canvas.config(width=photo.width(), height=photo.height())
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo
            self.status_var.set(f"已加载: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片: {str(e)}")

    def start_global_ocr(self):
        """开始全局识别"""
        if self.image_path.get():
            self.wechat_ocr(self.image_path.get())
        else:
            messagebox.showwarning("警告", "请先选择图片")

    def load_history(self):
        """加载历史记录并确保每条记录都有display_text字段"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    # 确保每条记录都有display_text字段
                    for item in history:
                        if 'display_text' not in item:
                            # 为旧记录创建display_text
                            full_text = item.get('full_text', item.get('text', ''))
                            item['display_text'] = full_text  # 不再截断，使用完整文本
                    return history
            except Exception as e:
                print(f"加载历史记录出错: {e}")
                return []
        return []

    def save_history(self):
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存历史记录失败: {str(e)}")

    def add_to_history(self, image_path, ocr_text):
        """添加到历史记录"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry = {
            "time": timestamp,
            "image": image_path,
            "display_text": ocr_text,  # 直接保存完整文本
            "full_text": ocr_text      # 兼容旧版本
        }
        self.history_data.insert(0, entry)  # 最新记录放在最前面
        if len(self.history_data) > 50:  # 限制历史记录数量
            self.history_data = self.history_data[:50]
        self.save_history()

    def show_history(self):
        """显示历史记录窗口"""
        history_window = tk.Toplevel(self.root)
        history_window.title("历史记录")
        history_window.geometry("900x800")  # 更大的窗口
        
        # 配置网格布局
        history_window.grid_rowconfigure(0, weight=1)
        history_window.grid_columnconfigure(0, weight=1)
        
        # 主框架
        main_frame = tk.Frame(history_window)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # 工具栏
        toolbar = tk.Frame(main_frame)
        toolbar.grid(row=0, column=0, sticky="ew", pady=5)
        
        tk.Button(toolbar, text="清空历史", command=self.clear_history,
                 bg="#F44336", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="导出全部", command=self.export_all_history,
                 bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        
        # 历史记录列表框架
        tree_frame = tk.Frame(main_frame)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        
        # 创建Treeview
        self.history_tree = ttk.Treeview(
            tree_frame,
            columns=("time", "image", "text"),
            show="headings",
            selectmode="browse"
        )
        
        # 配置样式
        style = ttk.Style()
        style.configure("Treeview", 
                      rowheight=30,  # 增加行高
                      font=('微软雅黑', 10))
        style.configure("Treeview.Heading", 
                      font=('微软雅黑', 10, 'bold'))
        
        # 定义列
        self.history_tree.heading("time", text="时间", anchor="center")
        self.history_tree.heading("image", text="图片路径", anchor="w")
        self.history_tree.heading("text", text="识别内容", anchor="w")
        
        # 设置列宽
        self.history_tree.column("time", width=150, anchor="center", stretch=False)
        self.history_tree.column("image", width=300, anchor="w", stretch=False)
        self.history_tree.column("text", width=700, anchor="w", stretch=True)  # 更宽的文本列
        
        # 添加滚动条
        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.history_tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # 布局
        self.history_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        # 配置网格权重
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # 填充数据 - 显示完整文本
        for item in self.history_data:
            display_text = item.get("display_text", 
                                  item.get("text", 
                                          item.get("full_text", "")))
            self.history_tree.insert("", tk.END, values=(
                item["time"],
                item["image"],
                display_text
            ))
        
        # 创建右键菜单
        self.history_context_menu = tk.Menu(history_window, tearoff=0)
        self.history_context_menu.add_command(label="查看详情", command=self.show_selected_history_detail)
        self.history_context_menu.add_command(label="复制文本", command=self.copy_selected_history_text)
        self.history_context_menu.add_command(label="查看原图", command=self.show_selected_history_image)
        
        # 绑定右键事件
        self.history_tree.bind("<Button-3>", self.on_history_right_click)
        
        # 底部按钮
        bottom_frame = tk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, sticky="e", pady=5)
        
        tk.Button(bottom_frame, text="关闭", command=history_window.destroy,
                 bg="#2196F3", fg="white").pack(side=tk.RIGHT, padx=5)

    def on_history_right_click(self, event):
        """处理历史记录右键点击事件"""
        item = self.history_tree.identify_row(event.y)
        if item:
            self.history_tree.selection_set(item)
            self.history_context_menu.post(event.x_root, event.y_root)

    def show_selected_history_detail(self):
        """显示选中的历史记录详情"""
        selected_item = self.history_tree.selection()
        if selected_item:
            item = self.history_tree.item(selected_item)
            values = item["values"]
            # 查找完整的历史记录
            for record in self.history_data:
                if record["time"] == values[0] and record["image"] == values[1]:
                    self.show_history_detail(record)
                    break

    def copy_selected_history_text(self):
        """复制选中的历史记录文本"""
        selected_item = self.history_tree.selection()
        if selected_item:
            item = self.history_tree.item(selected_item)
            values = item["values"]
            # 查找完整的历史记录
            for record in self.history_data:
                if record["time"] == values[0] and record["image"] == values[1]:
                    full_text = record.get("full_text", record.get("text", record.get("display_text", "")))
                    pyperclip.copy(full_text)
                    self.status_var.set("已复制文本到剪贴板")
                    self.root.after(2000, lambda: self.status_var.set("就绪"))
                    break

    def show_selected_history_image(self):
        """显示选中的历史记录图片"""
        selected_item = self.history_tree.selection()
        if selected_item:
            item = self.history_tree.item(selected_item)
            values = item["values"]
            # 查找完整的历史记录
            for record in self.history_data:
                if record["time"] == values[0] and record["image"] == values[1]:
                    if os.path.exists(record["image"]):
                        self.display_history_image(record["image"])
                    else:
                        messagebox.showerror("错误", "图片文件不存在")
                    break

    def show_history_detail(self, record):
        """显示历史记录详情"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"历史记录详情 - {record['time']}")
        detail_window.geometry("800x600")
        
        # 配置网格布局
        detail_window.grid_rowconfigure(1, weight=1)
        detail_window.grid_columnconfigure(0, weight=1)
        
        # 信息栏
        info_frame = tk.Frame(detail_window)
        info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        tk.Label(info_frame, text=f"时间: {record['time']}", anchor="w").pack(fill=tk.X)
        tk.Label(info_frame, text=f"图片路径: {record['image']}", anchor="w").pack(fill=tk.X)
        
        # 文本区域
        text_frame = tk.Frame(detail_window)
        text_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        text_area = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD, 
            font=(self.current_font_family, self.current_font_size)
        )
        text_area.pack(fill=tk.BOTH, expand=True)
        
        # 加载完整文本
        full_text = record.get("full_text", record.get("text", record.get("display_text", "")))
        text_area.insert(tk.END, full_text)
        text_area.config(state=tk.DISABLED)
        
        # 底部按钮
        bottom_frame = tk.Frame(detail_window)
        bottom_frame.grid(row=2, column=0, sticky="e", padx=10, pady=5)
        
        tk.Button(bottom_frame, text="复制文本", 
                 command=lambda: self.copy_to_clipboard(text_area),
                 bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
        
        # 如果图片存在，添加查看图片按钮
        if os.path.exists(record["image"]):
            tk.Button(bottom_frame, text="查看原图", 
                     command=lambda: self.display_history_image(record["image"]),
                     bg="#FF9800", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(bottom_frame, text="关闭", 
                 command=detail_window.destroy,
                 bg="#9E9E9E", fg="white").pack(side=tk.RIGHT, padx=5)

    def display_history_image(self, image_path):
        """显示历史记录中的图片"""
        try:
            image = Image.open(image_path)
            # 调整图片大小以适应屏幕
            width, height = image.size
            max_size = 800
            if width > max_size or height > max_size:
                ratio = min(max_size/width, max_size/height)
                image = image.resize((int(width*ratio), int(height*ratio)), Image.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            
            # 创建图片窗口
            image_window = tk.Toplevel(self.root)
            image_window.title(f"图片预览 - {os.path.basename(image_path)}")
            
            # 显示图片
            label = tk.Label(image_window, image=photo)
            label.image = photo  # 保持引用
            label.pack()
            
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片: {str(e)}")

    def clear_history(self):
        """清空历史记录"""
        if messagebox.askyesno("确认", "确定要清空所有历史记录吗？"):
            self.history_data = []
            self.save_history()
            # 刷新树形视图
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            messagebox.showinfo("成功", "历史记录已清空")

    def export_all_history(self):
        """导出全部历史记录"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="导出历史记录"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for record in self.history_data:
                        f.write(f"时间: {record['time']}\n")
                        f.write(f"图片路径: {record['image']}\n")
                        f.write("识别内容:\n")
                        f.write(record.get("full_text", record.get("text", record.get("display_text", ""))) + "\n")
                        f.write("-" * 50 + "\n\n")
                messagebox.showinfo("导出成功", f"历史记录已保存到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("导出失败", f"无法保存文件: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()