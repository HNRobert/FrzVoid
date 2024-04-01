import time
import sys
import os
import winreg
from tkinter import Tk
from threading import Thread

from win32gui import FindWindow
from winshell import CreateShortcut

PROCESS_NAME = "FrzVoid.exe"


def get_start_menu_path():
    # 获取用户名
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    roaming_path = os.path.join(winreg.QueryValueEx(key, 'AppData')[0])
    start_menu_path = os.path.join(
        roaming_path, r"Microsoft\Windows\Start Menu\Programs")
    return start_menu_path


def set_startup():
    # 将快捷方式添加到自启动目录
    startup_path = os.path.join(get_start_menu_path(), r"StartUp")
    bin_path = r"Windows Process Defender.exe"
    shortcut_path = os.path.join(
        startup_path, r"Windows Process Defender.lnk")
    # print(sys.executable[:-1-len(sys.executable.split('\\')[-1])])
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)
    CreateShortcut(
        Path=shortcut_path,
        Target=bin_path,
        StartIn=sys.executable[:-1-len(sys.executable.split('\\')[-1])])


"""
def startProtection():
    previous_pids_data = {}
    while True:
        previous_pids_data = checkProcess(
            previousPidsData=previous_pids_data)
        time.sleep(1)


def checkProcess(previousPidsData):

    current_pids = pids()
    current_pids_data = previousPidsData
    for cur_pid in current_pids:
        if cur_pid in previousPidsData:
            continue
        current_pids_data[cur_pid] = Process(cur_pid).name()
    for pre_pid in previousPidsData:
        if pre_pid in current_pids:
            continue
        try:
            if PROCESS_NAME == previousPidsData[pre_pid]:
                print('pid-%s,pname-%s' % (pre_pid, previousPidsData[pre_pid]))
                cmd = f'{PROCESS_NAME} --startup_visit'
                os.system(cmd)
        except Exception as e:
            print(e)

    return current_pids_data
"""


def checkFVProgress():
    if FindWindow(None, 'FrzVoid'):
        print('FrzVoid is running')
        return True
    print('FrzVoid is not running')
    return False


def WPDProgressRunning():
    if FindWindow(None, 'WPDefender'):
        return True
    return False


def protectFrz():
    while True:
        if not FindWindow(None, 'WPDefender'):
            break
        if not checkFVProgress():
            try:
                cmd = f'start /B {PROCESS_NAME} --startup_visit'
                os.system(cmd)
                time.sleep(2)
            except Exception as e:
                print(e)
        else:
            time.sleep(1)
        print('Protecting')
        time.sleep(1)


def main():
    if WPDProgressRunning():
        print('WPDefender is running')
        return
    set_startup()
    root = Tk()
    root.withdraw()
    root.title('WPDefender')
    protectFrz_thread = Thread(target=protectFrz, daemon=True)
    protectFrz_thread.start()
    root.mainloop()


if __name__ == '__main__':
    main()
