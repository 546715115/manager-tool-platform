"""
Process Manager Module - 进程管理模块

用于管理工具进程的启动和停止。
"""

import subprocess
import psutil
import signal
from port_scanner import is_port_available, find_available_port


def is_process_running(pid):
    """
    检查进程是否在运行。

    Args:
        pid: 进程ID

    Returns:
        bool: 进程在运行返回 True，否则返回 False
    """
    if pid is None:
        return False
    try:
        psutil.Process(pid)
        return True
    except psutil.NoSuchProcess:
        return False


def start_tool(cmd, port):
    """
    启动工具进程。

    Args:
        cmd: 启动命令（可包含 {port} 占位符）
        port: 期望端口号

    Returns:
        tuple: (success, actual_port, error_msg)
            - success: 启动是否成功
            - actual_port: 实际使用的端口号
            - error_msg: 错误信息，成功时为 None
    """
    # 检查端口是否可用
    if not is_port_available(port):
        actual_port = find_available_port(port)
        if actual_port is None:
            return False, port, "无可用端口"
    else:
        actual_port = port

    # 启动进程
    try:
        # 替换端口占位符
        actual_cmd = cmd.replace('{port}', str(actual_port))
        subprocess.Popen(actual_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, actual_port, None
    except Exception as e:
        return False, actual_port, str(e)


def stop_tool(pid):
    """
    停止工具进程。

    Args:
        pid: 进程ID

    Returns:
        bool: 停止是否成功
    """
    if pid is None:
        return False

    try:
        proc = psutil.Process(pid)
        proc.terminate()
        proc.wait(timeout=5)
        return True
    except psutil.TimeoutExpired:
        proc.kill()
        return True
    except psutil.NoSuchProcess:
        return True  # 进程已不存在，视为停止成功
    except Exception:
        return False


if __name__ == '__main__':
    # 简单测试
    print("is_process_running test: process running =", is_process_running(None))
