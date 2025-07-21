import os
import cv2
import re
from datetime import datetime
import subprocess
import sys

def get_timestamp_from_filename(filename):
    # Extract timestamp and index from filename
    # Support format: photo_2025-07-04_23-38-59_168.jpg
    match = re.match(r'photo_(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})_(\d+)', filename)
    if match:
        year, month, day, hour, minute, second, index = match.groups()
        timestamp = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        return timestamp, int(index)
    return None, None

def create_timelapse(input_dir, output_file, fps=24):
    try:
        # Get all image files
        image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if not image_files:
            print("No image files found in the input directory!")
            return
        
        # Sort files by timestamp and index
        sorted_files = []
        for filename in image_files:
            timestamp, index = get_timestamp_from_filename(filename)
            if timestamp:
                sorted_files.append((timestamp, index, filename))
        
        if not sorted_files:
            # 如果没有任何符合timestamp格式的图片，则按文件名升序排序
            print("未找到符合时间戳格式的图片，按文件名排序处理。")
            image_files.sort()  # 文件名升序
            sorted_files = [(None, 0, filename) for filename in image_files]
        else:
            sorted_files.sort(key=lambda x: (x[0], x[1]))
        
        if not sorted_files:
            print("No valid image files found!")
            return
        
        # Get the first image to determine video dimensions
        first_image_path = os.path.join(input_dir, sorted_files[0][2])
        first_image = cv2.imread(first_image_path)
        if first_image is None:
            print(f"Failed to read the first image: {first_image_path}")
            return
        
        height, width, _ = first_image.shape

        # Directly use ffmpeg to create H.264 video
        # 优先使用项目根目录下的 ffmpeg.exe
        local_ffmpeg = os.path.join(os.path.dirname(sys.argv[0]), 'ffmpeg.exe')
        ffmpeg_path = local_ffmpeg if os.path.exists(local_ffmpeg) else 'ffmpeg'

        # Create a temporary file list for ffmpeg
        list_file_path = os.path.join(input_dir, 'filelist.txt')
        with open(list_file_path, 'w') as f:
            for filename in sorted(image_files):
                f.write(f"file '{os.path.join(input_dir, filename)}'\n")

        cmd = [
            ffmpeg_path,
            '-y',
            '-r', str(fps),
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file_path,
            '-vcodec', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-s', f'{width}x{height}',
            output_file
        ]

        print(f"\n正在用 ffmpeg 生成 H.264 mp4: {output_file}")
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"H.264 视频已保存为: {output_file}")

        # Clean up the temporary file list
        os.remove(list_file_path)

    except subprocess.CalledProcessError as e:
        print(f"ffmpeg 执行失败: {e.stderr}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Get input directory from user
    while True:
        input_directory = input("请输入照片目录的完整路径: ").strip()
        if os.path.exists(input_directory):
            break
        print("目录不存在，请重新输入！")
    
    # Get output filename from user (without extension)
    output_name = input("请输入输出视频文件名（不包含后缀）: ").strip()
    if not output_name:
        output_name = "timelapse_output"
    output_video = f"{output_name}.mp4"  # Changed to .mp4 extension
    
    # Get FPS from user
    while True:
        try:
            fps = int(input("请输入视频帧率（默认24）: ").strip() or "24")
            if fps > 0:
                break
            print("帧率必须大于0，请重新输入！")
        except ValueError:
            print("请输入有效的数字！")
    
    create_timelapse(input_directory, output_video, fps)