import logging
import chromadb
import os
import threading
from chromadb.utils import embedding_functions

from long_memory.long_memory_interface import AbstractLongMemory, LongMemoryItem

# 系统数据路径
SYSTEM_DATA_PATH = "./data/system_data"
# 默认集合名称
DEFAULT_COLLECTION_NAME = "long_memory_collection"

class ChromaLongMemory(AbstractLongMemory):
    def __init__(self, collection_name=DEFAULT_COLLECTION_NAME, cache_size=100):
        # 初始化日志记录器
        self._logger = logging.getLogger(__name__)
        # 初始化集合为 None
        self._collection = None
        # 使用提供的集合名称（或默认值）
        self._collection_name = collection_name
        # 初始化缓存字典
        self._cache = {}
        # 缓存大小限制
        self._cache_size = cache_size
        # 初始化线程锁以确保线程安全
        self._lock = threading.Lock()
        
    def init(self):
        # 持久化数据目录
        persist_directory = os.path.join(os.path.split(os.path.abspath(__file__))[0], "../../",
                                         SYSTEM_DATA_PATH, "long_memory")

        try:
            # 创建客户端实例
            client = chromadb.PersistentClient(path=persist_directory)
            # 获取或创建指定名称的集合
            self._collection = client.get_or_create_collection(name=self._collection_name)

            # 记录初始化信息
            self._logger.info("Initializing ChromaLongMemory...")
            # 进行一次搜索以确保初始化正常
            self.search(text="init message", n_results=1)
            self._logger.info("ChromaLongMemory initialized successfully")
        except Exception as e:
            # 记录初始化失败信息
            self._logger.error(f"Failed to initialize ChromaLongMemory: {e}")
            raise

    def save(self, items: [LongMemoryItem]):
        if not items:
            return

        documents = []
        metadatas = []
        ids = []
        to_delete_ids = []

        with self._lock:
            for item in items:
                # 根据内容搜索相似项
                old_memories = self.search(text=item.content, n_results=5)
                # 收集需要删除的项的 ID
                to_delete_ids.extend([old_memory.id for old_memory in old_memories if old_memory.distance < 0.2])
                # 准备保存的文档、元数据和 ID
                documents.append(item.content)
                metadatas.append(item.metadata)
                ids.append(item.id)

            # 删除重复项
            self.delete(to_delete_ids)
            try:
                # 将新项添加到集合中
                self._collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids,
                )
                # 更新缓存
                self._update_cache(items)
            except Exception as e:
                # 记录保存失败信息
                self._logger.error(f"Failed to save items to ChromaLongMemory: {e}")

    def search(self, text: str, n_results: int, metadata_filter: dict = None) -> [LongMemoryItem]:
        # 生成缓存键
        cache_key = (text, n_results, frozenset(metadata_filter.items()) if metadata_filter else None)
        
        with self._lock:
            # 检查缓存
            if cache_key in self._cache:
                self._logger.info(f"Cache hit for key: {cache_key}")
                return self._cache[cache_key]        
        try:
            # 从集合中查询结果
            results = self._collection.query(
                query_texts=[text],
                n_results=n_results,
                where=metadata_filter,
            )
            # 初始化结果项
            items = [LongMemoryItem.new(content="", metadata={}, id="") for _ in range(len(results.get('ids')[0]))]

            # 更新结果项的属性
            for k, v in results.items():
                if k == 'ids':
                    for i in range(len(v[0])):
                        items[i].id = v[0][i]
                elif k == 'metadatas':
                    for i in range(len(v[0])):
                        items[i].metadata = v[0][i]
                elif k == 'documents':
                    for i in range(len(v[0])):
                        items[i].content = v[0][i]
                elif k == 'distances':
                    for i in range(len(v[0])):
                        items[i].distance = v[0][i]
                        
            with self._lock:
                # 更新缓存，如果缓存满了，删除最旧的项
                if len(self._cache) >= self._cache_size:
                    self._cache.pop(next(iter(self._cache)))
                self._cache[cache_key] = items    
                                    
            return items
        except Exception as e:
            # 记录搜索失败信息
            self._logger.error(f"Search failed in ChromaLongMemory: {e}")
            return []

    def delete(self, ids: list):
        if not ids:
            return
        try:
            # 从集合中删除指定的项
            self._collection.delete(ids=ids)
        except Exception as e:
            # 记录删除失败信息
            self._logger.error(f"Failed to delete items from ChromaLongMemory: {e}")
            
    def _update_cache(self, items):
        # 更新缓存
        for item in items:
            cache_key = (item.content, 1, frozenset(item.metadata.items()))
            self._cache[cache_key] = [item]

    def _invalidate_cache(self, ids):
        # 使缓存中的项失效
        keys_to_remove = [k for k, v in self._cache.items() if any(item.id in ids for item in v)]
        for key in keys_to_remove:
            del self._cache[key]
