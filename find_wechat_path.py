import os
import re


def find_wechat_path():
    # 假设微信安装在默认的路径下
    common_paths = r"C:\Program Files\Tencent\WeChat"

    # 定义匹配版本号文件夹的正则表达式
    version_pattern = re.compile(r'\[\d+\.\d+\.\d+\.\d+\]')

    path_temp = os.listdir(common_paths)
    for temp in path_temp:
        # 下载是正则匹配到[3.9.10.27]
        # 使用正则表达式匹配版本号文件夹
        if version_pattern.match(temp):
            wechat_path = os.path.join(common_paths, temp)
            if os.path.isdir(wechat_path):
                return wechat_path


def find_wechatocr_exe():
    # 获取APPDATA路径
    appdata_path = os.getenv("APPDATA")
    if not appdata_path:
        print("APPDATA environment variable not found.")
        return None

    # 定义WeChatOCR的基本路径
    base_path = os.path.join(appdata_path, r"Tencent\WeChat\XPlugin\Plugins\WeChatOCR")

    # 定义匹配版本号文件夹的正则表达式
    version_pattern = re.compile(r'\d+')

    try:
        # 获取路径下的所有文件夹
        path_temp = os.listdir(base_path)
    except FileNotFoundError:
        print(f"The path {base_path} does not exist.")
        return None

    for temp in path_temp:
        # 使用正则表达式匹配版本号文件夹
        if version_pattern.match(temp):
            wechatocr_path = os.path.join(base_path, temp, 'extracted', 'WeChatOCR.exe')
            if os.path.isfile(wechatocr_path):
                return wechatocr_path

    # 如果没有找到匹配的文件夹，返回 None
    return None


def main():
    wechat_path = find_wechat_path()
    print(wechat_path)

    wechatocr_path = find_wechatocr_exe()
    print(wechatocr_path)


if __name__ == '__main__':
    main()
