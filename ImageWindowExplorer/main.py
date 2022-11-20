import tkinter as tk
from imgcls import *


if __name__ == '__main__':
    root = tk.Tk()

    viewer = ImageViewer(root)

    viewer.initialize_interface()
    viewer.configure_layout()

    root.mainloop()
