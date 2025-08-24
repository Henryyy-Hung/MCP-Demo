import tkinter as tk

def dialogue(prompt: str) -> str:
    # 用来存放用户的输入结果
    result = {'value': None}
    root = tk.Tk()
    root.title("AI 的问题")
    root.resizable(False, False)  # 不允许拖动改变窗口大小
    # 先设置一个固定的“理想”窗口大小
    win_width = 300
    win_height = 150
    # 获取屏幕尺寸
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    # 计算居中的位置
    x = (screen_width - win_width) // 2
    y = (screen_height - win_height) // 2
    # 设置窗口大小及位置
    root.geometry(f"{win_width}x{win_height}+{x}+{y}")
    # 如果你想让这个窗口在最前面，可以加这一行
    root.attributes('-topmost', True)
    # --- 界面布局 ---
    # 提示文字
    lbl = tk.Label(root, text=prompt, anchor='w', justify='left')
    lbl.pack(fill='x', padx=10, pady=(20, 5))
    # 文本输入框
    v = tk.StringVar()
    entry = tk.Entry(root, textvariable=v, width=40)
    entry.pack(pady=(0, 15))
    entry.focus_set()
    # 按钮区域
    btn_frame = tk.Frame(root)
    btn_frame.pack()
    def on_ok():
        result['value'] = v.get()
        # 销毁窗口，退出 mainloop
        root.destroy()
    def on_cancel():
        # 不设置 result['value']，直接销毁窗口
        root.destroy()
    tk.Button(btn_frame, text="OK",     width=10, command=on_ok).pack(side='left', padx=5)
    tk.Button(btn_frame, text="Cancel", width=10, command=on_cancel).pack(side='left', padx=5)
    # 进入事件循环
    root.mainloop()
    # 返回结果；如果用户按了 Cancel 或者直接关窗口，则返回提示字符串
    return result['value'] if result['value'] is not None else "user reject the input request."