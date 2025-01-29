import tkinter as tk

root = tk.Tk()
print(f"Ventanas activas antes: {len(root.tk.eval('winfo children .').split())}")

new_win = tk.Toplevel(root)
print(f"Ventanas activas después: {len(root.tk.eval('winfo children .').split())}")

root.mainloop()
