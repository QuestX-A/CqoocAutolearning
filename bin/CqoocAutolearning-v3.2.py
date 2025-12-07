"""
！！！！！！！！！！必读信息！！！！！！！！！！

免责声明：
    本项目及其相关文档（以下简称“项目”）仅供教育和学习目的使用。作者提供此项目时，不提供任何形式的明示或暗示的担保，包括但不限于对适销性、特定用途适用性、所有权和非侵权性的任何保证。
    在任何情况下，作者均不对任何个人或实体因使用或无法使用本项目而可能遭受的任何直接、间接、偶然、特殊、惩罚性或后果性损失承担责任，无论这些损失是基于合同、侵权行为（包括疏忽）或其他原因造成的，即使作者已被告知此类损失的可能性。
    在使用本项目时，用户应自行承担风险。作者不对任何因使用或依赖本软件而产生的损失或损害承担责任。
    用户应确保遵守所有适用的法律和法规，并对其使用本软件的行为负责。本软件不得用于任何非法目的，或者以任何非法方式使用。
------------------------------------------------------------------
开源声明：
    本项目为 “cqooc平台学习助手-v3.2”，在下文简称为“项目”
    技术学习与资源分享 QQ群：383127132
    如果你在本QQ群：383127132 使用了这个项目（我们欢迎任何自然人使用），请遵守开源条约

------------------请自觉遵守开源条约，不可盈利！！！！！-----------------
----------我们欢迎你对项目进行开发贡献，并在群内开源共享！！！！！----------
使用说明：
    因为课程有结束时间，所以没有一次罗列，且爬取网站数据是不道德且违法的，
    所以我们希望用户可以自行添加课程在本脚本中

    目前本项目示例包含: '马克思主义基本原理': '2d80dd146c376768',

    若对其他课程有需求，请在项目第 322 行CourseManager中 添加课程名与课程ID

    注：ID在课程学习的网址上
    例如：https://www.cqooc.com/course/detail/courseStudy?id=2d80dd146c376768
    其中 id=2d80dd146c376768 指明ID
-------------------------------------------------------------------
版本声明：
当前版本信息：
    “项目3.2”
        作者：QuestX
        更新时间：2025 年 4 月 20 日
        ·修复了对部分视频和文档解析失败的错误
------------------------------------------------------------------
历史版本信息：
    “项目3.1”
        作者：QuestX
        更新时间：2025 年 4 月 19 日
        ·美化了 GUI ，优化提示功能，优化交互功能
        ·修复了“ 停止学习 ”按钮点击无效、卡顿或未响应问题，
        ·修复了已知 bug，优化逻辑
        ·编写说明文案
    --------------------------------------------------------------
    “项目2.8”
        作者：积不出的Calculus
        ·初步具备 gui 的功能
        ·在 Edge 浏览器即可使用
------------------------------------------------------------------
特别声明
    “项目1.0”
        作者：李伟
        开源地址：https://github.com/2841952537/cqooc_class
-------------------------------------------------------------------

依赖库的安装（在命令行工具输入）：
    pip install DrissionPage
    pip install tqdm
-------------------------------------------------------------------
   QuestX向您问好。
-------------------------------------------------------------------
"""

import time
import re
from DrissionPage import ChromiumPage, ChromiumOptions
from tqdm import tqdm
import random
import tkinter as tk
from tkinter import scrolledtext, StringVar
from tkinter import ttk
from tkinter.ttk import Progressbar
import threading
import sys

# 全局变量
page = None
stop_flag = threading.Event()
progress_bar = None
current_task = None


def random_sleep(min_time=1, max_time=3):
    """
    随机休眠一段时间，模拟人类操作间隔
    :param min_time: 最短休眠时间
    :param max_time: 最长休眠时间
    """
    time.sleep(random.uniform(min_time, max_time))


def get_element_safe(ele, xpath, timeout=0.2):
    """
    安全地获取页面元素，避免因元素不存在导致程序崩溃
    :param ele: 父元素对象
    :param xpath: xpath表达式
    :param timeout: 超时时间
    :return: 元素对象或None
    """
    try:
        return ele.ele(xpath, timeout=timeout)
    except Exception:
        return None


