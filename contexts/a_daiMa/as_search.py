#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快捷键脚本：复制key后按 Ctrl+Alt+F 自动跳到 Android Studio 全局搜索
依赖安装: pip install keyboard pyautogui pyperclip pywin32
"""

import time
import keyboard
import pyautogui
import pyperclip
import win32gui
import win32con
import ctypes

# ========== 配置 ==========
HOTKEY = 'shift'
AS_WINDOW_TITLE = 'homerunpet'
# ==========================

pyautogui.PAUSE = 0.15
pyautogui.FAILSAFE = True


def find_android_studio_hwnd():
    result = []
    def enum_callback(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        if AS_WINDOW_TITLE in title and win32gui.IsWindowVisible(hwnd):
            result.append((hwnd, title))
    win32gui.EnumWindows(enum_callback, None)
    return result


def activate_window(hwnd):
    """用 keybd_event 模拟 Alt 键绕过 Windows 前台限制"""
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.1)
    # 模拟按下 Alt，Windows 就允许切换前台窗口了
    ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)       # Alt 按下
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    ctypes.windll.user32.keybd_event(0x12, 0, 0x0002, 0)  # Alt 松开
    time.sleep(0.4)


def trigger_search():
    key = pyperclip.paste().strip()
    if not key:
        print('⚠️  剪贴板为空，请先复制key')
        return

    print(f'🔍 搜索: {key}')

    windows = find_android_studio_hwnd()
    if not windows:
        print('❌ 未找到Android Studio窗口，请确认AS已打开')
        return

    hwnd, title = windows[0]
    print(f'✅ 找到窗口: {title}')
    activate_window(hwnd)

    # 打开全局搜索
    pyautogui.hotkey('alt', 'g')
    time.sleep(0.5)

    # 清空并输入key
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.typewrite(key, interval=0.03)
    print(f'✅ 已输入到全局搜索框: {key}')


print('=' * 40)
print(f'✅ 脚本已启动')
print(f'📋 操作步骤:')
print(f'   1. 在飞书表格复制key值 (Ctrl+C)')
print(f'   2. 按 {HOTKEY.upper()} 触发搜索')
print(f'🛑 按 Ctrl+C 退出脚本')
print('=' * 40)

keyboard.add_hotkey(HOTKEY, trigger_search)
keyboard.wait()