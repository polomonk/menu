#!/usr/bin/env python3
# coding=utf-8
"""
                    $ read me $
    记录了常用命令，使用回车或空格执行命令.
    ### 使用方法:
        1.使用上下左右或者hjkl键移动选择命令，如何按空格或回车执行命令
        2.直接按对应数字也可执行对应命令
    ### 注意：
        1.默认执行文件需要修改成当前python3路径
        2.命令是在在终端新开一个线程执行的，不会读取临时环境变量
"""

import os
import signal
from abc import ABC, abstractmethod

if os.name == 'nt':  # windows
    import msvcrt
    from colorama import Fore, Back, Style, init

    init(autoreset=True)


    def get_char():
        return msvcrt.getch().decode()


    def print_green(to_paint, end="\r\n"):
        print(Fore.GREEN + to_paint, end=end)


    def print_blue(to_paint, end="\r\n"):
        print(Fore.BLUE + to_paint, end=end)


    def print_red(to_paint, end="\r\n"):
        print(Fore.RED + to_paint, end=end)

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


    class ColorType:
        default = "\033[0m"
        green = "\033[32;1m"
        blue = "\033[34;1m"
        red = "\033[31;1m"


    def print_green(to_paint):
        print(ColorType.green + to_paint + ColorType.default)


    def print_blue(to_paint):
        print(ColorType.blue + to_paint + ColorType.default)


    def print_red(to_paint):
        print(ColorType.red + to_paint + ColorType.default)


class Observer(ABC):
    def __init__(self):
        pass

    # @abstractproperty
    def notify(self):
        pass


class Observable:
    def __init__(self):
        self.observers = []

    def add_observer(self, observer: Observer):
        self.observers.append(observer)

    # @abstractproperty
    def notify(self):
        for observer in self.observers:
            observer.notify()


class MutableValue(Observable):
    def __init__(self, value=""):
        super().__init__()
        self.value = value

    def __add__(self, other):
        return self.value + other.value

    def __radd__(self, other):
        if hasattr(other, 'value'):
            return str(self.value + other.value)
        else:
            try:
                s = str(other)
            except:
                s = ""
            return s + self.value

    def __iadd__(self, other):
        return self.value + other.value

    def __repr__(self):
        return self.value

    def __str__(self):
        return self.value

    def set_value(self, value: str):
        self.value = value
        self.notify()
        # print("MutableValue.set_value:"+self.value)

    def get_value(self):
        return self.value

    # def notify(self):
    #     pass


class ItemComponent(Observer, ABC):
    def __init__(self, name, *args):
        super().__init__()
        self.item_list: list[ItemComponent] = []
        self.name = name
        self.executor: BaseExecutor() = None
        # self.observer: Observer() = None

    def add(self, item):
        self.item_list.append(item)
        return self

    def append(self, item):
        self.item_list.append(item)
        return self

    def len(self):
        return len(self.item_list)

    def set_executor(self, executor):
        self.executor = executor
        return self

    def exec(self):
        raise Exception

    def subscribe(self, observable: Observable):
        if observable is not None:
            observable.add_observer(self)
            return self


class CmdItem(ItemComponent):
    def notify(self):
        self.cmd = " ".join(self.cmd_parts)

    def __init__(self, name, cmd_parts: list = None):
        super().__init__(name=name)
        self.cmd_parts = None  # 占位
        self.set_cmd_parts(cmd_parts)
        self.executor: CmdExecutor() = CmdExecutor()

    def get_cmd(self):
        # self.cmd = "".join(self.cmd_parts)
        cmd = ""
        for i in self.cmd_parts:
            cmd += i
        return cmd

    def set_cmd(self, cmd: str):
        self.cmd_parts = [cmd]
        return self

    def set_cmd_parts(self, parts: list):
        self.cmd_parts = parts
        if self.cmd_parts is None:
            self.cmd_parts = [""]
            return
        # self.cmd = "".join(self.cmd_parts)
        self.cmd_parts = parts
        return self

    def exec(self):
        self.executor.execute(self.get_cmd())


class InputCmdItem(CmdItem):
    def __init__(self, name):
        super().__init__(name=name)
        self.executor = InputExecutor()


class ItemMutableValue(ItemComponent):
    def __init__(self, name, mutable_value: MutableValue(), value: str):
        super().__init__(name=name)
        self.mutable_value: MutableValue() = mutable_value
        self.executor: MutableValueExecutor() = MutableValueExecutor()
        self.value = value
        # print("itemMutableValue:"+self.value)

    def set_mutable_value(self, mutable_value: MutableValue()):
        self.mutable_value = mutable_value
        return self

    # def set_value(self, value):
    #     self.value = value
    #     return self

    def exec(self):
        # print("itemMutableValue exec params:"+self.value)
        self.executor.execute(self.mutable_value, self.value)


