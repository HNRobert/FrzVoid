from win32gui import FindWindow, GetWindowText, PostMessage
from win32con import WM_CLOSE


hwnd = FindWindow(None, 'WPDefender')
print(GetWindowText(hwnd))
PostMessage(hwnd, WM_CLOSE, 0, 0)
hwnd = FindWindow(None, 'FrzVoid')
print(GetWindowText(hwnd))
PostMessage(hwnd, WM_CLOSE, 0, 0)
