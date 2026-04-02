"""
Port Scanner Module - 端口扫描模块

用于检测端口可用性和查找空闲端口。
"""

import socket


def is_port_available(port, host='127.0.0.1'):
    """
    检测端口是否可用。

    Args:
        port: 端口号
        host: 主机地址，默认为 127.0.0.1

    Returns:
        bool: 端口可用返回 True，端口被占用返回 False
    """
    if not (1024 <= port <= 65535):
        return False

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((host, port))
        sock.close()
        return result != 0  # 连接失败 = 端口可用
    except (socket.error, OSError):
        return False


def find_available_port(base_port, max_attempts=100):
    """
    查找空闲端口，自动顺延。

    从 base_port 开始检测，如果被占用则 port += 1，
    直到找到可用端口或达到最大尝试次数。

    Args:
        base_port: 起始端口号
        max_attempts: 最大尝试次数，默认为 100

    Returns:
        int or None: 找到可用端口返回端口号，未找到返回 None
    """
    port = base_port

    # 确保起始端口在有效范围内
    if port < 1024:
        port = 1024
    if port > 65535:
        return None

    for _ in range(max_attempts):
        if port > 65535:
            break
        if is_port_available(port):
            return port
        port += 1

    return None  # 未找到可用端口


if __name__ == '__main__':
    # 简单测试
    print(f"Port 80 available: {is_port_available(80)}")
    print(f"Port 5000 available: {is_port_available(5000)}")

    port = find_available_port(5000)
    print(f"First available port from 5000: {port}")