class SettingItem(ItemComponent):
    def __init__(self, name, mutable_value: MutableValue() = None, optionals: list = None):
        super().__init__(name=name)
        self.mutable_value: MutableValue() = mutable_value
        self.optionals = optionals
        self.executor: SettingExecutor() = SettingExecutor()
        self.subscribe(mutable_value)

    def bind_mutable_value(self, mutable_value: MutableValue()):
        self.mutable_value = mutable_value
        return self

    def set_optionals(self, optionals):
        self.optionals = optionals
        return self

    def exec(self):
        self.executor.execute(self.name, self.mutable_value, self.optionals)


class TitleItem(ItemComponent):
    pass


class RootItem(ItemComponent):
    def get_title(self, col):
        return self.item_list[col]

    def get_item(self, col, row):
        if self.len() >= col and self.item_list[col].len() >= row:
            return self.item_list[col].item_list[row]
        else:
            return None

    def item_count(self, col):
        return self.item_list[col].len()

    def max_item_count(self):
        max_item = 0
        for t in self.item_list:
            max_item = max(max_item, t.len())
        return max_item


class BaseExecutor(ABC):
    @abstractmethod
    def execute(self, *args):
        raise Exception


class CmdExecutor(BaseExecutor):
    def execute(self, cmd):
        print_blue("执行:" + cmd)
        os.system(cmd)  # 无返回值


class InputExecutor(BaseExecutor):
    def execute(self, cmd):
        print_blue("执行:" + cmd, end="")
        cmd = cmd + input(Fore.CYAN)
        print_blue(Fore.WHITE, end="")
        os.system(cmd)  # 无返回值


class SettingExecutor(BaseExecutor):
    def execute(self, name: str, mutable_value: MutableValue, optionals: list):
        g.stack.append(root.item_list)
        root.item_list = []
        title = TitleItem(name)
        root.item_list.append(title)
        for option in optionals:
            title.item_list.append(ItemMutableValue(str(option), mutable_value, str(option)))
        g.current_row = 0  # 符合用户直觉
        update_showing()


class MutableValueExecutor(BaseExecutor):
    def execute(self, mutable_value: MutableValue, value):
        mutable_value.set_value(value)
        root.item_list = g.stack.pop()
        update_showing()


class InterceptorComponent(ABC):
    def __init__(self):
        self._next: InterceptorComponent = None

    @abstractmethod
    def set_next(self, interceptor):
        pass

    def intercept(self, key: str):
        pass


class BaseInterceptor(InterceptorComponent):
    def set_next(self, interceptor: InterceptorComponent):
        self._next = interceptor
        return self._next


class MoveInterceptor(BaseInterceptor):

    def intercept(self, key: str):
        if key == "h" or key == "H":
            move(-1, 0)
        elif key == "j" or key == "J":
            move(0, 1)
        elif key == "k" or key == "K":
            move(0, -1)
        elif key == "l" or key == "L":
            move(1, 0)
        elif key == "[":  # 上下左右前缀符
            second_key = get_char()
            if second_key == "B":  # 下移
                move(0, 1)
            elif second_key == "A":  # 上移
                move(0, -1)
            elif second_key == "C":  # 右移
                move(1, 0)
            elif second_key == "D":  # 左移
                move(-1, 0)
        else:
            self._next.intercept(key)


class JumpInterceptor(BaseInterceptor):

    def intercept(self, key: str):
        if key == "g":  # 回到第一行
            second_key = get_char()
            if second_key == "g":
                if g.max_row >= 1:
                    g.current_row = 0
        elif key == "G":  # 回到最后一行
            g.current_row = g.max_row - 1
        else:
            self._next.intercept(key)


class ExecInterceptor(BaseInterceptor):
    def intercept(self, key: str):
        if key == "\n" or key == "\r" or key == " ":
            exec_item()
        elif key in map(str, range(1, g.max_row)):
            g.current_row = int(key)
            exec_item()
        # ctrl-c
        elif key == "\x03":
            for (pid, proc) in enumerate(g.proc_list):
                os.kill(proc, signal.SIGKILL)
            g.proc_list.clear()
            print_red("退出所有子线程！")
        elif key == "q" or key == "Q":
            exit(0)
        else:
            self._next.intercept(key)


