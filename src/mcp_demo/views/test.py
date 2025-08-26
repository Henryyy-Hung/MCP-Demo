import sys
import ctypes
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk  # 导入 ttk 模块

def modern_input_dialog(
        message,
        title="请输入",
        win_width=400,    # 整个窗口的固定宽度
        padding=25        # 四周间距
    ) -> str:
    # ----- DPI 感知（仅 Windows）-----
    if sys.platform == "win32":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except:
                pass

    root = tk.Tk()
    root.withdraw()
    # 设置缩放比例（默认 1.0，可设为 1.25 等用于高分屏）
    root.tk.call('tk', 'scaling', 1.0)

    result = {'value': None}
    win = tk.Toplevel(root)
    win.title(title)
    win.resizable(False, False)
    win.configure(bg="#FFFFFF")
    win.attributes("-topmost", True)
    win.grab_set()

    if sys.platform == "win32":
        # 必须先强制更新窗口布局和创建，否则 hwnd 不可用或修改失败
        win.update_idletasks()  # 这一步非常重要！
        GWL_STYLE = -16
        WS_MINIMIZEBOX = 0x00020000
        WS_MAXIMIZEBOX = 0x00010000
        WS_SYSMENU = 0x00080000
        # 获取原生窗口句柄
        hwnd = ctypes.windll.user32.GetParent(win.winfo_id())
        # 读取当前窗口样式
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        # 移除最小化和最大化按钮，保留系统菜单（含关闭按钮）
        new_style = (style & ~WS_MINIMIZEBOX & ~WS_MAXIMIZEBOX) | WS_SYSMENU
        # 写回新的样式
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, new_style)
        # 可选：刷新窗口非客户区（标题栏）
        ctypes.windll.user32.SetWindowPos(
            hwnd,
            0,  # Z顺序
            0, 0, 0, 0,  # 位置大小不变
            0x0001 | 0x0002 | 0x0040  # SWP_NOMOVE | SWP_NOSIZE | SWP_FRAMECHANGED
        )

    # —— 所有字体都加粗 ——
    f_msg = tkFont.Font(family="Arial", size=16, weight="bold")
    f_ent = tkFont.Font(family="Arial", size=16, weight="bold")
    f_btn = tkFont.Font(family="Arial", size=16, weight="bold")

    # 计算 wraplength：窗口宽度减去左右 padding
    wrap_len = win_width - padding * 2

    # 提示消息标签
    lbl = tk.Label(
        win,
        text=message,
        font=f_msg,
        fg="#333",
        bg="#FFF",
        wraplength=wrap_len,
        justify="left"
    )
    lbl.pack(padx=padding, pady=(padding, 20), anchor="w")

    # 输入框
    style = ttk.Style()
    style.theme_use('default')  # 使用默认主题便于自定义
    style.configure(
        'Modern.TEntry',
        padding=(8, 6),        # 左右 15px 内边距，上下 10px（可选）
        relief='solid'
    )
    style.map('Modern.TEntry',
        fieldbackground=[('', '#F9F9F9')],
        foreground=[('', '#000')],
        background=[('', '#F9F9F9')]
    )
    entry = ttk.Entry(
        win,
        font=f_ent,
        style='Modern.TEntry'
    )
    entry.pack(padx=padding, pady=(0, padding), fill="x")
    entry.focus_set()

    # 按钮容器（填满整行，用于右对齐布局）
    frm = tk.Frame(win, bg="#FFF")
    frm.pack(fill="x", padx=padding, pady=(0, padding))

    def on_ok(e=None):
        result['value'] = entry.get()
        win.destroy()

    def on_cancel(e=None):
        win.destroy()

    def make_btn(master, text, cmd, bg, fg):
        return tk.Button(
            master, text=text, command=cmd,
            font=f_btn, bg=bg, fg=fg,
            bd=0,
            padx=20,  # 增大宽度
            pady=8,
            activebackground=bg,
            activeforeground=fg
        )

    # 创建按钮（注意：先创建的按钮会出现在右边的左边，所以先创建“取消”）
    btn_cancel = make_btn(frm, "取消", on_cancel, "#DDD", "#333")
    btn_ok = make_btn(frm, "确认", on_ok, "#008CBA", "#FFF")

    # 按顺序从右向左打包（右对齐）
    btn_cancel.pack(side="right")
    btn_ok.pack(side="right", padx=(0, 25))  # 两个按钮之间加点空隙

    # 键盘快捷键
    win.bind("<Return>", on_ok)
    win.bind("<Escape>", on_cancel)

    # 更新布局以获取实际高度
    win.update_idletasks()
    hh = win.winfo_height()
    ww = win_width

    # 居中显示
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - ww) // 2
    y = (sh - hh) // 2
    win.geometry(f"{ww}x{hh}+{x}+{y}")

    win.wait_window()
    root.destroy()
    return result['value']


# —— 测试代码 ——
if __name__ == "__main__":
    ans = modern_input_dialog(
        "请输入您的用户名，我们将用它来在系统里称呼您，欢迎使用本软件！",
        title="用户登录",
        win_width=600  # 自定义窗口宽度
    )
    print("输入结果：", ans)
