@echo off
setlocal enabledelayedexpansion

REM 设置颜色代码
set "GREEN=[32m"
set "RED=[31m"
set "YELLOW=[33m"
set "RESET=[0m"

REM 设置Docker配置
set "DOCKER_USERNAME=inkeds"
set "IMAGE_NAME=frp-manager-api"
set "VERSION=1.0.0"

echo %GREEN%开始构建和推送流程...%RESET%

REM 检查Docker是否已安装
docker --version > nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%错误: Docker未安装或未运行%RESET%
    exit /b 1
)

REM 检查是否已登录Docker Hub
docker info | findstr "Username" > nul
if %errorlevel% neq 0 (
    echo %YELLOW%请登录Docker Hub...%RESET%
    docker login
    if !errorlevel! neq 0 (
        echo %RED%错误: Docker Hub登录失败%RESET%
        exit /b 1
    )
)

REM 清理旧的构建缓存
echo %YELLOW%清理Docker构建缓存...%RESET%
docker builder prune -f

REM 构建基本镜像
echo %GREEN%开始构建镜像 %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%%RESET%
docker build -t %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION% .
if %errorlevel% neq 0 (
    echo %RED%错误: 镜像构建失败%RESET%
    exit /b 1
)

REM 标记latest版本
docker tag %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION% %DOCKER_USERNAME%/%IMAGE_NAME%:latest

REM 推送到Docker Hub
echo %YELLOW%推送镜像到Docker Hub...%RESET%
docker push %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%
docker push %DOCKER_USERNAME%/%IMAGE_NAME%:latest

if %errorlevel% neq 0 (
    echo %RED%错误: 推送到Docker Hub失败%RESET%
    exit /b 1
)

echo %GREEN%镜像已成功推送到Docker Hub！%RESET%
echo %GREEN%镜像地址：%RESET%
echo %YELLOW%- docker pull %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%%RESET%
echo %YELLOW%- docker pull %DOCKER_USERNAME%/%IMAGE_NAME%:latest%RESET%

REM 询问是否推送到GitHub Container Registry
set /p PUSH_TO_GITHUB="是否推送到GitHub Container Registry? (y/n): "
if /i "%PUSH_TO_GITHUB%"=="y" (
    REM 设置GitHub相关变量
    set /p GITHUB_USERNAME="请输入GitHub用户名: "
    set /p GITHUB_TOKEN="请输入GitHub Personal Access Token: "

    REM 登录到GitHub Container Registry
    echo %GITHUB_TOKEN% | docker login ghcr.io -u %GITHUB_USERNAME% --password-stdin
    if %errorlevel% neq 0 (
        echo %RED%错误: GitHub Container Registry登录失败%RESET%
        exit /b 1
    )

    REM 标记GitHub Container Registry镜像
    docker tag %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION% ghcr.io/%GITHUB_USERNAME%/%IMAGE_NAME%:%VERSION%
    docker tag %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION% ghcr.io/%GITHUB_USERNAME%/%IMAGE_NAME%:latest

    REM 推送到GitHub Container Registry
    echo %YELLOW%推送镜像到GitHub Container Registry...%RESET%
    docker push ghcr.io/%GITHUB_USERNAME%/%IMAGE_NAME%:%VERSION%
    docker push ghcr.io/%GITHUB_USERNAME%/%IMAGE_NAME%:latest

    if %errorlevel% neq 0 (
        echo %RED%错误: GitHub Container Registry推送失败%RESET%
        exit /b 1
    )

    echo %GREEN%镜像已成功推送到GitHub Container Registry！%RESET%
    echo %GREEN%GitHub Container Registry镜像地址：%RESET%
    echo %YELLOW%- docker pull ghcr.io/%GITHUB_USERNAME%/%IMAGE_NAME%:%VERSION%%RESET%
    echo %YELLOW%- docker pull ghcr.io/%GITHUB_USERNAME%/%IMAGE_NAME%:latest%RESET%
)

echo %GREEN%所有操作已完成！%RESET%
pause
