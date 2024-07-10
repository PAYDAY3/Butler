#!/bin/bash

# 配置参数
LOG_FILE="/my_package/logging.txt"  # 访问日志文件路径
THRESHOLD=15                                     # 触发屏蔽的请求次数阈值
TIME_WINDOW=300                                   # 检测时间窗口（秒）
DROP_LOG="/tmp/drop_ip.log"                      # 被屏蔽IP记录文件

# 获取当前时间戳
CURRENT_TIMESTAMP=$(date +%s)

# 定义一个关联数组，用于存储IP地址及其最近访问时间
declare -A IP_LAST_ACCESS

# 遍历访问日志文件
while IFS= read -r LINE; do
  # 从日志行中提取IP地址和时间戳
  IP=$(echo "$LINE" | awk '{print $1}')
  TIMESTAMP=$(echo "$LINE" | awk '{print $4}')
  TIMESTAMP=$(date -d "$TIMESTAMP" +%s)  # 将日期字符串转换为时间戳

  # 检查IP地址是否已存在于关联数组中
  if [[ -n "${IP_LAST_ACCESS[$IP]}" ]]; then
    # 计算IP地址上次访问时间与当前时间的间隔
    TIME_DIFF=$((CURRENT_TIMESTAMP - ${IP_LAST_ACCESS[$IP]}))
    # 如果间隔小于时间窗口，则记录访问次数
    if [[ "$TIME_DIFF" -le "$TIME_WINDOW" ]]; then
      ((IP_COUNTS[$IP]++))
    fi
  fi

  # 更新IP地址的最近访问时间
  IP_LAST_ACCESS[$IP]=$TIMESTAMP
done < "$LOG_FILE"

# 遍历所有IP地址，检查是否超过阈值
for IP in "${!IP_COUNTS[@]}"; do
  COUNT="${IP_COUNTS[$IP]}"
  if [[ "$COUNT" -gt "$THRESHOLD" ]]; then
    # 检查IP地址是否已被屏蔽
    if ! iptables -vnL | grep -q "$IP"; then
      # 屏蔽IP地址
      iptables -I INPUT -s "$IP" -j DROP
      echo "$(date +'%D_%T') $IP" >> "$DROP_LOG"
      echo "已屏蔽IP地址：$IP"
    fi
  fi
done
