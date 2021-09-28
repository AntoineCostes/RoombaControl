import kivy
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.button import *
from kivy.uix.behaviors import *
import os
os.environ['KIVY_IMAGE'] = 'sdl2'

control = '''
GridLayout:
    id:grid
    cols: 3

    Button:
        text: "Validation"
        background_color: 0.1, 0.7, 0.1, 1
    ToggleButton:
        group: "move"
        background_normal:  app.dirpath+"/pics/up.png"
        background_down:  app.dirpath+"/pics/up_down.png"
    Button:
        text: "Erreur"
        background_color: .8, 0, 0, 1

    ToggleButton:
        group: "move"
        background_normal:  app.dirpath+"/pics/left.png"
        background_down:  app.dirpath+"/pics/left_down.png"
    Button:
        text: "STOP"
        on_press: for x in (x for x in grid.children if isinstance(x, ToggleButton)): x.state = "normal"

    ToggleButton:
        group: "move"
        background_normal:  app.dirpath+"/pics/right.png"
        background_down:  app.dirpath+"/pics/right_down.png"

    Button:
        text: "?"
    ToggleButton:   
        group: "move"
        background_normal:  app.dirpath+"/pics/down.png"
        background_down:  app.dirpath+"/pics/down_down.png"
    Button:
        text: "?"

    Button:
        text: "?"
    Button:
        text: "?"
    Button:
        text: "?"

    Button:
        text: "?"
    Button:
        text: "?"
    Button:
        text: "?"
'''

class RoombaApp(App):
    def build(self):
        print("-------------- HELLO")
        self.dirpath = os.path.dirname(os.path.abspath(__file__))
        print(self.dirpath)
        return Builder.load_string(control)


if __name__ == '__main__':
    RoombaApp().run()
