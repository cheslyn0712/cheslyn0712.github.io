@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo 检查 Ruby...
where ruby >nul 2>&1
if errorlevel 1 (
    echo.
    echo [错误] 未检测到 Ruby。请先安装 Ruby：
    echo    winget install --id=RubyInstallerTeam.RubyWithDevKit.3.4 -e
    echo.
    echo 安装完成后，请关闭并重新打开终端，再运行此脚本。
    pause
    exit /b 1
)

echo Ruby 版本:
ruby --version
echo.

echo 安装依赖...
bundle install
if errorlevel 1 (
    echo [错误] bundle install 失败
    pause
    exit /b 1
)

echo.
echo 启动 Jekyll 服务器...
echo 在浏览器中打开: http://127.0.0.1:4000
echo 按 Ctrl+C 可停止服务器
echo.
bundle exec jekyll serve --livereload