def get_elements_safe(ele, xpath, timeout=0.2):
    """
    安全地获取多个页面元素，避免因元素不存在导致程序崩溃
    :param ele: 父元素对象
    :param xpath: xpath表达式
    :param timeout: 超时时间
    :return: 元素对象列表或空列表
    """
    try:
        return ele.eles(xpath, timeout=timeout)
    except Exception:
        return []


def get_document_reading_time():
    """
    获取文档阅读时间
    """
    reading_time_ele = get_element_safe(page, 'x:.//div[@data-v-246bbee8][contains(text(), "完成倒计时")]')
    if reading_time_ele:
        try:
            reading_time_text = reading_time_ele.text
            reading_time = int(re.search(r'完成倒计时：(\d+)s', reading_time_text).group(1))
            return reading_time
        except (AttributeError, ValueError):
            print("无法将文档阅读时间转换为整数，使用默认值60秒。")
    return 60


def update_progress_bar(current, total):
    if progress_bar:
        progress = (current / total) * 100
        progress_bar['value'] = progress
        progress_bar.update_idletasks()


def run_word():
    """
    处理文档学习，等待文档阅读时间模拟阅读
    """
    reading_time = get_document_reading_time()
    print(f'开始阅读文档，预计{reading_time}秒...')
    for i in range(reading_time):
        if stop_flag.is_set():
            break
        root.after(1000, update_progress_bar, i + 1, reading_time)
        time.sleep(1)


def run_video(right_box):
    """
    处理视频学习，包括获取视频时长、静音、播放和等待播放完成
    :param right_box: 视频框元素对象
    """
    # 处理开始播放时间和结束播放时间
    start_time_ele = get_element_safe(right_box, 'x:.//span[@class="dplayer-ptime"]')
    end_time_ele = get_element_safe(right_box, 'x:.//span[@class="dplayer-dtime"]')
    if not start_time_ele or not end_time_ele:
        print('视频时间解析失败，跳过该视频')
        return
    start_time = re.findall(r'(.*):(.*)', start_time_ele.text)
    start_time = int(start_time[0][0]) * 60 + int(start_time[0][1])
    end_time = re.findall(r'(.*):(.*)', end_time_ele.text)
    end_time = int(end_time[0][0]) * 60 + int(end_time[0][1])
    video_time = end_time - start_time

    # 点击静音
    mute_button = get_element_safe(right_box, 'x:.//button[@class="dplayer-icon dplayer-volume-icon"]')
    if mute_button:
        mute_button.click()
        random_sleep()
    else:
        print('点击静音失败，未找到静音按钮')

    # 点击播放按钮
    play_button = get_element_safe(right_box, 'x:.//button[@class="dplayer-icon dplayer-play-icon"]')
    if play_button:
        play_button.click()
        random_sleep()
    else:
        print('点击播放按钮失败，未找到播放按钮')

    # 等待播放时间
    print(f'开始播放视频，预计{video_time}秒...')
    for i in range(video_time):
        if stop_flag.is_set():
            break
        root.after(int((1 + random.uniform(-0.2, 0.2)) * 1000), update_progress_bar, i + 1, video_time)
        time.sleep(1 + random.uniform(-0.2, 0.2))


def run():
    """
    判断当前学习内容是文档还是视频，并调用相应处理函数
    """
    right_box = get_element_safe(page, 'x:.//div[@class="video-box"]')
    if not right_box:
        print('获取视频框元素失败')
        return
    is_word = get_element_safe(right_box, 'x:./div[@class="ifrema"]')

    if is_word:
        print('识别到课件：开始阅读文档')
        run_word()
    else:
        print('识别到视频：开始播放视频')
        run_video(right_box)


