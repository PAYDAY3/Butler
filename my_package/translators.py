import os
import requests
import uuid
from bs4 import BeautifulSoup
from dotenv import load_dotenv

def load_api_key():
    # 从环境变量加载Azure Cognitive Services的API密钥
    load_dotenv()
    return os.getenv('AZURE_TRANSLATE_KEY')

def translate_text(text, target_language='en'):
    api_key = load_api_key()
    endpoint = "https://api.cognitive.microsofttranslator.com"

    # 准备请求头和请求参数
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4())
    }
    params = {
        "api-version": "3.0",
        "to": target_language
    }

    # 发送翻译请求
    translate_url = f"{endpoint}/translate"
    body = [{"text": text}]
    response = requests.post(translate_url, headers=headers, params=params, json=body)
    response.raise_for_status()
    translated_text = response.json()[0]['translations'][0]['text']
    
    return translated_text

def translate_file(input_file, output_file, target_language='en'):
    # 读取输入文件内容
    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()

    # 翻译文本
    translated_text = translate_text(text, target_language)

    # 将翻译结果写入输出文件
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(translated_text)

    print(f"文件翻译成功，已保存到 {output_file}")

def translate_website(url, target_language='en'):
    # 获取网页内容
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # 提取网页中的文本内容
    text_elements = soup.find_all(text=True)

    # 构建要翻译的文本列表
    text_to_translate = "\n".join([element.strip() for element in text_elements if element.strip()])

    # 翻译文本
    translated_text = translate_text(text_to_translate, target_language)

    # 替换原始文本为翻译后的文本
    for element in text_elements:
        if element.strip():
            translated_text = translate_text(element.strip(), target_language)
            element.replace_with(translated_text)

    # 输出翻译后的网页内容
    translated_html = soup.prettify()
    print(translated_html)

def translators():
    choice = input("请选择翻译类型: 1. 文件 2. 网页\n")
    to_language = input("请输入目标语言代码（例如：zh, en, es）:\n")

    if choice == '1':
        file_path = input("请输入文件路径:\n")
        output_file = input("请输入输出文件路径:\n")
        translate_file(file_path, output_file, to_language)
    elif choice == '2':
        url = input("请输入网页URL:\n")
        translate_website(url, to_language)
    else:
        print("无效选择")

if __name__ == "__main__":
    translators()
