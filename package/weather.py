import requests
from bs4 import BeautifulSoup
from jarvis.jarvis import takecommand,speak

def get_weather_from_web(city):
    # 定义目标网页的URL
    url = "https://weather.cma.cn"
    
    # 发送HTTP请求并获取网页内容
    response = requests.get(url)
    response.raise_for_status()  # 检查请求是否成功
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 提取所需的天气信息 
    try:
        temperature = soup.find('span', class_='CurrentConditions--tempValue--3KcTQ').text
        description = soup.find('div', class_='CurrentConditions--phraseValue--2xXSr').text
        humidity = soup.find('span', attrs={"data-testid": "PercentageValue"}).text
        wind = soup.find('span', class_='Wind--windWrapper--3Ly7c').text
        
        weather_info = {
            "temperature": temperature,  # 摄氏温度
            "description": description,  # 天气描述
            "humidity": humidity,        # 湿度
            "wind": wind                 # 风速和风向
        }
        
        return weather_info
    except AttributeError:
        return None

def display_weather_info(weather_info, jarvis):

    if weather_info:
        weather_text = f"{weather_info['description']}，" \
                       f"温度: {weather_info['temperature']} 摄氏度，" \
                       f"湿度: {weather_info['humidity']}%，" \
                       f"风速: {weather_info['wind']}"

        print(weather_text) 
        speak(weather_text)   
    else:
        speak("没有找到城市的天气信息。")
