import os
import asyncpg
from typing import Any, List, Dict, Optional, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PostgresHandler:
    """
    Handler for PostgreSQL database operations using a single connection.
    """
    def __init__(self, connection_url: Optional[str] = None):
        """
        Initialize the PostgreSQL handler.
        
        Args:
            connection_url: PostgreSQL connection URL. If None, gets from POSTGRES_URL env var.
        """
        self.connection_url = connection_url or os.environ.get("POSTGRES_URL")
        self.connection = None
        
        if not self.connection_url:
            raise ValueError("PostgreSQL connection URL is required. Set POSTGRES_URL environment variable.")
    
    async def connect(self) -> None:
        """
        Create a single connection to the PostgreSQL database.
        """
        if self.connection is None:
            try:
                self.connection = await asyncpg.connect(
                    dsn=self.connection_url,
                    timeout=10
                )
            except Exception as e:
                raise ConnectionError(f"Failed to connect to PostgreSQL: {str(e)}")
    
    async def close(self) -> None:
        """
        Close the connection.
        """
        if self.connection:
            await self.connection.close()
            self.connection = None
    
    async def run_query(
        self, 
        query: str, 
        params: Optional[List[Any]] = None, 
        fetch_type: str = "all"
    ) -> Union[List[Dict[str, Any]], Dict[str, Any], int, None]:
        """
        Run a SQL query and return the results.
        
        Args:
            query: SQL query string
            params: Query parameters to pass to the query
            fetch_type: Type of fetch operation ('all', 'one', 'val', or 'status')
        
        Returns:
            Query results based on fetch_type:
            - 'all': List of dictionaries containing all rows
            - 'one': Single dictionary containing first row
            - 'val': Single value from first column of first row
            - 'status': Number of rows affected (for INSERT/UPDATE/DELETE)
        """
        if self.connection is None:
            await self.connect()
        
        params = params or []
        
        try:
            if fetch_type == "all":
                # Return all rows as dictionaries
                rows = await self.connection.fetch(query, *params)
                return [dict(row) for row in rows]
            
            elif fetch_type == "one":
                # Return a single row as dictionary
                row = await self.connection.fetchrow(query, *params)
                return dict(row) if row else None
            
            elif fetch_type == "val":
                # Return a single value
                return await self.connection.fetchval(query, *params)
            
            elif fetch_type == "status":
                # Execute query and return status (rows affected)
                status = await self.connection.execute(query, *params)
                if status.startswith("INSERT") or status.startswith("UPDATE") or status.startswith("DELETE"):
                    return int(status.split()[1])
                return 0
            
            else:
                raise ValueError(f"Invalid fetch_type: {fetch_type}")
                
        except Exception as e:
            # Log the error and re-raise
            print(f"Database error executing query: {str(e)}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            raise
    
    async def execute_transaction(self, queries: List[Dict[str, Any]]) -> List[Any]:
        """
        Execute multiple queries as a single transaction.
        
        Args:
            queries: List of query dictionaries, each with keys:
                    - 'query': SQL query string
                    - 'params': Query parameters (optional)
                    - 'fetch_type': Fetch type for this query (optional)
        
        Returns:
            List of results for each query
        """
        if self.connection is None:
            await self.connect()
        
        results = []
        
        try:
            # Start a transaction
            async with self.connection.transaction():
                for q in queries:
                    query = q["query"]
                    params = q.get("params", [])
                    fetch_type = q.get("fetch_type", "status")
                    
                    if fetch_type == "all":
                        rows = await self.connection.fetch(query, *params)
                        results.append([dict(row) for row in rows])
                    
                    elif fetch_type == "one":
                        row = await self.connection.fetchrow(query, *params)
                        results.append(dict(row) if row else None)
                    
                    elif fetch_type == "val":
                        val = await self.connection.fetchval(query, *params)
                        results.append(val)
                    
                    elif fetch_type == "status":
                        status = await self.connection.execute(query, *params)
                        if status.startswith("INSERT") or status.startswith("UPDATE") or status.startswith("DELETE"):
                            results.append(int(status.split()[1]))
                        else:
                            results.append(0)
                    
                    else:
                        raise ValueError(f"Invalid fetch_type: {fetch_type}")
        
        except Exception as e:
            print(f"Transaction error: {str(e)}")
            print(f"Queries: {queries}")
            raise
            
        return results

# Example usage:
# 
# async def example():
#     db = PostgresHandler()
#     try:
#         # Connect to database
#         await db.connect()
#         
#         # Run a simple query
#         users = await db.run_query("SELECT * FROM users WHERE active = $1", [True])
#         
#         # Insert data
#         user_id = await db.run_query(
#             "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING id",
#             ["John Doe", "john@example.com"],
#             fetch_type="val"
#         )
#         
#         # Run a transaction
#         results = await db.execute_transaction([
#             {
#                 "query": "INSERT INTO orders (user_id, product_id) VALUES ($1, $2) RETURNING id",
#                 "params": [user_id, 123],
#                 "fetch_type": "val"
#             },
#             {
#                 "query": "UPDATE inventory SET stock = stock - 1 WHERE product_id = $1",
#                 "params": [123]
#             }
#         ])
#         
#     finally:
#         # Close connection
#         await db.close() 