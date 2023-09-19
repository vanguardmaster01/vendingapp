from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Bezier
# from kivy.graphics.texture import Texture
from kivy.properties import StringProperty
from PIL import Image as PILImage
import io
import math

from DbFuncs import db
from DbFuncs import db_create
from model.Product import Product

from screens.item import ItemScreen
import os
from dotenv import load_dotenv
from Observers.Observer import Observer

load_dotenv()

class ListScreen(Screen, Observer):
    WIDTH = int(os.environ.get('screenX'))
    def __init__(self, **kwargs):
        super(ListScreen, self).__init__(**kwargs)
        self.screenX = int(os.environ.get('screenX'))
        self.itemLength = int(os.environ.get('itemLength'))
        self.productImageHeight = 0
        self.scroll_position = 0
        self.scroll_move_dis = self.itemLength
        self.scroll_y_dis = 0
        self.scroll_y_offset = 0
    
    def on_pre_enter(self, *args):
        self.update()

    def update(self):
        print("---list is updating---")
        Clock.schedule_once(self.retrieve_image_layout, 0)
        Clock.schedule_once(self.retrieve_up_and_down_image, 0)
        Clock.schedule_once(self.retrieve_category_layout, 0)

    # prevent to delay, so we can get image_layou and draw dynamically
    def retrieve_image_layout(self, dt):

        # get all products.
        self.products = db.get_products()

        self.on_draw_item_images()

    def on_draw_item_images(self):
        image_layout = self.ids.image_layout  # Access the image_layout widget
        image_layout.clear_widgets()
        # draw Items
        if self.products:
            # get scroll_y step 
            # self.scroll_y_dis = 1 / (math.ceil(len(products) / 2)  - 1)           

            for product in self.products:
                image = self.on_draw_item(product)
                self.productImageHeight = image.height
                container = BoxLayout()
                print('window.width:', Window.width)
                lp = (Window.width / 2 - self.productImageHeight - 10) / 2
                container.padding = [lp ,10,lp,10]
                container.size_hint_y = None
                container.height = image.height  + 10
                container.add_widget(image)
                image_layout.add_widget(container)

        else:
            image_layout.add_widget(Label(text='Image not found', color=(0,0,0,1)))

        rowCnt = math.ceil(len(self.products) / 2 + 1)
        image_layout.height = rowCnt * self.productImageHeight + (rowCnt - 1) * 20
    
    
    # draw one image
    def on_draw_item(self, product):
        image = ImageItem()
        image_stream = io.BytesIO(product.thumbnail)
        img = CoreImage(image_stream, ext='png')
        image.texture = img.texture
        image.name = product.itemno
        image.manager = self.manager      

        return image
    
    ###################################################################
    def retrieve_up_and_down_image(self, dt):
        up_image = self.ids.up_image
        # up_image.size_hint_x = None
        # up_image.width = self.screenX * 2 / 3
        up_image.bind(on_touch_down = self.on_up_img_click)
        down_image = self.ids.down_image
        # down_image.size_hint_x = None
        # down_image.width = self.screenX * 2 / 3
        down_image.bind(on_touch_down = self.on_down_img_click)

    def on_up_img_click(self, instance, touch):
        if instance.collide_point(*touch.pos):
            # image_scroll_view.scroll_y = 1
            # if(self.scroll_position > 0):
            #     self.ids.image_scroll_view.scroll_y += self.scroll_y_dis
            #     self.scroll_position -= self.scroll_move_dis

            imageScrollView = self.ids.image_scroll_view
            imageLayout = self.ids.image_layout
            if imageLayout.children:
                firstChild = imageLayout.children[-1]
                imageScrollView.scroll_to(firstChild)
          
    def on_down_img_click(self, instance, touch):
        if instance.collide_point(*touch.pos):
            # image_scroll_view.scroll_y = 1
            # if(self.ids.image_scroll_view.scroll_y > 0.01):
            #     self.ids.image_scroll_view.scroll_y -= self.scroll_y_dis
            #     self.scroll_position += self.scroll_move_dis

            imageScrollView = self.ids.image_scroll_view
            imageLayout = self.ids.image_layout
            if imageLayout.children:
                lastChild = imageLayout.children[0]
                imageScrollView.scroll_to(lastChild)


    ########################################################################

    def retrieve_category_layout(self, dt):

        self.machines = db.get_machines()
        self.on_draw_category_images()

    def on_draw_category_images(self):
        categoryLayout = self.ids.category_layout  # Access the image_layout widget

        categoryLayout.clear_widgets()
        categoryLayout.width = 5
        if self.machines:
            for machine in self.machines:
                image = self.on_draw_category_item(machine)
                categoryLayout.add_widget(image)
                categoryLayout.width += image.width
            
        else:
            categoryLayout.add_widget(Label(text='Image not found', color=(0,0,0,1)))


    def on_draw_category_item(self, machine):
        boxlayout = BoxLayout(orientation='vertical')
        boxlayout.width = Window.width / 6
        
        image = CategoryItem()
        image_stream = io.BytesIO(machine.thumbnail)
        img = CoreImage(image_stream, ext='png')
        image.texture = img.texture
        specLabel = Label(text= machine.value)
        specLabel.color = (0,0,0,1)
        specLabel.font_size = 15

        nameLabel = Label(text= (machine.name))
        nameLabel.color = (0,0,0,1)
        nameLabel.font_size = 15
        nameLabel.background_color = (1,1,1,1)

        boxlayout.add_widget(image)
        boxlayout.add_widget(specLabel)
        boxlayout.add_widget(nameLabel)
        boxlayout.height = 100

        return boxlayout

    def on_resize(self):
        print('window_size: ', Window.width)
        self.on_draw_item_images()
        self.on_draw_category_images()


# product image item
class ImageItem(Image):
    def __init__(self, **kwargs):
        super(ImageItem, self).__init__(**kwargs)
        self.manager = None
        self.itemLength = os.environ.get('itemLength')

        self.size = (self.itemLength, self.itemLength)
        self.size_hint = (None, None)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.manager.current = 'Item'
            self.manager.get_screen("Item").set_item_id(self.name)

# top bar image
class CategoryItem(Image):
    def __init__(self, **kwargs):
        super(CategoryItem, self).__init__(**kwargs)


# image scroll view
class ImageScrollView(ScrollView):
    def __init__(self, **kwargs):
        super(ImageScrollView, self).__init__(**kwargs)

        # self.imageLayout = self.ids.image_layout

    # def on_touch_move(self, touch):
    #     if self.collide_point(*touch.pos):
    #         if touch.dy > 0 and self.scroll_y < 1:  # Scrolling up
    #             print(f'scroll----{self.scroll_y}')
    #             self.scroll_y -= self.scroll_y_dis  # Adjust the scroll_y value to modify the scrolling speed
    #         elif self.scroll_y > 0.01:  # Scrolling down
    #             print(f'scroll+++++{self.scroll_y}')
    #             self.scroll_y += self.scroll_y_dis
    #         else:
    #             print('out')

    #     return super(ImageScrollView, self).on_touch_move(touch)
