import struct
import base64
import requests
from .Docu import *
from .PhigrosTools.SaveDecoder import SaveDecoder

class PhigrosAPI:
    def __init__(self, session_token: str):
        """Initializes the PhigrosAPI client.

        Args:
            session_token (str): The session token from the ".userdata" file (property "sessionToken").
        """
        self.__httpHeaders = {
            **PHIGROS_TAPTAP_HEADER,
            "X-LC-Session": session_token
        }
        self.user_info = self.get_user()
        self._save = self.get_save()
        self.player_summary = self.get_player_summary()
        self.docu = SaveDecoder(self._save["gameFile"]["url"])

    def get_user(self):
        """Retrieves the user's information from the Phigros API.

        Returns:
                PlayerInfo: A dictionary containing the user's information.
        """
        response = requests.get(
            f"{PHIGROS_SERVICE_BASE_URL}/users/me",
            headers= self.__httpHeaders
        )

        result = response.json()
        return result

    def get_save(self):
        """Retrieves the player's save data from the Phigros API.

        Returns:
                PlayerProfile: A dictionary containing the player's save data.
        """
        response = requests.get(
            f"{PHIGROS_SERVICE_BASE_URL}/classes/_GameSave",
            headers=self.__httpHeaders,
            params={"limit": 1}
        )

        data_save_list = response.json().get("results")
        if len(data_save_list) == 0:
            raise Exception("No save data found")
        
        return data_save_list[0]

    def get_player_summary(self):
        """Retrieves and parses the player's summary data from the save file.
        
        Returns:
                PlayerSummary: A dictionary containing the player's summary information.
        """
        try:
            result = self._save
            username = self.user_info["nickname"]
            updatedAt = result["updatedAt"]
            url = result["gameFile"]["url"]

            summary = base64.b64decode(result["summary"])
            
            pos = 0
            save_ver = summary[pos]; pos += 1
            challenges = struct.unpack("<H", summary[pos:pos+2])[0]; pos += 2
            rks = struct.unpack("<f", summary[pos:pos+4])[0]; pos += 4
            game_ver = summary[pos]; pos += 1
            pos += 1
            avatar_len = summary[pos]; pos += 1
            avatar = summary[pos:pos+avatar_len].decode('utf-8', errors = 'ignore')
            pos += avatar_len
            completion_raw = struct.unpack("<12H", summary[pos:pos+24])

            player_summary = {
                "username": username,
                "updated_at": updatedAt,
                "url": url,
                "save_ver": save_ver,
                "challenges": challenges,
                "rks": rks,
                "display_rks": f"{rks:.2f}",
                "game_ver": game_ver,
                "avatar": avatar,
                "completion": {
                    "EZ": list(completion_raw[0:3]),
                    "HD": list(completion_raw[3:6]),
                    "IN": list(completion_raw[6:9]),
                    "AT": list(completion_raw[9:12])
                }
            }
            return player_summary
        except:
            return {}