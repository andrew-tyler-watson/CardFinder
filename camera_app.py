from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.textinput import TextInput

from scipy import ndimage

import numpy as np
import cv2

from kivy.app import EventDispatcher

from cv2 import CAP_PROP_FRAME_WIDTH
from cv2 import CAP_PROP_FRAME_HEIGHT

from PIL import Image as tesImage
import pytesseract


class CardCameraApp(App):
    def build(self):
        return CardCameraContainer()


class CardCameraContainer(BoxLayout):
    def __init__(self, **kwargs):
        super(CardCameraContainer, self).__init__(**kwargs)
        self.focus = 100
        self.focus_change = -5
        self.brightness = 1
        self.contrast = 1
        self.gamma = 1
        self.should_invert = False
        self.should_run_brightness_filter = True
        self.should_run_gaussian_blur_filter = True
        self.should_run_contrast_filter = True
        self.should_run_otsu_thresh_filter = True
        self.should_run_brightness_filter = True
        self.camera = cv2.VideoCapture(0)
        self.camera.set(CAP_PROP_FRAME_WIDTH, 1920)
        self.camera.set(CAP_PROP_FRAME_HEIGHT, 1080)

        self.text_block = TextInput(size_hint=(1, 1), pos_hint={'x': .15, 'y': 0.0})
        self.img1 = Image(size_hint=(3, 1), pos_hint={'x': 0.0, 'y': 0.15})
        self.btn1 = Button(text="Take", size_hint=(.7, .1), pos_hint={'x': .15})

        self.brightness_minus_btn = Button(text="brightness\n-", size_hint=(.7, .1), pos_hint={'x': .60})
        self.brightness_plus_btn = Button(text="brightness\n+", size_hint=(.7, .1), pos_hint={'x': .75})
        self.contrast_minus_btn = Button(text="contrast\n-", size_hint=(.7, .1), pos_hint={'x': .90})
        self.contrast_plus_btn = Button(text="contrast\n+", size_hint=(.7, .1), pos_hint={'x': 1.05})
        self.focus_minus_btn = Button(text="focus\n-", size_hint=(.7, .1), pos_hint={'x': .30})
        self.focus_plus_btn = Button(text="focus\n+", size_hint=(.7, .1), pos_hint={'x': .45})
        self.gamma_minus_btn = Button(text="gamma\n-", size_hint=(.7, .1), pos_hint={'x': .30, 'y': .85})
        self.gamma_plus_btn = Button(text="gamma\n+", size_hint=(.7, .1), pos_hint={'x': .45, 'y': .85})
        self.invert_btn = Button(text="invert", size_hint=(.7, .1), pos_hint={'x': .60, 'y': .85})

        self.btn1.bind(on_press=lambda x: self.find_card())

        self.brightness_minus_btn.bind(on_press=lambda x: self.set_brightness(-5))
        self.brightness_plus_btn.bind(on_press=lambda x: self.set_brightness(5))
        self.contrast_minus_btn.bind(on_press=lambda x: self.set_contrast(-.3))
        self.contrast_plus_btn.bind(on_press=lambda x: self.set_contrast(.3))
        self.focus_minus_btn.bind(on_press=lambda x: self.set_focus(-5))
        self.focus_plus_btn.bind(on_press=lambda x: self.set_focus(5))
        self.gamma_minus_btn.bind(on_press=lambda x: self.set_gamma(-1))
        self.gamma_plus_btn.bind(on_press=lambda x: self.set_gamma(1))
        self.invert_btn.bind(on_press=lambda x: self.toggle_invert())

        self.add_widget(self.img1)
        self.add_widget(self.btn1)
        self.add_widget(self.focus_minus_btn)
        self.add_widget(self.focus_plus_btn)
        self.add_widget(self.brightness_minus_btn)
        self.add_widget(self.brightness_plus_btn)
        self.add_widget(self.contrast_minus_btn)
        self.add_widget(self.contrast_plus_btn)
        self.add_widget(self.gamma_minus_btn)
        self.add_widget(self.gamma_plus_btn)
        self.add_widget(self.text_block)
        self.add_widget(self.invert_btn)

        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def update(self, dt):
        _, frame = self.camera.read()
        processed_frame = self.process_frame(frame)

        buf1 = cv2.flip(processed_frame, 0)
        buf = buf1.tobytes()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        self.img1.texture = texture1

    def set_focus(self, increment):
        self.focus = self.focus + increment
        self.camera.set(cv2.CAP_PROP_GAMMA, self.focus)

    def find_card(self):
        _, frame = self.camera.read()

        processed_frame = self.process_frame(frame)

        text = pytesseract.image_to_string(processed_frame)
        self.text_block.text = text

    def process_frame(self, frame):
        # frame = cv2.dilate(frame, self.get_kernel(5), iterations=5)

        # frame = self.apply_contrast_and_brightness(frame)
        frame = self.turn_gray_bgr(frame)
        frame = self.adjust_gamma(frame)
        if self.should_invert:
            frame = self.invert(frame)

        return frame
        # if self.should_run_gaussian_blur_filter:
        #     frame = cv2.GaussianBlur(frame, (5, 5), 0)
        # if self.should_run_otsu_thresh_filter:
        #     _, frame = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        #
        # return cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

    def set_brightness(self, change):
        self.brightness += change

    def set_contrast(self, change):
        self.contrast += change

    def apply_contrast_and_brightness(self, frame):
        return cv2.addWeighted(frame, self.contrast_multiplier, frame, 0, self.brightness_change)

    def get_kernel(self, size):
        return np.ones((size, size), np.uint8)

    def turn_gray_bgr(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    def set_gamma(self, arg):
        values = [.04, .1, .2, .4, .67, 1, 1.5, 2.5, 5.0, 10.0, 25.0]
        index = values.index(self.gamma)
        if arg == -1 and index is not 0:
            self.gamma = values[index - 1]
        elif arg == 1 and index is not len(values) - 1:
            self.gamma = values[index + 1]

    def adjust_gamma(self, frame):
        lookUpTable = np.empty((1, 256), np.uint8)
        for i in range(256):
            lookUpTable[0, i] = np.clip(pow(i / 255.0, self.gamma) * 255.0, 0, 255)
        return cv2.LUT(frame, lookUpTable)

    def invert(self, frame):
        return cv2.bitwise_not(frame)
    def toggle_invert(self):
        self.should_invert = not self.should_invert


if __name__ == "__main__":
    CardCameraApp().run()