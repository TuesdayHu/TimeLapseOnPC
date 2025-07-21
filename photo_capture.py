import cv2
import time
import os

def get_supported_resolutions(cap, log_func=print):
    """
    获取摄像头支持的所有分辨率。
    参数：
        cap: cv2.VideoCapture对象
        log_func: 日志输出函数，默认为print
    返回：
        支持的分辨率列表，如[(1280, 720), ...]
    """
    resolutions = []
    # 常见分辨率列表
    common_resolutions = [
        (640, 480),
        (800, 600),
        (1024, 768),
        (1280, 720),
        (1280, 800),
        (1366, 768),
        (1920, 1080),
        (2560, 1440),
        (3840, 2160)
    ]
    log_func("正在测试摄像头支持的分辨率...")
    for width, height in common_resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if actual_width == width and actual_height == height:
            resolutions.append((width, height))
            log_func(f"支持的分辨率: {width}x{height}")
    return resolutions

def calc_timestamp_params(image_shape, timestamp):
    """
    计算时间戳绘制所需的字体、位置、底框等参数。
    参数：
        image_shape: 图像的shape (高, 宽, 通道)
        timestamp: 时间戳字符串
    返回：
        包含字体、缩放、位置、底框等信息的字典
    """
    h, w = image_shape[:2]
    text = timestamp
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2.0
    thickness = 3
    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    max_h = h // 10
    while (text_h > max_h) and font_scale > 0.1:
        font_scale -= 0.1
        (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    x = 5
    y = h - 5
    rect_w = text_w + 16
    rect_h = text_h + 16
    rect = (x-8, y-text_h-8, rect_w, rect_h)
    return {
        'font': font,
        'font_scale': font_scale,
        'thickness': thickness,
        'text_pos': (x, y),
        'rect': rect
    }

def add_timestamp_to_image(image, timestamp, params):
    """
    在图片左下角添加时间戳。
    参数：
        image: 原始图像
        timestamp: 时间戳字符串
        params: calc_timestamp_params返回的参数字典
    返回：
        添加了时间戳的新图像
    """
    font = params['font']
    font_scale = params['font_scale']
    thickness = params['thickness']
    x, y = params['text_pos']
    rect_x, rect_y, rect_w, rect_h = params['rect']
    overlay = image.copy()
    cv2.rectangle(overlay, (rect_x, rect_y), (rect_x+rect_w, rect_y+rect_h), (0,0,0), -1)
    alpha = 0.5
    image = cv2.addWeighted(overlay, alpha, image, 1-alpha, 0)
    cv2.putText(image, timestamp, (x, y), font, font_scale, (255,255,255), thickness, cv2.LINE_AA)
    return image

def capture_timelapse(a, b, output_dir, log_func=print, stop_event=None, progress_callback=None, resolution=None, add_timestamp=True):
    """
    执行延时拍摄，保存带时间戳的图片。
    参数：
        a: 拍摄间隔（秒）
        b: 拍摄次数
        log_func: 日志输出函数，默认为print
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    max_retries = 3
    retry_delay = 2  # seconds
    cap = None
    for retry in range(max_retries):
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
        supported_resolutions = get_supported_resolutions(cap, log_func=log_func)
        if resolution:
        log_func(f"\n尝试设置分辨率: {resolution[0]}x{resolution[1]}")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
    else:
        if not supported_resolutions:
            log_func("未检测到可用分辨率，程序退出")
            cap.release()
            return
        target_resolution = (1280, 720)
        best_resolution = min(supported_resolutions, 
                            key=lambda x: abs(x[0] - target_resolution[0]) + abs(x[1] - target_resolution[1]))
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
    # 计算一次时间戳参数
    sample_timestamp = time.strftime("%Y-%m-%d_%H:%M:%S")
    params = calc_timestamp_params(frame.shape, sample_timestamp)
    try:
        for i in range(b):
            if stop_event and stop_event.is_set():
                log_func("拍摄已停止")
                break

            ret, frame = cap.read()
            if not ret:
                log_func(f"Error: Could not capture frame {i+1}")
                continue

            if add_timestamp:
                timestamp = time.strftime("%Y-%m-%d_%H:%M:%S")
                frame = add_timestamp_to_image(frame, timestamp, params)
                filename = os.path.join(output_dir, f"photo_{timestamp.replace(':','-')}_{i+1}.jpg")
            else:
                timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
                filename = os.path.join(output_dir, f"photo_{timestamp}_{i+1}.jpg")

            cv2.imwrite(filename, frame)
            log_func(f"Saved photo {i+1}/{b} to {filename}")

            if progress_callback:
                progress_callback(i + 1)

            if i < b - 1:
                if stop_event:
                    # 使用事件的wait方法替代sleep，以便能被立即中断
                    if stop_event.wait(a):
                        log_func("拍摄已停止")
                        break # 如果事件被设置，则退出循环
                else:
                    time.sleep(a)
    finally:
        cap.release()
        log_func("Timelapse capture completed!")

if __name__ == "__main__":
    try:
        a = float(input("请输入拍摄间隔时间（秒）："))
        b = int(input("请输入拍摄次数："))
        if a <= 0 or b <= 0:
            print("请输入大于0的整数！")
        else:
            capture_timelapse(a, b)
    except ValueError:
        print("请输入有效的整数！")
