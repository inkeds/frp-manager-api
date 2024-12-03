#!/bin/bash

# 如果第一个参数是 "manage"，则运行管理脚本
if [ "${1}" = "manage" ]; then
    exec python manage.py
fi

# 否则，执行传入的命令
exec "$@"
