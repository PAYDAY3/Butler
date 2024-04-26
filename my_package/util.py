# — coding: utf-8 –
import json
import re
import os
import datetime
import statistics

def read_jsonline(address):
    not_mark = []
    with open(address, 'r', encoding="utf-8") as f:
        for jsonstr in f.readlines():
            jsonstr = json.loads(jsonstr)
            not_mark.append(jsonstr)
    return not_mark


def save_json(ls, address):
    json_str = json.dumps(ls, indent=4)
    with open(address, 'w', encoding='utf-8') as json_file:
        json.dump(ls, json_file, ensure_ascii=False, indent=4)


def read_json(address):
    with open(address, 'r', encoding='utf-8') as json_file:
        json_data = json.load(json_file)
    return json_data


def remove_key(item, key_to_remove):
    if isinstance(item, dict):
        if key_to_remove in item:
            del item[key_to_remove]
        for key, value in list(item.items()):  # 使用list包裹，防止字典大小改变时引发错误
            item[key] = remove_key(value, key_to_remove)
    elif isinstance(item, list):
        for index, value in enumerate(item):
            item[index] = remove_key(value, key_to_remove)
    return item


def data_clean(dic, key):
    dic = remove_key(dic, key)
    return dic


def lowercase_parameter_keys(input_dict):
    if "parameters" in input_dict and isinstance(input_dict["parameters"], dict):
        # Convert all keys in the "parameters" dictionary to uppercase
        input_dict["parameters"] = {change_name(k.lower()): v for k, v in input_dict["parameters"].items()}
    return input_dict


def build_index(base_path):
    index = {}
    for root, dirs, files in os.walk(base_path):
        for dir_name in dirs:
            if dir_name not in index:
                index[dir_name] = []
            index[dir_name].append(root)
    return index


def change_name(name):
    change_list = ["from", "class", "return", "false", "true", "id", "and", "", "ID"]
    if name in change_list:
        name = "is_" + name.lower()
    return name


def standardize(string):
    res = re.compile("[^\\u4e00-\\u9fa5^a-z^A-Z^0-9^_]")
    string = res.sub("_", string)
    string = re.sub(r"(_)\1+", "_", string).lower()
    while True:
        if len(string) == 0:
            return string
        if string[0] == "_":
            string = string[1:]
        else:
            break
    while True:
        if len(string) == 0:
            return string
        if string[-1] == "_":
            string = string[:-1]
        else:
            break
    if string[0].isdigit():
        string = "get_" + string
    return string


def get_last_processed_index(progress_file):
    """Retrieve the last processed index from the progress file."""
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            last_index = f.read().strip()
            return int(last_index) if last_index else 0
    else:
        return 0


def update_progress(progress_file, index):
    """Update the last processed index in the progress file."""
    with open(progress_file, 'w', encoding='utf-8') as f:
        f.write(str(index))
def get_current_timestamp():
    return datetime.datetime.now().timestamp()

def convert_timestamp_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)

def convert_datetime_to_timestamp(datetime_object):
    return datetime_object.timestamp()

def is_valid_email(email):
    regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return bool(re.match(regex, email))

def is_valid_url(url):
    regex = r"^(http|https)://\S+$"
    return bool(re.match(regex, url))

def is_valid_json(json_string):
    try:
        json.loads(json_string)
        return True
    except ValueError:
        return False

def calculate_mean(numbers):
    return statistics.mean(numbers)

def calculate_median(numbers):
    return statistics.median(numbers)

def calculate_standard_deviation(numbers):
    return statistics.stdev(numbers)

def remove_html_tags(string):
    return re.sub(r"<.*?>", "", string)

def extract_numbers(string):
    return re.findall(r"\d+", string)

def truncate_string(string, length):
    return string[:length] if len(string) > length else string

def create_directory(directory_path):
    os.makedirs(directory_path, exist_ok=True)

def delete_directory(directory_path):
    shutil.rmtree(directory_path, ignore_errors=True)

def copy_file(source_path, destination_path):
    shutil.copyfile(source_path, destination_path)

def generate_random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def convert_to_boolean(value):
    if isinstance(value, str):
        return value.lower() in ("true", "1")
    elif isinstance(value, int):
        return value != 0
    else:
        return bool(value)

def get_file_extension(filename):
    return os.path.splitext(filename)[1]

if __name__ == '__main__':
    print("util.py")