class ErrorInterceptor(BaseInterceptor):
    def intercept(self, key: str):
        print_red("Invalid input:'" + g.input_key + "'")
        # self._next.intercept(str)


class GlobalValue:
    input_key = ""
    current_col = 0  # 当前列
    current_row = 0  # 当前行
    max_row = 0  # 最大行
    max_col = 0  # 最大列
    current_max_row = 0  # 当前列
    stack = []
    proc_list = []


g = GlobalValue()

mv_apk_path = MutableValue()
mv_apk_name = MutableValue()
mv_activity_in_package = MutableValue()
mv_device_id = MutableValue()
mv_apk_package = MutableValue()

root = RootItem("root")
root.add(TitleItem("设置")
         .add(SettingItem("指定设备", mv_device_id, ["-s PDG10A0100001", "-s 2", "-s 3"]))
         .add(SettingItem("mv_apk目录", mv_apk_path,
                          ["D:\AndroidProject\CameraMonitor\CameraMonitor\systemSign5.1", "ads", "2d"]))
         .add(SettingItem("mv_apk包名", mv_apk_path, ["com.cv.cameramonitor", "ads", "2d"]))
         .add(SettingItem("mv_activity名", mv_activity_in_package, ["ui.CameraActivity", "ads", "2d"]))
         .add(SettingItem("mv_apk名字", mv_apk_name, ["app-debug_OS5.1_signed.apk", "ads", "2d"])))
root.add(TitleItem("adb命令")
         .add(CmdItem("获取权限", ["adb ", mv_device_id, " root"]))
         .add(CmdItem("重新挂载", ["adb ", mv_device_id, " remount"]))
         .add(CmdItem("安装mv_apk", ["adb ", mv_device_id, " install -r ", mv_apk_path]))
         .add(CmdItem("签名mv_apk", [""]))
         .add(CmdItem("启动mv_apk", ["adb shell am start ", mv_apk_package, ".MainActivity"])))
# .add(ItemCmd("安装系统目录下mv_apk", "adb shell pm install -r /system/app/{0}/{0}.mv_apk".format(mv_apk_name.value))))

root.add(TitleItem("git操作")
         .add(CmdItem("代码状态").set_cmd("git status"))
         .add(CmdItem("全部添加到git缓存").set_cmd("git add ."))
         .add(CmdItem("git log").set_cmd("git log"))
         .add(CmdItem("提交代码").set_cmd("git commit -m ").set_executor(InputExecutor()))
         .add(CmdItem("修正上次提交").set_cmd("git commit --amend")))

exe_path = "/usr/bin/lym"
root.add(TitleItem("其他命令")
         # .add(ItemCmd("添加到环境变量", 'setx path "Scripts;%path%;{}" /m'.format(os.path.abspath(__file__))))
         .add(CmdItem("添加到环境变量", ['setx path "Scripts;%path%;', os.path.dirname(__file__), ";"]))
         .add(CmdItem("链接", ["ln -s ", os.path.abspath(__file__), " ", exe_path + " && chmod +x " + exe_path])))


def exec_item():
    # current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # 获取当前时间current_time
    item = root.get_item(g.current_col, g.current_row)
    if item is not None:
        print_blue("执行：" + root.get_item(g.current_col, g.current_row).name)  # 打印蓝色字体
        item.exec()


# 显示func_list的全部内容
def show_item_list():
    for title in root.item_list:
        if g.current_col == root.item_list.index(title):
            print_green(title.name, end="\t")
        else:
            print(title.name, end="\t")
    print("")
    count = 1
    for item in root.get_title(g.current_col).item_list:
        if item is None:
            continue
        item2print = str(count) + "." + item.name
        count += 1
        if g.current_row == root.item_list[g.current_col].item_list.index(item):
            print_green(item2print)
        else:
            print(item2print)
    # 补齐行数
    for i in range(g.max_row - g.current_max_row):
        print("")


def move(diff_col, diff_row):
    g.current_row += diff_row
    g.current_col += diff_col
    g.current_col %= g.max_col
    g.current_max_row = root.get_title(g.current_col).len()
    g.current_row %= g.current_max_row


def update_showing():
    g.max_col = root.len()
    g.max_row = root.max_item_count()
    move(0, 0)  # 初始化


def main():
    update_showing()
    interceptor = MoveInterceptor()
    interceptor.set_next(JumpInterceptor()) \
        .set_next(ExecInterceptor()) \
        .set_next(ErrorInterceptor())
    while True:
        # os.system("clear")
        print("")
        show_item_list()
        g.input_key = get_char()
        interceptor.intercept(g.input_key)


if __name__ == "__main__":
    main()
