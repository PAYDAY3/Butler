
import sqlite3
import os
import threading
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from my_package import Logging

# 短期记忆数据路径
SYSTEM_DATA_PATH = "./data/system_data"
# 默认集合名称
DEFAULT_COLLECTION_NAME = "short_term_memory_collection"
# 数据库文件名称
DATABASE_FILE_NAME = "short_term_memory.db"

class ShortTermMemoryItem:
    def __init__(self, id: str, content: str, metadata: Dict[str, str]):
        self.id = id
        self.content = content
        self.metadata = metadata
        self.timestamp = datetime.now()
    
    @classmethod
    def new(cls, content: str, metadata: Dict[str, str], id: str):
        return cls(id, content, metadata)

class SQLiteShortTermMemory:
    def __init__(self, collection_name: str = DEFAULT_COLLECTION_NAME, cache_size: int = 100):
        self._logger = Logging.getLogger(__name__)
        self._conn: Optional[sqlite3.Connection] = None
        self._collection_name = collection_name
        self._cache: Dict[Tuple[str, int, Optional[frozenset]], List[ShortTermMemoryItem]] = {}
        self._cache_size = cache_size
        self._lock = threading.Lock()

    def init(self):
        db_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], "../../", SYSTEM_DATA_PATH, DATABASE_FILE_NAME)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        try:
            self._conn = sqlite3.connect(db_path)
            self._create_table()
            self._logger.info("初始化 SQLiteShortTermMemory...")
            self._logger.info("SQLiteShortTermMemory 初始化成功")
        except Exception as e:
            self._logger.error(f"初始化 SQLiteShortTermMemory 失败: {e}")
            raise

    def _create_table(self):
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self._collection_name} (
            id TEXT PRIMARY KEY,
            content TEXT,
            metadata TEXT,
            timestamp TEXT
        );
        """
        with self._conn:
            self._conn.execute(create_table_sql)

    def save(self, items: List[ShortTermMemoryItem]):
        if not items:
            return

        with self._lock:
            try:
                with self._conn:
                    for item in items:
                        self._conn.execute(f"""
                        INSERT INTO {self._collection_name} (id, content, metadata, timestamp) VALUES (?, ?, ?, ?)
                        """, (item.id, item.content, str(item.metadata), item.timestamp.isoformat()))
                self._update_cache(items)
            except Exception as e:
                self._logger.error(f"保存项到 SQLiteShortTermMemory 失败: {e}")

    def search(self, text: str, n_results: int, metadata_filter: Optional[Dict[str, str]] = None) -> List[ShortTermMemoryItem]:
        cache_key = (text, n_results, frozenset(metadata_filter.items()) if metadata_filter else None)

        with self._lock:
            if cache_key in self._cache:
                self._logger.info(f"缓存命中键: {cache_key}")
                return self._cache[cache_key]

        try:
            cursor = self._conn.cursor()
            if metadata_filter:
                filter_conditions = " AND ".join([f"json_extract(metadata, '$.{key}') = ?" for key in metadata_filter.keys()])
                filter_values = list(metadata_filter.values())
                query = f"""
                SELECT id, content, metadata, timestamp FROM {self._collection_name}
                WHERE content LIKE ? AND {filter_conditions}
                LIMIT ?
                """
                cursor.execute(query, (f"%{text}%", *filter_values, n_results))
            else:
                query = f"""
                SELECT id, content, metadata, timestamp FROM {self._collection_name}
                WHERE content LIKE ?
                LIMIT ?
                """
                cursor.execute(query, (f"%{text}%", n_results))

            rows = cursor.fetchall()
            items = [ShortTermMemoryItem.new(content=row[1], metadata=eval(row[2]), id=row[0]) for row in rows]

            with self._lock:
                if len(self._cache) >= self._cache_size:
                    self._cache.pop(next(iter(self._cache)))
                self._cache[cache_key] = items

            return items
        except Exception as e:
            self._logger.error(f"SQLiteShortTermMemory 搜索失败: {e}")
            return []

    def delete(self, ids: List[str]):
        if not ids:
            return
        try:
            with self._conn:
                self._conn.executemany(f"""
                DELETE FROM {self._collection_name} WHERE id = ?
                """, [(id,) for id in ids])
            self._invalidate_cache(ids)
        except Exception as e:
            self._logger.error(f"从 SQLiteShortTermMemory 删除项失败: {e}")

    def _update_cache(self, items: List[ShortTermMemoryItem]):
        for item in items:
            cache_key = (item.content, 1, frozenset(item.metadata.items()))
            self._cache[cache_key] = [item]

    def _invalidate_cache(self, ids: List[str]):
        keys_to_remove = [k for k, v in self._cache.items() if any(item.id in ids for item in v)]
        for key in keys_to_remove:
            del self._cache[key]

    def clear_memory(self):
        try:
            with self._conn:
                self._conn.execute(f"DELETE FROM {self._collection_name}")
            self._cache.clear()
            self._logger.info("所有短期记忆已清除")
        except Exception as e:
            self._logger.error(f"清除所有短期记忆失败: {e}")
