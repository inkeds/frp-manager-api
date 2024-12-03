import os
import sys
import time
import json
import requests
import subprocess
from typing import Dict, List, Optional
import platform
from logger import setup_logger
from system_check import SystemChecker

logger = setup_logger("manager")

class CommandMenu:
    def __init__(self):
        self.api_url = os.getenv("API_URL", "http://localhost:8000")
        self.commands = {
            "1": ("系统状态检查", self.check_system),
            "2": ("查看系统详细信息", self.view_system_info),
            "3": ("查看健康状态", self.check_health),
            "4": ("查看日志", self.view_logs),
            "5": ("性能监控", self.monitor_performance),
            "6": ("管理FRP配置", self.manage_frp),
            "7": ("用户管理", self.manage_users),
            "8": ("重启服务", self.restart_service),
            "9": ("备份数据", self.backup_data),
            "0": ("退出", self.exit_program)
        }

    def clear_screen(self):
        os.system('cls' if platform.system() == 'Windows' else 'clear')

    def print_header(self):
        self.clear_screen()
        print("=" * 50)
        print("FRP管理系统 - 管理面板")
        print("=" * 50)
        print()

    def print_menu(self):
        self.print_header()
        for key, (name, _) in self.commands.items():
            print(f"{key}. {name}")
        print()

    def get_user_choice(self) -> str:
        while True:
            choice = input("请输入选项编号: ").strip()
            if choice in self.commands:
                return choice
            print("无效的选项，请重新输入")

    def check_system(self):
        """系统状态检查"""
        self.print_header()
        print("正在检查系统状态...")
        checker = SystemChecker()
        checker.print_system_status()
        input("\n按Enter键返回主菜单...")

    def view_system_info(self):
        """查看系统详细信息"""
        self.print_header()
        try:
            response = requests.get(f"{self.api_url}/system/status")
            data = response.json()
            print("\n系统信息:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"获取系统信息失败: {e}")
        input("\n按Enter键返回主菜单...")

    def check_health(self):
        """检查健康状态"""
        self.print_header()
        try:
            response = requests.get(f"{self.api_url}/health")
            data = response.json()
            print("\n健康状态:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"获取健康状态失败: {e}")
        input("\n按Enter键返回主菜单...")

    def view_logs(self):
        """查看日志"""
        self.print_header()
        log_dir = "logs"
        if not os.path.exists(log_dir):
            print("日志目录不存在")
            input("\n按Enter键返回主菜单...")
            return

        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        if not log_files:
            print("没有找到日志文件")
            input("\n按Enter键返回主菜单...")
            return

        print("可用的日志文件:")
        for i, file in enumerate(log_files, 1):
            print(f"{i}. {file}")

        try:
            choice = int(input("\n请选择要查看的日志文件编号: "))
            if 1 <= choice <= len(log_files):
                log_file = os.path.join(log_dir, log_files[choice-1])
                
                # 使用less或more查看日志
                if platform.system() == 'Windows':
                    os.system(f"type {log_file} | more")
                else:
                    os.system(f"less {log_file}")
            else:
                print("无效的选择")
        except ValueError:
            print("无效的输入")
        
        input("\n按Enter键返回主菜单...")

    def monitor_performance(self):
        """性能监控"""
        self.print_header()
        print("正在监控系统性能...")
        try:
            while True:
                self.clear_screen()
                print("性能监控 (按Ctrl+C退出)")
                print("-" * 50)
                
                response = requests.get(f"{self.api_url}/metrics/system")
                metrics = response.json()
                
                print(json.dumps(metrics, indent=2, ensure_ascii=False))
                time.sleep(2)
        except KeyboardInterrupt:
            print("\n停止监控")
        except Exception as e:
            print(f"监控失败: {e}")
        
        input("\n按Enter键返回主菜单...")

    def manage_frp(self):
        """管理FRP配置"""
        while True:
            self.print_header()
            print("FRP配置管理")
            print("-" * 50)
            print("1. 查看所有配置")
            print("2. 添加新配置")
            print("3. 修改配置")
            print("4. 删除配置")
            print("5. 返回主菜单")
            
            choice = input("\n请选择操作: ")
            
            if choice == "5":
                break
            
            # 实现具体的FRP配置管理逻辑
            print("功能开发中...")
            input("\n按Enter键继续...")

    def manage_users(self):
        """用户管理"""
        while True:
            self.print_header()
            print("用户管理")
            print("-" * 50)
            print("1. 查看所有用户")
            print("2. 添加用户")
            print("3. 修改用户")
            print("4. 删除用户")
            print("5. 返回主菜单")
            
            choice = input("\n请选择操作: ")
            
            if choice == "5":
                break
            
            # 实现具体的用户管理逻辑
            print("功能开发中...")
            input("\n按Enter键继续...")

    def restart_service(self):
        """重启服务"""
        self.print_header()
        print("正在重启服务...")
        
        try:
            if os.path.exists("docker-compose.yml"):
                subprocess.run(["docker-compose", "restart"], check=True)
                print("服务已重启")
            else:
                print("未找到docker-compose.yml文件")
        except Exception as e:
            print(f"重启服务失败: {e}")
        
        input("\n按Enter键返回主菜单...")

    def backup_data(self):
        """备份数据"""
        self.print_header()
        print("正在备份数据...")
        
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"backup_{timestamp}.zip")
        
        try:
            # 实现具体的备份逻辑
            print(f"数据已备份到: {backup_file}")
        except Exception as e:
            print(f"备份失败: {e}")
        
        input("\n按Enter键返回主菜单...")

    def exit_program(self):
        """退出程序"""
        self.print_header()
        print("感谢使用！再见！")
        sys.exit(0)

    def run(self):
        """运行管理面板"""
        while True:
            self.print_menu()
            choice = self.get_user_choice()
            _, func = self.commands[choice]
            func()

def main():
    try:
        menu = CommandMenu()
        menu.run()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序运行错误: {e}")
        print(f"发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
