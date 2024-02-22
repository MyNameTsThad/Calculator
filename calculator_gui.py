import math
import os, platform
import tkinter as tk
import webbrowser
from tkinter import ttk, messagebox
import re
# os.environ["QT_QPA_PLATFORM"] = "xcb"

latestAns = 0
isShowingAnswerOrEmpty = True

functionDefinitions = {
    "√": lambda number, power: f"{number} ** (1 / {power})",
    "sin": lambda number: f"math.sin({number})",
    "cos": lambda number: f"math.cos({number})",
    "tan": lambda number: f"math.tan({number})",
    "asin": lambda number: f"math.asin({number})",
    "acos": lambda number: f"math.acos({number})",
    "atan": lambda number: f"math.atan({number})",
    "log": lambda number, base: f"math.log({number}, {base})",
    "ln": lambda number: f"math.log({number}, math.e)",
    "base": lambda number, base1, base2: f"base('{number}', {base1}, {base2})",
    "!": lambda number: f"math.factorial({number})",
    "abs": lambda number: f"abs({number})",
    "round": lambda number, precision: f"round({number}, {precision})",
    "ceil": lambda number: f"math.ceil({number})",
    "floor": lambda number: f"math.floor({number})",
    "rad2deg": lambda number: f"math.degrees({number})",
    "deg2rad": lambda number: f"math.radians({number})",
    "frac": lambda number: f"{number} - math.floor({number})",
}


def open_secret():
    try:
        youtube_link = "https://youtu.be/dQw4w9WgXcQ?si=p-sywHqzrAo2Bb73"
        webbrowser.open(youtube_link)
    except Exception as e:
        print("Error:", e)


def base(number: str, base1: int, base2: int) -> int:
    # step 1: convert the number to base 10
    base10 = int(number, base1)
    # step 2: convert the number to the new base (if the converted number is 10 or greater, use letters)
    baseN = ""
    if base2 != 10:
        while base10 > 0:
            remainder = base10 % base2
            base10 //= base2
            baseN = (str(remainder) if remainder < 10 else chr(remainder + 55)) + baseN
    else:
        baseN = str(base10)

    return baseN


def update_result(value):
    result_label["text"] = value
    update_font_size()
    check_secret()


def check_secret():
    if result_label["text"] == "86084399":
        import Limbo.limbo
    if result_label["text"] == "69420":
        open_secret()


def handle_input(num):
    global isShowingAnswerOrEmpty
    result = result_label.cget("text")
    update_result(result + str(num) if not isShowingAnswerOrEmpty else str(num))
    isShowingAnswerOrEmpty = False


def handle_decimal_point():
    expr = result_label.cget("text")
    # split the expression by operators into segments
    segments = re.split(r"[+\-×÷()\[\]πAns,]", expr)
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
    # pos of first parenthesis
    first = subexpr.index("(")
    function = subexpr[:first]

    # determine the arguments based on how deep the comma is nested
    depth = 0
    arg = ""
    args = []
    for char in subexpr[first + 1:-1]:
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
    expr = re.sub(r"\[(.*)]", handle_functions, expr)

    # preprocess the expression (complex)
    #  add multiplication operator between a number and a parenthesis
    expr = re.sub(r"(\d)\(", r"\1*(", expr)
    expr = re.sub(r"(\d)\[", r"\1*[", expr)
    #  add multiplication operator between a parenthesis and a number
    expr = re.sub(r"\)(\d)", r")*\1", expr)
    expr = re.sub(r"\](\d)", r"]*\1", expr)
    #  add multiplication operator between a parenthesis and a parenthesis
    expr = re.sub(r"\)(\()", r")*(", expr)
    expr = re.sub(r"\](\()", r"]*(", expr)
    expr = re.sub(r"\)(\[)", r")*[", expr)
    expr = re.sub(r"\](\[)", r"]*[", expr)
    # remove leading zeros
    expr = re.sub(r"\b0+(\d+)", r"\1", expr)

    for i, op in enumerate(["π", "Ans", "E"]):
        #  add multiplication operator between a number and op
        expr = re.sub(fr"(\d){op}", fr"\1*{op}", expr)
        #  add multiplication operator between op and a number
        expr = re.sub(fr"{op}(\d)", fr"{op}*\1", expr)
        #  add multiplication operator between op and a parenthesis
        expr = re.sub(fr"{op}\(", fr"{op}*(", expr)
        expr = re.sub(fr"{op}\[", fr"{op}*[", expr)
        #  add multiplication operator between a parenthesis and op
        expr = re.sub(fr"\){op}", fr")*{op}", expr)
        expr = re.sub(fr"\]{op}", fr"]*{op}", expr)

    # preprocess the expression (simple)
    expr = expr.replace("×", "*")
    expr = expr.replace("÷", "/")
    expr = expr.replace("mod", "%")
    expr = expr.replace("π", "math.pi")
    expr = expr.replace("E", "math.e")
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
        pasted = re.sub(r"[^0-9+\-*/()\[\]πmodAns,.√^BCDEF]", "", clipboard)

        update_result(current + pasted if not isShowingAnswerOrEmpty else pasted)
        isShowingAnswerOrEmpty = False
    elif key == "x":
        root.clipboard_clear()
        root.clipboard_append(result_label["text"])
        clear_result()


