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
