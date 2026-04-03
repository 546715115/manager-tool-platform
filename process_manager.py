"""
Process Manager Module - 进程管理模块

用于管理工具进程的启动和停止。
"""

import subprocess
import psutil
import signal
import time
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


def get_process_by_port(port):
    """
    通过端口获取进程PID。

    Args:
        port: 端口号

    Returns:
        int: 进程PID，如果未找到返回 None
    """
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return conn.pid
    except (psutil.AccessDenied, AttributeError):
        pass
    return None


def start_tool(cmd, port):
    """
    启动工具进程。

    Args:
        cmd: 启动命令（可包含 {port} 占位符）
        port: 期望端口号

    Returns:
        tuple: (success, actual_port, pid, error_msg)
            - success: 启动是否成功
            - actual_port: 实际使用的端口号
            - pid: 进程ID，成功时返回，失败时为 None
            - error_msg: 错误信息，成功时为 None
    """
    # 检查端口是否可用
    if not is_port_available(port):
        actual_port = find_available_port(port)
        if actual_port is None:
            return False, port, None, "无可用端口"
    else:
        actual_port = port

    # 启动进程
    try:
        # 替换端口占位符
        actual_cmd = cmd.replace('{port}', str(actual_port))
        # Windows下需要通过bash执行Git Bash风格命令
        process = subprocess.Popen(['bash', '-c', actual_cmd],
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL,
                                    start_new_session=True)
        # 等待进程启动
        time.sleep(2)
        # 通过端口获取真正的进程PID
        real_pid = get_process_by_port(actual_port)
        if real_pid:
            return True, actual_port, real_pid, None
        # 如果找不到，返回bash进程PID作为后备
        return True, actual_port, process.pid, None
    except Exception as e:
        return False, actual_port, None, str(e)


def stop_tool(pid, port=None):
    """
    停止工具进程。

    Args:
        pid: 进程ID
        port: 端口号（用于通过端口查找进程）

    Returns:
        bool: 停止是否成功
    """
    stopped = False

    # 如果PID存在，尝试停止
    if pid:
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            gone, alive = psutil.wait_procs([proc], timeout=5)
            if alive:
                proc.kill()
            stopped = True
        except psutil.NoSuchProcess:
            # 进程已不存在，继续尝试通过端口停止
            pass
        except Exception:
            pass

    # 如果未成功停止，尝试通过端口查找并停止
    if not stopped and port:
        real_pid = get_process_by_port(port)
        if real_pid:
            try:
                proc = psutil.Process(real_pid)
                proc.terminate()
                gone, alive = psutil.wait_procs([proc], timeout=5)
                if alive:
                    proc.kill()
                stopped = True
            except Exception:
                pass

    # 如果仍未停止，返回False
    return stopped or pid is None


if __name__ == '__main__':
    # 简单测试
    print("is_process_running test: process running =", is_process_running(None))
