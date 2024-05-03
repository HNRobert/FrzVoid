import os
import sys
import time
import tkinter.font as tk_font
from base64 import b64decode
from configparser import ConfigParser
from hashlib import md5
from tkinter import ttk, Tk, Menu, BooleanVar
from subprocess import (Popen, PIPE, CREATE_NO_WINDOW)
from threading import Thread

from win32gui import FindWindow, ShowWindow
from psutil import pids, Process

from nmico import icon as nmico_data

DEFAULT_VOID = 'a bad software\'s name|a part of another evil app\'s name'
FRZ_DATA = 'C:/ProgramData/Frzvoid/data.ini'
FRZ_REC_DICT = 'C:/ProgramData/Frzvoid/name.ini'
FRZ_DATA_PATH = 'C:/ProgramData/Frzvoid'
FRZ_ICON = 'C:/ProgramData/Frzvoid/icon.ico'


class CheckFVProgress:

    def __init__(self):
        self.hwnd = FindWindow(None, 'FrzVoid Settings')
        self.continue_this_progress = True
        if self.proc_root_on():
            self.continue_this_progress = False

    def proc_root_on(self):
        # print(GetWindowText(hwnd))
        # PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        if self.hwnd and not is_startup():
            try:
                ShowWindow(self.hwnd, 5)
                return True
            except Exception as e:
                print(e)
                return False
        elif self.hwnd:  # Is running, but on startup, then don't show its window
            return True
        return False


def turn_schedule(state: bool, result_var: BooleanVar):
    add_scd_cmd = f'schtasks /create /tn FrzVoidStartup /tr "\\"{sys.argv[0]}\\" \\"--startup_visit\\"" /sc ONLOGON /rl highest /f'
    del_sch_cmd = f'schtasks /delete /tn FrzVoidStartup /f'
    cmd = add_scd_cmd if state else del_sch_cmd
    p = Popen(cmd, stdin=PIPE, creationflags=CREATE_NO_WINDOW)
    p.communicate(input=b'y\n')
    result_var.set(get_startup_state())


def get_startup_state():
    chk_cmd = f'schtasks /query /tn FrzVoidStartup'
    return bool("".join(os.popen(chk_cmd).readlines()))


def is_startup():
    if "--startup_visit" in sys.argv:
        return True
    return False


def file_md5(file_path: str) -> str:
    if not os.path.isfile(file_path):
        return ""
    h = md5()
    with open(file_path, 'rb') as f:
        while b := f.read(8192):
            h.update(b)
    return h.hexdigest()


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
        name = data[0].rstrip('\n')
        return name


def read_data():
    return get_data().split('|')


def add_rec(item_md5: str, item_name: str):
    global md5_features, has_new_rec
    if not os.path.exists(FRZ_DATA_PATH):
        os.makedirs(FRZ_DATA_PATH)
    if item_md5 not in md5_features:
        has_new_rec = True
        md5_features += [item_md5]
        ban_state_dict[item_md5] = BooleanVar()
        ban_state_dict[item_md5].set(True)
        banned_dict.set("Name", item_md5, item_name)
        banned_dict.set("State", item_md5, "true")
        banned_dict.write(open(FRZ_REC_DICT, "w+", encoding='utf-8'))


def start_freeze():
    previous_pids = []
    while continueKilling:
        previous_pids = kill_freeze(
            previous_pids=[] if has_new_save or has_new_rec else previous_pids)
        time.sleep(1)


