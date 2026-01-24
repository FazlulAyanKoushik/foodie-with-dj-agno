"""
Knowledge base management for restaurant chat using Agno v2 and ChromaDB.
Provides per-restaurant knowledge base instances with dynamic configuration.
"""
import os
from typing import Dict, Optional
from decouple import config
from agno.knowledge import Knowledge
from agno.vectordb.chroma import ChromaDb


# Cache for knowledge base instances per restaurant
_knowledge_cache: Dict[str, Knowledge] = {}


def get_chroma_db(collection_name: str) -> ChromaDb:
    """
    Get ChromaDB instance with dynamic configuration.
    Supports local persistent storage and remote Chroma Cloud / Production servers.

    Args:
        collection_name: Name of the ChromaDB collection

    Returns:
        Configured ChromaDb instance
    """
    chroma_path = config("CHROMA_DB_PATH", default="chroma_data")
    chroma_host = config("CHROMA_DB_HOST", default=None)
    chroma_port_raw = config("CHROMA_DB_PORT", default=None)
    chroma_port = int(chroma_port_raw) if chroma_port_raw else None

    chroma_tenant = config("CHROMA_TENANT", default="default")
    chroma_database = config("CHROMA_DATABASE", default="default")
    chroma_api_key = config("CHROMA_API_KEY", default=None)
    chroma_ssl = config("CHROMA_SSL", default=False, cast=bool)

    # Note: For Chroma Cloud or remote servers, we use HttpClient settings
    # Agno passes extra kwargs to the underlying Chroma client
    client_kwargs = {}

    if chroma_host:
        client_kwargs["host"] = chroma_host
        if chroma_port:
            client_kwargs["port"] = chroma_port

        client_kwargs["ssl"] = chroma_ssl
        client_kwargs["tenant"] = chroma_tenant
        client_kwargs["database"] = chroma_database

        if chroma_api_key:
            from chromadb.config import Settings
            client_kwargs["settings"] = Settings(
                chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
                chroma_client_auth_credentials=chroma_api_key
            )

        return ChromaDb(
            collection=collection_name,
            persistent_client=False,
            **client_kwargs
        )

    # Use local persistent ChromaDB (development)
    # Ensure the directory exists
    os.makedirs(chroma_path, exist_ok=True)

    return ChromaDb(
        collection=collection_name,
        path=chroma_path,
        persistent_client=True,
    )


def get_restaurant_knowledge(restaurant_uid: str) -> Knowledge:
    """
    Get or create a Knowledge instance for a specific restaurant.
    Each restaurant has its own ChromaDB collection for data isolation.

    Args:
        restaurant_uid: Unique identifier for the restaurant

    Returns:
        Knowledge instance configured for the restaurant
    """
    # Check cache first
    if restaurant_uid in _knowledge_cache:
        return _knowledge_cache[restaurant_uid]

    # Create collection name based on restaurant UID
    collection_name = f"restaurant_{restaurant_uid}"

    # Initialize ChromaDB for this restaurant
    vector_db = get_chroma_db(collection_name)

    # Create Knowledge instance
    knowledge = Knowledge(
        name=f"Restaurant {restaurant_uid} Knowledge",
        vector_db=vector_db,
        max_results=10,  # Number of documents to retrieve
    )

    # Cache the instance
    _knowledge_cache[restaurant_uid] = knowledge

    return knowledge


def clear_knowledge_cache(restaurant_uid: Optional[str] = None):
    """
    Clear the knowledge cache for a specific restaurant or all restaurants.
    Useful when knowledge base needs to be reloaded.

    Args:
        restaurant_uid: Optional restaurant UID. If None, clears all cache.
    """
    global _knowledge_cache

    if restaurant_uid:
        _knowledge_cache.pop(restaurant_uid, None)
    else:
        _knowledge_cache.clear()
