from __future__ import annotations

import logging
from typing import Any

import requests
import threading as thread
import time


from .websocket import WebsocketClient

_LOGGER = logging.getLogger(__name__)

API_ENDPOINT_LOGIN = "https://api.pushover.net/1/users/login.json"
API_ENDPOINT_DEVICE_REGISTRATION = "https://api.pushover.net/1/devices.json"
API_ENDPOINT_DOWNLOAD_MESSAGES =  "https://api.pushover.net/1/messages.json"

DEFAULT_TIMEOUT = 30

API_ENDPOINT_DELETE_MESSAGE_PREFIX =  "https://api.pushover.net/1/devices/"
API_ENDPOINT_DELETE_MESSAGE_SUFFIX = "/update_highest_message.json"
API_ENDPOINT_ACKNOWLEDGE_EMERGENCY_MESSAGE_PREFIX =  "https://api.pushover.net/1/receipts/"
API_ENDPOINT_ACKNOWLEDGE_EMERGENCY_MESSAGE_SUFFIX = "/acknowledge.json"



class PushoverClient:
    """Initialize api client object."""

    def __init__(
        self,
        email: str,
        password: str,
        timeout: int = DEFAULT_TIMEOUT,
        user_id: str | None = None,
        secret: str | None = None,
        device_name: str = "pythonClient",
        device_id: str | None = None,
    ) -> None:
        
        """Initialize the client object."""
        self.email = email
        self.password = password
        self.device_name = device_name
        self.os = "O"
        self.timeout = timeout
        self.user_id = user_id
        self.secret = secret
        self.device_id = device_id
        self.callback_to_hass = None
        
    def login(self, two_factor_token = None) -> Any:
        
        
        self.register_callback_to_hass(callback=self.test_test) ##test test test test!!!!!!!!!!!
        
        
        
        if self.user_id and self.secret and not self.device_id:
            #skip the login, already have tokens
            print("skipping login")
            self.password = None
            self.device_id = self.register_device(device_name=self.device_name, secret=self.secret)
            return
        if self.device_id:
            print("skipping registration")
            return
        
        data = {'email':self.email,
                  'password':self.password,
                }
        
        if two_factor_token is not None:
            data['twofa'] = two_factor_token
        
           
        resp_data = requests.post(url=API_ENDPOINT_LOGIN, data=data)
        
        
        #add resp_data.raise_for_status
        
        if resp_data.status_code == 412:
            pass
            #retry with TFA
            
        if not resp_data.ok:
            pass
            #return with some error
            
        try:
            self.password = None
            self.user_id = resp_data.json()['id']
            self.secret = resp_data.json()['secret']
        except KeyError:
            print("Keyerror")
            #Make an exception
        
        self.device_id = self.register_device(device_name=self.device_name, secret=self.secret)
             
        return resp_data

    
    def register_device(self, device_name, secret):
        if self.device_id:
            #Already registered the device
            print("ALready registered, skipping register")
            return
        
        data = {'secret':secret,
                'name':device_name,
                'os':self.os,
                }

        resp_data = requests.post(url=API_ENDPOINT_DEVICE_REGISTRATION, data=data)
        
        #add resp_data.raise_for_status
              
       
        if not resp_data.ok:
            print("SOmething is wrong") 
            #return with some error
        
        if not resp_data.json()['status']:
            #return with the error
            print(resp_data.json()['error'])
            
        try:
            return resp_data.json()['id']
        except KeyError:
            print("Keyerror")
            #Make an exception
            
            
    def download_undelivered_messages(self, device_id, secret):
        data = {'secret':secret,
                'device_id':device_id,
        }
        
        resp_data = requests.get(url=API_ENDPOINT_DOWNLOAD_MESSAGES, data=data)
        
        
        if not resp_data.ok:
            print("SOmething is wrong")
            
        try:
            messages = resp_data.json()['messages']
        except KeyError:
            print("Keyerror")
            #do something
        
        #acknowledge emergency message
        
        if self.callback_to_hass:     
            self.callback_to_hass(messages) 
        return messages
    
    def delete_messages(self, device_id, secret, message_id):
        
        data = {'secret':secret,
                'device_id':device_id,
                'message':message_id,
                }

        url_full = API_ENDPOINT_DELETE_MESSAGE_PREFIX + device_id + API_ENDPOINT_DELETE_MESSAGE_SUFFIX
        resp_data = requests.post(url=url_full, data=data)       
        return resp_data
    
    def acknowledge_emergency_message(self, receipt_id, secret):
        data = {'secret':secret,
                }
        url_full = API_ENDPOINT_ACKNOWLEDGE_EMERGENCY_MESSAGE_PREFIX + receipt_id + API_ENDPOINT_ACKNOWLEDGE_EMERGENCY_MESSAGE_SUFFIX
        resp_data = requests.post(url=url_full, data=data)       
        return resp_data
    
    def websocket_message_received_callback(self, websocket, message):
        
        message = message.decode()
        if message == "#":
            print("keep alive")
            return
        if message == "!":
            print("sync")
            self.download_undelivered_messages(device_id=self.device_id, secret=self.secret)
            return
        if message == "R":
            print("Reconnect")
            websocket.close()
            self.initialize_websocket_client(device_id=self.device_id, secret=self.secret)
            return
        if message == "E":
            print("SOmething is wrong, DO not reconnect. Log in again or enable the device")
            return
        if message == "A":
            print("Device logged in someone else, closing connection")
            return
        
    
    def initialize_websocket_client(self, device_id, secret):
        self.websocket_client = WebsocketClient(device_id=device_id, secret=secret)
        # self.websocket_client.listen(self.websocket_message_received_callback)
        thread.Thread(target=self.websocket_client.listen,
                      kwargs={"on_message_callback":self.websocket_message_received_callback}).start()
        
        
    def register_callback_to_hass(self, callback):
        self.callback_to_hass = callback
        
    def test_test(self, message):
        print("Send this to hass VVVVVVVVVVVVVV")
        print(message)