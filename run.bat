@echo off
if exist ffmpeg.exe (
    echo ffmpeg.exe found. Starting GUI...
    python photo_capture_gui.py
) else (
    echo Downloading ffmpeg for video transcoding, please wait...
    python download_ffmpeg.py
    if errorlevel 1 (
        echo.
        echo Failed to download ffmpeg.exe. Please check your network and try again.
        echo If this problem persists, please manually download ffmpeg.exe and place it in the project root directory.
        pause
        exit /b 1
    )
    echo.
    echo ffmpeg download completed. Starting GUI...
    python photo_capture_gui.py
)