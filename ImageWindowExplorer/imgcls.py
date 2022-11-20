import tkinter as tk
from tkinter import filedialog as fd

from PIL import Image, ImageTk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import numpy as np
from os import getcwd


class MainImage:
    """Main image representation"""
    def __init__(self, image_obj: Image.Image, position_callback_lst: list[callable]):
        self.cursor_X = None
        self.cursor_Y = None
        self._raw_image = image_obj.convert('RGB')
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

    def get_rgb_values(self):
        """Returns pixel values by channels"""
        pixels_count = self.size[0] * self.size[1]

        pixels_values = np.ndarray(shape=(pixels_count, 3))
        pixel_ind = 0

        for x in range(self.size[0]):
            for y in range(self.size[1]):
                # Get RGB values for current pixel
                pixels_values[pixel_ind] = self._raw_image.getpixel((x, y))
                pixel_ind += 1

        return pixels_values

    def get_window_stats(self, left, upper, right, bottom):
        """Counts mean and variance in the defined window"""
        mean_vec = np.zeros(shape=3)

        # Mean of (pixel value)^2 for variance calculation improvement
        pixel_2_mean_vec = np.zeros(shape=3)
        pixel_count = (bottom - upper) * (right - left)

        for x in range(left, right):
            for y in range(upper, bottom):
                pixel_rgb_value = np.array(self._raw_image.getpixel((x, y)))

                mean_vec += pixel_rgb_value
                pixel_2_mean_vec += pixel_rgb_value * pixel_rgb_value.T

        mean_vec /= pixel_count
        pixel_2_mean_vec /= pixel_count

        var_vec = pixel_2_mean_vec - np.power(mean_vec, 2)

        return mean_vec, var_vec

    def get_pixel_rgb(self, x, y):
        """Returns pixel RGB value"""
        return self._raw_image.getpixel((x, y))


class ImageViewer:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.main_image = None

        self.main_image_canvas = None
        self.main_image_id = None
        self.small_image_canvas = None

        self.small_image = None
        self.small_image_id = None
        self.border_id = None

        self.graphics_window = None
        self.show_plot_window_btn = None
        self.information_panel_frame = None
        self.information_window = None

        self.tool_bar = None

    def open_image(self, image_path: str):
        """Opens image from the filesystem and updates main_image field"""
        image_obj = Image.open(image_path)
        return MainImage(image_obj, [self._draw_small_image, self._draw_border, self._update_statistics])

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

    def _update_statistics(self, cursor_X, cursor_Y):
        """Shows pixel x,y, mean, variance, intensity and RGB params in the right panel"""
        x, y = cursor_X, cursor_Y
        # Collect information
        R_channel, G_channel, B_channel = self.main_image.get_pixel_rgb(cursor_X, cursor_Y)
        wind_mean, wind_var = self.main_image.get_window_stats(*self._calculate_border_coordinates(cursor_X, cursor_Y))
        intensity = (R_channel + G_channel + B_channel) / 3
        # Round decimals
        wind_mean = np.around(wind_mean, decimals=2)
        wind_var = np.around(wind_var, decimals=2)
        intensity = np.around(intensity, decimals=2)

        # Update information window content
        self.information_window.update_view(x, y, (R_channel, G_channel, B_channel), intensity, wind_mean, wind_var)

    def _on_open_command(self):
        """Open command callback handler"""
        # Get filename from user
        filename = fd.askopenfilename(title='Open image', initialdir=getcwd(),
                                      filetypes=((('Any', '*.*'), ('PNG', '*.png'),
                                                  ('JPG', '*.jpg'), ('JPEG', '*.jpeg'))))
        new_image = self.open_image(filename)
        self._update_main_image(new_image)

    def _update_main_image(self, new_image_obj: MainImage):
        """Updates main image with new one"""
        if self.main_image_id is not None:
            self.main_image_canvas.delete(self.main_image_id)
        # Add new image to the canvas
        self.main_image = new_image_obj
        self.configure_layout()

    def initialize_interface(self):
        """Initialises interface elements"""
        self.main_image_canvas = tk.Canvas(self.root)
        self.small_image_canvas = tk.Canvas(self.root)
        self.show_plot_window_btn = tk.Button(self.root)
        self.information_panel_frame = tk.Frame(self.root)
        self.information_window = InformationPanel(self.information_panel_frame)
        self.tool_bar = tk.Menu(self.root)

        self._update_main_image(self.open_image('abc.jpg'))

    def configure_layout(self):
        # Main canvas
        self.main_image_canvas.bind('<Motion>', self.main_image.mouse_move_handler)
        self.main_image_canvas.place(x=0, y=0)
        self.main_image_id = self.main_image_canvas.create_image((0, 0), image=self.main_image.photo_image, anchor='nw')
        self.main_image_canvas.config(width=self.main_image.size[0], height=self.main_image.size[1])
        # Small canvas
        img_pos_X, img_pos_Y = self.main_image.size[0] + 20, 20
        self.small_image_canvas.config(width=50, height=50)
        self.small_image_canvas.place(x=img_pos_X, y=img_pos_Y)
        # Information panel
        self.information_panel_frame.config(width=250, height=110, relief=tk.RAISED, borderwidth=2)
        self.information_panel_frame.grid_propagate(False)
        self.information_panel_frame.place(x=img_pos_X, y=10)
        self.information_window.configure_layout()
        # Toolbar
        # Add elements to the menu if it is empty
        if self.tool_bar.index("end") < 2:
            self.tool_bar.add_command(label='Open', command=self._on_open_command)
            self.tool_bar.add_command(label='Show graphics', command=self.show_image_histogram_window)
        self.root.config(menu=self.tool_bar)
        # Root
        self.root.geometry(f'{self.main_image.size[0] + 300}x{self.main_image.size[1]}')
        self.root.resizable(False, False)

    def show_image_histogram_window(self):
        self.graphics_window = GraphicsWindow(self.root, (6, 4))

        self.graphics_window.initialize_components()

        x_label = 'Channel value'
        y_label = 'Frequency'
        plot_titles = ['Red', 'Green', 'Blue']
        # Transpose pixel values for plotting histogram
        pixel_values = self.main_image.get_rgb_values().T

        self.graphics_window.plot_histogram(pixel_values, x_label, y_label, plot_titles)


