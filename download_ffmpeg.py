import os
import sys
import urllib.request
import zipfile

FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
ZIP_NAME = "ffmpeg-release-essentials.zip"
TARGET_EXE = "ffmpeg.exe"

def download_with_progress(url, filename):
    def show_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(100, downloaded * 100 // total_size)
        print(f"\r下载进度: {percent}%", end="")
    print(f"正在下载: {url}")
    try:
        urllib.request.urlretrieve(url, filename, show_progress)
        print("\n下载完成!")
        return True
    except Exception as e:
        print(f"\n下载失败: {e}")
        return False

def extract_ffmpeg_exe(zip_path, target_dir):
    print("正在解压 ffmpeg.exe ...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if member.endswith('/ffmpeg.exe'):
                    zip_ref.extract(member, target_dir)
                    src = os.path.join(target_dir, member)
                    dst = os.path.join(target_dir, TARGET_EXE)
                    os.replace(src, dst)
                    print(f"已提取: {dst}")
                    return True
        print("未找到 ffmpeg.exe！请手动解压。")
        return False
    except Exception as e:
        print(f"解压失败: {e}")
        return False

def main():
    if os.path.exists(TARGET_EXE):
        print(f"{TARGET_EXE} 已存在，无需重复下载。")
        sys.exit(0)
    if not download_with_progress(FFMPEG_URL, ZIP_NAME):
        print("\nDownload failed. Please check your network and try again.")
        sys.exit(1)
    success = extract_ffmpeg_exe(ZIP_NAME, os.getcwd())
    os.remove(ZIP_NAME)
    if success:
        print("ffmpeg.exe 下载并解压完成！")
        sys.exit(0)
    else:
        print("Download or extraction failed. Please restart this script. If the problem persists, manually download ffmpeg.exe and place it in the project root directory.")
        sys.exit(1)

if __name__ == "__main__":
    main() 