def get_detail_info(x_chapter):
    """
    获取小章节的详细信息，判断学习状态并处理未完成的章节
    :param x_chapter: 小章节元素对象
    """
    detaill_infos = get_elements_safe(x_chapter, 'x:.//div[@class="second-level-inner-box"]/div')
    total = len(detaill_infos)
    for i, detaill_info in enumerate(detaill_infos):
        if stop_flag.is_set():
            break
        status_img = get_element_safe(detaill_info, 'x:.//div[@class="complate-icon"]//img', timeout=0.2)
        title_ele = get_element_safe(detaill_info, 'x:.//p[@class="title"]')
        if not title_ele:
            print('未找到标题元素，跳过该章节')
            continue
        title = title_ele.text

        if not status_img:
            print(f'> {title}   未定义')
        elif status_img.link in [
            'data:image/png;base64,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',
            'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAbVJREFUSEu9ls8rRFEUx7/nzsjvjWQxSSTPJE1Zv0nUjEiIhRQbxQKTUiSr914pK6mJFWUjlqL8ysbCrJWVIWUh/wBF4R3d18w0zMwzi7nztu/7zuee7zn3nEdweQJGV/2H+BqCzf0gNAPwJeQvYDxC0EmZ7T26ta6ec4WhbC9aDd3HBIsZkwB73A4B0DcRdolhxK3Yy19tBqDV0AcZ2GNwtVd4EPJ3IuzvRLvPj7rqWnSshbPyCPRKwETcih2nC34BWszgPGBvgCFk0OWeOTTU1P8KqJl67oQINiAWHszraFKUAsiT28SHBBKLoRlM6+NZA7kC5BcEWzANJzNxAI7nwJ20ZSk8mzO41P4LcBiOXX5ZEwegmfo2M09JW7bG1lxrmg/ASYRo596MTZNsxXd8PnmF8JxH9jM8/0vLFyC7qxwljaRZwTm27c3etm5ER1fdOzJPi1IFFiJCmqGfMrhvfcTAQKCnsADQGWmmHmdm7SJygKbahsICiO4l4JWZq25WLlFZWlFowFtRAIotUl5k1W2q/KIpHxVFGXYJiLpxnbxdShdOEqJ0ZaZB1C399GFUiN+WH16q+w/WuLNCAAAAAElFTkSuQmCC'
        ]:
            print(f'> {title}   未完成')
            title_ele.click()
            random_sleep()
            page.wait.load_start(timeout=1)
            run()
        else:
            print(f'> {title}   已完成')
        update_progress_bar(i + 1, total)


def get_x_chapter(chapters):
    """
    获取小章节信息并处理
    :param chapters: 大章节元素对象列表
    """
    x_chapters = get_elements_safe(chapters, 'x:.//div[@class="first-level-inner-box"]/div')
    total = len(x_chapters)
    for i, x_chapter in enumerate(x_chapters):
        if stop_flag.is_set():
            break
        x_chapter_title = get_element_safe(x_chapter, 'x:.//div[@class="p"]//span[@class="title-big"]')
        if not x_chapter_title:
            continue
        print(f'---------> {x_chapter_title.text}')
        get_detail_info(x_chapter)
        update_progress_bar(i + 1, total)


def get_chapter():
    """
    获取大章节信息，展开未展开的章节并处理小章节
    """
    chapters = get_elements_safe(page, 'x:.//div[@class="left-box"]/div[@class="menu-box"]/div')
    print(f"获取到的大章节数量: {len(chapters)}")
    total = len(chapters)
    for i, chapter in enumerate(chapters):
        if stop_flag.is_set():
            break
        chapter_title = get_element_safe(chapter, 'x:.//p[@class="title-big"]')
        if not chapter_title:
            print(f"未找到第 {i} 个大章节的标题元素，跳过该章节")
            continue
        print(f'\n==================== {chapter_title.text} ====================')

        is_open = get_element_safe(chapter, 'x:.//div[@class="first-level-inner-box"]/@style', timeout=0.2)
        if not is_open or is_open == 'height: 0px;':
            chapter_title.click()
            random_sleep()

        get_x_chapter(chapter)
        update_progress_bar(i + 1, total)


def is_logged_in(username, password):
    """
    判断用户是否登录，若未登录则进行登录操作
    """
    while True:
        try:
            page.get('https://www.cqooc.com/index/home')
            page.wait.load_start(timeout=1)
            no_login_status = get_element_safe(page, 'xpath=//span[@class="login-logo"]', timeout=1)
            if no_login_status:
                print('账号未登录，请先完成登录！')
                no_login_status.click()
                random_sleep()
                username_input = get_element_safe(page, 'xpath=//div[@class="username-box"]//input')
                password_input = get_element_safe(page, 'xpath=//div[@class="password-box"]//input')
                if username_input and password_input:
                    username_input.input(username)
                    password_input.input(password)
                    random_sleep()
                    submit_button = get_element_safe(page, 'xpath=//div[@class="submit-btn"]')
                    if submit_button:
                        submit_button.click()
                        random_sleep()
            else:
                print('账号已登录!--->开始运行!')
                break
        except Exception as e:
            print(f"访问页面时出现错误: {e}")
            print("请检查网络连接或重新启动程序。")
            return


