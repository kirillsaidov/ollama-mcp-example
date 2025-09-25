# module mongo_mcp_server

# system
import os, sys
import datetime
from typing import Any, Dict, List, Optional

# libs
from mcp.server.fastmcp import FastMCP
from pymongo import MongoClient
from bson import ObjectId


# init global state
mcp = FastMCP("MongoDB MCP Server")
mongo_client = MongoClient(os.getenv("MONGODB_RUI", "mongodb://localhost:27017"))


def conv_to_json_compatible_types(v: Any) -> Any:
    """Convert common BSON types to compatible JSON-friendly types. For example: datetime object => ISO time as string.
    """
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, datetime.datetime):
        return v.isoformat()
    if isinstance(v, list):
        return [conv_to_json_compatible_types(i) for i in v]
    if isinstance(v, dict):
        return {k: conv_to_json_compatible_types(val) for k, val in v.items()}
    return v
    

@mcp.tool()
def mongo_list_records(db_name: str, collection_name: str, query: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """List records in MongoDB collection.

    Args:
        db_name (str): mongo database name
        collection_name (str): mongo collection name
        query (Optional[Dict[str, Any]]): optional simple MongoDB filter as a dict. Defaults to None.
        limit (int): maximum number of records to retrieve. Defaults to 100.
    """
    if not query: query = {}

    # query collection
    col = mongo_client[db_name][collection_name]
    cursor = col.find(query).limit(limit)
    records = [conv_to_json_compatible_types(d) for d in cursor]

    return records
    

if __name__ == '__main__':
    mcp.run(transport='stdio')
    

