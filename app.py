from pathlib import Path


ESCAPE_EXIT = False
ROOT_DIR = Path.cwd()
BG_IMAGE = 'bg.jpg'
BLANK_IMAGE = 'blank.png'


# KIVY_CONSOLE = False
import os
# os.environ['KIVY_NO_CONSOLELOG'] = str(int(KIVY_CONSOLE))  # Prevent kivy console output
from kivy.app import App as kvApp
from kivy.core.window import Window
from kivy.config import Config
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color
from kivy.graphics import Rectangle


Config.set('kivy', 'exit_on_escape', str(int(ESCAPE_EXIT)))


class App(kvApp):
    def __init__(self, title='GUI App', **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.root = AnchorLayout()
        self.make_widgets()
        self.set_info_text('Loading...')
        Clock.schedule_once(lambda *a: self.startup(), 1)
        self.hotkeys = Hotkeys(callback=self.resolve_keypress)

    def startup(self):
        self.set_info_text('')

    def resolve_keypress(self, modifiers, key_name, key_code):
        if 'ctrl' in modifiers and key_name == 'f':
            self.top_bar.focus()
        if 'ctrl' in modifiers and key_name == 'q':
            quit()

    def make_widgets(self):
        # Clear all
        self.root.clear_widgets()
        self.root.canvas.clear()
        self.root.canvas.before.clear()
        self.root.canvas.after.clear()

        # Background and main frame
        make_bg(self.root, (1,1,1,0.5), source=str(ROOT_DIR / BG_IMAGE))
        main_frame = BoxLayout(orientation='vertical')
        self.root.add_widget(main_frame)

        # Search
        self.top_bar = TopBar(search_callback=self._do_search)
        main_frame.add_widget(self.top_bar)

        # Output
        output_frame = BoxLayout(orientation='vertical')
        main_frame.add_widget(output_frame)

        self.table_label = Label()
        set_size(self.table_label, y=100)
        output_frame.add_widget(self.table_label)
        self.table_image = Image(allow_stretch=True)
        self.clear_image()
        output_frame.add_widget(self.table_image)

        self.table_label2 = Label()
        set_size(self.table_label2, y=100)
        output_frame.add_widget(self.table_label2)
        self.table_image2 = Image(allow_stretch=True)
        self.clear_image2()
        output_frame.add_widget(self.table_image2)

    def set_info_text(self, text):
        self.top_bar.info_text.text = str(text)

    def set_text(self, text):
        self.table_label.text = str(text)

    def set_image(self, image_name, force_refresh=True):
        source = ROOT_DIR / image_name
        if not source.is_file():
            source = ROOT_DIR / BLANK_IMAGE
        self.table_image.source = str(source)
        if force_refresh:
            self.table_image.reload()

    def clear_image(self):
        self.set_image(BLANK_IMAGE)

    def set_text2(self, text):
        self.table_label2.text = str(text)

    def set_image2(self, image_name, force_refresh=True):
        source = ROOT_DIR / image_name
        if not source.is_file():
            source = ROOT_DIR / BLANK_IMAGE
        self.table_image2.source = str(source)
        if force_refresh:
            self.table_image2.reload()

    def clear_image2(self):
        self.set_image2(BLANK_IMAGE)

    def _do_search(self, uinput):
        self.set_info_text('Searching...')
        Clock.schedule_once(lambda *a: self._do_search_and_clear(uinput), 0.1)

    def _do_search_and_clear(self, uinput):
        self.do_search(uinput)
        self.set_info_text('')

    def do_search(self, uinput):
        self.table_label.text = 'App.do_search() not implemented.'
        self.table_label2.text = f'uinput: {uinput}'


class TopBar(BoxLayout):
    def __init__(self, search_callback, **kwargs):
        super().__init__(**kwargs)
        self.search_callback = search_callback
        main_frame = self
        make_bg(self, (0.02,0,0.05,1))

        label = Label(text='Enter search:')
        set_size(label, x=100)
        main_frame.add_widget(label)

        self.uinput = TextInput(multiline=False)
        self.uinput.bind(on_text_validate=self.do_input)
        set_size(self.uinput, x=300)
        main_frame.add_widget(self.uinput)

        search_btn = Button(text='Search', on_release=self.do_input)
        set_size(search_btn, x=100)
        main_frame.add_widget(search_btn)

        self.info_text = Label()
        # set_size(self.info_text, x=75)
        main_frame.add_widget(self.info_text)

        qbutton = Button(text='Quit', on_release=lambda *a: quit())
        set_size(qbutton, x=75)
        main_frame.add_widget(qbutton)

        set_size(main_frame, y=30)

    def focus(self):
        self.uinput.focus = True
        self.uinput.select_all()

    def do_input(self, *a):
        self.search_callback(self.uinput.text)


class Hotkeys(Widget):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        set_size(self, x=0, y=0)
        self.callback = callback
        self.keyboard = Window.request_keyboard(lambda: None, self)
        self.keyboard.fbind('on_key_down', self._on_key_down)

    def _on_key_down(self, window, key, key_hex, modifiers):
        key_code, key_name = key
        # print(f'Key pressed: {modifiers} + {key_name} (key code: {key_code})')
        self.callback(modifiers, key_name, key_code)


def _update_bg(widget, *args):
    widget._bg.pos = widget.pos
    widget._bg.size = widget.size


def make_bg(widget, color=None, source=None, **kwargs):
    if color is None:
        color = (1,1,1,1)
    with widget.canvas.before:
        widget._bg_color = Color(*color)
        widget._bg = Rectangle(size=widget.size, pos=widget.pos)
        widget._bg.source = source
        widget.bind(
            pos=lambda w, *a: _update_bg(w),
            size=lambda w, *a: _update_bg(w),
        )
    return color


def set_size(widget, x=None, y=None, hx=1, hy=1):
    hx = hx if x is None else None
    hy = hy if y is None else None
    x = widget.width if x is None else x
    y = widget.height if y is None else y

    widget.size_hint = (hx, hy)
    widget.size = (int(x), int(y))
    return widget
