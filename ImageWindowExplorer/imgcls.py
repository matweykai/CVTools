import tkinter as tk
from PIL import Image, ImageTk


class MainImage:
    """Main image representation"""
    def __init__(self, image_obj: Image.Image, position_callback_lst: list[callable]):
        self.cursor_X = None
        self.cursor_Y = None
        self._raw_image = image_obj
        self.photo_image = ImageTk.PhotoImage(image_obj)
        self.position_callback_lst = position_callback_lst
        self.size = (self.photo_image.width(), self.photo_image.height())

    def mouse_move_handler(self, event):
        """Callback function on mouse movement"""
        self.cursor_X = event.x
        self.cursor_Y = event.y

        for temp_clbk in self.position_callback_lst:
            temp_clbk(self.cursor_X, self.cursor_Y)

    def crop(self, left, upper, right, bottom):
        """Crops raw image and returns """
        return ImageTk.PhotoImage(self._raw_image.crop((left, upper, right, bottom)))


class ImageViewer:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.main_image = None

        self.main_image_canvas = None
        self.small_image_canvas = None

        self.small_image = None
        self.small_image_id = None
        self.border_id = None

    def open_image(self, image_path: str):
        """Opens image from the filesystem and updates main_image field"""
        image_obj = Image.open(image_path)
        self.main_image = MainImage(image_obj, [self._draw_small_image, self._draw_border])

    def _calculate_border_coordinates(self, cursor_X, cursor_Y):
        """Calculates small image coordinates with x and y mouse coordinates"""
        left = max([0, cursor_X - 11])
        upper = max([0, cursor_Y - 11])
        right = min([cursor_X + 12, self.main_image.size[0]])
        bottom = min([cursor_Y + 12, self.main_image.size[1]])

        return left, upper, right, bottom

    def _draw_small_image(self, cursor_X, cursor_Y):
        """Draws small image. Source is under the latest mouse position"""
        left, upper, right, bottom = self._calculate_border_coordinates(cursor_X, cursor_Y)

        self.small_image = self.main_image.crop(left, upper, right, bottom)
        # Delete previous small image
        if self.small_image_id is not None:
            self.small_image_canvas.delete(self.small_image_id)
        # Draw new small image
        self.small_image_id = self.small_image_canvas.create_image((0, 0), anchor='nw', image=self.small_image)

    def _draw_border(self, cursor_X, cursor_Y):
        """Draws rectangle over the main image. Source is under the latest mouse position"""
        left, upper, right, bottom = self._calculate_border_coordinates(cursor_X, cursor_Y)

        left = max([0, left - 1])
        upper = max([0, upper - 1])
        right = min([right + 1, self.main_image.size[0]])
        bottom = min([bottom + 1, self.main_image.size[1]])

        # Delete previous rectangle
        if self.border_id is not None:
            self.main_image_canvas.delete(self.border_id)

        self.border_id = self.main_image_canvas.create_rectangle(left, upper, right, bottom,
                                                                 width=1,
                                                                 outline='black')

    def initialize_interface(self):
        """Initialises interface elements"""
        self.main_image_canvas = tk.Canvas(self.root)

        self.small_image_canvas = tk.Canvas(self.root, width=50, height=50)

    def configure_layout(self):
        # Main canvas
        self.main_image_canvas.bind('<Motion>', self.main_image.mouse_move_handler)
        self.main_image_canvas.place(x=0, y=0)
        self.main_image_canvas.create_image((0, 0), image=self.main_image.photo_image, anchor='nw')
        self.main_image_canvas.config(width=self.main_image.size[0], height=self.main_image.size[1])
        # Small canvas
        img_pos_X, img_pos_Y = self.main_image.size[0] + 20, 20
        self.small_image_canvas.place(x=img_pos_X, y=img_pos_Y)
        # Root
        self.root.geometry(f'{self.main_image.size[0] + 100}x{self.main_image.size[1]}')
        self.root.resizable(False, False)
