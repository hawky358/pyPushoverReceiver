import websocket

WEBSOCKET_URL = "wss://client.pushover.net/push"


class WebsocketClient:

    def __init__(
        self,
        device_id: str,
        secret: str
    ) -> None:
        
        
        self.device_id = device_id    
        self.secret = secret
        self.login_token = "login:" + device_id + ":" + secret + chr(10)
        
    def listen(self, on_message_callback):

        # websocket.enableTrace(True)
        wsapp = websocket.WebSocketApp(WEBSOCKET_URL, on_message=on_message_callback, on_open=self.on_open)
        wsapp.run_forever()
      
    def on_open(self, websocket):
        websocket.send(self.login_token)
       
      