def update_font_size():
    font_size = 25
    if len(result_label["text"]) > 40:
        font_size = 15
    if len(result_label["text"]) > 70:
        font_size = 10
    if len(result_label["text"]) > 100:
        font_size = 7
    result_label.configure(font=(font_family, font_size))


def show_about():
    messagebox.showinfo("SKILL ISSUE Calculator")


def bind_key(key, command):
    root.bind(key, lambda _: command())


root = tk.Tk()
root.option_add("*tearOff", False)
root.title("SKILL ISSUE Calculator")
root.configure(bg="#242424")
root.geometry("960x540")

font_family = "Inter"
# if os is windows, set the font to Segoe UI
# if os is posix, set the font to Inter
# if os is mac, set the font to San Francisco
if platform.system() == "Windows":
    font_family = "Segoe UI"
elif platform.system() == "Darwin":
    font_family = "San Francisco"

style = ttk.Style()
style.theme_use('alt')
style.configure('TButton', background='black', foreground='white', width=20, borderwidth=1, focusthickness=3,
                focuscolor='none')
style.map('TButton', background=[('active', 'black')])

button = ttk.Button(root, text='Quit')
button.place(relx=0.3, rely=0.4)
# remove the border of the buttons and add a little padding
style.configure("TButton", borderwidth=0, padding=10)
style.configure("Operator.TButton", foreground="white", background="#3A3A3A", font=(font_family, 14))
style.configure("Numpad.TButton", foreground="white", background="#505050", font=(font_family, 14))
style.configure("Enter.TButton", foreground="white", background="#E66100", font=(font_family, 14))
style.configure("TFrame", background="#242424")
style.configure("TLabel", background="#242424", foreground="white", font=(font_family, 25))
style.map("Operator.TButton", background=[("active", "#4A4A4A")])
style.map("Numpad.TButton", background=[("active", "#656565")])
style.map("Enter.TButton", background=[("active", "#FF7F00")])

frm = ttk.Frame(root, padding=10)
frm.configure(style="TFrame")
frm.pack(expand=True, fill=tk.BOTH)

result_label = ttk.Label(frm, text="0", justify="left", anchor="e")
result_label.grid(column=0, columnspan=10, row=0, sticky="e")
for i in range(10):
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
bind_key("e", lambda: handle_input("E"))
bind_key("E", lambda: handle_input("E"))
bind_key("m", lambda: handle_input("mod"))
bind_key("s", lambda: handle_input("[√(,2)]"))
bind_key("_", lambda: handle_input("Ans"))
bind_key("<Control-c>", lambda: cut_copy_paste("c"))
bind_key("<Control-v>", lambda: cut_copy_paste("v"))
bind_key("<Control-x>", lambda: cut_copy_paste("x"))
bind_key("A", lambda: handle_input("A"))
bind_key("B", lambda: handle_input("B"))
bind_key("C", lambda: handle_input("C"))
bind_key("D", lambda: handle_input("D"))
bind_key("E", lambda: handle_input("E"))
bind_key("F", lambda: handle_input("F"))
bind_key("a", lambda: handle_input("A"))
bind_key("b", lambda: handle_input("B"))
bind_key("c", lambda: handle_input("C"))
bind_key("d", lambda: handle_input("D"))
bind_key("e", lambda: handle_input("E"))
bind_key("f", lambda: handle_input("F"))

