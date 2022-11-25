import tkinter as tk
from videoanalysing import SimpleVideoAnalyser
from PIL import ImageTk, Image
import cv2


class VideoAnalyzerGUI:
    """ Controls all gui interactions with the app """
    def __init__(self, root: tk.Tk):
        self.root = root
        self.video_frame = None
        self.video_canvas = None
        self.information_frame = None
        self.raw_canvas = None
        self.norm_canvas = None
        self.labels_frame = None

    def _open_video(self, path):
        """ Open video and update video_obj instance """
        self.video_analyzer = SimpleVideoAnalyser(path)
        self.video_obj = self.video_analyzer.video_obj

    def show_video(self):
        """ Shows video in the video frame widget """
        self._update_video_frame()

    def update_raw_plot(self):
        pass

    def update_norm_plot(self):
        pass

    def _update_video_frame(self):
        """ Updates video frame in Canvas widget """
        ret, frame = self.video_obj.read()

        if ret:
            # Convert color from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            image = Image.fromarray(frame)
            # Optimize video frame size
            image.thumbnail(size=(self.video_frame.winfo_width(),
                                  self.video_frame.winfo_height()))

            self.photo = ImageTk.PhotoImage(image=image)
            self.video_canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        else:
            # Repeat video
            self.video_obj.set(cv2.CAP_PROP_POS_FRAMES, 0)
        # Repeat this function after some time
        self.root.after(50, self._update_video_frame)

    def configure_layout(self):
        """ Initialises and configures all widgets """
        root_height = self.root.winfo_height()
        root_width = self.root.winfo_width()

        # Video frame configuration
        self.video_frame = tk.Frame(self.root)
        self.video_frame.config(height=int(0.95 * root_height), width=int(0.95 * root_height * 4 / 3), borderwidth=2, relief='groove')
        self.video_frame.place(x=0, y=0)
        self.video_frame.update()

        t_width = self.video_frame.winfo_width()
        t_height = self.video_frame.winfo_height()

        self.video_canvas = tk.Canvas(self.video_frame,
                                      width=t_width,
                                      height=t_height)
        self.video_canvas.place(x=0, y=0)

        # Information frame configuration
        self.information_frame = tk.Frame(self.root)
        self.information_frame.config(height=root_height, width=root_width - self.video_frame.winfo_width(), borderwidth=2, relief='groove')
        self.information_frame.place(x=self.video_frame.winfo_width(), y=0)

        # Raw canvas configuration
        self.information_frame.update()
        inf_frame_height = self.information_frame.winfo_height()
        inf_frame_width = self.information_frame.winfo_width()

        self.raw_canvas = tk.Canvas(self.information_frame)
        self.raw_canvas.config(height=3/7 * inf_frame_height, width=inf_frame_width, borderwidth=2, relief='groove')
        self.raw_canvas.pack()

        # Normalized canvas configuration
        self.norm_canvas = tk.Canvas(self.information_frame, borderwidth=2, relief='groove')
        self.norm_canvas.config(height=3/7 * inf_frame_height, width=inf_frame_width)
        self.norm_canvas.pack()

        # Labels frame configuration
        self.labels_frame = tk.Frame(self.information_frame, borderwidth=2, relief='groove')
        self.labels_frame.config(height=1/7 * inf_frame_height, width=inf_frame_width)
        self.labels_frame.pack()
