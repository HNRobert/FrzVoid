import base64
import os
import sys
import time
import tkinter.font as tk_font
from tkinter import ttk, Tk, Menu, BooleanVar
from subprocess import (Popen, PIPE, CREATE_NO_WINDOW)
from threading import Thread
from win32gui import FindWindow, ShowWindow
from psutil import pids, Process

from nmico import icon as nmico_data

DEFAULT_VOID = 'a bad software\'s name|a part of another evil app\'s name'
FRZ_DATA = 'C:/ProgramData/Frzvoid/data.ini'
FRZ_DATA_PATH = 'C:/ProgramData/Frzvoid'
FRZ_ICON_PATH = 'C:/ProgramData/Frzvoid/icon.ico'


class CheckFVProgress:

    def __init__(self):
        self.hwnd = FindWindow(None, 'FrzVoid Settings')
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
            except Exception as e:
                print(e)
                return False
        return False


def turn_schedule(state: bool, result_var: BooleanVar):
    add_scd_cmd = f'schtasks /create /tn FrzVoidStartup /tr "{sys.argv[0]} --startup_visit" /sc ONLOGON /rl highest /f'
    del_sch_cmd = f'schtasks /delete /tn FrzVoidStartup /f'
    cmd = add_scd_cmd if state else del_sch_cmd
    p = Popen(cmd, stdin=PIPE, creationflags=CREATE_NO_WINDOW)
    p.communicate(input=b'y\n')
    result_var.set(get_startup_state())


def get_startup_state():
    chk_cmd = f'schtasks /query /tn FrzVoidStartup'
    return bool("".join(os.popen(chk_cmd).readlines()))


def is_startup():
    if "--startup_visit" in sys.argv or "--wpd" in sys.argv:
        return True
    return False


def write_data(name):
    global features, has_new_save
    features = name.split('|')
    if not os.path.exists(FRZ_DATA_PATH):
        os.makedirs(FRZ_DATA_PATH)
    with open(FRZ_DATA, 'w') as f:
        f.write(name)
    has_new_save = True


def get_data():
    with open(FRZ_DATA, 'r') as f:
        data = f.readlines()
        if not data:
            return ""
        name = data[0]
        return name


def read_data():
    return get_data().split('|')


def start_freeze():
    previous_pids = []
    while continueKilling:
        previous_pids = kill_freeze(
            name_list=features, previous_pids=[] if has_new_save else previous_pids)
        time.sleep(1)


def kill_freeze(name_list, previous_pids):
    global has_new_save
    has_new_save = False
    current_pids = pids()
    for a_pid in current_pids:
        if a_pid in previous_pids:
            continue
        try:
            p = Process(a_pid)
            if any(feature != '' and feature in p.name() for feature in name_list):
                print('pid-%s,pname-%s' % (p.pid, p.name()))
                time.sleep(0.5)
                cmd = f'start /B tskill {p.pid}'
                os.system(cmd)
        except Exception as e:
            print(e)
    return current_pids


def mk_ui(hide_root):
    def save_data():
        name = target_name_entry.get()
        write_data(name)
        save_btn.config(text="Success!")
        root.after(1000, lambda: save_btn.config(text="Save & Apply"))

    def exit_program():
        global continueKilling
        continueKilling = False
        root.quit()
        root.destroy()

    root = Tk()
    if hide_root:
        root.withdraw()
    root.geometry('465x135')
    root.title('FrzVoid Settings')
    root.iconbitmap(FRZ_ICON_PATH)
    root.protocol('WM_DELETE_WINDOW', root.withdraw)
    tkfont = tk_font.nametofont("TkDefaultFont")
    tkfont.config(family='Microsoft YaHei UI')
    root.option_add("*Font", tkfont)
    target_name_label = ttk.Label(root, text='Targets:')
    target_name_label.grid(row=0, column=0, padx=10, pady=5, sticky='NSEW')
    target_name_entry = ttk.Entry(root)
    target_name_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=0,
                           ipadx=100, sticky='NSEW')
    target_name_entry.insert(0, get_data())
    notice_label = ttk.Label(
        root, text='Note: Enter targets, split by "|"')
    notice_label.grid(row=2, column=0, padx=10, pady=0, sticky='NSEW')
    close_btn = ttk.Button(root, text='Exit', command=exit_program)
    close_btn.grid(row=3, column=0, padx=10, ipadx=5, pady=5, sticky='NSEW')
    save_btn = ttk.Button(root, text='Save & Apply', command=save_data)
    save_btn.grid(row=3, column=1, padx=10, ipadx=25, pady=5, sticky='NSEW')
    root.bind('<Return>', save_data)
    root.grid_columnconfigure(1, weight=1, minsize=200)

    main_menu = Menu(root)
    option_menu = Menu(main_menu, tearoff=False)
    is_startup_set = BooleanVar(value=get_startup_state())
    option_menu.add_checkbutton(label="Start when any user logs in", variable=is_startup_set,
                                command=lambda: Thread(turn_schedule(is_startup_set.get(), is_startup_set)).start())
    main_menu.add_cascade(label="Options", menu=option_menu)
    root.config(menu=main_menu)
    root.mainloop()


def main():
    global features, continueKilling, has_new_save
    if not os.path.exists(FRZ_DATA):
        write_data(DEFAULT_VOID)
    if not os.path.exists(FRZ_ICON_PATH):
        with open(FRZ_ICON_PATH, 'wb') as f:
            f.write(base64.b64decode(nmico_data))
    features = read_data()
    continueKilling = True
    has_new_save = False
    checkpgs_result = CheckFVProgress()
    time.sleep(0.1)
    if not checkpgs_result.continue_this_progress:
        return
    hide_root = False
    if is_startup():
        hide_root = True
    start_freeze_thread = Thread(target=start_freeze, daemon=True)
    start_freeze_thread.start()
    mk_ui(hide_root=hide_root)


if __name__ == '__main__':
    main()
