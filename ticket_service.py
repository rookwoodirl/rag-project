from db import PostgresHandler
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class TicketService:
    """Service for managing tickets with proper versioning"""
    
    def __init__(self):
        self.db = PostgresHandler()
    
    async def initialize_db(self):
        """Initialize the database with the SQL schema if needed"""
        try:
            with open('sql/create_tables.sql', 'r') as f:
                sql = f.read()
                
            # Execute the SQL as a transaction
            await self.db.run_query(sql, fetch_type="status")
            return True
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            return False
    
    async def create_ticket(self, ticket_category: str, ticket_number: str, description: str) -> Optional[Dict[str, Any]]:
        """Create a new ticket"""
        try:
            # Check if ticket with same number and category already exists (active)
            existing = await self.db.run_query(
                """
                SELECT id FROM tickets 
                WHERE ticket_number = $1 
                AND ticket_category = $2
                AND is_active = TRUE
                """, 
                [ticket_number, ticket_category],
                fetch_type="one"
            )
            
            if existing:
                raise ValueError(f"Active ticket with number {ticket_number} in category {ticket_category} already exists")
            
            # Insert new ticket
            ticket = await self.db.run_query(
                """
                INSERT INTO tickets (
                    ticket_category, 
                    ticket_number, 
                    description, 
                    version,
                    valid_from
                ) VALUES ($1, $2, $3, 1, CURRENT_TIMESTAMP)
                RETURNING *
                """,
                [ticket_category, ticket_number, description],
                fetch_type="one"
            )
            
            return ticket
            
        except Exception as e:
            print(f"Error creating ticket: {str(e)}")
            raise
    
    async def get_ticket(self, ticket_number: str, ticket_category: str = None, include_history: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get a ticket by number and optionally category
        If include_history is True, returns all versions of the ticket
        """
        try:
            if include_history:
                # Get all versions of the ticket
                query = """
                SELECT * FROM tickets 
                WHERE ticket_number = $1
                """
                params = [ticket_number]
                
                if ticket_category:
                    query += " AND ticket_category = $2"
                    params.append(ticket_category)
                
                query += " ORDER BY version DESC"
                
                tickets = await self.db.run_query(query, params)
                return tickets
            else:
                # Get only the active version
                query = """
                SELECT * FROM tickets 
                WHERE ticket_number = $1
                AND is_active = TRUE
                """
                params = [ticket_number]
                
                if ticket_category:
                    query += " AND ticket_category = $2"
                    params.append(ticket_category)
                
                ticket = await self.db.run_query(query, params, fetch_type="one")
                return ticket
                
        except Exception as e:
            print(f"Error getting ticket: {str(e)}")
            raise
    
    async def list_tickets(self, 
                         category: Optional[str] = None,
                         active_only: bool = True,
                         limit: int = 100, 
                         offset: int = 0) -> Dict[str, Any]:
        """List tickets with optional filtering"""
        try:
            # Base query
            query = """
            SELECT * FROM tickets 
            WHERE 1=1
            """
            count_query = """
            SELECT COUNT(*) FROM tickets
            WHERE 1=1
            """
            
            params = []
            
            # Add filters
            if active_only:
                query += " AND is_active = TRUE"
                count_query += " AND is_active = TRUE"
            
            if category:
                params.append(category)
                param_idx = len(params)
                query += f" AND ticket_category = ${param_idx}"
                count_query += f" AND ticket_category = ${param_idx}"
            
            # Add pagination
            query += " ORDER BY updated_at DESC LIMIT $" + str(len(params) + 1) + " OFFSET $" + str(len(params) + 2)
            params.extend([limit, offset])
            
            # Execute queries
            tickets = await self.db.run_query(query, params)
            total = await self.db.run_query(count_query, params[:-2], fetch_type="val")
            
            return {
                "tickets": tickets,
                "total": total
            }
            
        except Exception as e:
            print(f"Error listing tickets: {str(e)}")
            raise
    
    async def update_ticket(self, 
                         ticket_number: str, 
                         ticket_category: Optional[str] = None,
                         description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update a ticket with versioning"""
        try:
            # Start a transaction
            async with self.db.connection.transaction():
                # Get current active ticket
                query = """
                SELECT * FROM tickets 
                WHERE ticket_number = $1
                AND is_active = TRUE
                """
                params = [ticket_number]
                
                if ticket_category:
                    query += " AND ticket_category = $2"
                    params.append(ticket_category)
                
                current_ticket = await self.db.run_query(query, params, fetch_type="one")
                
                if not current_ticket:
                    raise ValueError(f"No active ticket found with number {ticket_number}")
                
                # Determine what needs to be updated
                new_category = ticket_category if ticket_category else current_ticket["ticket_category"]
                new_description = description if description else current_ticket["description"]
                
                # Check if any changes are being made
                if (new_category == current_ticket["ticket_category"] and 
                    new_description == current_ticket["description"]):
                    return current_ticket  # No changes needed
                
                # 1. Set valid_to and is_active=False on the current version
                await self.db.run_query(
                    """
                    UPDATE tickets 
                    SET valid_to = CURRENT_TIMESTAMP, is_active = FALSE
                    WHERE id = $1
                    """,
                    [current_ticket["id"]],
                    fetch_type="status"
                )
                
                # 2. Insert new version
                new_ticket = await self.db.run_query(
                    """
                    INSERT INTO tickets (
                        ticket_category, 
                        ticket_number, 
                        description, 
                        version,
                        valid_from
                    ) VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP)
                    RETURNING *
                    """,
                    [
                        new_category,
                        ticket_number,
                        new_description, 
                        current_ticket["version"] + 1
                    ],
                    fetch_type="one"
                )
                
                return new_ticket
                
        except Exception as e:
            print(f"Error updating ticket: {str(e)}")
            raise
    
    async def delete_ticket(self, ticket_number: str, ticket_category: Optional[str] = None) -> bool:
        """Soft-delete a ticket by marking it as inactive and setting valid_to"""
        try:
            # Find the active ticket
            query = """
            SELECT * FROM tickets 
            WHERE ticket_number = $1
            AND is_active = TRUE
            """
            params = [ticket_number]
            
            if ticket_category:
                query += " AND ticket_category = $2"
                params.append(ticket_category)
            
            ticket = await self.db.run_query(query, params, fetch_type="one")
            
            if not ticket:
                raise ValueError(f"No active ticket found with number {ticket_number}")
            
            # Soft delete
            result = await self.db.run_query(
                """
                UPDATE tickets 
                SET is_active = FALSE, valid_to = CURRENT_TIMESTAMP
                WHERE id = $1
                RETURNING id
                """,
                [ticket["id"]],
                fetch_type="one"
            )
            
            return result is not None
            
        except Exception as e:
            print(f"Error deleting ticket: {str(e)}")
            raise
    
    async def hard_delete_ticket(self, ticket_number: str, ticket_category: Optional[str] = None) -> int:
        """Hard-delete a ticket (all versions) - USE WITH CAUTION"""
        try:
            query = """
            DELETE FROM tickets 
            WHERE ticket_number = $1
            """
            params = [ticket_number]
            
            if ticket_category:
                query += " AND ticket_category = $2"
                params.append(ticket_category)
            
            rows_affected = await self.db.run_query(query, params, fetch_type="status")
            return rows_affected
            
        except Exception as e:
            print(f"Error hard deleting ticket: {str(e)}")
            raise
    
    async def close(self):
        """Close the database connection"""
        await self.db.close() 