class CourseManager:
    def __init__(self):
        self.courses = {
            # 因为课程有结束时间，所以没有一次罗列，且爬取网站数据是不道德且违法的，
            # 所以我们希望用户可以自行增、删、改、查课程在本项目中
            '马克思主义基本原理': 'b30a5d90eda2ba4f',

            # 可继续添加更多课程
        }

    def get_course_selection(self, master):
        # 在GUI中添加课程选择下拉菜单
        self.master = master
        self.course_var = StringVar()
        self.course_dropdown = ttk.Combobox(master,
                                            textvariable=self.course_var,
                                            values=list(self.courses.keys()))
        # 使用 grid 几何管理器
        self.course_dropdown.grid(row=2, column=1, sticky=tk.W, columnspan=5, padx=5, pady=10)
        self.course_dropdown.current(0)

    def get_course_id(self):
        return self.courses[self.course_var.get()]


def start_learning(username_entry, password_entry, log_text, course_manager):
    global page, current_task
    stop_flag.clear()
    username = username_entry.get()
    password = password_entry.get()

    co = ChromiumOptions()
    co.set_argument('--start-maximized')
    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    co.set_browser_path(edge_path)
    co.set_timeouts(base=0.2)
    page = ChromiumPage(co)

    print('''
                     ！！！使用协议！！！
免责声明：
    本项目及其相关文档（以下简称“项目”）仅供教育和学习目的使用。作者提供此项目时，不提供任何形式的明示或暗示的担保，包括但不限于对适销性、特定用途适用性、所有权和非侵权性的任何保证。
    在任何情况下，作者均不对任何个人或实体因使用或无法使用本项目而可能遭受的任何直接、间接、偶然、特殊、惩罚性或后果性损失承担责任，无论这些损失是基于合同、侵权行为（包括疏忽）或其他原因造成的，即使作者已被告知此类损失的可能性。
    在使用本项目时，用户应自行承担风险。作者不对任何因使用或依赖本软件而产生的损失或损害承担责任。
    用户应确保遵守所有适用的法律和法规，并对其使用本软件的行为负责。本软件不得用于任何非法目的，或者以任何非法方式使用。
------------------------------------------------------------
当前版本信息：
    “项目3.2”
        作者：QuestX
        更新时间：2025 年 4 月 20 日
        ·修复了对部分视频和文档解析失败的错误
------------------------------------------------------------
历史版本信息：
    “项目3.1”
        作者：QuestX
        更新时间：2025 年 4 月 19 日
        ·美化了 GUI ，优化提示功能，优化交互功能
        ·修复了“ 停止学习 ”按钮点击无效、卡顿或未响应问题，
        ·修复了已知 bug，优化逻辑
        ·编写说明文案
    ------------------------------------------------------------
    “项目2.8”
        作者：积不出的Calculus
        初步具备 gui 的功能，并在 Edge 浏览器即可使用
    ----------------------------------------------------
    如果你在本QQ群：383127132使用了这个项目
    （我们欢迎任何自然人使用）。
    请自觉遵守开源条约，不可盈利！！！！！\n
    ---我们欢迎你对项目进行开发贡献，并在群内开源共享！！！！！---
    
    因为课程有结束时间，且似乎没人课程ID不一样，
    所以没有一次罗列，爬取网站数据是不道德且违法的，
    所以我们希望用户可以自行添加课程在本脚本中
    
    目前本项目添加课程: '马克思主义基本原理': '2d80dd146c376768',
                     
    ----------------------------------------------------
    若对其他课程有需求，请在项目第322行 
    CourseManager中添加课程名与课程ID
    注：ID在课程学习的网址上
    例如：https://www.cqooc.com/course/detail
    /courseStudy?id=2d80dd146c376768
    # 其中 id=2d80dd146c376768 指明ID
    ----------------------------------------------------

    QuestX 向您问好。
    ____________________________________________________
    ''')
    print('等待页面加载中...预计30秒...请耐心等待片刻！')

    def learning_task():
        is_logged_in(username, password)
        if page._d_connect:
            course_id = course_manager.get_course_id()
            page.get(f'https://www.cqooc.com/course/detail/courseStudy?id={course_id}&kkzt=true')
            page.wait.load_start(timeout=3)
            get_chapter()
        else:
            print("无法与浏览器建立连接，请检查设置。")

    current_task = threading.Thread(target=learning_task)
    current_task.start()