ttk.Button(frm, text="C", style="Operator.TButton", command=clear_result).grid(column=0, row=1, sticky="nsew", padx=3,
                                                                               pady=3)
ttk.Button(frm, text="(", style="Operator.TButton", command=lambda: handle_input("(")).grid(column=1, row=1,
                                                                                            sticky="nsew", padx=3,
                                                                                            pady=3)
ttk.Button(frm, text=")", style="Operator.TButton", command=lambda: handle_input(")")).grid(column=2, row=1,
                                                                                            sticky="nsew", padx=3,
                                                                                            pady=3)
ttk.Button(frm, text="mod", style="Operator.TButton", command=lambda: handle_input("mod")).grid(column=3, row=1,
                                                                                                sticky="nsew", padx=3,
                                                                                                pady=3)
ttk.Button(frm, text="π", style="Operator.TButton", command=lambda: handle_input("π")).grid(column=4, row=1,
                                                                                            sticky="nsew", padx=3,
                                                                                            pady=3)
ttk.Button(frm, text="√", style="Operator.TButton", command=lambda: handle_input("[√(,2)]")).grid(column=4, row=2,
                                                                                                  sticky="nsew", padx=3,
                                                                                                  pady=3)
ttk.Button(frm, text="^", style="Operator.TButton", command=lambda: handle_input("^")).grid(column=4, row=3,
                                                                                            sticky="nsew", padx=3,
                                                                                            pady=3)
ttk.Button(frm, text="base", style="Operator.TButton", command=lambda: handle_input("[base(,2,10)]")).grid(column=5,
                                                                                                           row=1,
                                                                                                           sticky="nsew",
                                                                                                           padx=3,
                                                                                                           pady=3)
ttk.Button(frm, text="sin", style="Operator.TButton", command=lambda: handle_input("[sin()]")).grid(column=6, row=1,
                                                                                                    sticky="nsew",
                                                                                                    padx=3, pady=3)
ttk.Button(frm, text="cos", style="Operator.TButton", command=lambda: handle_input("[cos()]")).grid(column=7, row=1,
                                                                                                    sticky="nsew",
                                                                                                    padx=3, pady=3)
ttk.Button(frm, text="tan", style="Operator.TButton", command=lambda: handle_input("[tan()]")).grid(column=8, row=1,
                                                                                                    sticky="nsew",
                                                                                                    padx=3, pady=3)
ttk.Button(frm, text="×10ⁿ", style="Operator.TButton", command=lambda: handle_input("×(10^)")).grid(column=5, row=2,
                                                                                                    sticky="nsew",
                                                                                                    padx=3, pady=3)
ttk.Button(frm, text="asin", style="Operator.TButton", command=lambda: handle_input("[asin()]")).grid(column=6, row=2,
                                                                                                      sticky="nsew",
                                                                                                      padx=3, pady=3)
ttk.Button(frm, text="acos", style="Operator.TButton", command=lambda: handle_input("[acos()]")).grid(column=7, row=2,
                                                                                                      sticky="nsew",
                                                                                                      padx=3, pady=3)
ttk.Button(frm, text="atan", style="Operator.TButton", command=lambda: handle_input("[atan()]")).grid(column=8, row=2,
                                                                                                      sticky="nsew",
                                                                                                      padx=3, pady=3)
ttk.Button(frm, text="x⁻¹", style="Operator.TButton", command=lambda: handle_input("^-1")).grid(column=5, row=3,
                                                                                                sticky="nsew", padx=3,
                                                                                                pady=3)
ttk.Button(frm, text="e", style="Operator.TButton", command=lambda: handle_input("E")).grid(column=6, row=3,
                                                                                            sticky="nsew", padx=3,
                                                                                            pady=3)
