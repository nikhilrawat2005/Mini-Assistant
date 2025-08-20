# main.py
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivy.core.window import Window
from threading import Thread
import time
import queue
import sys
import os

# Add your MiniAssistant zip folder path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "MiniAssistant"))

# Import Mini modules
from mini import Mini

KV = '''
#:import hex kivy.utils.get_color_from_hex
#:import dp kivy.metrics.dp

<ChatBubble>:
    size_hint: (0.8 if root.sender == "user" else 0.75, None)
    height: content.height + dp(20)
    pos_hint: {'right': 1} if root.sender == "user" else {'x': 0}
    padding: dp(10)
    md_bg_color: 
        hex("#4A76FF") if root.sender == "user" else hex("#F5F7FF")
    radius: [dp(20), dp(20), dp(20), dp(4)] if root.sender == "user" else [dp(20), dp(20), dp(4), dp(20)]
    
    BoxLayout:
        id: content
        orientation: 'vertical'
        size_hint_y: None
        height: lbl.texture_size[1] + dp(10)
        spacing: dp(5)
        
        MDLabel:
            id: lbl
            text: root.text
            font_size: "16sp"
            size_hint_y: None
            height: self.texture_size[1]
            text_size: self.width, None
            halign: 'right' if root.sender == "user" else 'left'
            valign: 'center'
            color: 
                (1, 1, 1, 1) if root.sender == "user" else (0.1, 0.1, 0.1, 1)
            markup: True
            bold: True if root.sender == "user" else False

<ChatBox>:
    orientation: "vertical"
    canvas.before:
        Color:
            rgba: hex("#F0F4FF")
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        size_hint_y: 0.12
        padding: dp(15)
        md_bg_color: hex("#4A76FF")
        
        MDLabel:
            text: "Mini Assistant"
            font_size: "22sp"
            theme_text_color: "Custom"
            text_color: (1, 1, 1, 1)
            halign: "center"
            valign: "center"
            bold: True

    ScrollView:
        id: scroll
        size_hint_y: 0.74
        do_scroll_x: False
        bar_width: dp(6)
        bar_color: hex("#4A76FF")
        bar_inactive_color: hex("#4A76FF80")
        effect_cls: "ScrollEffect"
        
        BoxLayout:
            id: chat_output
            orientation: "vertical"
            size_hint_y: None
            height: self.minimum_height
            padding: [dp(15), dp(15), dp(15), dp(25)]
            spacing: dp(15)

    BoxLayout:
        size_hint_y: 0.14
        padding: [dp(15), dp(5), dp(15), dp(10)]
        md_bg_color: hex("#FFFFFF")
        spacing: dp(10)

        MDTextField:
            id: user_input
            hint_text: "Type your message..."
            mode: "rectangle"
            line_color_normal: hex("#4A76FF")
            line_color_focus: hex("#4A76FF")
            cursor_color: hex("#4A76FF")
            foreground_color: hex("#333333")
            padding: [dp(15), dp(15), dp(15), dp(15)]
            multiline: False
            on_text_validate: root.send_message()
            
        MDFloatingActionButton:
            icon: "send"
            md_bg_color: hex("#4A76FF")
            theme_icon_color: "Custom"
            icon_color: (1, 1, 1, 1)
            elevation: 0
            on_release: root.send_message()
            size_hint: (None, None)
            size: [dp(50), dp(50)]
            pos_hint: {'center_y': 0.5}

        MDFloatingActionButton:
            id: mic_button
            icon: "microphone"
            md_bg_color: hex("#FF3B3B") if root.voice_mode else hex("#4CAF50")
            theme_icon_color: "Custom"
            icon_color: (1, 1, 1, 1)
            elevation: 0
            on_release: root.toggle_voice_mode()
            size_hint: (None, None)
            size: [dp(50), dp(50)]
            pos_hint: {'center_y': 0.5}
'''

class ChatBubble(MDCard):
    text = StringProperty("")
    sender = StringProperty("mini")
    timestamp = StringProperty("")

class ChatBox(BoxLayout):
    voice_mode = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.msg_queue = queue.Queue()
        self.mini = Mini()

        # Start background threads
        Thread(target=self.background_task, daemon=True).start()
        Thread(target=self.voice_listener_task, daemon=True).start()

        Clock.schedule_once(self.add_welcome_message, 0.5)

    def add_welcome_message(self, dt):
        welcome_msg = "Hello! I'm Mini Assistant. How can I help you today?"
        self.add_bubble(welcome_msg, sender="mini")

    def send_message(self):
        user_msg = self.ids.user_input.text.strip()
        if user_msg:
            self.add_bubble(user_msg, sender="user")
            self.ids.user_input.text = ""
            self.msg_queue.put(user_msg)

    def toggle_voice_mode(self):
        self.voice_mode = not self.voice_mode
        self.mini.voice_mode = self.voice_mode
        # update button color immediately
        self.ids.mic_button.md_bg_color = (1, 0, 0, 1) if self.voice_mode else (0.3, 0.7, 0.3, 1)

    def background_task(self):
        while True:
            if not self.msg_queue.empty():
                msg = self.msg_queue.get()
                try:
                    response = self.mini.get_response(msg)
                except Exception as e:
                    response = f"⚠️ Oops! Something went wrong: {str(e)}"
                Clock.schedule_once(lambda dt, resp=response: self.add_bubble(resp, sender="mini"))
            time.sleep(0.1)

    def voice_listener_task(self):
        """Listen to Mini’s stt_queue for recognized speech"""
        while True:
            if self.mini and not self.mini.stt_queue.empty():
                spoken_text = self.mini.stt_queue.get()
                if spoken_text:
                    Clock.schedule_once(lambda dt, txt=spoken_text: self.add_bubble(txt, sender="user"))
                    self.msg_queue.put(spoken_text)
            time.sleep(0.1)

    def add_bubble(self, message, sender="mini"):
        bubble = ChatBubble(text=message, sender=sender)
        self.ids.chat_output.add_widget(bubble)
        Clock.schedule_once(self.scroll_to_bottom, 0.05)

    def scroll_to_bottom(self, dt):
        scrollview = self.ids.scroll
        if scrollview.height < self.ids.chat_output.height:
            scrollview.scroll_y = 0

class MiniApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "700"
        Window.size = (400, 700)
        Window.clearcolor = (0.95, 0.95, 1, 1)
        Builder.load_string(KV)
        return ChatBox()

if __name__ == "__main__":
    MiniApp().run()
