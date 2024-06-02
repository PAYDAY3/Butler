import requests
import time
import random
import redis
from bs4 import BeautifulSoup
import os

downloaded_images = "" #放存数据文件

# 设置User Agent列表
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    # Add more user agents here
]

# 随机选择 User Agent
def get_random_user_agent():
    return random.choice(user_agents)

# 设置headers
def get_headers():
    user_agent = get_random_user_agent()
    headers = {'User-Agent': user_agent}
    return headers

# 设置爬虫的起始url
start_url = 'https://www.bing.com'

# 设置爬虫的深度限制
max_depth = 2

# 设置爬虫的延迟时间
delay_time = 1

# 创建一个set来存储已经访问过的url
visited_urls = set()

# 创建一个队列来存储需要访问的url
url_queue = [start_url]

# 创建一个Redis客户端来存储爬虫的状态
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# 创建一个文件夹用于存储下载的图片
if not os.path.exists(downloaded_images):
    os.makedirs(downloaded_images)

def download_image(url, filename):
    response = requests.get(url)
    with open(os.path.join(downloaded_images, filename), 'wb') as f:
        f.write(response.content)
        
def search_and_crawl_images(search_query):
    search_url = 'https://www.bing.com/search'
    params = {'q': search_query, 'tbm': 'isch'}
    headers = get_headers()
    response = requests.get(search_url, params=params, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    image_links = [img.get('src') for img in soup.find_all('img')]
    for img_url in image_links:
        download_image(img_url, os.path.basename(img_url))

def crawl_website(start_url, max_depth):
    while url_queue:
        url = url_queue.pop(0)
        if url in visited_urls:
            continue
        visited_urls.add(url)
        response = requests.get(url, headers=get_headers())
        soup = BeautifulSoup(response.content, 'html.parser')
        links = [link.get('href') for link in soup.find_all('a', href=True)]
        for link in links:
            if link not in visited_urls:
                url_queue.append(link)
        images = [img.get('src') for img in soup.find_all('img')]
        for image_url in images:
            download_image(image_url, os.path.basename(image_url))
        time.sleep(delay_time + random.random())
        if len(visited_urls) >= max_depth:
            break
    redis_client.set('crawler_state', str(len(visited_urls)))


def main():
    search_query = input('输入搜索查询: ')
    search_and_crawl_images(search_query)
    crawl_website(start_url, max_depth)
    print('爬虫结束！')

if __name__ == '__main__':
    main()
