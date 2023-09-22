from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

from DbFuncs import db
from DbFuncs import db_create

from screens.item import ItemScreen
from screens.list import ListScreen
from screens.ad import AdScreen
import os
from dotenv import load_dotenv
load_dotenv()
import apis.api as api
import asyncio
from kivy.clock import Clock
import threading
import time
from config.utils import initThreadLock, setThreadStatus, getThreadStatus, THREAD_INIT, THREAD_RUNNING, THREAD_STOPPING, THREAD_FINISHED
from config.utils import set_main_script_dir
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
import signal
from Observers.Subject import subject
from config import utils

set_main_script_dir(os.path.dirname(__file__))
loop = None

class MainApp(App):
    class WindowManager(ScreenManager):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            with self.canvas.before:
                Color(1, 1, 1, 1) # a white color
                self.rect = Rectangle(pos=self.pos, size=self.size)
                self.bind(pos=self.update_rect, size=self.update_rect)

        def update_rect(self, *args):
            self.rect.pos = self.pos
            self.rect.size = self.size

    def build(self):

        initThreadLock()

        self.delta = 0
        self.advsleeptime = os.environ.get('advsleeptime')
        
        self._thread = threading.Thread(target=self.between_callback)
        self._thread.start()

        db.openDatabase() 
        db_create.create_tables()
        
        Builder.load_file('./kv/list.kv')
        
        self.sm = self.WindowManager()
        self.adScreen = AdScreen(name='Ad')        
        self.listScreen = ListScreen(name='List')        
        self.itemScreen = ItemScreen(name='Item') 
        self.sm.add_widget(self.adScreen)
        self.sm.add_widget(self.listScreen)
        self.sm.add_widget(self.itemScreen)
        subject.add_observer(self.adScreen, "Ad")
        subject.add_observer(self.listScreen, "List")
        #subject.add_observer(self.itemScreen, "Item")

        print("main thread ida", threading.get_native_id())

        width = int(os.environ.get('screenX'))
        height = int(os.environ.get('screenY'))
        Window.size = (width, height)

        self.countEvent = Clock.schedule_interval(self.count_time, 1)
        
        self.adScreen.bind(on_touch_down=self.touch_screen)
        self.listScreen.bind(on_touch_down=self.touch_screen)
        self.itemScreen.bind(on_touch_down=self.touch_screen)
        
        Window.bind(on_request_close=self.on_request_close)
        Window.bind(on_resize=self.on_resize)

        return self.sm

    def touch_screen(self, instance, touch):
        self.delta = 0
   
    def wait_apithread_stop(self, td):  
        try:
            self._thread.join(0.1)
            if getThreadStatus() == THREAD_FINISHED:
                self._thread.join()
                self.stopEvent.cancel() 
                db.closeDatabase()
                self.stop()
        except RuntimeError:
            pass        
  
    def count_time(self, dt):
        self.delta += 1
        if self.delta > int(self.advsleeptime):
            self.sm.current = 'Ad'
            # self.listScreen.clear_widgets()
            # self.listScreen.__init__()
            # self.itemScreen.clear_widgets()
            # self.itemScreen.__init__()
            self.delta = 0

    def on_request_close(self, *args):
        print('request_close')
        self.textpopup(title='Exit', text='Are you sure?')
        return True
    
    def wait_threadstop(self, *args):
        if getThreadStatus() != THREAD_FINISHED:

            self.countEvent.cancel()
            setThreadStatus(THREAD_STOPPING)
            self.stopEvent = Clock.schedule_interval(self.wait_apithread_stop, 0.2)
            # loop.stop()
            # exit(0)
        else : 
            self.stop()

    def textpopup(self, title='', text=''):
        box = BoxLayout(orientation='vertical')
        box.add_widget(Label(text=text))
        mybutton = Button(text='OK', size_hint=(1, 0.5))
        # box.add_widget(progress_bar)
        box.add_widget(mybutton)
        popup = Popup(title=title, content=box, size_hint=(None, None), size=(300, 150), auto_dismiss = False)
        mybutton.bind(on_release=self.wait_threadstop)
        # mybutton.bind(on_release=self.stop)
        popup.open()
    
    def between_callback(self):
        global loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(api.connect_to_server())
        except:
            pass

    def on_resize(self, window, width, height):
        self.listScreen.on_resize()
        self.itemScreen.on_resize()

if __name__ == '__main__':
    def stop_application(signum, frame):
        global loop
        if loop is not None:
            loop.stop()
            exit(0)
    
    signal.signal(signal.SIGINT, stop_application)
    # signal.signal(signal.SIGTERM, stop_application)

    MainApp().run()