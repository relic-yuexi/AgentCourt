# EMDB/db.py

import os
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions


class db:
    def __init__(self, agent_name, EmbeddingModelName="BAAI/bge-m3", device="cpu"):
        self.agent_name = agent_name
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EmbeddingModelName, device=device
        )
        self.client = self._create_client()
        self.experience_collection = self._create_collection("experience")
        self.case_collection = self._create_collection("case")
        self.legal_collection = self._create_collection("legal")

    def _create_client(self):
        client_path = os.path.join("db", self.agent_name)
        os.makedirs(client_path, exist_ok=True)
        return chromadb.PersistentClient(path=client_path)

    def _create_collection(self, collection_name):
        return self.client.get_or_create_collection(
            name=f"{self.agent_name}_{collection_name}",
            embedding_function=self.embedding_fn,
        )

    def add_to_experience(self, id, document, metadata=None):
        self.experience_collection.add(
            documents=[document], metadatas=[metadata] if metadata else None, ids=[id]
        )

    def add_to_case(self, id, document, metadata=None):
        self.case_collection.add(
            documents=[document], metadatas=[metadata] if metadata else None, ids=[id]
        )

    def add_to_legal(self, id, document, metadata=None):
        self.legal_collection.add(
            documents=[document], metadatas=[metadata] if metadata else None, ids=[id]
        )

    def query_experience(self, query_text, n_results=5, include=["documents"]):
        result = self.experience_collection.query(
            query_texts=[query_text], n_results=n_results, include=include
        )
        documents = result.get("documents", [[]])[0]
        return documents[0] if documents else ""

    def query_experience_metadatas(self, query_text, n_results=5):
        result = self.experience_collection.query(
            query_texts=[query_text], n_results=n_results, include=["metadatas"]
        )
        metadatas = result.get("metadatas", [[]])[0]

        # 查找包含 "context" 键的第一个字典
        for metadata in metadatas:
            if "context" in metadata:
                return metadata["context"]

        # 如果没有找到包含 "context" 的字典，返回空字符串
        return ""

    def query_experience_documents(self, query_text, n_results=5):
        result = self.experience_collection.query(
            query_texts=[query_text], n_results=n_results, include=["documents"]
        )
        documents = result.get("documents", [[]])[0]
        return documents[0] if documents else ""

    def query_case(self, query_text, n_results=5, include=["documents"]):
        result = self.case_collection.query(
            query_texts=[query_text], n_results=n_results, include=include
        )
        documents = result.get("documents", [[]])[0]
        return documents[0] if documents else ""

    def query_case_documents(self, query_text, n_results=5):
        result = self.case_collection.query(
            query_texts=[query_text], n_results=n_results, include=["documents"]
        )
        documents = result.get("documents", [[]])[0]
        return documents[0] if documents else ""

    def query_case_metadatas(self, query_text, n_results=5):
        result = self.case_collection.query(
            query_texts=[query_text], n_results=n_results, include=["metadatas"]
        )
        metadatas = result.get("metadatas", [[]])[0]

        # 查找包含 "context" 键的第一个字典
        for metadata in metadatas:
            if "response_directions" in metadata:
                return metadata["response_directions"]

        # 如果没有找到包含 "context" 的字典，返回空字符串
        return ""

    def query_legal(self, query_text, n_results=5, include=["documents"]):
        result = self.legal_collection.query(
            query_texts=[query_text], n_results=n_results, include=include
        )
        documents = result.get("documents", [[]])[0]
        return documents[0] if documents else ""