def stop_learning():
    global current_task
    stop_flag.set()

    # 移除 current_task.join() 以避免主线程阻塞
    # if current_task and current_task.is_alive():
        # current_task.join()

    print("学习已停止，正在关闭浏览器...")
    print("请注意，自动学习已停止！！如果想继续自动学习，请点击“开始学习”！")
    # 检查 page 是否存在且连接有效，若有效则关闭浏览器
    if page and page._d_connect:
        page.quit()


class PrintLogger:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)

    def flush(self):
        pass


def create_gui():
    global progress_bar, root
    root = tk.Tk()
    root.title("cqooc平台学习助手-v3.2  作者：QuestX")
    root.config(padx=20, pady=20)  # 增大窗口内边距，提升整体留白舒适度

    # 统一字体样式（增强视觉一致性）
    font_label = ('微软雅黑', 12)  # 标签字体
    font_entry = ('微软雅黑', 12)  # 输入框字体
    font_button = ('微软雅黑', 12, 'bold')  # 按钮字体
    log_font = ('Courier New', 10)  # 日志字体

    # 账号输入框（标签与输入框严格对齐）
    tk.Label(root, text="账号:", font=font_label).grid(
        row=0, column=0,
        padx=5, pady=5,  # 统一边距
        sticky=tk.E  # 标签右对齐
    )
    username_entry = tk.Entry(root, font=font_entry, width=20)  # 适当加宽输入框
    username_entry.grid(
        row=0, column=1,
        padx=5, pady=5,
        sticky=tk.W  # 输入框左对齐，紧贴标签
    )

    # 密码输入框（与账号输入框布局一致）
    tk.Label(root, text="密码:", font=font_label).grid(
        row=1, column=0,
        padx=5, pady=5,
        sticky=tk.E
    )
    password_entry = tk.Entry(root, font=font_entry, show="*", width=20)
    password_entry.grid(
        row=1, column=1,
        padx=5, pady=5,
        sticky=tk.W
    )

    # 课程选择区域（标签与下拉框间距优化）
    tk.Label(root, text="课程:", font=font_label).grid(
        row=2, column=0,
        padx=5, pady=5,
        sticky=tk.E
    )
    course_manager = CourseManager()
    course_manager.get_course_selection(root)  # 下拉框在CourseManager中定义

    # 日志显示区域（增加边框，提升辨识度）
    log_frame = tk.Frame(root, bd=1, relief=tk.SOLID)  # 添加边框
    log_frame.grid(row=3, column=0, columnspan=2, pady=15, sticky=tk.NSEW)
    log_text = scrolledtext.ScrolledText(log_frame,
                                         width=60, height=15,
                                         font=log_font,
                                         wrap=tk.WORD
                                         )
    log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # 将标准输出重定向到日志文本框
    sys.stdout = PrintLogger(log_text)

    # 进度条（调整长度，居中显示）
    progress_bar = Progressbar(root,
                               orient=tk.HORIZONTAL,
                               length=400,  # 稍长于输入框区域
                               mode='determinate'
                               )
    progress_bar.grid(row=4, column=0, columnspan=2, pady=10, sticky=tk.EW)

    # 按钮区域（对称居中布局，使用框架统一管理）
    button_frame = tk.Frame(root)
    button_frame.grid(row=5, column=0, columnspan=2, pady=15)

    start_button = tk.Button(button_frame,
                             text="开始学习",
                             command=lambda: start_learning(username_entry, password_entry, log_text, course_manager),
                             font=font_button,
                             width=12,
                             bg="#4CAF50",
                             fg="white"
                             )
    start_button.pack(side=tk.LEFT, padx=15)  # 左按钮，适当增加间距

    stop_button = tk.Button(button_frame,
                            text="停止学习",
                            command=stop_learning,
                            font=font_button,
                            width=12,
                            bg="#f44336",
                            fg="white"
                            )
    stop_button.pack(side=tk.LEFT, padx=15)  # 右按钮，与左按钮对称

    # 列配置（确保两列等宽，组件居中）
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    for row in range(6):
        root.rowconfigure(row, weight=1)

    root.mainloop()

if __name__ == '__main__':
    create_gui()
