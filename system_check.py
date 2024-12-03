import psutil
import platform
import os
from typing import Dict, List, Tuple
import json
from logger import setup_logger

logger = setup_logger("system_check")

class SystemRequirements:
    MIN_CPU_CORES = 1
    MIN_MEMORY_GB = 1
    MIN_DISK_GB = 10
    RECOMMENDED_CPU_CORES = 2
    RECOMMENDED_MEMORY_GB = 2
    RECOMMENDED_DISK_GB = 20

class SystemChecker:
    @staticmethod
    def get_system_info() -> Dict:
        """获取系统信息"""
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "cpu_cores": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "disk_total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
            "python_version": platform.python_version(),
        }

    @staticmethod
    def check_docker() -> bool:
        """检查Docker是否已安装"""
        try:
            return os.system("docker --version") == 0
        except:
            return False

    @staticmethod
    def check_requirements() -> Tuple[List[str], List[str]]:
        """检查系统是否满足运行要求"""
        warnings = []
        errors = []
        
        # 获取系统信息
        cpu_cores = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)
        disk_gb = psutil.disk_usage('/').total / (1024**3)

        # 检查最低要求
        if cpu_cores < SystemRequirements.MIN_CPU_CORES:
            errors.append(f"CPU核心数不足: 当前{cpu_cores}核, 最低要求{SystemRequirements.MIN_CPU_CORES}核")
        elif cpu_cores < SystemRequirements.RECOMMENDED_CPU_CORES:
            warnings.append(f"CPU核心数较低: 当前{cpu_cores}核, 建议{SystemRequirements.RECOMMENDED_CPU_CORES}核")

        if memory_gb < SystemRequirements.MIN_MEMORY_GB:
            errors.append(f"内存不足: 当前{memory_gb:.1f}GB, 最低要求{SystemRequirements.MIN_MEMORY_GB}GB")
        elif memory_gb < SystemRequirements.RECOMMENDED_MEMORY_GB:
            warnings.append(f"内存较低: 当前{memory_gb:.1f}GB, 建议{SystemRequirements.RECOMMENDED_MEMORY_GB}GB")

        if disk_gb < SystemRequirements.MIN_DISK_GB:
            errors.append(f"磁盘空间不足: 当前{disk_gb:.1f}GB, 最低要求{SystemRequirements.MIN_DISK_GB}GB")
        elif disk_gb < SystemRequirements.RECOMMENDED_DISK_GB:
            warnings.append(f"磁盘空间较低: 当前{disk_gb:.1f}GB, 建议{SystemRequirements.RECOMMENDED_DISK_GB}GB")

        # 检查Docker
        if not SystemChecker.check_docker():
            errors.append("未检测到Docker，请先安装Docker")

        return warnings, errors

    @staticmethod
    def print_system_status():
        """打印系统状态报告"""
        logger.info("正在检查系统状态...")
        
        # 获取系统信息
        system_info = SystemChecker.get_system_info()
        
        # 检查要求
        warnings, errors = SystemChecker.check_requirements()
        
        # 打印报告
        logger.info("\n系统信息:")
        logger.info(json.dumps(system_info, indent=2, ensure_ascii=False))
        
        if warnings:
            logger.warning("\n警告:")
            for warning in warnings:
                logger.warning(f"- {warning}")
        
        if errors:
            logger.error("\n错误:")
            for error in errors:
                logger.error(f"- {error}")
        
        if not (warnings or errors):
            logger.info("\n✓ 系统满足所有运行要求")
        
        return len(errors) == 0  # 返回是否可以运行

if __name__ == "__main__":
    SystemChecker.print_system_status()
