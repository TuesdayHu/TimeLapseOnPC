# TimeLapseOnPC

一个简单易用的延时摄影工具，能够通过电脑摄像头定时拍摄照片并合成为视频。
A simple and easy-to-use timelapse tool that captures photos at intervals using your computer's camera and converts them into videos.

## 功能特点 | Features
- 图形化界面操作，简单直观 | Graphical user interface for easy operation
- 支持自定义拍摄间隔和时长 | Customizable capture interval and duration
- 可选择摄像头分辨率 | Selectable camera resolution
- 照片自动添加时间戳 | Automatic timestamp on photos
- 支持将拍摄的照片合成为视频 | Convert captured photos into video
- 可自定义视频帧率和输出路径 | Customizable video frame rate and output path

## 安装步骤 | Installation Steps
1. 确保已安装Python 3.x环境 | Ensure Python 3.x environment is installed
2. 克隆或下载本项目到本地 | Clone or download this project to your local machine
3. 安装依赖包： | Install dependencies:
```bash
pip install -r requirements.txt
```

## 使用方法 | Usage
1. 运行程序： | Run the program:
   双击`run.bat`文件或在命令行中执行： | Double-click `run.bat` or execute in command line:
   ```bash
   python photo_capture_gui.py
   ```

2. 定时拍照 | Timelapse Capture:
   - 在"定时拍照"标签页中，设置拍摄间隔（秒/分钟）和拍摄时长（分钟/小时） | In the "定时拍照" (Timelapse Capture) tab, set capture interval (seconds/minutes) and duration (minutes/hours)
   - 选择是否添加时间戳 | Choose whether to add timestamp
   - 选择摄像头分辨率 | Select camera resolution
   - 设置照片保存路径 | Set photo save path
   - 点击"开始拍摄"按钮 | Click "开始拍摄" (Start Capture) button

3. 照片转视频 | Photo to Video:
   - 在"照片转视频"标签页中，选择照片读取路径（默认为照片保存路径） | In the "照片转视频" (Photo to Video) tab, select photo input path (default is photo save path)
   - 设置输出视频名称和保存路径 | Set output video name and save path
   - 设置视频帧率（默认为24） | Set video frame rate (default is 24)
   - 点击"开始生成视频"按钮 | Click "开始生成视频" (Start Video Generation) button

## 项目结构 | Project Structure
```
TimeLapseOnPC/
├── VideoOutput/          # 视频输出目录 | Video output directory
├── photo2video.py        # 照片转视频功能模块 | Photo to video conversion module
├── photo_capture.py      # 拍照功能核心模块 | Core photo capture module
├── photo_capture_gui.py  # GUI界面模块 | GUI interface module
├── requirements.txt      # 项目依赖 | Project dependencies
├── run.bat               # 程序启动脚本 | Program startup script
├── LICENSE               # 许可证文件 | License file
└── README.md             # 项目说明文档 | Project documentation
```

## 依赖项 | Dependencies
- opencv-python==4.8.1.78

## 依赖说明

本项目依赖 ffmpeg 进行视频转码。请前往 [ffmpeg 官网](https://ffmpeg.org/download.html) 或 [Gyan.dev Windows builds](https://www.gyan.dev/ffmpeg/builds/) 下载 Windows 版本的 ffmpeg。

- 下载后，将 `ffmpeg.exe` 放到项目根目录下（与 photo2video.py 同级）。
- 如果未检测到本地 ffmpeg.exe，程序会尝试使用系统环境变量中的 ffmpeg。
- 建议不要将 ffmpeg.exe 上传到 git 仓库，请在 `.gitignore` 中添加 `ffmpeg.exe`。

## 注意事项 | Notes
- 确保电脑已连接摄像头并授予访问权限 | Ensure the computer has a connected camera and grant access permissions
- 拍摄过程中请勿关闭程序窗口 | Do not close the program window during capture
- 生成视频可能需要一定时间，取决于照片数量和电脑性能 | Video generation may take time depending on the number of photos and computer performance
- 建议使用较高配置的电脑以获得更好的性能体验 | A higher configuration computer is recommended for better performance

## 许可证 | License
本项目使用MIT许可证，详情请见LICENSE文件。 | This project uses the MIT License. See the LICENSE file for details.
