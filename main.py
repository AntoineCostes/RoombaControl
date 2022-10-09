import kivy
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.button import *
from kivy.uix.label import *
from kivy.uix.behaviors import *
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.animation import Animation

from oscpy.server import OSCThreadServer
import socket
import os
#os.environ['KIVY_IMAGE'] = 'sdl2'

#TODO slider speed and /motors [l, R]
control = '''
BoxLayout:
    orientation:'vertical'

    GridLayout:
        cols: 3
        size_hint_y:0.2
        FlashingLabel:
            id:ping
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
                text: "192.168.1.39"
                halign:'center'
                height:self.line_height*2
                size_hint_y: None
                pos_hint_y: 0.5
        OSCButton:
            text: "Hello"
            address:"hello"

    Slider:
        size_hint_y:0.2
        on_value:app.send("speed", [self.value])
        min:0
        max:1
        value:0.5

    GridLayout:
        id:grid
        cols: 3
        OSCButton:
            text: "Validation"
            address:"song/validate"
            background_color: 0.1, 0.7, 0.1, 1
        OSCToggle:
            group: "move"
            address:"move"
            value:0
            background_normal:  app.dirpath+"/pics/up.png"
            background_down:  app.dirpath+"/pics/up_down.png"
        OSCButton:
            text: "Erreur"
            address:"song/error"
            background_color: .8, 0, 0, 1

        OSCToggle:
            group: "move"
            address:"move"
            value:1
            background_normal:  app.dirpath+"/pics/left.png"
            background_down:  app.dirpath+"/pics/left_down.png"
        Button:
            text: "STOP"
            on_press: app.stop()
        OSCToggle:
            group: "move"
            address:"move"
            value:2
            background_normal:  app.dirpath+"/pics/right.png"
            background_down:  app.dirpath+"/pics/right_down.png"

        OSCButton:
            text: "blip"
            address:"song/victory"
        OSCToggle:
            group: "move"
            address:"move"
            value:3
            background_normal:  app.dirpath+"/pics/down.png"
            background_down:  app.dirpath+"/pics/down_down.png"
        OSCButton:
            text: "blop"
            address:"song/kraftwerk"

        OSCToggle:
            text: "LED Home"
            address:"home"
        OSCToggle:
            text: "LED Warning"
            address:"warning"
        OSCToggle:
            text: "LED Dirt"
            address:"dirt"

'''
TARGET_PORT = 9000
LISTENING_PORT = 12000

class FlashingLabel(Label):
    background_color = ListProperty([.3, .3, .3, 1])

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            local_ip = socket.gethostbyname(socket.gethostname())
            print(local_ip)
            broadcast_ip = local_ip[:local_ip.rfind(".")]+".255"
            print(broadcast_ip)
            App.get_running_app().osc.send_message("/yo", [], broadcast_ip, port=TARGET_PORT)
            # broadcast yo

    def flash(self):
        self.background_color = (0, 1, 0, 1)
        #self.canvas.ask_update()
        flash_anim = Animation(background_color=(.3, .3, .3, 1), t='out_sine', duration=2)
        #flash_anim += Animation(background_color=(0, .5, 0, 1), t='out_bounce')
        flash_anim.start(self);

class OSCToggle(ToggleButtonBehavior, Button):
    address = StringProperty("toggle")
    value = NumericProperty(0)

    def on_state(self, widget, value):
        if self.state=="down":
            App.get_running_app().send(self.address, [self.value])

class OSCButton(Button):
    address = StringProperty("button")

    def on_press(self):
        App.get_running_app().send(self.address, [1])

    def on_release(self):
        App.get_running_app().send(self.address, [0])


class RoombaApp(App):
    def build(self):
        print("-------------- HELLO")
        # OSC setup
        self.osc = OSCThreadServer()
        sock = self.osc.listen(address='0.0.0.0', port=LISTENING_PORT, default=True)
        self.address = 'localhost'

        @self.osc.address(b'/yo')
        def yo(*values):
            print("yo received")
            if(len(values)>1):
                self.root.ids.ip.text = values[1]

        @self.osc.address(b'/ping')
        def ping(*values):
            print("ping received")
            self.root.ids.ping.flash()

        # pics directory
        self.dirpath = os.path.dirname(os.path.abspath(__file__))
        print(self.dirpath)

        return Builder.load_string(control)

    def send(self, address, args):
        print("send msg")
        print('/roomba/'+address)
        print(args)
        self.osc.send_message('/roomba/'+address, args, self.root.ids.ip.text, port=TARGET_PORT)

    def stop(self):
        for x in (x for x in self.root.ids.grid.children if isinstance(x, OSCToggle)):
            x.state = "normal"
        self.send("stop", [])

    def on_exit(self):
        print("exit")
        self.osc.stop()

if __name__ == '__main__':
    RoombaApp().run()