def kill_freeze(previous_pids, ):
    global has_new_save, has_new_rec
    has_new_save = False
    has_new_rec = False
    current_pids = pids()
    for a_pid in current_pids:
        if a_pid in previous_pids:
            continue
        try:
            p = Process(a_pid)
            p_name = p.name()
            p_pid = p.pid
            if p_pid in [0, 4]:
                continue
            p_exe = p.exe()
            p_md5 = file_md5(p_exe)
            if (any(feature != '' and feature in p_name for feature in features) or
                    any(md5_feature != '' and md5_feature == p_md5 and ban_state_dict[md5_feature].get() for md5_feature in md5_features)):
                print('pid-%s,pname-%s' % (p_pid, p_name))
                add_rec(p_md5, p_exe)
                time.sleep(0.5)
                cmd = f'start /B tskill {p_pid}'
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

    def update_banned():
        nonlocal menu_empty
        ban_menu.delete(0, 'end')
        menu_empty = True
        for md5_feature in md5_features:
            add_banned_option(md5_feature)
        if menu_empty:
            ban_menu.add_command(label='(Empty)')

    def add_banned_option(md5_feature):
        nonlocal menu_empty
        label_name = banned_dict.get("Name", md5_feature)
        if any(feature in os.path.basename(label_name) for feature in features):
            ban_menu.add_checkbutton(label=label_name, variable=ban_state_dict[md5_feature],
                                     command=lambda: set_banning_state(
                                         md5_feature, ban_state_dict[md5_feature].get()))
            menu_empty = False

    def set_banning_state(md5_feature, state):
        global has_new_rec
        if state:
            has_new_rec = True
        banned_dict.set("State", md5_feature, str(state))
        banned_dict.write(open(FRZ_REC_DICT, "w+", encoding='utf-8'))

    root = Tk()
    if hide_root:
        root.withdraw()
    root.geometry('465x135')
    root.title('FrzVoid Settings')
    root.iconbitmap(FRZ_ICON)
    root.protocol('WM_DELETE_WINDOW', root.withdraw)
    tkfont = tk_font.nametofont("TkDefaultFont")
    tkfont.config(family='Microsoft YaHei UI')
    root.option_add("*Font", tkfont)

    menu_empty = True
    for item_md5 in banned_dict.options("State"):
        ban_state_dict[item_md5] = BooleanVar()
        ban_state_dict[item_md5].set(banned_dict.getboolean("State", item_md5))

    target_name_label = ttk.Label(root, text='Targets:')
    target_name_label.grid(row=0, column=0, padx=10, pady=5, sticky='NSEW')
    target_name_entry = ttk.Entry(root)
    target_name_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=0,
                           ipadx=100, sticky='NSEW')
    target_name_entry.insert(0, get_data())
    notice_label = ttk.Label(
        root, text='Note: Enter targets, split with "|"')
    notice_label.grid(row=2, column=0, padx=10, pady=0, sticky='NSEW')
    close_btn = ttk.Button(root, text='Exit', command=exit_program)
    close_btn.grid(row=3, column=0, padx=10, ipadx=5, pady=5, sticky='NSEW')
    save_btn = ttk.Button(root, text='Save & Apply', command=save_data)
    save_btn.grid(row=3, column=1, padx=10, ipadx=25, pady=5, sticky='NSEW')
    root.bind_all('<Return>', lambda event: save_data())
    root.bind_all('<Control-s>', lambda event: save_data())
    root.grid_columnconfigure(1, weight=1, minsize=200)

    main_menu = Menu(root)
    option_menu = Menu(main_menu, tearoff=False)
    is_startup_set = BooleanVar(value=get_startup_state())
    option_menu.add_checkbutton(label="Start when any user logs in", variable=is_startup_set,
                                command=lambda: Thread(turn_schedule(is_startup_set.get(), is_startup_set)).start())
    ban_menu = Menu(main_menu, tearoff=False, postcommand=update_banned)
    main_menu.add_cascade(label="Options", menu=option_menu)
    main_menu.add_cascade(label="Banned apps tracking", menu=ban_menu)
    root.config(menu=main_menu)
    root.mainloop()


def main():
    global features, md5_features, continueKilling, has_new_save, has_new_rec, banned_dict, ban_state_dict
    checkpgs_result = CheckFVProgress()
    time.sleep(0.1)
    if not checkpgs_result.continue_this_progress:
        return

    if not os.path.exists(FRZ_DATA):
        write_data(DEFAULT_VOID)
    if not os.path.exists(FRZ_ICON):
        with open(FRZ_ICON, 'wb') as f:
            f.write(b64decode(nmico_data))
    if not os.path.exists(FRZ_REC_DICT):
        with open(FRZ_REC_DICT, 'w') as f:
            f.write("")
    banned_dict = ConfigParser()
    banned_dict.read(FRZ_REC_DICT, encoding='utf-8')
    if not banned_dict.has_section("Name"):
        banned_dict.add_section("Name")
    if not banned_dict.has_section("State"):
        banned_dict.add_section("State")

    features = read_data()
    md5_features = banned_dict.options("Name")
    ban_state_dict = {}

    continueKilling = True
    has_new_save = False

    has_new_rec = False
    start_freeze_thread = Thread(target=start_freeze, daemon=True)
    start_freeze_thread.start()
    mk_ui(hide_root=is_startup())


if __name__ == '__main__':
    main()
