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
        self.brightness_change = 0
        self.contrast_multiplier = 1
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

        self.btn1.bind(on_press=lambda x: self.find_card())

        self.brightness_minus_btn.bind(on_press=lambda x: self.set_brightness(-5))
        self.brightness_plus_btn.bind(on_press=lambda x: self.set_brightness(5))
        self.contrast_minus_btn.bind(on_press=lambda x: self.set_contrast(-1))
        self.contrast_plus_btn.bind(on_press=lambda x: self.set_contrast(1))
        self.focus_minus_btn.bind(on_press=lambda x: self.set_focus(-5))
        self.focus_plus_btn.bind(on_press=lambda x: self.set_focus(5))

        self.add_widget(self.img1)
        self.add_widget(self.btn1)
        self.add_widget(self.focus_minus_btn)
        self.add_widget(self.focus_plus_btn)
        self.add_widget(self.brightness_minus_btn)
        self.add_widget(self.brightness_plus_btn)
        self.add_widget(self.contrast_minus_btn)
        self.add_widget(self.contrast_plus_btn)
        self.add_widget(self.text_block)

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
        self.camera.set(cv2.CAP_PROP_FOCUS, self.focus)

    def find_card(self):
        _, frame = self.camera.read()

        processed_frame = self.process_frame(frame)

        text = pytesseract.image_to_string(processed_frame)
        self.text_block.text = text

    def process_frame(self, frame):
        # filtered = cv2.dilate(frame, kernel, iterations=15)

        frame = self.apply_contrast_and_brightness(frame)
        gray_grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # gray_in_rgb = cv2.cvtColor(gray_grayscale, cv2.COLOR_GRAY2RGB)
        # gray_in_bgr = cv2.cvtColor(gray_grayscale, cv2.COLOR_GRAY2BGR)
        if self.should_run_gaussian_blur_filter:
            frame = cv2.GaussianBlur(gray_grayscale, (7, 7), 0)
        if self.should_run_otsu_thresh_filter:
            _, capped_gray = cv2.threshold(blurred_grayscale, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        last_process = capped_gray
        if frame.shape[0]

        return cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

    def set_brightness(self, change):
        self.brightness_change += change

    def set_contrast(self, change):
        self.contrast_multiplier += change

    def apply_contrast_and_brightness(self, frame):
        return cv2.addWeighted(frame, self.contrast_multiplier, frame, 0, self.brightness_change)


if __name__ == "__main__":
    CardCameraApp().run()
