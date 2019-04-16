# Pixiv Spider

针对P站的爬虫，不断更新中。

## 环境要求

自己看着配吧，缺啥补啥，都pip install 就行

## 更新日志

### 4/16/2019

#### 变更

上传了github，增加了readme文档

#### 描述

1. 直接在IDE中运行，按照提示输入`mode`和`delay`参数；

2. 命令行输入：

   ```
   python pixivSpider.py -m='r' -d='2'
   ```

   `-m`即`mode`，`-d`即delay

3. `mode`为访问p站的模式，参数取值有`r`和`n`，表示r18模式和正常模式，默认值为`n`；

4. `delay`为日期修正参数，表示选择距离今天几天前的日期，如`delay=1`即昨天，一般来说，由于p站日榜更新不是每日实时的，通常取`delay=2`，默认值也为2；

5. 程序运行需要当前目录下有`image_normal`或`image_r18`目录；

6. 程序运行时如果报错请检查`image_normal`或`image_r18`目录下是否已经存在目标日期目录。