import math
import tkinter as tk
from tkinter import ttk, messagebox
import re

latestAns = 0
isShowingAnswerOrEmpty = True

functionDefinitions = {
    "√": lambda number, power: f"{number} ** (1 / {power})",
}


def update_result(value):
    result_label["text"] = value


def handle_input(num):
    global isShowingAnswerOrEmpty
    result = result_label.cget("text")
    update_result(result + str(num) if not isShowingAnswerOrEmpty else str(num))
    isShowingAnswerOrEmpty = False


def handle_decimal_point():
    expr = result_label.cget("text")
    # split the expression by operators into segments
    segments = re.split(r"[+\-*/()[]πAns,]", expr)
    # if the last segment has a decimal point, don't add another
    if not segments[-1].__contains__("."):
        update_result(expr + ".")


def handle_backspace():
    global isShowingAnswerOrEmpty
    if not len(result_label["text"]) > 1:
        isShowingAnswerOrEmpty = True
    update_result(result_label["text"][:-1] if not isShowingAnswerOrEmpty else "0")


def handle_functions(match: re.Match[str]):
    subexpr = match.group(1)
    print(f"subexpr: {subexpr}")
    # the function name is the character before the first parenthesis
    # the arguments are the characters inside the first and last parenthesis
    function = subexpr[0]
    args = subexpr[2:-1]

    # determine the arguments based on how deep the comma is nested
    depth = 0
    arg = ""
    args = []
    for char in subexpr[2:-1]:
        if char == "," and depth == 0:
            args.append(arg.strip())
            arg = ""
        else:
            arg += char
            if char in "([": depth += 1
            if char in ")]": depth -= 1
    args.append(arg.strip())

    args = list(filter(lambda x: x != "", args))

    print(f"function: {function}, args: {args}")

    # if any of the args has a function, replace it with the result of the function
    for i, arg in enumerate(args):
        args[i] = preprocess(arg)

    # if the function is defined, call it with the args
    if function in functionDefinitions:
        return "(" + functionDefinitions[function](*map(str, args)) + ")"
    else:
        return match.group(0)


def preprocess(expr: str):
    # preprocess the expression (functions)
    #  format: √(power,number) -> (number**(1/power))
    expr = re.sub(r"\[(.*)]", handle_functions, expr)
    #  format:

    # preprocess the expression (complex)
    #  add multiplication operator between a number and a parenthesis
    expr = re.sub(r"(\d)\(", r"\1*(", expr)
    #  add multiplication operator between a parenthesis and a number
    expr = re.sub(r"\)(\d)", r")*\1", expr)
    #  add multiplication operator between a parenthesis and a parenthesis
    expr = re.sub(r"\)(\()", r")*(", expr)
    # remove leading zeros
    expr = re.sub(r"\b0+(\d+)", r"\1", expr)

    for i, op in enumerate(["π", "Ans"]):
        #  add multiplication operator between a number and op
        expr = re.sub(fr"(\d){op}", fr"\1*{op}", expr)
        #  add multiplication operator between op and a number
        expr = re.sub(fr"{op}(\d)", fr"{op}*\1", expr)
        #  add multiplication operator between op and a parenthesis
        expr = re.sub(fr"{op}\(", fr"{op}*(", expr)
        #  add multiplication operator between a parenthesis and op
        expr = re.sub(fr"\){op}", fr")*{op}", expr)

    # preprocess the expression (simple)
    expr = expr.replace("mod", "%")
    expr = expr.replace("π", "math.pi")
    expr = expr.replace("^", "**")
    expr = expr.replace("Ans", str(latestAns))

    return expr


def eval_result():
    global latestAns, isShowingAnswerOrEmpty
    try:
        expr = preprocess(result_label["text"])

        print(expr)

        result = eval(expr)
        update_result(str(result))
        latestAns = result
    except Exception as e:
        print(e)
        update_result("Error: " + e.__class__.__name__)

    isShowingAnswerOrEmpty = True


def clear_result():
    global isShowingAnswerOrEmpty
    update_result("0")
    isShowingAnswerOrEmpty = True


def cut_copy_paste(key):
    global isShowingAnswerOrEmpty
    if key == "c":
        root.clipboard_clear()
        root.clipboard_append(result_label["text"])
    elif key == "v":
        clipboard = root.clipboard_get()
        current = result_label.cget("text")
        # sanitize the clipboard, only allow typable characters like digits, operators, and parentheses, and pi, mod, Ans
        pasted = re.sub(r"[^0-9+\-*/()\[\]πmodAns,.√^]", "", clipboard)

        update_result(current + pasted if not isShowingAnswerOrEmpty else pasted)
        isShowingAnswerOrEmpty = False
    elif key == "x":
        root.clipboard_clear()
        root.clipboard_append(result_label["text"])
        clear_result()


def show_about():
    messagebox.showinfo("SKILL ISSUE Calculator")


