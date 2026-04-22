# Phigros API 存档解析包

## 文件树

```
PhigrosAPI/
├── PhigrosTools\
├── __init__.py
├── Core.py
├── Docu.py # 根 url 和请求头
└── README.md
```

## 使用示例

```python
from PhigrosAPI import PhigrosAPI
api = PhigrosAPI('你的 session_token')

api.user_info: dict # TapTap 账户信息
api.player_summary: dict # Phigros 玩家信息
api.docu: SaveDecoder # 游戏数据，参考工具包内文档
api.docu.ava: list[str] # 已获得的头像名字
api.docu.col: list[dict{'id': str, 'num': int, 'read': int}]: # 已获得的收集品信息
api.docu.ill: list[str]: # 已获得的曲绘名字
api.docu.son: list[str]: # 已解锁的单曲名字（来自单曲精选集）
api.docu.rec: list[dict{'id': str, 'rec': list[dict{"score": int, "acc": float, "fc": bool} | {}]}]: # 所有成绩
api.docu.pro: dict: # 存档进度
```