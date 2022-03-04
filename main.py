#!/usr/local/bin/python3.8
# -*- coding: utf-8 -*-
"""
                    $ read me $
    这是一个通过键盘上下左右移动选中常用命令，使用回车或空格执行命令的脚本.

    ### 使用方法:
        1.使用上下左右或者hjkl键移动选择命令，如何按空格或回车执行命令
        2.直接按对应数字也可执行对应命令

    ### 添加自定义命令:
        1.功能名称 func_${func}_${name}，简要显示要执行的功能
        2.命令执行 cmd_${func}_${name}，命令执行变量命名需要和功能变量命名名称一致
        3.将所有功能变量 func_${func}_${name} 添加到 func_${func} 功能列表中
        4.将新定义的功能列表 func_${func} 添加到 func_list 列表中

    ### 注意：
        1.默认执行文件需要修改成当前python3路径
        1.所有功能变量命名需要和功能名称一致，使用cmd_和func_前缀
        2.命令是在在终端新开一个线程执行的，不会读取环境变量
        3.使用subprocess.Popn(..., env=None)参数可以读取环境变量env，但是不能读取临时环境变量set中的值

"""

import datetime
import os
import re
import signal
import shlex
import subprocess

input_key = ""
current_col = 0  # 当前列
current_row = 0  # 当前行
max_row = 0  # 最大行
max_col = 0  # 最大列

# 编译相关参数
app_name = "MyRecorder"
build_dir = "/media/root/WorkSpace/TX105_MT6762/20220208/alps/"
package_name = "com.bird.myrecorder"
main_activity = package_name + ".activities.MainActivity"
out_dir = "out/target/product/k62v1_64_bsp/system/app/"
cmd_build_mode_reinstall = "adb root && adb remount && adb shell mkdir -p /system/app/{0} && adb push {1}{0}/{0}.apk \
system/app/{0}/{0}.apk && adb shell pm install -r /system/app/{0}/{0}.apk && adb shell am start  {2}/{3}".format(
    app_name, out_dir, package_name, main_activity)
cmd_build_mode_rebuild = "mmm packages/bird_app/{0}/ &&{1}".format(app_name, cmd_build_mode_reinstall)
cmd_build_mode_build = 'bash -c "source ./build/envsetup.sh && lunch 91 && {0}"'.format(cmd_build_mode_rebuild)
cmd_build_mode_rebuild = 'bash -c "{0}"'.format(cmd_build_mode_rebuild)     # 无法读取临时环境变量，不能实现
cmd_build_R = "./mk -ud tx105c_demo_5mc4ch_elink_1600x720_r128_16_p01_sn15_v00 R"  # 105编译mk
# 编译相关信息显示
func_build_title = "adb编译"
func_build_mode_reinstall = "重装" + app_name
func_build_mode_rebuild = "编译并重装" + app_name  # 无法实现，移除
func_build_mode_build = "编译" + app_name
func_build_R = "R编译"
func_build = [func_build_title, func_build_mode_reinstall, func_build_mode_build, func_build_R]

# mtklog相关参数
dst_dir = "/tmp/mtklog/"
cmd_log_start = "adb shell am start com.mediatek.mtklogger/com.mediatek.mtklogger.MainActivity"
cmd_log_pull = "adb pull /sdcard/mtklog/mobilelog/ " + dst_dir
dst_dir += "*"  # 没有指定文件名，则打开所有文件
cmd_log_edit = "nvim " + dst_dir + "/APLog_20*/main_log_*"
cmd_log_runtime = "adb logcat -v time | grep -E 'AndroidRuntime|FATAL|denied.*myrecorder'"
# mtklog相关信息显示
func_log_title = "mtklog"
func_log_start = "启动mtklog"
func_log_pull = "拉取mtklog/mobilelog"
func_log_edit = "查看日志"
func_log_runtime = "AndroidRuntime日志"
func_log = [func_log_title, func_log_start, func_log_pull, func_log_edit, func_log_runtime]

# 脚本文件相关参数
exe_path = "/usr/bin/lym"
cmd_script_slink = "ln -s " + os.path.abspath(__file__) + " " + exe_path + " && chmod +x " + exe_path
# 脚本文件相关信息显示
func_script_title = "脚本文件"
func_script_slink = "软链接到/usr/bin/lym"
func_script = [func_script_title, func_script_slink]

# 总结
local_keys = locals().copy()
func_list = [func_build, func_log, func_script]     # 新加的功能列表（数组）放这里
proc_list = []


