import kivy
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.button import *
from kivy.uix.label import *
from kivy.uix.behaviors import *
from kivy.properties import ListProperty, StringProperty
from kivy.animation import Animation

from oscpy.server import OSCThreadServer
import socket
import os
#os.environ['KIVY_IMAGE'] = 'sdl2'

control = '''
GridLayout:
    id:grid
    cols: 3

    OSCButton:
        text: "Validation"
        address:"validate"
        background_color: 0.1, 0.7, 0.1, 1
    OSCToggle:
        group: "move"
        address:"forward"
        background_normal:  app.dirpath+"/pics/up.png"
        background_down:  app.dirpath+"/pics/up_down.png"
    OSCButton:
        text: "Erreur"
        address:"error"
        background_color: .8, 0, 0, 1

    OSCToggle:
        group: "move"
        address:"left"
        background_normal:  app.dirpath+"/pics/left.png"
        background_down:  app.dirpath+"/pics/left_down.png"
    Button:
        text: "STOP"
        on_press: app.stop()
    OSCToggle:
        group: "move"
        address:"right"
        background_normal:  app.dirpath+"/pics/right.png"
        background_down:  app.dirpath+"/pics/right_down.png"

    OSCButton:
        text: "blip"
        address:"song1"
    OSCToggle:
        group: "move"
        address:"back"
        background_normal:  app.dirpath+"/pics/down.png"
        background_down:  app.dirpath+"/pics/down_down.png"
    OSCButton:
        text: "blop"
        address:"song2"

    Button:
        text: "?"
    Button:
        text: "?"
    Button:
        text: "?"

    FlashingLabel:
        id:detect
        text: "Ping"
        canvas.before:
            Color:
                rgba: self.background_color
            Rectangle:
                size: self.size
                pos: self.pos

    AnchorLayout:
        TextInput:
            id:ip
            text: "192.168.43.255"
            halign:'center'
            height:self.line_height*2
            size_hint_y: None
            pos_hint_y: 0.5
    Button:
        text: "?"
'''

class FlashingLabel(Label):
    background_color = ListProperty([.5, .5, .5, 1])

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            local_ip = socket.gethostbyname(socket.gethostname())
            print(local_ip)
            broadcast_ip = local_ip[:local_ip.rfind(".")]+".255"
            print(broadcast_ip)
            App.get_running_app().osc.send_message("/yo", [local_ip], broadcast_ip, port=12000)
            # broadcast yo

    def flash(self):
        self.background_color = (0, 1, 0, 1)
        #self.canvas.ask_update()
        flash_anim = Animation(background_color=(0, .5, 0, 1), t='out_sine', duration=.2)
        #flash_anim += Animation(background_color=(0, .5, 0, 1), t='out_bounce')
        flash_anim.start(self);

class OSCToggle(ToggleButtonBehavior, Button):
    address = StringProperty("toggle")

    def on_state(self, widget, value):
        App.get_running_app().send('/'+self.address, [1 if self.state=="down" else 0])

class OSCButton(Button):
    address = StringProperty("button")

    def on_press(self):
        App.get_running_app().send('/'+self.address, [1])

    def on_release(self):
        App.get_running_app().send('/'+self.address, [0])


class RoombaApp(App):
    def build(self):
        print("-------------- HELLO")
        # OSC setup
        self.osc = OSCThreadServer()
        sock = self.osc.listen(address='0.0.0.0', port=9000, default=True)
        self.address = 'localhost'

        @self.osc.address(b'/yo')
        def yo(*values):
            print("yo received")
            if(len(values)>1):
                self.root.ids.ip.text = values[1]

        @self.osc.address(b'/ping')
        def ping(*values):
            self.root.ids.ping.flash()

        # pics directory
        self.dirpath = os.path.dirname(os.path.abspath(__file__))
        print(self.dirpath)

        return Builder.load_string(control)

    def send_test(self):
        self.osc.send_message('/test', [1, 2, 3, 'coucou'], self.root.ids.ip.text, port=12000)

    def send(self, address, args):
        self.osc.send_message(address, args, self.root.ids.ip.text, port=12000)

    def stop(self):
        for x in (x for x in self.root.children if isinstance(x, ToggleButtonBehavior)):
            x.state = "normal"
        self.send("/stop", [])

    def on_exit(self):
        print("exit")
        self.osc.stop()

if __name__ == '__main__':
    RoombaApp().run()
