# 微信OCR截图识别工具 

## 1. 软件概述

微信OCR截图识别工具是一款基于微信OCR引擎的桌面应用程序，能够识别图片或屏幕截图中的文字内容。软件具有简洁的用户界面、高效的文字识别能力和完善的历史记录功能。

### 主要功能

- 加载本地图片进行文字识别
- 屏幕截图并识别选定区域的文字
- 全局OCR识别功能
- 查看和管理历史识别记录
- 导出识别结果

## 2. 软件要求

- 操作系统: Windows 10/11 
- 需要安装微信客户端(用于OCR引擎)

## 3. 安装指南

### 从源代码运行

1. Python 3.10.11编译的

2. Tkinter 8.6.13

   PIL(Pillow) 10.4.0

## 4. 使用说明

### 4.1 主界面介绍

![image](https://github.com/TangTony2023/WechatOCR_Update/blob/main/Photo/2025-04-11%2012%2055%2005.png)

1. **功能按钮区**: 包含"载入图片"、"屏幕截图"、"全局识别"和"历史记录"四个主要功能按钮
2. **图片显示区**: 显示当前加载的图片
3. **状态栏**: 显示当前操作状态和提示信息

### 4.2 基本操作流程

#### 4.2.1 载入图片识别

1. 点击"载入图片"按钮
2. 选择要识别的图片文件
3. 图片将显示在主界面
4. 点击"全局识别"按钮开始识别
5. 识别结果将在新窗口中显示

#### 4.2.2 屏幕截图识别

1. 点击"屏幕截图"按钮
2. 主窗口将最小化，屏幕变暗
3. 按住鼠标左键拖动选择要识别的区域
4. 释放鼠标左键完成截图
5. 截图将自动加载到主界面
6. 点击"全局识别"按钮开始识别

#### 4.2.3 查看历史记录

1. 点击"历史记录"按钮
2. 历史记录窗口将显示所有识别记录
3. 右键点击记录可选择:
   - 查看详情
   - 复制文本
   - 查看原图

### 4.3 识别结果窗口

![image](https://github.com/TangTony2023/WechatOCR_Update/blob/main/Photo/2025-04-11%2012%2059%2039.png)

1. **文本显示区**: 显示识别出的文字内容
2. **工具栏**:
   - 导出文本: 将识别结果保存为文本文件
   - 字体设置: 调整显示字体和大小
   - 一键复制: 复制全部文本到剪贴板
3. **右键菜单**:
   - 复制: 复制选中文本
   - 全选: 选择全部文本

### 4.4 历史记录管理

![image](https://github.com/TangTony2023/WechatOCR_Update/blob/main/Photo/2025-04-11%2013%2001%2032.png)

1. **工具栏**:
   - 清空历史: 删除所有历史记录
   - 导出全部: 将所有历史记录导出为文本文件
2. **记录列表**: 按时间顺序显示历史记录
   - 时间: 识别时间
   - 图片路径: 识别图片的保存位置
   - 识别内容: 识别结果的预览
3. **右键菜单**:
   - 查看详情: 在新窗口查看完整识别结果
   - 复制文本: 复制该记录的识别文本
   - 查看原图: 查看识别时使用的原始图片

## 5. 高级功能

### 5.1 字体设置

在识别结果窗口中，点击"字体设置"按钮可以:

- 选择不同的字体(支持中英文字体)
- 调整字体大小(8-36磅)

### 5.2 批量导出

在历史记录窗口中，点击"导出全部"按钮可以将所有历史记录导出为一个文本文件，方便存档或进一步处理。

### 5.3 自动保存

所有识别的图片和结果都会自动保存到程序目录下的"ocr_images"文件夹和"ocr_history.json"文件中。



## 6. 联系方式

如有任何问题，请联系:

- 邮箱: [tonysoft2023@gmail.com](mailto:tonysoft2023@gmail.com)



---

如果你对此项目有兴趣，请你捐赠一下。你的鼓励是我前进的最大动力。

![image](https://github.com/TangTony2023/WechatOCR_Update/blob/main/Photo/IMG_1677.JPG)

