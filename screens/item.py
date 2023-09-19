from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.button import ButtonBehavior, Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Triangle, Bezier
import io
import math
from functools import partial

from DbFuncs import db
from DbFuncs import db_create
from model.Product import Product

from kivy.graphics import RoundedRectangle, Color, Line
import os
from dotenv import load_dotenv
from Observers.Observer import Observer

load_dotenv()

class ItemScreen(Screen, Observer):
    def __init__(self, **kwargs):
        super(ItemScreen, self).__init__(**kwargs)
        self.itemId = None

    def update(self):
        print("---tiem is updating---")
        Clock.schedule_once(self.draw_page, 0)

    def set_item_id(self, id):
        self.itemId = id
        self.update()

    def draw_page(self, dt):
        product = db.get_product(self.itemId)

        if product:
            # display name
            self.draw_title(product.name)

            # display product (image, price, ...)
            self.draw_product_info(product)

            # inputMoneyLabel = Label(text='Geld einwerfen')
            # self.ids.input_money_button.width = inputMoneyLabel.width
            # self.ids.input_money_button.text = inputMoneyLabel.text
            self.caution = product.caution
            self.draw_bigo()

            self.ids.back_img.bind(on_touch_down = self.on_back_press)
        else:
            self.manager.current = 'List'
            self.clear_widgets()
            self.__init__()
        
    def draw_title(self, name):
        titleLabel = self.ids.title_lable
        titleLabel.text = name
        titleLabel.color = (1, 0, 0, 1)
        titleLabel.font_size = 30  
        titleLabel.size_hint_x = None 
        titleLabel.width = 300

    def draw_product_info(self, product):
        image = Image()
        image_stream = io.BytesIO(product.thumbnail)
        img = CoreImage(image_stream, ext='png')
        image.texture = img.texture
        self.ids.item_image_layout.add_widget(image)

        self.draw_label(product.itemno)
        self.draw_label('600')
        self.draw_label(product.nicotine)
        self.draw_label(product.batterypack)
        self.draw_label(product.tankvolumn)

        priceStr = str(product.price) + ' EUR'
        priceLabel = Label(
            text= priceStr,
            size_hint=(None, None),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},  # Center the label on the image
            color=(0, 0, 0, 1),  # Set the text color (white in this example)
            font_size = 30
        )
        self.ids.price_layout.add_widget(priceLabel)

    # display infos
    def draw_label(self, value):
        boxLayout = BoxLayout()
        boxLayout.size_hint_x = None
        boxLayout.padding = [10, 2, 2, 2]

        firstLabel = Label(text=value)
        firstLabel.color = (0,0,0,1)
        firstLabel.halign = 'left'
        firstLabel.size_hint_x = None
        firstLabel.text_size = (firstLabel.width, None)
        boxLayout.add_widget(firstLabel)
        self.ids.info_layout.add_widget(boxLayout)

    # display bigo (labels, img on the top-right )
    def draw_bigo(self):
        bigoLayout = self.ids.bigo_layout
        bigoLayout.clear_widgets()
        bigoLayout.canvas.clear()

        for i in range (1):
            caution = Label(text=self.caution)
            caution.halign='left'
            caution.valign = 'middle'
            caution.color = (.1,.1,.1,.5)
            caution.size_hint_x = None
            caution.size = (500, caution.height /2 )
            caution.text_size = (caution.width, None)

            bigoLayout.add_widget(caution)

        # Create an Image widget
        img = Image(source='./img/bigo.png')
        # Calculate the position for the image (top-right corner)
        screenX = Window.width
        screenY = Window.height
        image_x = screenX - img.width - 20
        image_y = screenY / 3 - img.height / 2 -100
        # Draw the image on the canvas
        with bigoLayout.canvas:
            Color(rgba=(1,1,1,1))
            Rectangle(pos=(image_x, image_y), size=img.size, texture=img.texture)


    def on_back_press(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.manager.current = 'List'
            self.clear_widgets()
            self.__init__()

    def on_buy_press(self):
        print(f'buy_pressed')

    def on_money_button_press(self):
        print('money_button_press')

    def on_resize(self):
        if self.caution:
            self.draw_bigo()

class CountNumber(GridLayout):
    def __init__(self, **kwargs):
        super(CountNumber, self).__init__(**kwargs)
        self.number = 0
        self.cols = 2
        self.padding = [0,0,25,0]
        self.number_text = None
        self.draw_widget()

    def draw_widget(self):
        self.number_text = Label(
            text=str(self.number),
            color=(0,0,0,1),
            font_size = 30
        )
        self.number_text.size_hint_x = 0.6
        self.add_widget(self.number_text)

        controlLayout = BoxLayout(orientation='vertical')
        controlLayout.size_hint_x = None
        controlLayout.width = 30

        incImg = Image(source='./img/up-shape.png')
        incImg.allow_stretch = True
        incImg.bind(on_touch_down = self.increase_number)
        controlLayout.add_widget(incImg)
        decImg = Image(source='./img/down-shape.png')
        decImg.allow_stretch = True
        decImg.bind(on_touch_down = self.decrease_number)
        controlLayout.add_widget(decImg)

        self.add_widget(controlLayout)

    def increase_number(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.number += 1
            self.update_number()
    def decrease_number(self, instance, touch):
        if instance.collide_point(*touch.pos):
            if self.number > 0:
                self.number -= 1
                self.update_number()

    def update_number(self):
        self.number_text.text = str(self.number)


class RoundedBorderGrid(GridLayout):
    def __init__(self, **kwargs):
        super(RoundedBorderGrid, self).__init__(**kwargs)
        
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 0, 0, 1)  # Set the color of the border

            # Parameters for top left rounded corner
            top_left_center = (self.x, self.top)
            top_left_radius = 20

            # Parameters for top right rounded corner
            top_right_center = (self.right, self.top)
            top_right_radius = 20

            # Parameters for straight bottom corners
            bottom_left = (self.x, self.y)
            bottom_right = (self.right, self.y)

            self.draw_rounded_border(top_left_center, top_left_radius, top_right_center, top_right_radius, bottom_left,
                                     bottom_right, width=2)

    def draw_rounded_border(self, top_left_center, top_left_radius, top_right_center, top_right_radius, bottom_left,
                            bottom_right, width=2):
        diameter_top_left = top_left_radius * 2
        diameter_top_right = top_right_radius * 2

        # Draw the top-left rounded corner
        with self.canvas.before:
            Bezier(points=[bottom_left, bottom_left, top_left_center[0] - top_left_radius,
                           top_left_center[1] + top_left_radius, bottom_left], segment_length=20, width=width)

        # Draw the top-right rounded corner
        with self.canvas.before:
            Bezier(points=[bottom_right, bottom_right, top_right_center[0] + top_right_radius,
                           top_right_center[1] + top_right_radius, bottom_right], segment_length=20, width=width)

        # Draw the straight bottom sides
        with self.canvas.before:
            Color(1, 1, 1, 1)  # Set the color for straight borders
            Bezier(points=[bottom_left, bottom_right], width=width)