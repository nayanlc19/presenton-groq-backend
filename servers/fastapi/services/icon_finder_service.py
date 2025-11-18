import asyncio
import json
import os


class IconFinderService:
    def __init__(self):
        self.collection_name = "icons"
        self._client = None
        self._collection = None
        self._initialized = False

    def _initialize_icons_collection(self):
        """Lazy initialization - only runs when first icon search is requested"""
        if self._initialized:
            return
        
        # Import ChromaDB only when needed (optional dependency)
        try:
            import chromadb
            from chromadb.config import Settings
            from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
        except ImportError:
            print("ChromaDB not installed - icon search will fail gracefully")
            self._initialized = True
            return
            
        print("Initializing icons collection (lazy load)...")
        
        # Use APP_DATA_DIRECTORY if available, otherwise use relative path
        app_data_dir = os.environ.get("APP_DATA_DIRECTORY", ".")
        chroma_path = os.path.join(app_data_dir, "chroma")
        
        try:
            self._client = chromadb.PersistentClient(
                path=chroma_path, settings=Settings(anonymized_telemetry=False)
            )
        except Exception as e:
            print(f"Failed to initialize ChromaDB at {chroma_path}: {e}")
            print("Icon search will return empty results")
            self._initialized = True
            return
        
        self.embedding_function = ONNXMiniLM_L6_V2()
        model_path = os.path.join(chroma_path, "models")
        self.embedding_function.DOWNLOAD_PATH = model_path
        self.embedding_function._download_model_if_not_exists()
        try:
            self._collection = self._client.get_collection(
                self.collection_name, embedding_function=self.embedding_function
            )
        except Exception:
            with open("assets/icons.json", "r") as f:
                icons = json.load(f)

            documents = []
            ids = []

            for i, each in enumerate(icons["icons"]):
                if each["name"].split("-")[-1] == "bold":
                    doc_text = f"{each['name']} {each['tags']}"
                    documents.append(doc_text)
                    ids.append(each["name"])

            if documents:
                self._collection = self._client.create_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function,
                    metadata={"hnsw:space": "cosine"},
                )
                self._collection.add(documents=documents, ids=ids)
        
        self._initialized = True
        print("Icons collection initialized.")

    async def search_icons(self, query: str, k: int = 1):
        # Lazy initialization on first use
        if not self._initialized:
            await asyncio.to_thread(self._initialize_icons_collection)
        
        # If ChromaDB not available, return empty list
        if self._collection is None:
            print("ChromaDB not available - returning empty icon list")
            return []
        
        result = await asyncio.to_thread(
            self._collection.query,
            query_texts=[query],
            n_results=k,
        )
        return [f"/static/icons/bold/{each}.svg" for each in result["ids"][0]]


ICON_FINDER_SERVICE = IconFinderService()