def bind_key(key, command):
    root.bind(key, lambda _: command())


root = tk.Tk()
root.option_add("*tearOff", False)
root.title("SKILL ISSUE Calculator")

style = ttk.Style()
style.configure("Operator.TButton", foreground="white", background="#3A3A3A", font=("Inter", 14))
style.configure("Numpad.TButton", foreground="white", background="#505050", font=("Inter", 14))
style.configure("Enter.TButton", foreground="white", background="#E66100", font=("Inter", 14))
style.map("Operator.TButton", background=[("active", "#4A4A4A")])
style.map("Numpad.TButton", background=[("active", "#656565")])
style.map("Enter.TButton", background=[("active", "#FF7F00")])
frm = ttk.Frame(root, padding=10)

frm.pack(expand=True, fill=tk.BOTH)

result_label = ttk.Label(frm, text="0", font=("Inter", 25), justify="left", anchor="e")
result_label.grid(column=0, columnspan=5, row=0, sticky="e")
for i in range(5):
    frm.columnconfigure(i, weight=1)

for j in range(6):
    frm.rowconfigure(j, weight=1)

# menu_bar = tk.Menu(root)
# file_menu = tk.Menu(menu_bar)
# file_menu.add_command(label="About", command=show_about)
# file_menu.add_command(label="Quit", command=root.destroy)
# menu_bar.add_cascade(label="File", menu=file_menu)
# root.config(menu=menu_bar)

bind_key("<Return>", eval_result)
bind_key("c", clear_result)
bind_key("<Escape>", clear_result)
bind_key("<BackSpace>", handle_backspace)
bind_key("Q", root.destroy)
bind_key(".", handle_decimal_point)
bind_key("^", lambda: handle_input("^"))
bind_key("(", lambda: handle_input("("))
bind_key(")", lambda: handle_input(")"))
bind_key("[", lambda: handle_input("["))
bind_key("]", lambda: handle_input("]"))
bind_key(",", lambda: handle_input(","))
bind_key("p", lambda: handle_input("π"))
bind_key("m", lambda: handle_input("mod"))
bind_key("s", lambda: handle_input("[√(,2)]"))
bind_key("_", lambda: handle_input("Ans"))
bind_key("<Control-c>", lambda: cut_copy_paste("c"))
bind_key("<Control-v>", lambda: cut_copy_paste("v"))
bind_key("<Control-x>", lambda: cut_copy_paste("x"))

ttk.Button(frm, text="C", style="Operator.TButton", command=clear_result).grid(column=0, row=1, sticky="nsew")
ttk.Button(frm, text="(", style="Operator.TButton", command=lambda: handle_input("(")).grid(column=1, row=1,
                                                                                            sticky="nsew")
ttk.Button(frm, text=")", style="Operator.TButton", command=lambda: handle_input(")")).grid(column=2, row=1,
                                                                                            sticky="nsew")
ttk.Button(frm, text="mod", style="Operator.TButton", command=lambda: handle_input("mod")).grid(column=3, row=1,
                                                                                                sticky="nsew")
ttk.Button(frm, text="π", style="Operator.TButton", command=lambda: handle_input("π")).grid(column=4, row=1,
                                                                                            sticky="nsew")
ttk.Button(frm, text="√", style="Operator.TButton", command=lambda: handle_input("[√(,2)]")).grid(column=4, row=2,
                                                                                                  sticky="nsew")
ttk.Button(frm, text="^", style="Operator.TButton", command=lambda: handle_input("^")).grid(column=4, row=3,
                                                                                            sticky="nsew")

for i in range(1, 10):
    ttk.Button(frm, text=str(i), style="Numpad.TButton", command=lambda i=i: handle_input(i)).grid(column=(i - 1) % 3,
                                                                                                   row=(i - 1) // 3 + 2,
                                                                                                   sticky="nsew")
    bind_key(str(i), lambda i=i: handle_input(i))

ttk.Button(frm, text="0", style="Numpad.TButton", command=lambda: handle_input(0)).grid(column=0, row=5, sticky="nsew")
bind_key("0", lambda: handle_input(0))

ttk.Button(frm, text=".", style="Operator.TButton", command=handle_decimal_point).grid(column=1, row=5, sticky="nsew")
ttk.Button(frm, text="%", style="Operator.TButton", command=handle_backspace).grid(column=2, row=5, sticky="nsew")

ttk.Button(frm, text="=", style="Enter.TButton", command=eval_result).grid(column=4, row=4, rowspan=2, sticky="nsew")

for i, op in enumerate(['+', '-', '*', '/']):
    ttk.Button(frm, text=op, style="Operator.TButton", command=lambda op=op: handle_input(op)).grid(column=3,
                                                                                                    row=i + 2,
                                                                                                    sticky="nsew")
    bind_key(op, lambda op=op: handle_input(op))

root.mainloop()
