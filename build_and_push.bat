@echo off
REM 设置你的Docker Hub用户名
set DOCKER_USERNAME=your-username
REM 设置镜像名称和版本
set IMAGE_NAME=frp-manager-api
set VERSION=1.0.0

REM 登录到Docker Hub
docker login

REM 构建镜像
docker build -t %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION% .
docker tag %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION% %DOCKER_USERNAME%/%IMAGE_NAME%:latest

REM 推送镜像到Docker Hub
docker push %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%
docker push %DOCKER_USERNAME%/%IMAGE_NAME%:latest

echo 镜像已成功推送到Docker Hub
pause
