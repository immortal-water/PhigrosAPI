# Phigros 存档解析工具包

## 文件树

```
PhigrosTools/
├── __init__.py
├── ByteReader.py
├── SaveReader.py
├── SaveDecoder.py
├── Docu.py # 密钥
└── README.md
```

## 类

```python
class ByteReader: # 数据读入
    def __init__(self, data: bytes): # 使用 bytes 初始化
    def read_bool(self) -> bool: # 读入 1 比特布尔数
    def align_to_byte(self): # 使指针指到字节末尾
    def read_int(self, len: int = 0) -> int: # 读入 len 字节整数，0 为变长整数
    def read_float(self) -> float: # 读入 4 字节浮点数
    def read_string(self) -> str: # 读入 1 字节整数 len，再读入 len 字节字符串
    def read_keydata(self) -> list[int]: # 读入 Phigros 收集要素附加字段
    def read_record(self) -> list[dict]: # 读入 Phigros 歌曲成绩附加字段
class SaveReader: # 存档游戏数据下载解密
    def __init__(self, url: str): # 从 url 下载并解密
    gameKey # 解密 gameKey bytes
    gameProgress # 解密 gameProgress bytes
    gameRecord # 解密 gameRecord bytes
    settings # 解密 settings bytes
    user # 解密 user bytes
class SaveDecoder:
    def __init__(self, url: str): # 从 url 获得数据并解码
    ava: list[str] # 已获得的头像名字
    col: list[dict{'id': str, 'num': int, 'read': int}]: # 已获得的收集品信息
    ill: list[str]: # 已获得的曲绘名字
    son: list[str]: # 已解锁的单曲名字（来自单曲精选集）
    rec: list[dict{'id': str, 'rec': list[dict{"score": int, "acc": float, "fc": bool} | {}]}]: # 所有成绩
    pro: dict: # 存档进度
```

## 编码格式

首先对于下载的 zip，其文件树为

```
zip/
├── gameKey
├── gameProgress
├── gameRecord
├── settings
└── user
```

所有文件第一个字节为版本标识，剩余字节用密钥解密得到原始 'bytes'

### 一、gameKey 文件格式

存储游戏中的头像、曲绘、收集品、单曲精选集解锁信息。

| 字节偏移/顺序 | 字段/结构 | 类型/说明 |
| :--- | :--- | :--- |
| 0 | 条目数量 | 变长整数 |
| 1 | 第 1 条记录开始 | - |
| ... | 单字节表示名称长度 + 名称 | 字符串 |
| ... | 单字节表示 Data 长度 + KeyData | 二进制数据（详见 KeyData 表格） |
| ... | 第 2 条记录开始 | - |
| ... | ... | 后续条目重复上述结构 |

#### KeyData 格式（5 个标志位）

| 字节偏移 | 字段 | 类型/说明 |
| :--- | :--- | :--- |
| 0 | 标志位 | 1 字节。位 0-4 含义：<br>bit0: 文件是否已阅读（附加数据为已阅读数量）<br>bit1: 是否为已解锁的精选集内单曲<br>bit2: 是否为文件（附加数据为文件数量）<br>bit3: 是否为曲绘<br>bit4: 是否为头像 |
| 1 | 对每个为 1 的位（按位顺序） | 依次出现 |
| ... | 数值 | 1 字节，对应标志位的具体数据 |

### 二、gameRecord 文件格式

存储每首歌曲在 5 种难度（EZ HD IN AT 旧版）下的游玩记录（分数、准确度、FC 状态）。

| 字节偏移/顺序 | 字段/结构 | 类型/说明 |
| :--- | :--- | :--- |
| 0 | 记录数量 | 变长整数 |
| 1 | 第 1 条记录开始 | - |
| ... | 单字节表示名称长度 + 歌曲ID | 字符串，最后 2 字节为 `\x00\x00` |
| ... | 单字节表示 Data 长度 + Data | 二进制数据（详见 RecordData 表格） |
| ... | 第 2 条记录开始 | - |
| ... | ... | 后续条目重复上述结构 |

#### RecordData 格式（5 种难度）

| 字节偏移 | 字段 | 类型/说明 |
| :--- | :--- | :--- |
| 0 | 完成标志 (fns_flag) | 1 字节。位 0-4 表示对应难度是否有记录 |
| 1 | FC 标志 (fc_flag) | 1 字节。位 0-4 表示对应难度是否 FC |
| 2 | 对每个有记录的难度 | 循环出现 |
| ... | 分数 | 4 字节整数 |
| ... | 准确度 | 4 字节浮点数 |

## 三、gameProgress 文件格式

| 顺序 | 字段 | 类型/大小 | 说明 |
| :--- | :--- | :--- | :--- |
| 1 | `is_first_run` | 1 位 | 布尔 |
| 2 | `legacy_chapter_finished` | 1 位 | 布尔 |
| 3 | `already_show_collection_tip` | 1 位 | 布尔 |
| 4 | `already_show_auto_unlock_in_tip` | 1 位 | 布尔 |
| 5 | `completed` | 字符串 | 1 字节长度 + UTF-8 |
| 6 | `song_update_info` | 1 字节 | 整数 |
| 7 | `challenge_mode_rank` | 2 字节 | 整数（大端序） |
| 8 | `money_0` | 变长整数 | - |
| 9 | `money_1` | 变长整数 | - |
| 10 | `money_2` | 变长整数 | - |
| 11 | `money_3` | 变长整数 | - |
| 12 | `money_4` | 变长整数 | - |
| 13 | `unlock_flag_of_spasmodic` | 1 字节 | 整数 |
| 14 | `unlock_flag_of_igallta` | 1 字节 | 整数 |
| 15 | `unlock_flag_of_rrharil` | 1 字节 | 整数 |
| 16 | `flag_of_song_record_key` | 1 字节 | 整数 |
| 17 | `random_version_unlocked` | 1 字节 | 整数 |
| 18 | `chapter8_unlock_begin` | 1 位 | 布尔 |
| 19 | `chapter8_unlock_second_phase` | 1 位 | 布尔 |
| 20 | `chapter8_passed` | 1 位 | 布尔 |
| 21 | `chapter8_song_unlocked` | 1 字节 | 整数 |