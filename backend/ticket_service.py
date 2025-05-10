import os
import asyncio
import asyncpg
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import json
import uuid
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

class TicketService:
    """Service for managing tickets and todo items using PostgreSQL"""
    
    def __init__(self):
        """Initialize the ticket service"""
        self.db_url = os.environ.get("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self.pool = None
    
    async def get_connection(self):
        """Get a database connection from the pool"""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(self.db_url)
        
        return await self.pool.acquire()
    
    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def initialize_db(self) -> bool:
        """Initialize database tables if they don't exist"""
        try:
            conn = await self.get_connection()
            try:
                # Create tickets table
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS tickets (
                        id SERIAL PRIMARY KEY,
                        ticket_number TEXT UNIQUE NOT NULL,
                        ticket_category TEXT NOT NULL,
                        description TEXT NOT NULL,
                        completion_criteria TEXT,
                        status TEXT NOT NULL DEFAULT 'active',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create todo_items table
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS todo_items (
                        id SERIAL PRIMARY KEY,
                        ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
                        description TEXT NOT NULL,
                        done BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        position INTEGER NOT NULL DEFAULT 0
                    )
                ''')
                
                return True
            finally:
                await self.pool.release(conn)
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            return False
    
    async def create_ticket(self, 
                         ticket_category: str, 
                         ticket_number: Optional[str] = None,
                         description: str = "",
                         completion_criteria: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new ticket
        
        Args:
            ticket_category: Category of the ticket (e.g., 'bug', 'feature')
            ticket_number: Optional ticket number, will be auto-generated if not provided
            description: Ticket description
            completion_criteria: Criteria for marking the ticket as complete
        
        Returns:
            Created ticket details
        """
        if not ticket_number:
            # Generate a ticket number if not provided
            prefix = ticket_category.upper()[:3]
            timestamp = int(datetime.now().timestamp())
            random_suffix = uuid.uuid4().hex[:4]
            ticket_number = f"{prefix}-{timestamp}-{random_suffix}"
        
        try:
            conn = await self.get_connection()
            try:
                # Insert ticket and return all fields
                row = await conn.fetchrow('''
                    INSERT INTO tickets (ticket_number, ticket_category, description, completion_criteria)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id, ticket_number, ticket_category, description, completion_criteria, status, 
                              created_at, updated_at
                ''', ticket_number, ticket_category, description, completion_criteria)
                
                # Convert to dictionary
                ticket = dict(row)
                
                # Format datetime objects to ISO strings
                ticket['created_at'] = ticket['created_at'].isoformat()
                ticket['updated_at'] = ticket['updated_at'].isoformat()
                
                # Add empty todo_items array
                ticket['todo_items'] = []
                
                return ticket
            finally:
                await self.pool.release(conn)
        except asyncpg.UniqueViolationError:
            raise ValueError(f"Ticket with number {ticket_number} already exists")
        except Exception as e:
            print(f"Error creating ticket: {str(e)}")
            raise
    
    async def get_ticket(self, 
                      ticket_number: str,
                      ticket_category: Optional[str] = None,
                      include_history: bool = False,
                      include_todos: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get a ticket by number
        
        Args:
            ticket_number: The ticket number
            ticket_category: Optional category to further filter by
            include_history: Whether to include ticket history
            include_todos: Whether to include todo items
        
        Returns:
            Ticket details or None if not found
        """
        try:
            conn = await self.get_connection()
            try:
                # Build query based on whether category is provided
                query = '''
                    SELECT id, ticket_number, ticket_category, description, completion_criteria, status, 
                           created_at, updated_at
                    FROM tickets
                    WHERE ticket_number = $1
                '''
                params = [ticket_number]
                
                if ticket_category:
                    query += " AND ticket_category = $2"
                    params.append(ticket_category)
                
                # Only get active tickets unless history is requested
                if not include_history:
                    query += f" AND status = 'active'"
                
                # Get the ticket
                row = await conn.fetchrow(query, *params)
                
                if not row:
                    return None
                
                # Convert to dictionary
                ticket = dict(row)
                
                # Format datetime objects
                ticket['created_at'] = ticket['created_at'].isoformat()
                ticket['updated_at'] = ticket['updated_at'].isoformat()
                
                # Include todo items if requested
                if include_todos:
                    todo_rows = await conn.fetch('''
                        SELECT id, description, done, created_at, updated_at, position
                        FROM todo_items
                        WHERE ticket_id = $1
                        ORDER BY position ASC
                    ''', ticket['id'])
                    
                    todo_items = []
                    for todo_row in todo_rows:
                        todo_item = dict(todo_row)
                        todo_item['created_at'] = todo_item['created_at'].isoformat()
                        todo_item['updated_at'] = todo_item['updated_at'].isoformat()
                        todo_items.append(todo_item)
                    
                    ticket['todo_items'] = todo_items
                
                return ticket
            finally:
                await self.pool.release(conn)
        except Exception as e:
            print(f"Error getting ticket: {str(e)}")
            raise
    
    async def list_tickets(self,
                        category: Optional[str] = None, 
                        active_only: bool = True,
                        include_todos: bool = False,
                        limit: int = 100,
                        offset: int = 0) -> Dict[str, Any]:
        """
        List tickets with optional filtering
        
        Args:
            category: Optional category to filter by
            active_only: Whether to only include active tickets
            include_todos: Whether to include todo items
            limit: Maximum number of tickets to return
            offset: Offset for pagination
        
        Returns:
            List of tickets
        """
        try:
            conn = await self.get_connection()
            try:
                # Build query based on filters
                query = '''
                    SELECT id, ticket_number, ticket_category, description, completion_criteria, status, 
                           created_at, updated_at
                    FROM tickets
                    WHERE 1=1
                '''
                params = []
                
                if category:
                    query += f" AND ticket_category = ${len(params) + 1}"
                    params.append(category)
                
                if active_only:
                    query += f" AND status = 'active'"
                
                # Add count query for pagination
                count_query = query.replace("SELECT id, ticket_number, ticket_category, description, completion_criteria, status, created_at, updated_at", "SELECT COUNT(*)")
                
                # Add pagination
                query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
                params.extend([limit, offset])
                
                # Get total count
                total = await conn.fetchval(count_query, *params[:-2] if params else [])
                
                # Get tickets
                rows = await conn.fetch(query, *params)
                
                tickets = []
                for row in rows:
                    ticket = dict(row)
                    
                    # Format datetime objects
                    ticket['created_at'] = ticket['created_at'].isoformat()
                    ticket['updated_at'] = ticket['updated_at'].isoformat()
                    
                    # Include todo items if requested
                    if include_todos:
                        todo_rows = await conn.fetch('''
                            SELECT id, description, done, created_at, updated_at, position
                            FROM todo_items
                            WHERE ticket_id = $1
                            ORDER BY position ASC
                        ''', ticket['id'])
                        
                        todo_items = []
                        for todo_row in todo_rows:
                            todo_item = dict(todo_row)
                            todo_item['created_at'] = todo_item['created_at'].isoformat()
                            todo_item['updated_at'] = todo_item['updated_at'].isoformat()
                            todo_items.append(todo_item)
                        
                        ticket['todo_items'] = todo_items
                    else:
                        ticket['todo_items'] = []
                    
                    tickets.append(ticket)
                
                return {
                    "tickets": tickets,
                    "total": total,
                    "limit": limit,
                    "offset": offset
                }
            finally:
                await self.pool.release(conn)
        except Exception as e:
            print(f"Error listing tickets: {str(e)}")
            raise
    
    async def update_ticket(self,
                         ticket_number: str,
                         ticket_category: Optional[str] = None,
                         description: Optional[str] = None,
                         completion_criteria: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Update a ticket
        
        Args:
            ticket_number: The ticket number to update
            ticket_category: New category (optional)
            description: New description (optional)
            completion_criteria: Criteria for marking the ticket as complete (optional)
        
        Returns:
            Updated ticket details or None if not found
        """
        if not ticket_category and not description and completion_criteria is None:
            raise ValueError("At least one of ticket_category, description, or completion_criteria must be provided")
        
        try:
            conn = await self.get_connection()
            try:
                # First, check if the ticket exists and get its ID
                ticket_id = await conn.fetchval('''
                    SELECT id FROM tickets
                    WHERE ticket_number = $1 AND status = 'active'
                ''', ticket_number)
                
                if not ticket_id:
                    return None
                
                # Build update query based on what's provided
                query_parts = []
                params = [ticket_id]
                
                if ticket_category:
                    query_parts.append(f"ticket_category = ${len(params) + 1}")
                    params.append(ticket_category)
                
                if description:
                    query_parts.append(f"description = ${len(params) + 1}")
                    params.append(description)
                
                if completion_criteria is not None:
                    query_parts.append(f"completion_criteria = ${len(params) + 1}")
                    params.append(completion_criteria)
                
                # Always update the updated_at timestamp
                query_parts.append("updated_at = CURRENT_TIMESTAMP")
                
                # Build the full query
                query = f'''
                    UPDATE tickets
                    SET {", ".join(query_parts)}
                    WHERE id = $1
                    RETURNING id, ticket_number, ticket_category, description, completion_criteria, status, 
                              created_at, updated_at
                '''
                
                # Update the ticket
                row = await conn.fetchrow(query, *params)
                
                if not row:
                    return None
                
                # Convert to dictionary
                ticket = dict(row)
                
                # Format datetime objects
                ticket['created_at'] = ticket['created_at'].isoformat()
                ticket['updated_at'] = ticket['updated_at'].isoformat()
                
                # Include todo items
                todo_rows = await conn.fetch('''
                    SELECT id, description, done, created_at, updated_at, position
                    FROM todo_items
                    WHERE ticket_id = $1
                    ORDER BY position ASC
                ''', ticket['id'])
                
                todo_items = []
                for todo_row in todo_rows:
                    todo_item = dict(todo_row)
                    todo_item['created_at'] = todo_item['created_at'].isoformat()
                    todo_item['updated_at'] = todo_item['updated_at'].isoformat()
                    todo_items.append(todo_item)
                
                ticket['todo_items'] = todo_items
                
                return ticket
            finally:
                await self.pool.release(conn)
        except Exception as e:
            print(f"Error updating ticket: {str(e)}")
            raise
    
    async def delete_ticket(self,
                         ticket_number: str,
                         ticket_category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Soft delete a ticket (mark as inactive)
        
        Args:
            ticket_number: The ticket number to delete
            ticket_category: Optional category to further filter by
        
        Returns:
            Deleted ticket details or None if not found
        """
        try:
            conn = await self.get_connection()
            try:
                # Build query based on whether category is provided
                query = '''
                    UPDATE tickets
                    SET status = 'inactive', updated_at = CURRENT_TIMESTAMP
                    WHERE ticket_number = $1 AND status = 'active'
                '''
                params = [ticket_number]
                
                if ticket_category:
                    query += " AND ticket_category = $2"
                    params.append(ticket_category)
                
                query += '''
                    RETURNING id, ticket_number, ticket_category, description, completion_criteria, status, 
                              created_at, updated_at
                '''
                
                # Update the ticket
                row = await conn.fetchrow(query, *params)
                
                if not row:
                    return None
                
                # Convert to dictionary
                ticket = dict(row)
                
                # Format datetime objects
                ticket['created_at'] = ticket['created_at'].isoformat()
                ticket['updated_at'] = ticket['updated_at'].isoformat()
                
                return ticket
            finally:
                await self.pool.release(conn)
        except Exception as e:
            print(f"Error deleting ticket: {str(e)}")
            raise
    
    async def hard_delete_ticket(self,
                              ticket_number: str,
                              ticket_category: Optional[str] = None) -> int:
        """
        Hard delete a ticket (remove from database)
        
        Args:
            ticket_number: The ticket number to delete
            ticket_category: Optional category to further filter by
        
        Returns:
            Number of tickets deleted
        """
        try:
            conn = await self.get_connection()
            try:
                # Build query based on whether category is provided
                query = '''
                    DELETE FROM tickets
                    WHERE ticket_number = $1
                '''
                params = [ticket_number]
                
                if ticket_category:
                    query += " AND ticket_category = $2"
                    params.append(ticket_category)
                
                # Delete the ticket (todo items will be deleted via CASCADE)
                result = await conn.execute(query, *params)
                
                # Parse the result to get number of deleted rows
                deleted = int(result.split(" ")[-1])
                
                return deleted
            finally:
                await self.pool.release(conn)
        except Exception as e:
            print(f"Error hard deleting ticket: {str(e)}")
            raise
    
    # Todo item methods
    
    async def add_todo_item(self,
                         ticket_number: str,
                         description: str,
                         position: Optional[int] = None) -> Dict[str, Any]:
        """
        Add a todo item to a ticket
        
        Args:
            ticket_number: The ticket number
            description: Description of the todo item
            position: Optional position in the list (default: add to end)
        
        Returns:
            Created todo item details
        """
        try:
            conn = await self.get_connection()
            try:
                # Get the ticket ID
                ticket_id = await conn.fetchval('''
                    SELECT id FROM tickets
                    WHERE ticket_number = $1 AND status = 'active'
                ''', ticket_number)
                
                if not ticket_id:
                    raise ValueError(f"Ticket {ticket_number} not found or inactive")
                
                # If position not specified, add to end
                if position is None:
                    position = await conn.fetchval('''
                        SELECT COALESCE(MAX(position) + 1, 0) FROM todo_items
                        WHERE ticket_id = $1
                    ''', ticket_id)
                
                # Insert todo item
                row = await conn.fetchrow('''
                    INSERT INTO todo_items (ticket_id, description, position)
                    VALUES ($1, $2, $3)
                    RETURNING id, description, done, created_at, updated_at, position
                ''', ticket_id, description, position)
                
                # Convert to dictionary
                todo_item = dict(row)
                
                # Format datetime objects
                todo_item['created_at'] = todo_item['created_at'].isoformat()
                todo_item['updated_at'] = todo_item['updated_at'].isoformat()
                
                # Add ticket information
                todo_item['ticket_number'] = ticket_number
                
                return todo_item
            finally:
                await self.pool.release(conn)
        except Exception as e:
            print(f"Error adding todo item: {str(e)}")
            raise
    
    async def update_todo_item(self,
                            todo_id: int,
                            description: Optional[str] = None,
                            done: Optional[bool] = None,
                            position: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Update a todo item
        
        Args:
            todo_id: ID of the todo item
            description: New description (optional)
            done: New completion status (optional)
            position: New position (optional)
        
        Returns:
            Updated todo item details or None if not found
        """
        if not description and done is None and position is None:
            raise ValueError("At least one of description, done, or position must be provided")
        
        try:
            conn = await self.get_connection()
            try:
                # Build update query based on what's provided
                query_parts = []
                params = [todo_id]
                
                if description:
                    query_parts.append(f"description = ${len(params) + 1}")
                    params.append(description)
                
                if done is not None:
                    query_parts.append(f"done = ${len(params) + 1}")
                    params.append(done)
                
                if position is not None:
                    query_parts.append(f"position = ${len(params) + 1}")
                    params.append(position)
                
                # Always update the updated_at timestamp
                query_parts.append("updated_at = CURRENT_TIMESTAMP")
                
                # Build the full query
                query = f'''
                    UPDATE todo_items
                    SET {", ".join(query_parts)}
                    WHERE id = $1
                    RETURNING id, ticket_id, description, done, created_at, updated_at, position
                '''
                
                # Update the todo item
                row = await conn.fetchrow(query, *params)
                
                if not row:
                    return None
                
                # Convert to dictionary
                todo_item = dict(row)
                
                # Format datetime objects
                todo_item['created_at'] = todo_item['created_at'].isoformat()
                todo_item['updated_at'] = todo_item['updated_at'].isoformat()
                
                # Get ticket number
                ticket_number = await conn.fetchval('''
                    SELECT ticket_number FROM tickets
                    WHERE id = $1
                ''', todo_item['ticket_id'])
                
                todo_item['ticket_number'] = ticket_number
                
                return todo_item
            finally:
                await self.pool.release(conn)
        except Exception as e:
            print(f"Error updating todo item: {str(e)}")
            raise
    
    async def delete_todo_item(self, todo_id: int) -> bool:
        """
        Delete a todo item
        
        Args:
            todo_id: ID of the todo item to delete
        
        Returns:
            True if deleted, False if not found
        """
        try:
            conn = await self.get_connection()
            try:
                # Delete the todo item
                result = await conn.execute('''
                    DELETE FROM todo_items
                    WHERE id = $1
                ''', todo_id)
                
                # Parse the result to get number of deleted rows
                deleted = int(result.split(" ")[-1])
                
                return deleted > 0
            finally:
                await self.pool.release(conn)
        except Exception as e:
            print(f"Error deleting todo item: {str(e)}")
            raise
    
    async def get_todo_items(self, ticket_number: str) -> List[Dict[str, Any]]:
        """
        Get all todo items for a ticket
        
        Args:
            ticket_number: The ticket number
        
        Returns:
            List of todo items
        """
        try:
            conn = await self.get_connection()
            try:
                # Get the ticket ID
                ticket_id = await conn.fetchval('''
                    SELECT id FROM tickets
                    WHERE ticket_number = $1 AND status = 'active'
                ''', ticket_number)
                
                if not ticket_id:
                    raise ValueError(f"Ticket {ticket_number} not found or inactive")
                
                # Get todo items
                rows = await conn.fetch('''
                    SELECT id, description, done, created_at, updated_at, position
                    FROM todo_items
                    WHERE ticket_id = $1
                    ORDER BY position ASC
                ''', ticket_id)
                
                todo_items = []
                for row in rows:
                    todo_item = dict(row)
                    todo_item['created_at'] = todo_item['created_at'].isoformat()
                    todo_item['updated_at'] = todo_item['updated_at'].isoformat()
                    todo_item['ticket_number'] = ticket_number
                    todo_items.append(todo_item)
                
                return todo_items
            finally:
                await self.pool.release(conn)
        except Exception as e:
            print(f"Error getting todo items: {str(e)}")
            raise 