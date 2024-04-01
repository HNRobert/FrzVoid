import os
import sys
import time
from tkinter import ttk, Tk
from threading import Thread


from win32gui import FindWindow, ShowWindow
from psutil import pids, Process

DEFAULT_VOID = 'DFStd.exe,DFEnt.exe,install.exe,Freeze,Deep,冰点,还原,精灵,360,安全卫士,电脑管家,鲁大师'
FRZ_DATA = 'C:/ProgramData/Frzvoid/data.ini'
FRZ_DATA_PATH = 'C:/ProgramData/Frzvoid'


class CheckFVProgress:

    def __init__(self):
        self.hwnd = FindWindow(None, 'FrzVoid')
        self.continue_this_progress = True
        if self.proc_root_on():
            self.continue_this_progress = False

    def proc_root_on(self):
        # print(GetWindowText(hwnd))
        # PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        if self.hwnd:
            try:
                ShowWindow(self.hwnd, 5)
                return True
            except:
                return False
        return False


"""
def WPDProgressRunning():
    if FindWindow(None, 'WPDefender'):
        return True
    return False
"""


def get_startup_state():
    if "--startup_visit" in sys.argv:
        return True
    return False


def writeData(name):
    global features
    features = name.split(',')
    if not os.path.exists(FRZ_DATA_PATH):
        os.makedirs(FRZ_DATA_PATH)
    with open(FRZ_DATA, 'w') as f:
        f.write(name)


def getData():
    with open(FRZ_DATA, 'r') as f:
        data = f.readlines()
        name = data[0]
        return name


def readData():
    return getData().split(',')


def startFreeze():
    previous_pids = []
    while continueKilling:
        if not FindWindow(None, 'FrzVoid'):
            break
        previous_pids = killFreeze(
            nameList=features, previousPids=previous_pids)
        time.sleep(1)


def killFreeze(nameList, previousPids):

    current_pids = pids()
    for a_pid in current_pids:
        if a_pid in previousPids:
            continue
        try:
            p = Process(a_pid)
            # or feature in p.parent().name()
            if any(feature != '' and feature in p.name() for feature in nameList):
                print('pid-%s,pname-%s' % (p.pid, p.name()))
                time.sleep(0.5)
                cmd = f'start /B tskill {p.pid}'
                os.system(cmd)
        except Exception as e:
            print(e)

    return current_pids


def mk_ui(hideRoot):

    def save_close():
        root.withdraw()
        name = targetNameEntry.get()
        writeData(name)

    def exit_program():
        global continueKilling
        continueKilling = False
        root.quit()
        root.destroy()

    root = Tk()
    if hideRoot:
        root.withdraw()
    root.geometry('365x115')
    root.title('FrzVoid')
    root.protocol('WM_DELETE_WINDOW', root.withdraw)
    targetNameLabel = ttk.Label(root, text='Target-name:')
    targetNameLabel.grid(row=0, column=0, padx=10, pady=5, sticky='NW')
    targetNameEntry = ttk.Entry(root)
    targetNameEntry.grid(row=1, column=0, padx=10, pady=0,
                         ipadx=100, sticky='NW')
    targetNameEntry.insert(0, getData())
    noticeLabel = ttk.Label(
        root, text='Notice: Enter target-name, split by ","')
    noticeLabel.grid(row=2, column=0, padx=10, pady=0, sticky='NW')
    closeBtn = ttk.Button(root, text='Exit', command=exit_program)
    closeBtn.grid(row=3, column=0, padx=10, ipadx=25, pady=5, sticky='NW')
    saveBtn = ttk.Button(root, text='Save', command=save_close)
    saveBtn.grid(row=3, column=0, padx=220, ipadx=25, pady=5, sticky='NW')
    root.bind('<Return>', save_close)
    root.mainloop()


def main():
    global features, continueKilling
    if not os.path.exists(FRZ_DATA):
        writeData(DEFAULT_VOID)
    features = readData()
    continueKilling = True
    checkpgs_result = CheckFVProgress()
    time.sleep(0.5)
    if not checkpgs_result.continue_this_progress:
        return

    hideRoot = False
    if get_startup_state():
        hideRoot = True
    startFreeze_thread = Thread(target=startFreeze, daemon=True)
    startFreeze_thread.start()
    mk_ui(hideRoot=hideRoot)


if __name__ == '__main__':
    main()