class InformationPanel:
    """Represents information panel from the right side of the app"""
    def __init__(self, root):
        # String variables for dynamical text update
        self.x_y_str_var = tk.StringVar()
        self.rgb_str_var = tk.StringVar()
        self.intensity_str_var = tk.StringVar()
        self.mean_str_var = tk.StringVar()
        self.var_str_var = tk.StringVar()
        # Labels widgets
        self.x_y_label = tk.Label(root, textvariable=self.x_y_str_var)
        self.rgb_label = tk.Label(root, textvariable=self.rgb_str_var)
        self.intensity_label = tk.Label(root, textvariable=self.intensity_str_var)
        self.mean_label = tk.Label(root, textvariable=self.mean_str_var)
        self.var_label = tk.Label(root, textvariable=self.var_str_var)

    def update_view(self, x_val, y_val, RGB: tuple[int, int, int], intensity, mean, variance):
        """Updates values in labels"""
        self.x_y_str_var.set(f'x = {x_val:4d}; y = {y_val:4d}')
        self.rgb_str_var.set(f'R: {RGB[0]:4d} G: {RGB[1]:4d} B: {RGB[2]:4d}')
        self.intensity_str_var.set(f'Intensity = {intensity:6.2f}')
        self.mean_str_var.set(f'𝝻_R = {mean[0]:6.2f} 𝝻_G = {mean[1]:6.2f} 𝝻_B = {mean[2]:6.2f}')
        self.var_str_var.set(f'𝗗_R = {variance[0]:7.2f} 𝗗_G = {variance[1]:7.2f} 𝗗_B = {variance[2]:7.2f}')

    def configure_layout(self):
        """Configures layout and places labels"""
        self.x_y_label.grid(row=0, sticky=tk.W)
        self.rgb_label.grid(row=1, sticky=tk.W)
        self.intensity_label.grid(row=2, sticky=tk.W)
        self.mean_label.grid(row=3, sticky=tk.W)
        self.var_label.grid(row=4, sticky=tk.W)


class GraphicsWindow:
    """Represents window with region for plotting graphics"""
    def __init__(self, parent_widget, size: tuple[int, int]):
        self.parent_widget = parent_widget
        self.width = size[0]
        self.height = size[1]
        self.window_widget = tk.Toplevel(self.parent_widget)

        self.chart_type = None
        self.figure = None

    def initialize_components(self):
        """Initialises plot region"""
        self.figure = plt.Figure(figsize=(self.width, self.height), dpi=100)
        # Represent Figure as Widget
        self.chart_type = FigureCanvasTkAgg(self.figure, self.window_widget)
        self.chart_type.get_tk_widget().place(x=0, y=0)

    def plot_histogram(self,
                       values: np.ndarray,
                       x_label: str,
                       y_label: str,
                       plot_labels: list[str]):
        """Plot values histograms with specified titles and x, y labels"""

        plots_number = values.shape[0]
        # Clear plot region
        self.figure.clear()
        cur_ax = self.figure.add_subplot(111)

        for plot_ind in range(plots_number):
            # PLot histogram
            cur_ax.hist(values[plot_ind, :], rwidth=0.8, bins=255, density=True, label=plot_labels[plot_ind])

        # Configure plot parameters
        cur_ax.set_xlim(0, 255)
        cur_ax.set_xlabel(x_label)
        cur_ax.set_ylabel(y_label)
        cur_ax.legend()
        # Update plot region
        self.chart_type.draw()
        # Update window size parameters
        self.window_widget.geometry(f'{96 * self.width}x{96 * self.height}')
        self.window_widget.resizable(False, False)
