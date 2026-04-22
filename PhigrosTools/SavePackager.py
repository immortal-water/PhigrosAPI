from .SaveDecoder import SaveDecoder
from .Docu import DECRYPT_KEY, DECRYPT_IV
from .ByteWriter import ByteWriter
import io
import zipfile
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

class SavePackager:
    def __init__(self, docu: SaveDecoder):
        self._docu = docu
        self.raw_gameKey: bytes = self.encode_gameKey()
        self.raw_gameProgress: bytes = self.encode_gameProgress()
        self.raw_gameRecord: bytes = self._docu._files.gameRecord
        self.raw_settings: bytes = self._docu._files.settings
        self.raw_user: bytes = self._docu._files.user
        self.zip: bytes = self.encrypt_zip()

    def encode_gameKey(self) -> bytes:
        writer = ByteWriter()
        items = self._docu._collection
        writer.write_int(len(items))
        for name, data in items:
            writer.write_string(name)
            writer.write_keydata(data)
        return writer.get_bytes() + self._docu._gameKey_remaining


    def encode_gameProgress(self) -> bytes:
        writer = ByteWriter()
        pro = self._docu.pro

        writer.write_bool(pro['is_first_run'])
        writer.write_bool(pro['legacy_chapter_finished'])
        writer.write_bool(pro['already_show_collection_tip'])
        writer.write_bool(pro['already_show_auto_unlock_in_tip'])
        writer.align_to_byte()

        writer.write_string(pro['completed'])
        writer.write_int(pro['song_update_info'], 1)
        writer.write_int(pro['challenge_mode_rank'], 2)

        for m in pro['money']:
            writer.write_int(m)

        writer.write_int(pro['unlock_flag_of_spasmodic'], 1)
        writer.write_int(pro['unlock_flag_of_igallta'], 1)
        writer.write_int(pro['unlock_flag_of_rrharil'], 1)
        writer.write_int(pro['flag_of_song_record_key'], 1)
        writer.write_int(pro['random_version_unlocked'], 1)

        writer.write_bool(pro['chapter8_unlock_begin'])
        writer.write_bool(pro['chapter8_unlock_second_phase'])
        writer.write_bool(pro['chapter8_passed'])
        writer.align_to_byte()

        writer.write_int(pro['chapter8_song_unlocked'], 1)

        return writer.get_bytes() + self._docu._gameProgress_remaining

    def encrypt_zip(self) -> bytes:
        files = {
            'gameKey': [self._docu._files._gameKey_head, self.raw_gameKey],
            'gameProgress': [self._docu._files._gameProgress_head, self.raw_gameProgress],
            'gameRecord': [self._docu._files._gameRecord_head, self.raw_gameRecord],
            'settings': [self._docu._files._settings_head, self.raw_settings],
            'user': [self._docu._files._user_head, self.raw_user]
        }

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for name, [head, data] in files.items():
                cipher = AES.new(DECRYPT_KEY, AES.MODE_CBC, DECRYPT_IV)
                padded = pad(data, AES.block_size)
                encrypted = cipher.encrypt(padded)
                final = head + encrypted
                zf.writestr(name, final)

        return zip_buffer.getvalue()

    def save_zip(self, out_path):
        with open(out_path, 'wb') as f:
            f.write(self.zip)