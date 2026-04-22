import requests
from .Docu import *
from io import BytesIO
from zipfile import ZipFile
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

class SaveReader:
    """download zip from url and decrypt files from it

    every: bytes
    """
    def __init__(self, url: str):
        self._zip = requests.get(url).content
        with ZipFile(BytesIO(self._zip)) as zf:
            with zf.open('gameKey') as f:
                ls = f.read()
                self._gameKey_head = ls[0:1]
                cipher = AES.new(DECRYPT_KEY, AES.MODE_CBC, DECRYPT_IV).decrypt(ls[1:])
                raw = unpad(cipher, AES.block_size)
                self.gameKey = raw
            with zf.open('gameProgress') as f:
                ls = f.read()
                self._gameProgress_head = ls[0:1]
                cipher = AES.new(DECRYPT_KEY, AES.MODE_CBC, DECRYPT_IV).decrypt(ls[1:])
                raw = unpad(cipher, AES.block_size)
                self.gameProgress = raw
            with zf.open('gameRecord') as f:
                ls = f.read()
                self._gameRecord_head = ls[0:1]
                cipher = AES.new(DECRYPT_KEY, AES.MODE_CBC, DECRYPT_IV).decrypt(ls[1:])
                raw = unpad(cipher, AES.block_size)
                self.gameRecord = raw
            with zf.open('settings') as f:
                ls = f.read()
                self._settings_head = ls[0:1]
                cipher = AES.new(DECRYPT_KEY, AES.MODE_CBC, DECRYPT_IV).decrypt(ls[1:])
                raw = unpad(cipher, AES.block_size)
                self.settings = raw
            with zf.open('user') as f:
                ls = f.read()
                self._user_head = ls[0:1]
                cipher = AES.new(DECRYPT_KEY, AES.MODE_CBC, DECRYPT_IV).decrypt(ls[1:])
                raw = unpad(cipher, AES.block_size)
                self.user = raw

    def save_zip(self, out_path):
        with open(out_path, 'wb') as f:
            f.write(self._zip)