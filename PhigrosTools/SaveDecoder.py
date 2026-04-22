from .ByteReader import ByteReader
from .SaveReader import SaveReader

class SaveDecoder:
    """decode files from SaveReader

    ava:
        list[str]: avatars' name
    col:
        list[dict{'id': str, 'num': int, 'read': int}]: collections' info
    ill:
        list[str]: illustrations' name
    son:
        list[str]: unlocked songs' name
    rec:
        list[dict{'id': str, 'rec': list[dict{"score": int, "acc": float, "fc": bool} | {}]]: records' info
    pro:
        dict: profile
    """
    def __init__(self, url: str):
        self._files = SaveReader(url)
        [self._collection, self.ava, self.col, self.ill, self.son, self._gameKey_remaining] = self.decode_gameKey()
        [self.rec, self._gameRecord_remaining] = self.decode_gameRecord()
        [self.pro, self._gameProgress_remaining] = self.decode_gameProgress()
        # settings
        # user

    def decode_gameKey(self):
        reader = ByteReader(self._files.gameKey)
        items = []
        ava = []
        col = []
        ill = ['Introduction']
        son = []
        for _ in range(reader.read_int()):
            name = reader.read_string()
            data = reader.read_keydata()
            items.append([name, data])
            [num_file_read, is_unlock_song, num_file_get, is_illustration, is_avatar] = data
            if is_avatar:
                ava.append(name)
            if is_illustration:
                ill.append(name)
            if num_file_get:
                col.append({
                    'id': name,
                    'num': num_file_get,
                    'read': num_file_read
                })
            if is_unlock_song:
                son.append(name)
        return [items, ava, col, ill, son, reader.get_remaining()]

    def decode_gameRecord(self):
        reader = ByteReader(self._files.gameRecord)
        rec = [{'id': 'Introduction', 'rec': [{'score': 1000000, 'acc': 100.0, 'fc': True}, {}, {}, {}, {}]}]
        for _ in range(reader.read_int()):
            id = reader.read_string()[:-2]
            record = reader.read_record()
            rec.append({'id': id, 'rec': record})
        return [rec, reader.get_remaining()]
    
    def decode_gameProgress(self):
        reader = ByteReader(self._files.gameProgress)
        pro = {
                "is_first_run": reader.read_bool(),
                "legacy_chapter_finished": reader.read_bool(),
                "already_show_collection_tip": reader.read_bool(),
                "already_show_auto_unlock_in_tip": reader.read_bool(),
                "completed": reader.read_string(),
                "song_update_info": reader.read_int(1),
                "challenge_mode_rank": reader.read_int(2),
                "money": [reader.read_int() for _ in range(5)],
                "unlock_flag_of_spasmodic": reader.read_int(1),
                "unlock_flag_of_igallta": reader.read_int(1),
                "unlock_flag_of_rrharil": reader.read_int(1),
                "flag_of_song_record_key": reader.read_int(1),
                "random_version_unlocked": reader.read_int(1),
                "chapter8_unlock_begin": reader.read_bool(),
                "chapter8_unlock_second_phase": reader.read_bool(),
                "chapter8_passed": reader.read_bool(),
                "chapter8_song_unlocked": reader.read_int(1)
        }
        return [pro, reader.get_remaining()]