# # 把变量名还给变量-->数组中的元素不能转换成对应的变量
# def varname(p):
#     for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
#         # m = re.search(r'\bvarname\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
#         m = re.search(r'(?<=varname)\s*\(\s*([A-Za-z_\[\]][\[\]A-Za-z0-9_]*)\s*\)', line)
#         print(line)
#     if m:
#         return m.group(1)


def exec_func():
    global dst_dir
    for key, var in local_keys.items():
        # print(key, var)
        if var == func_list[current_col][current_row]:
            # 执行后会改变的变量
            current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # 获取当前时间current_time
            dst_dir = "/tmp/mtklog/" + current_time
            # 将字符变量转换成命令执行
            func2cmd = "cmd" + re.search(r"(?<=func)_.*", key).group(0)
            print("\033[34;1m{}\033[0m".format("执行：" + local_keys.get(func2cmd)))  # 打印蓝色字体
            # 子终端执行，使用subprocess替代
            os.system(local_keys.get(func2cmd))       # 无返回值
            # ret = os.popen(local_keys.get(func2cmd))  # 有返回值
            # 终端子shell执行，subprocess有大量自定义选项
            # subprocess.call(local_keys.get(func2cmd), close_fds=False, shell=True, env=None)
            # sub_proc = subprocess.Popen(local_keys.get(func2cmd), close_fds=False, shell=True, env=None,
            #                             stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            # proc_list.append(sub_proc.pid)    # 使用subprocess且有长时间执行的命令时可以放开注释，使用ctrl-c结束所有运行的命令


# 显示func_list的全部内容
def show_func_list():
    global func_list
    global current_row
    global current_col
    for col in range(len(func_list)):
        if col == current_col:
            print("\033[32;1m{}\033[0m".format(func_list[col][0]), end="\t")
        else:
            print(func_list[col][0], end="\t")
    print("")
    for raw in range(len(func_list[current_col])):
        item = str(raw) + "." + func_list[current_col][raw]
        if raw == 0:  # 标题不重复打印
            continue
        elif raw == current_row:
            print("\033[32;1m{}\033[0m".format(item))
        else:
            print(item)


if os.name == 'nt':
    import msvcrt


    def get_char():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)


    def get_char():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def move(diff_col, diff_row):
    global current_row
    global current_col
    global max_row
    current_row += diff_row
    current_col += diff_col
    current_col %= max_col
    max_row = len(func_list[current_col])
    current_row %= max_row
    if current_row == 0 and max_row > 0:
        current_row = 1


def main():
    global input_key
    global current_row
    global current_col
    global max_col
    global max_row
    max_col = len(func_list)
    max_row = len(func_list[current_col])
    move(0, 0)  # 初始化
    while True:
        # os.system("clear")
        print("")
        show_func_list()
        input_key = get_char()
        if input_key == "h" or input_key == "H":
            move(-1, 0)
        elif input_key == "j" or input_key == "J":
            move(0, 1)
        elif input_key == "k" or input_key == "K":
            move(0, -1)
        elif input_key == "l" or input_key == "L":
            move(1, 0)
        elif input_key == "[":  # 上下左右前缀符
            second_key = get_char()
            if second_key == "B":  # 下移
                move(0, 1)
            elif second_key == "A":  # 上移
                move(0, -1)
            elif second_key == "C":  # 右移
                move(1, 0)
            elif second_key == "D":  # 左移
                move(-1, 0)
        elif input_key == "g":  # 回到第一行
            second_key = get_char()
            if second_key == "g":
                if max_row >= 1:
                    current_row = 1
        elif input_key == "G":  # 回到最后一行
            current_row = max_row - 1
        elif input_key == "\n" or input_key == "\r" or input_key == " ":
            print("\033[34;1m{}\033[0m".format("执行：" + func_list[current_col][current_row]))  # 打印蓝色字体
            exec_func()
        elif input_key == "q" or input_key == "Q":
            break
        # ctrl-c
        elif input_key == "\x03":
            for (pid, proc) in enumerate(proc_list):
                os.kill(proc, signal.SIGKILL)
            proc_list.clear()
            print("\033[31;1m{}\033[0m".format("退出所有子线程！"))
        else:
            if input_key in map(str, range(1, max_row)):
                current_row = int(input_key)
                print("\033[34;1m{}\033[0m".format("执行：" + func_list[current_col][current_row]))
                exec_func()
            else:
                print("Invalid input:'" + input_key + "'")


if __name__ == "__main__":
    main()
