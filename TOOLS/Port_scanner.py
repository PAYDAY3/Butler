import socket
from prettytable import PrettyTable

# 字典映射常见端口到漏洞 (前15个)
vulnerabilities = {
    80: "HTTP (Hypertext Transfer Protocol) - 用于未加密的网页流量",
    443: "HTTPS (HTTP Secure) - 用于加密的网页流量",
    22: "SSH (Secure Shell) - 用于安全的远程访问",
    21: "FTP (File Transfer Protocol) - 用于文件传输",
    25: "SMTP (Simple Mail Transfer Protocol) - 用于电子邮件传输",
    23: "Telnet - 用于远程终端访问",
    53: "DNS (Domain Name System) - 用于域名解析",
    110: "POP3 (Post Office Protocol version 3) - 用于电子邮件接收",
    143: "IMAP (Internet Message Access Protocol) - 用于电子邮件接收",
    3306: "MySQL - 用于MySQL数据库访问",
    3389: "RDP (Remote Desktop Protocol) - 用于远程桌面连接 (Windows)",
    8080: "HTTP Alternate - 常用于备用HTTP端口",
    8000: "HTTP Alternate - 常用于备用HTTP端口",
    8443: "HTTPS Alternate - 常用于备用HTTPS端口",
    5900: "VNC (Virtual Network Computing) - 用于远程桌面访问",
    # 可以根据需要添加更多端口和漏洞
}

def display_table(open_ports):
    """
    显示打开端口及其可能存在的漏洞
    :param open_ports: 打开端口列表
    """
    table = PrettyTable(["Open Port", "Vulnerability"])
    for port in open_ports:
        vulnerability = vulnerabilities.get(port, "No known vulnerabilities associated with common services")
        table.add_row([port, vulnerability])
    print(table)

def scan_top_ports(target):
    """
    扫描目标的常见端口并返回打开端口
    :param target: 目标网站URL或IP地址
    :return: 打开端口列表
    """
    open_ports = []
    top_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 5900, 8000, 8080, 8443]  # 前15个常见端口
    for port in top_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)  # 根据需要调整超时时间
            result = sock.connect_ex((target, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except KeyboardInterrupt:
            sys.exit()
        except socket.error:
            pass
    return open_ports

def main():
    target = input("请输入要扫描开放端口的网站URL或IP地址: ")
    open_ports = scan_top_ports(target)
    if not open_ports:
        print("在目标上未找到开放端口。")
    else:
        print("开放端口及其可能存在的漏洞：")
        display_table(open_ports)

if __name__ == "__main__":
    main()