ttk.Button(frm, text="log", style="Operator.TButton", command=lambda: handle_input("[log(,10)]")).grid(column=7, row=3,
                                                                                                       sticky="nsew",
                                                                                                       padx=3, pady=3)
ttk.Button(frm, text="ln", style="Operator.TButton", command=lambda: handle_input("[ln()]")).grid(column=8, row=3,
                                                                                                  sticky="nsew", padx=3,
                                                                                                  pady=3)
ttk.Button(frm, text="!", style="Operator.TButton", command=lambda: handle_input("[!()]")).grid(column=5, row=4,
                                                                                                sticky="nsew",
                                                                                                padx=3, pady=3)
ttk.Button(frm, text="abs", style="Operator.TButton", command=lambda: handle_input("[abs()]")).grid(column=6, row=4,
                                                                                                    sticky="nsew",
                                                                                                    padx=3, pady=3)
ttk.Button(frm, text="round", style="Operator.TButton", command=lambda: handle_input("[round(,0)]")).grid(column=7,
                                                                                                          row=4,
                                                                                                          sticky="nsew",
                                                                                                          padx=3,
                                                                                                          pady=3)
ttk.Button(frm, text="ceil", style="Operator.TButton", command=lambda: handle_input("[ceil()]")).grid(column=8, row=4,
                                                                                                      sticky="nsew",
                                                                                                      padx=3, pady=3)
ttk.Button(frm, text="floor", style="Operator.TButton", command=lambda: handle_input("[floor()]")).grid(column=5,
                                                                                                        row=5,
                                                                                                        sticky="nsew",
                                                                                                        padx=3,
                                                                                                        pady=3)
ttk.Button(frm, text="rad2deg", style="Operator.TButton", command=lambda: handle_input("[rad2deg()]")).grid(column=6,
                                                                                                            row=5,
                                                                                                            sticky="nsew",
                                                                                                            padx=3,
                                                                                                            pady=3)
ttk.Button(frm, text="deg2rad", style="Operator.TButton", command=lambda: handle_input("[deg2rad()]")).grid(column=7,
                                                                                                            row=5,
                                                                                                            sticky="nsew",
                                                                                                            padx=3,
                                                                                                            pady=3)
ttk.Button(frm, text="frac", style="Operator.TButton", command=lambda: handle_input("[frac()]")).grid(column=8, row=5,
                                                                                                      sticky="nsew",
                                                                                                      padx=3, pady=3)

for i in range(1, 10):
    ttk.Button(frm, text=str(i), style="Numpad.TButton", command=lambda i=i: handle_input(i)).grid(column=(i - 1) % 3,
                                                                                                   row=(i - 1) // 3 + 2,
                                                                                                   sticky="nsew",
                                                                                                   padx=3, pady=3)
    bind_key(str(i), lambda i=i: handle_input(i))

ttk.Button(frm, text="0", style="Numpad.TButton", command=lambda: handle_input(0)).grid(column=0, row=5, sticky="nsew",
                                                                                        padx=3, pady=3)
bind_key("0", lambda: handle_input(0))

ttk.Button(frm, text=".", style="Operator.TButton", command=handle_decimal_point).grid(column=1, row=5, sticky="nsew",
                                                                                       padx=3, pady=3)
ttk.Button(frm, text="%", style="Operator.TButton", command=handle_backspace).grid(column=2, row=5, sticky="nsew",
                                                                                   padx=3, pady=3)

ttk.Button(frm, text="=", style="Enter.TButton", command=eval_result).grid(column=4, row=4, rowspan=2, sticky="nsew",
                                                                           padx=3, pady=3)

for i, op in enumerate([['+', '+'], ['-', '-'], ['×', '*'], ['÷', '/']]):
    ttk.Button(frm, text=op[0], style="Operator.TButton", command=lambda op=op[0]: handle_input(op)).grid(column=3,
                                                                                                          row=i + 2,
                                                                                                          sticky="nsew",
                                                                                                          padx=3,
                                                                                                          pady=3)
    bind_key(op[1], lambda op=op[0]: handle_input(op))

root.mainloop()
