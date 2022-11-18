import tkinter as tk
from imgcls import *


if __name__ == '__main__':
    root = tk.Tk()

    viewer = ImageViewer(root)

    viewer.open_image('abc.jpg')
    viewer.initialize_interface()
    viewer.configure_layout()

    root.mainloop()
