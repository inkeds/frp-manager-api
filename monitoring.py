from fastapi import HTTPException
import psutil
import time
from typing import Dict, Any
from logger import setup_logger

logger = setup_logger("monitoring")

class SystemMonitor:
    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """获取系统指标"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage("/").percent,
                "network_connections": len(psutil.net_connections()),
                "timestamp": int(time.time())
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to get system metrics"
            )

    @staticmethod
    def check_health() -> Dict[str, str]:
        """健康检查"""
        try:
            metrics = SystemMonitor.get_system_metrics()
            
            # 定义警告阈值
            warnings = []
            if metrics["cpu_percent"] > 80:
                warnings.append("High CPU usage")
            if metrics["memory_percent"] > 80:
                warnings.append("High memory usage")
            if metrics["disk_usage"] > 80:
                warnings.append("High disk usage")
            
            status = "healthy" if not warnings else "warning"
            return {
                "status": status,
                "warnings": warnings if warnings else None,
                "timestamp": metrics["timestamp"]
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": int(time.time())
            }
