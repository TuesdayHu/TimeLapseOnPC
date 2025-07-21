import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import threading
import time
import os
import cv2
from photo_capture import capture_timelapse, get_supported_resolutions
from photo2video import create_timelapse  # 新增导入

class TimelapseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("延时摄影控制台")
        self.root.geometry("700x320")
        self.root.resizable(False, False)

        # 创建Notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        # --- 第一个tab：定时拍照 ---
        self.tab_capture = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_capture, text="定时拍照")
        self.init_capture_tab(self.tab_capture)

        # --- 第二个tab：照片转视频 ---
        self.tab_video = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_video, text="照片转视频")
        self.init_video_tab(self.tab_video)

    def init_capture_tab(self, parent):
        # 默认保存路径
        self.save_dir = os.path.join(os.getcwd(), "PhotoOutput")
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        vcmd = (self.root.register(self.validate_positive_float), '%P')
        # 输入区
        input_frame = ttk.Frame(parent)
        input_frame.pack(pady=(20, 0), padx=10, fill='x')
        self.label_interval = ttk.Label(input_frame, text="拍摄间隔时间：")
        self.label_interval.pack(side='left')
        self.entry_interval = ttk.Entry(input_frame, width=8, validate='key', validatecommand=vcmd)
        self.entry_interval.pack(side='left', padx=(5, 0))
        self.entry_interval.insert(0, '1')
        self.combo_interval_unit = ttk.Combobox(input_frame, state='readonly', width=5)
        self.combo_interval_unit['values'] = ['分钟', '秒']
        self.combo_interval_unit.set('秒')
        self.combo_interval_unit.pack(side='left', padx=(5, 20))
        self.label_duration = ttk.Label(input_frame, text="拍摄时长：")
        self.label_duration.pack(side='left')
        self.entry_duration = ttk.Entry(input_frame, width=8, validate='key', validatecommand=vcmd)
        self.entry_duration.pack(side='left', padx=5)
        self.entry_duration.insert(0, '1')
        self.combo_duration_unit = ttk.Combobox(input_frame, state='readonly', width=5)
        self.combo_duration_unit['values'] = ['分钟', '小时']
        self.combo_duration_unit.set('小时')
        self.combo_duration_unit.pack(side='left', padx=(0, 5))
        self.add_timestamp_var = tk.IntVar(value=1)
        self.check_add_timestamp = ttk.Checkbutton(input_frame, text="添加时间戳", variable=self.add_timestamp_var)
        self.check_add_timestamp.pack(side='left', padx=(10, 0))
        # 分辨率和保存路径区
        action_frame = ttk.Frame(parent)
        action_frame.pack(pady=(10, 0), padx=10, fill='x')
        self.label_res = ttk.Label(action_frame, text="分辨率选择：")
        self.label_res.pack(side='left')
        self.combo_res = ttk.Combobox(action_frame, state='readonly', width=12)
        self.combo_res.pack(side='left', padx=(5, 20))
        self.combo_res['values'] = ["摄像头分辨率检测中..."]
        self.combo_res.set("摄像头分辨率检测中...")
        self.combo_res.config(state='disabled')
        self.label_save = ttk.Label(action_frame, text="照片保存路径：")
        self.label_save.pack(side='left')
        self.entry_save_path = ttk.Entry(action_frame, width=40, state='readonly')
        self.entry_save_path.pack(side='left', padx=(5, 0))
        self.entry_save_path.config(state='normal')
        self.entry_save_path.delete(0, tk.END)
        self.entry_save_path.insert(0, self.save_dir)
        self.entry_save_path.config(state='readonly')
        self.btn_choose_path = ttk.Button(action_frame, text="选择", command=self.choose_save_path)
        self.btn_choose_path.pack(side='left', padx=(5, 0))
        # 开始拍摄按钮单独一行
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=(8, 0), padx=10, fill='x')
        self.start_button = ttk.Button(btn_frame, text="开始拍摄", command=self.start_capture)
        self.start_button.pack(fill='x', expand=True)
        # 状态显示区
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill='both', padx=10, pady=(10, 0), expand=True)
        self.status_text = tk.Text(status_frame, height=3, state='disabled', wrap='none')
        self.status_text.pack(side='left', fill='both', expand=True)
        self.scrollbar = ttk.Scrollbar(status_frame, orient='vertical', command=self.status_text.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.status_text['yscrollcommand'] = self.scrollbar.set
        # 进度条区
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill='x', padx=10, pady=(5, 10))
        self.progress = ttk.Progressbar(progress_frame, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(fill='x', expand=True)
        # 标记是否已检测分辨率
        self.resolutions = []
        self.res_checked = False
        self.stop_flag = threading.Event()
        self.current_total = 0
        threading.Thread(target=self.detect_resolutions, daemon=True).start()

    def init_video_tab(self, parent):
        # 照片转视频tab内容
        frame = ttk.Frame(parent)
        frame.pack(pady=20, padx=10, fill='x')
        # 输入目录（改为读取路径，默认与照片保存路径同步）
        ttk.Label(frame, text="照片读取路径：").pack(side='left')
        self.video_input_dir = tk.StringVar(value=getattr(self, 'save_dir', os.path.join(os.getcwd(), "PhotoOutput")))
        self.entry_video_input = ttk.Entry(frame, textvariable=self.video_input_dir, width=40)
        self.entry_video_input.pack(side='left', padx=(5, 0))
        ttk.Button(frame, text="选择", command=self.choose_video_input_dir).pack(side='left', padx=(5, 20))
        # 输出文件名
        ttk.Label(frame, text="输出视频名：").pack(side='left')
        self.video_output_name = tk.StringVar(value="timelapse_output")
        self.entry_video_output = ttk.Entry(frame, textvariable=self.video_output_name, width=18)
        self.entry_video_output.pack(side='left', padx=(5, 0))
        # 新增：视频保存路径
        video_output_path_frame = ttk.Frame(parent)
        video_output_path_frame.pack(pady=(5, 0), padx=10, fill='x')
        ttk.Label(video_output_path_frame, text="视频保存路径：").pack(side='left')
        self.video_output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "VideoOutput"))
        self.entry_video_output_dir = ttk.Entry(video_output_path_frame, textvariable=self.video_output_dir, width=40, state='readonly')
        self.entry_video_output_dir.pack(side='left', padx=(5, 0))
        self.btn_choose_video_output_dir = ttk.Button(video_output_path_frame, text="选择", command=self.choose_video_output_dir)
        self.btn_choose_video_output_dir.pack(side='left', padx=(5, 0))
        # 帧率
        frame2 = ttk.Frame(parent)
        frame2.pack(pady=(0, 0), padx=10, fill='x')
        ttk.Label(frame2, text="帧率：").pack(side='left')
        self.video_fps = tk.StringVar(value="24")
        self.entry_video_fps = ttk.Entry(frame2, textvariable=self.video_fps, width=5)
        self.entry_video_fps.pack(side='left', padx=(5, 0))
        # 开始按钮
        btn_video_frame = ttk.Frame(parent)
        btn_video_frame.pack(pady=(8, 0), padx=10, fill='x')
        self.btn_video_start = ttk.Button(btn_video_frame, text="开始生成视频", command=self.start_video_generate)
        self.btn_video_start.pack(fill='x', expand=True)
        # 日志区
        self.video_status_text = tk.Text(parent, height=5, state='disabled', wrap='none')
        self.video_status_text.pack(fill='both', padx=10, pady=(10, 0), expand=True)

    def choose_save_path(self):
        path = filedialog.askdirectory(initialdir=self.save_dir, title="选择照片保存文件夹")
        if path:
            self.save_dir = path
            self.entry_save_path.config(state='normal')
            self.entry_save_path.delete(0, tk.END)
            self.entry_save_path.insert(0, self.save_dir)
            self.entry_save_path.config(state='readonly')
            # 同步更新视频读取路径
            self.video_input_dir.set(self.save_dir)

    def choose_video_input_dir(self):
        path = filedialog.askdirectory(title="选择照片读取路径")
        if path:
            self.video_input_dir.set(path)
    def choose_video_output_dir(self):
        path = filedialog.askdirectory(title="选择视频保存路径")
        if path:
            self.video_output_dir.set(path)

    def validate_positive_float(self, value):
        if value == '':
            return True
        if value == '.' or value == '0.':
            return True
        try:
            v = float(value)
            return v > 0
        except ValueError:
            return False

    def start_video_generate(self):
        input_dir = self.video_input_dir.get().strip()
        output_name = self.video_output_name.get().strip()
        fps_str = self.video_fps.get().strip()
        output_dir = self.video_output_dir.get().strip()
        if not input_dir or not os.path.exists(input_dir):
            self.append_video_status("请选择有效的照片读取路径！\n")
            return
        if not output_name:
            output_name = "timelapse_output"
        try:
            fps = int(fps_str)
            if fps <= 0:
                raise ValueError
        except ValueError:
            self.append_video_status("帧率必须为正整数！\n")
            return
        if not output_dir:
            output_dir = os.path.join(os.getcwd(), "VideoOutput")
        output_file = os.path.join(output_dir, f"{output_name}.mp4")
        self.btn_video_start.config(state='disabled')
        self.append_video_status(f"开始生成视频: {output_file}\n")
        threading.Thread(target=self.run_create_timelapse, args=(input_dir, output_file, fps), daemon=True).start()

    def run_create_timelapse(self, input_dir, output_file, fps):
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 重定向print输出到GUI
        class TextRedirector:
            def __init__(self, widget):
                self.widget = widget
            def write(self, str_):
                self.widget.root.after(0, self.widget.append_video_status, str_)
            def flush(self):
                pass
        
        import sys
        original_stdout = sys.stdout
        sys.stdout = TextRedirector(self)

        try:
            create_timelapse(input_dir, output_file, fps)
        except Exception as e:
            self.append_video_status(f"视频生成失败: {e}\n")
        finally:
            sys.stdout = original_stdout
            self.root.after(0, self.on_video_generate_complete)

    def append_video_status(self, msg):
        self.video_status_text.config(state='normal')
        self.video_status_text.insert('end', msg)
        self.video_status_text.see('end')
        self.video_status_text.config(state='disabled')

    def on_video_generate_complete(self):
        self.btn_video_start.config(state='normal')
        self.append_video_status("视频生成完成!\n")

    def start_capture(self):
        """
        读取用户输入，校验参数，自动计算拍摄张数，启动拍摄线程。
        """
        if not self.res_checked:
            self.append_status("分辨率未检测完成，无法开始拍摄。\n")
            return
        interval = self.entry_interval.get()
        interval_unit = self.combo_interval_unit.get()
        duration = self.entry_duration.get()
        duration_unit = self.combo_duration_unit.get()
        add_timestamp = self.add_timestamp_var.get() == 1
        try:
            interval = float(interval)
            duration = float(duration)
            if interval <= 0 or duration <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("输入错误", "请输入大于0的数字！")
            return
        # 统一间隔为秒
        if interval_unit == '分钟':
            interval_sec = interval * 60
        else:
            interval_sec = interval
        # 计算总拍摄张数
        if duration_unit == '小时':
            total_seconds = duration * 3600
        else:
            total_seconds = duration * 60
        count = int(total_seconds // interval_sec)
        if count < 1:
            messagebox.showerror("输入错误", "拍摄时长与间隔设置下，拍摄次数不足1次！")
            return
        # 选择分辨率
        selected_res = self.combo_res.get()
        if selected_res not in [f"{w}x{h}" for w, h in self.resolutions]:
            res = None  # 自动选择
        else:
            w, h = map(int, selected_res.split('x'))
            res = (w, h)
        self.append_status(f"准备开始拍摄：间隔{interval}{interval_unit}，时长{duration}{duration_unit}，共{count}次。\n")
        self.progress['value'] = 0
        self.progress['maximum'] = count
        self.current_total = count
        self.stop_flag.clear()
        self.start_button.config(text='停止拍摄', command=self.stop_capture, state='normal')
        threading.Thread(target=self.run_capture_timelapse, args=(interval_sec, count, res, add_timestamp), daemon=True).start()

    def stop_capture(self):
        """
        停止拍摄，设置停止标志。
        """
        self.stop_flag.set()
        self.append_status("用户已请求停止拍摄...\n")
        self.start_button.config(state='disabled')

    def detect_resolutions(self):
        """
        检测摄像头支持的分辨率，填充下拉框。
        """
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.resolutions = []
            self.combo_res['values'] = ["摄像头初始化失败"]
            self.combo_res.set("摄像头初始化失败")
            self.combo_res.config(state='disabled')
            self.append_status("无法打开摄像头，无法检测分辨率。\n")
            return
        def gui_log(msg):
            self.append_status(msg + '\n')
        resolutions = get_supported_resolutions(cap, log_func=gui_log)
        cap.release()
        if not resolutions:
            self.resolutions = []
            self.combo_res['values'] = ["摄像头初始化失败"]
            self.combo_res.set("摄像头初始化失败")
            self.combo_res.config(state='disabled')
            self.append_status("未检测到可用分辨率。\n")
            return
        self.resolutions = resolutions
        self.combo_res['values'] = [f"{w}x{h}" for w, h in resolutions]
        self.combo_res.set(self.combo_res['values'][-1])
        self.combo_res.config(state='readonly')
        self.res_checked = True
        self.append_status("分辨率检测完成，请选择分辨率或直接开始拍摄。\n")

    def run_capture_timelapse(self, interval, count, res, add_timestamp):
        """
        启动延时拍摄，支持分辨率选择。
        参数：
            interval: 拍摄间隔（秒）
            count: 拍摄次数
            res: 用户选择的分辨率，None为自动
            add_timestamp: 是否添加时间戳
        """
        def gui_log(msg):
            self.append_status(msg + '\n')

        def update_progress(i):
            self.progress['value'] = i
            self.root.update_idletasks()

        try:
            # 直接调用重构后的 capture_timelapse
            capture_timelapse(
                interval,
                count,
                self.save_dir,
                log_func=gui_log,
                stop_event=self.stop_flag,
                progress_callback=update_progress,
                resolution=res,
                add_timestamp=add_timestamp
            )
        except Exception as e:
            self.append_status(f"拍摄出错: {e}")
        finally:
            # 不论成功失败，都恢复按钮状态
            self.root.after(0, self.on_capture_complete)
                        frame_to_save = add_timestamp_to_image(frame, timestamp, params)
                    else:
                        frame_to_save = frame
                    filename = os.path.join(output_dir, f"photo_{timestamp.replace(':','-')}_{i+1}.jpg")
                    cv2.imwrite(filename, frame_to_save)
                    log_func(f"Saved photo {i+1}/{b} to {filename}")
                    update_progress(i+1)
                    if i < b - 1:
                        time.sleep(a)
            finally:
                cap.release()
                log_func("Timelapse capture completed!")
        # 选择分辨率逻辑
        if res is not None:
            patched_capture_timelapse(interval, count, log_func=gui_log)
        else:
            # 自动分辨率，需在外部加进度条
            def gui_capture_timelapse(a, b, log_func=print):
                output_dir = self.save_dir
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                max_retries = 3
                retry_delay = 2
                cap = None
                for retry in range(max_retries):
                    if self.stop_flag.is_set():
                        log_func("已停止拍摄")
                        return
                    log_func(f"尝试初始化摄像头 (尝试 {retry + 1}/{max_retries})...")
                    cap = cv2.VideoCapture(0)
                    if not cap.isOpened():
                        log_func("无法打开摄像头")
                        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                        if retry < max_retries - 1:
                            log_func(f"等待 {retry_delay} 秒后重试...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            log_func("达到最大重试次数，程序退出")
                            return
                    from photo_capture import get_supported_resolutions
                    supported_resolutions = get_supported_resolutions(cap, log_func=log_func)
                    if not supported_resolutions:
                        log_func("未检测到可用分辨率，程序退出")
                        cap.release()
                        return
                    target_resolution = (1280, 720)
                    best_resolution = min(supported_resolutions, key=lambda x: abs(x[0] - target_resolution[0]) + abs(x[1] - target_resolution[1]))
                    log_func(f"\n选择的分辨率: {best_resolution[0]}x{best_resolution[1]}")
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, best_resolution[0])
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, best_resolution[1])
                    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    log_func(f"当前摄像头分辨率: {width}x{height}")
                    ret, frame = cap.read()
                    if not ret:
                        log_func("摄像头初始化成功，但无法读取画面")
                        cap.release()
                        if retry < max_retries - 1:
                            log_func(f"等待 {retry_delay} 秒后重试...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            log_func("达到最大重试次数，程序退出")
                            return
                    log_func("摄像头初始化成功！")
                    break
                else:
                    log_func("摄像头初始化失败，程序退出")
                    return
                from photo_capture import calc_timestamp_params, add_timestamp_to_image
                sample_timestamp = time.strftime("%Y-%m-%d_%H:%M:%S")
                params = calc_timestamp_params(frame.shape, sample_timestamp)
                try:
                    for i in range(b):
                        if self.stop_flag.is_set():
                            log_func("已停止拍摄")
                            break
                        ret, frame = cap.read()
                        if not ret:
                            log_func(f"Error: Could not capture frame {i+1}")
                            continue
                        timestamp = time.strftime("%Y-%m-%d_%H:%M:%S")
                        if add_timestamp:
                            frame_to_save = add_timestamp_to_image(frame, timestamp, params)
                        else:
                            frame_to_save = frame
                        filename = os.path.join(output_dir, f"photo_{timestamp.replace(':','-')}_{i+1}.jpg")
                        cv2.imwrite(filename, frame_to_save)
                        log_func(f"Saved photo {i+1}/{b} to {filename}")
                        update_progress(i+1)
                        if i < b - 1:
                            time.sleep(a)
                finally:
                    cap.release()
                    log_func("Timelapse capture completed!")
            gui_capture_timelapse(interval, count, log_func=gui_log)
        # 拍摄结束后恢复按钮
        self.start_button.config(text='开始拍摄', command=self.start_capture, state='normal')
        self.stop_flag.clear()

    def append_status(self, msg):
        """
        向状态框追加日志信息。
        参数：
            msg: 日志字符串
        """
        self.status_text.config(state='normal')
        self.status_text.insert('end', msg)
        self.status_text.see('end')
        self.status_text.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = TimelapseApp(root)
    root.mainloop()