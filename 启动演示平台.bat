@echo off
cd /d "%~dp0"
echo 赣鄱智轨演示平台启动中... 浏览器访问 http://127.0.0.1:8000/index.html
python demo.py --no-browser
pause
