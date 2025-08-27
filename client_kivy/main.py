
import asyncio, json
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivy.clock import Clock, mainthread
import requests
from plyer import notification
import os

KV_PATH = os.path.join("kv", "main.kv")

class LoginScreen(Screen): pass
class ChatScreen(Screen): pass

class SolunaApp(App):
    def build(self):
        Builder.load_file(KV_PATH)
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(ChatScreen(name="chat"))
        self.token = None
        self.base = None
        self.peer = None
        self.conversation_id = None
        self.ws = None
        return sm

    def set_log(self, text):
        cl = self.root.get_screen("chat").ids.chatlog
        cl.text += text + "\n"

    def do_login(self, base, username, password, peer):
        self.base = base.rstrip("/")
        self.peer = peer
        r = requests.post(f"{self.base}/auth/login", json={"username": username, "password": password})
        if r.status_code != 200:
            rr = requests.post(f"{self.base}/auth/register", json={"username": username, "password": password})
            rr.raise_for_status()
            self.token = rr.json()["access_token"]
        else:
            self.token = r.json()["access_token"]

        h = requests.get(
            f"{self.base}/conversations/{peer}/history",
            headers={"Authorization": f"Bearer {self.token}"}
        ).json()
        self.conversation_id = h["conversation_id"]
        self.root.current = "chat"
        for m in h["messages"]:
            self.set_log(f"[{m['created_at']}] {m['sender_username']}: {m['content']}")
        Clock.schedule_once(lambda dt: self.start_ws())

    def start_ws(self):
        loop = asyncio.get_event_loop()
        if not loop.is_running():
            loop.create_task(self.ws_loop())
        else:
            asyncio.ensure_future(self.ws_loop())

    async def ws_loop(self):
        import websockets
        url = f"{self.base.replace('http', 'ws')}/ws/{self.conversation_id}?token={self.token}"
        async with websockets.connect(url, ping_interval=30) as ws:
            self.ws = ws
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                self.on_message(data)

    @mainthread
    def on_message(self, data):
        who = data.get("from", "?")
        content = data.get("content", "")
        self.set_log(f"{who}: {content}")
        try:
            notification.notify(title="Nuevo mensaje", message=f"{who}: {content}")
        except Exception:
            pass

    def send_msg(self, content):
        if not content.strip():
            return
        async def _send():
            await self.ws.send(json.dumps({"content": content}))
        asyncio.ensure_future(_send())

if __name__ == "__main__":
    SolunaApp().run()
