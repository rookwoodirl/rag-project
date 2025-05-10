import axios from 'axios';

// Initialize Axios client
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types from backend models
export interface Todo {
  id: number;
  description: string;
  done: boolean;
  position: number;
  created_at: string;
  updated_at: string;
  ticket_number: string;
}

export interface Ticket {
  id: number;
  ticket_number: string;
  ticket_category: string;
  description: string;
  completion_criteria?: string;
  status: string;
  created_at: string;
  updated_at: string;
  todo_items: Todo[];
}

// API Functions for Tickets
export const ticketApi = {
  // Get all tickets
  getTickets: async (params?: { 
    category?: string;
    active_only?: boolean;
    include_todos?: boolean;
    limit?: number;
    offset?: number;
  }) => {
    const response = await apiClient.get('/tickets', { params });
    return response.data;
  },

  // Get a single ticket by ticket number
  getTicket: async (ticketNumber: string, params?: {
    category?: string;
    include_history?: boolean;
  }) => {
    const response = await apiClient.get(`/tickets/${ticketNumber}`, { params });
    return response.data;
  },

  // Create a new ticket
  createTicket: async (ticket: {
    ticket_category: string;
    ticket_number?: string;
    description: string;
    completion_criteria?: string;
  }) => {
    const response = await apiClient.post('/tickets', ticket);
    return response.data;
  },

  // Update a ticket
  updateTicket: async (ticketNumber: string, ticket: {
    ticket_category?: string;
    description?: string;
    completion_criteria?: string;
  }) => {
    const response = await apiClient.put(`/tickets/${ticketNumber}`, ticket);
    return response.data;
  },

  // Delete a ticket
  deleteTicket: async (ticketNumber: string, params?: {
    category?: string;
    hard_delete?: boolean;
  }) => {
    await apiClient.delete(`/tickets/${ticketNumber}`, { params });
  },
};

// API Functions for Todo Items
export const todoApi = {
  // Get todos for a ticket
  getTodos: async (ticketNumber: string) => {
    const response = await apiClient.get(`/tickets/${ticketNumber}/todos`);
    return response.data;
  },

  // Create a todo item
  createTodo: async (ticketNumber: string, todo: {
    description: string;
    position?: number;
  }) => {
    const response = await apiClient.post(`/tickets/${ticketNumber}/todos`, todo);
    return response.data;
  },

  // Update a todo item
  updateTodo: async (todoId: number, todo: {
    description?: string;
    done?: boolean;
    position?: number;
  }) => {
    const response = await apiClient.put(`/todos/${todoId}`, todo);
    return response.data;
  },

  // Delete a todo item
  deleteTodo: async (todoId: number) => {
    await apiClient.delete(`/todos/${todoId}`);
  },
};

export default apiClient; 
