"use client";

import React, { useEffect, useState } from "react";
import { MessageSquare, CheckCircle, AlertCircle, Clock, Calendar, XCircle, CheckSquare, Square, PlusCircle } from 'lucide-react';
import { ticketApi, todoApi, Ticket as BackendTicket } from '../utils/api';

// Frontend interface for Todo
interface Todo {
  id: number | string;
  text: string;
  completed: boolean;
}

// Frontend interface for Suggested Todo
interface SuggestedTodo {
  id: string;
  text: string;
  completed: boolean;
}

// Frontend interface for Message
interface Message {
  id: number | string;
  sender: string;
  content: string;
  suggestedTodos?: SuggestedTodo[];
}

// Frontend interface for Ticket
interface Ticket {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  assignee: string;
  dueDate: string;
  tags: string[];
  todos: Todo[];
  messages: Message[];
}

// Convert backend ticket to frontend format
const mapBackendTicketToFrontend = (ticket: BackendTicket): Ticket => {
  return {
    id: ticket.ticket_number,
    title: ticket.ticket_category,
    description: ticket.description,
    status: ticket.status.toLowerCase(),
    priority: getPriorityFromDescription(ticket.description),
    assignee: 'Me',
    dueDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 2 weeks from now
    tags: ['life', getTagFromCategory(ticket.ticket_category)],
    todos: ticket.todo_items.map(todo => ({
      id: todo.id,
      text: todo.description,
      completed: todo.done
    })),
    messages: []
  };
};

// Helper functions to extract meaningful data
const getPriorityFromDescription = (description: string): string => {
  const lowerDesc = description.toLowerCase();
  if (lowerDesc.includes('urgent') || lowerDesc.includes('asap') || lowerDesc.includes('immediate')) {
    return 'high';
  } else if (lowerDesc.includes('soon') || lowerDesc.includes('next week')) {
    return 'medium';
  }
  return 'low';
};

const getTagFromCategory = (category: string): string => {
  const lowerCat = category.toLowerCase();
  if (lowerCat.includes('vacation') || lowerCat.includes('travel')) return 'travel';
  if (lowerCat.includes('home') || lowerCat.includes('house')) return 'home';
  if (lowerCat.includes('fitness') || lowerCat.includes('exercise')) return 'fitness';
  if (lowerCat.includes('work') || lowerCat.includes('job')) return 'work';
  return 'personal';
};

const CoachRAG = () => {
  // State for tickets from the backend
  const [backendTickets, setBackendTickets] = useState<BackendTicket[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Transform backend tickets to frontend format
  const tickets: Ticket[] = backendTickets.map(mapBackendTicketToFrontend);

  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [expandedTicket, setExpandedTicket] = useState<string | null>(null);
  const [newTodo, setNewTodo] = useState('');
  const [newMessage, setNewMessage] = useState('');

  // Fetch tickets from the backend
  useEffect(() => {
    const fetchTickets = async () => {
      try {
        setIsLoading(true);
        const response = await ticketApi.getTickets({ include_todos: true });
        setBackendTickets(response.tickets);
        
        // Set initial selected ticket if we have tickets
        if (response.tickets.length > 0) {
          const frontendTicket = mapBackendTicketToFrontend(response.tickets[0]);
          setSelectedTicket(frontendTicket);
          setExpandedTicket(frontendTicket.id);
        }
        
      } catch (err) {
        console.error('Failed to fetch tickets:', err);
        setError('Failed to load tickets. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTickets();
  }, []);

  // Handle ticket selection
  const toggleTicketExpand = (ticketId: string) => {
    if (expandedTicket === ticketId) {
      setExpandedTicket(null);
    } else {
      setExpandedTicket(ticketId);
      const ticket = tickets.find(t => t.id === ticketId);
      if (ticket) setSelectedTicket(ticket);
    }
  };

  // Handle todo completion toggle
  const toggleTodo = async (ticketId: string, todoId: number | string) => {
    try {
      // Find the todo
      const ticket = tickets.find(t => t.id === ticketId);
      if (!ticket) return;
      
      const todo = ticket.todos.find(t => t.id === todoId);
      if (!todo) return;
      
      // If it's a backend todo (has numeric ID)
      if (typeof todoId === 'number') {
        // Update in backend
        await todoApi.updateTodo(todoId, {
          done: !todo.completed
        });
        
        // Update in state
        setBackendTickets(prevTickets => 
          prevTickets.map(bTicket => {
            if (bTicket.ticket_number === ticketId) {
              return {
                ...bTicket,
                todo_items: bTicket.todo_items.map(bTodo => 
                  bTodo.id === todoId 
                    ? { ...bTodo, done: !bTodo.done } 
                    : bTodo
                )
              };
            }
            return bTicket;
          })
        );
      } else {
        // For frontend-only todos (not yet implemented)
        // This would be handled in local state
      }
    } catch (err) {
      console.error('Failed to toggle todo:', err);
      setError('Failed to update todo. Please try again.');
    }
  };

  // Add a new todo
  const addTodo = async (ticketId: string) => {
    if (!newTodo.trim()) return;
    
    try {
      // Create in backend
      const createdTodo = await todoApi.createTodo(ticketId, {
        description: newTodo
      });
      
      // Update state
      setBackendTickets(prevTickets => 
        prevTickets.map(ticket => {
          if (ticket.ticket_number === ticketId) {
            return {
              ...ticket,
              todo_items: [...ticket.todo_items, createdTodo]
            };
          }
          return ticket;
        })
      );
      
      setNewTodo('');
    } catch (err) {
      console.error('Failed to add todo:', err);
      setError('Failed to add todo. Please try again.');
    }
  };

  // Add message functionality
  const addMessage = (ticketId: string) => {
    if (!newMessage.trim()) return;
    
    // Since the backend doesn't have a messages endpoint,
    // this would be handled client-side only for now
    if (selectedTicket && selectedTicket.id === ticketId) {
      const newMsg = { 
        id: Date.now(), 
        sender: 'Me', 
        content: newMessage 
      };
      
      selectedTicket.messages = [...selectedTicket.messages, newMsg];
      setSelectedTicket({...selectedTicket});
      
      // Simulate AI response
      setTimeout(() => {
        if (selectedTicket) {
          const aiResponse = { 
            id: Date.now() + 1, 
            sender: 'AI', 
            content: `I've noted your message about "${newMessage}". How can I help with this task?` 
          };
          
          selectedTicket.messages = [...selectedTicket.messages, aiResponse];
          setSelectedTicket({...selectedTicket});
        }
      }, 1000);
      
      setNewMessage('');
    }
  };

  // Accept a suggested todo
  const acceptSuggestedTodo = async (ticketId: string, suggestedTodo: SuggestedTodo) => {
    try {
      // Create in backend
      const createdTodo = await todoApi.createTodo(ticketId, {
        description: suggestedTodo.text
      });
      
      // Update state
      setBackendTickets(prevTickets => 
        prevTickets.map(ticket => {
          if (ticket.ticket_number === ticketId) {
            return {
              ...ticket,
              todo_items: [...ticket.todo_items, createdTodo]
            };
          }
          return ticket;
        })
      );
    } catch (err) {
      console.error('Failed to add suggested todo:', err);
      setError('Failed to add suggested todo. Please try again.');
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch(priority) {
      case 'high': return <AlertCircle className="text-red-500" size={16} />;
      case 'medium': return <Clock className="text-yellow-500" size={16} />;
      case 'low': return <AlertCircle className="text-blue-500" size={16} />;
      default: return <AlertCircle className="text-gray-500" size={16} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'in-progress': return 'bg-blue-100 text-blue-800';
      case 'todo': return 'bg-gray-200 text-gray-800';
      case 'done': return 'bg-green-100 text-green-800';
      case 'backlog': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-200 text-gray-800';
    }
  };

  // Content to display when loading
  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-700">Loading your life projects...</p>
        </div>
      </div>
    );
  }

  // Content to display when there's an error
  if (error) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="text-center max-w-md px-4">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Something went wrong</h2>
          <p className="text-gray-700 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md font-medium hover:bg-indigo-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // If no tickets are available
  if (tickets.length === 0) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="text-center max-w-md px-4">
          <div className="text-gray-400 text-5xl mb-4">📋</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No projects found</h2>
          <p className="text-gray-700 mb-4">Create your first life project to get started.</p>
          <button 
            onClick={() => {/* Add create project logic */}}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md font-medium hover:bg-indigo-700"
          >
            Create Project
          </button>
        </div>
      </div>
    );
  }

  // Calculate completed todos for the selected ticket
  const completedTodos = selectedTicket?.todos.filter(todo => todo.completed).length || 0;
  const totalTodos = selectedTicket?.todos.length || 0;
  const progress = totalTodos ? Math.round((completedTodos / totalTodos) * 100) : 0;

  // Main content
  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 text-white p-4 flex flex-col">
        <div className="text-xl font-bold mb-8 text-white">LifeCoach</div>
        
        <div className="flex items-center space-x-2 p-2 bg-gray-800 rounded mb-4">
          <div className="w-2 h-2 rounded-full bg-green-400"></div>
          <span className="text-white">My Life Goals</span>
        </div>
        
        <nav className="flex-1">
          <ul>
            <li className="mb-1">
              <a href="#" className="flex items-center p-2 rounded hover:bg-gray-800 bg-gray-700 text-white">
                <MessageSquare size={16} className="mr-2" />
                <span>Projects</span>
              </a>
            </li>
            <li className="mb-1">
              <a href="#" className="flex items-center p-2 rounded hover:bg-gray-800 text-white">
                <CheckCircle size={16} className="mr-2" />
                <span>My Tasks</span>
              </a>
            </li>
          </ul>
        </nav>
        
        <div className="mt-auto">
          <div className="flex items-center p-2 text-white">
            <div className="w-8 h-8 rounded-full bg-blue-600 mr-2 flex items-center justify-center">
              <span className="font-medium text-white">ME</span>
            </div>
            <span>My Profile</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold text-gray-900">My Life Projects</h1>
            <div className="flex space-x-2">
              <button className="px-3 py-1 bg-gray-100 rounded-md text-sm font-medium text-gray-700">Filter</button>
              <button 
                className="px-3 py-1 bg-indigo-600 text-white rounded-md text-sm font-medium"
                onClick={() => {/* Add create project logic */}}
              >
                New Project
              </button>
            </div>
          </div>
        </header>

        {/* Project List and Detail View */}
        <div className="flex-1 flex overflow-hidden">
          {/* Project List */}
          <div className="w-1/3 overflow-y-auto border-r border-gray-200 bg-gray-50">
            {tickets.map(ticket => (
              <div 
                key={ticket.id} 
                className={`border-b border-gray-200 cursor-pointer ${expandedTicket === ticket.id ? 'bg-white' : 'hover:bg-gray-100'}`}
                onClick={() => toggleTicketExpand(ticket.id)}
              >
                <div className="p-4">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-mono text-gray-500">{ticket.id}</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(ticket.status)}`}>
                      {ticket.status}
                    </span>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-1">{ticket.title}</h3>
                  <p className="text-sm text-gray-700 line-clamp-2 mb-2">{ticket.description}</p>
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center">
                      {getPriorityIcon(ticket.priority)}
                      <span className="ml-1 text-gray-600 capitalize">{ticket.priority}</span>
                    </div>
                    <div className="flex items-center">
                      <span className="text-gray-600">{`${ticket.todos.filter(t => t.completed).length}/${ticket.todos.length}`}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Detail View */}
          {selectedTicket && (
            <div className="w-2/3 overflow-y-auto bg-white p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <div className="flex items-center mb-1">
                    <span className="text-sm text-gray-500 font-mono mr-2">{selectedTicket.id}</span>
                    <h2 className="text-2xl font-bold text-gray-900">{selectedTicket.title}</h2>
                  </div>
                  <div className="flex items-center">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(selectedTicket.status)}`}>
                      {selectedTicket.status}
                    </span>
                  </div>
                </div>
                <button className="px-4 py-2 bg-indigo-600 text-white rounded-md font-medium">
                  Edit
                </button>
              </div>

              <div className="bg-gray-50 p-6 rounded-lg mb-6">
                <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-3">Description</h3>
                <p className="text-base text-gray-700">{selectedTicket.description}</p>
              </div>

              <div className="grid grid-cols-2 gap-6 mb-6">
                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">Details</h3>
                  <ul className="space-y-3">
                    <li className="flex items-center text-sm">
                      <span className="w-24 text-gray-500 font-medium">Priority:</span>
                      <div className="flex items-center">
                        {getPriorityIcon(selectedTicket.priority)}
                        <span className="ml-2 text-gray-900 capitalize font-medium">{selectedTicket.priority}</span>
                      </div>
                    </li>
                    <li className="flex items-center text-sm">
                      <span className="w-24 text-gray-500 font-medium">Assignee:</span>
                      <div className="flex items-center">
                        <div className="w-6 h-6 rounded-full bg-blue-600 mr-2 flex items-center justify-center">
                          <span className="font-medium text-white text-xs">ME</span>
                        </div>
                        <span className="text-gray-900 font-medium">{selectedTicket.assignee}</span>
                      </div>
                    </li>
                    <li className="flex items-center text-sm">
                      <span className="w-24 text-gray-500 font-medium">Due:</span>
                      <div className="flex items-center">
                        <Calendar size={16} className="mr-2 text-gray-500" />
                        <span className="text-gray-900 font-medium">{selectedTicket.dueDate}</span>
                      </div>
                    </li>
                    <li className="flex items-start text-sm">
                      <span className="w-24 text-gray-500 font-medium mt-1">Tags:</span>
                      <div className="flex flex-wrap gap-2">
                        {selectedTicket.tags.map((tag, index) => (
                          <span key={index} className="px-2 py-1 bg-gray-200 rounded-full text-xs font-medium text-gray-700">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </li>
                  </ul>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">Progress</h3>
                  <div className="mb-4">
                    <div className="flex justify-between text-sm mb-2">
                      <span className="font-medium text-gray-900">{completedTodos} of {totalTodos} tasks completed</span>
                      <span className="font-medium text-gray-900">{progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div 
                        className="bg-indigo-600 h-2.5 rounded-full" 
                        style={{ width: `${progress}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <h4 className="text-xs font-semibold text-gray-900 uppercase tracking-wider mt-4 mb-2">Activity</h4>
                  <div className="text-sm text-gray-700">
                    <div className="flex items-center">
                      <div className="w-6 h-6 rounded-full bg-blue-600 mr-2 flex items-center justify-center">
                        <span className="font-medium text-white text-xs">M</span>
                      </div>
                      <span>You updated this project recently</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 p-6 rounded-lg mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider">To-Do List</h3>
                  <span className="text-sm font-medium text-gray-700">{completedTodos}/{totalTodos}</span>
                </div>
                
                <ul className="space-y-2 mb-4">
                  {selectedTicket.todos.map(todo => (
                    <li key={todo.id} className="flex items-center bg-white p-3 rounded-md shadow-sm">
                      <button 
                        className="mr-3 text-gray-400 hover:text-indigo-600"
                        onClick={() => toggleTodo(selectedTicket.id, todo.id)}
                      >
                        {todo.completed ? <CheckSquare size={20} className="text-indigo-600" /> : <Square size={20} />}
                      </button>
                      <span className={`text-base ${todo.completed ? 'line-through text-gray-400' : 'text-gray-900'}`}>
                        {todo.text}
                      </span>
                    </li>
                  ))}
                </ul>
                
                <div className="flex">
                  <input
                    type="text"
                    placeholder="Add new todo"
                    className="flex-1 text-base border border-gray-300 rounded-l-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
                    value={newTodo}
                    onChange={(e) => setNewTodo(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') addTodo(selectedTicket.id);
                    }}
                  />
                  <button 
                    className="bg-indigo-600 text-white px-4 py-2 rounded-r-md font-medium"
                    onClick={() => addTodo(selectedTicket.id)}
                  >
                    Add
                  </button>
                </div>
              </div>

              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">Messages</h3>
                <div className="space-y-4 max-h-80 overflow-y-auto mb-4">
                  {selectedTicket.messages.map(message => (
                    <div key={message.id} className={`p-4 rounded-lg ${message.sender === 'AI' ? 'bg-indigo-50 border border-indigo-100' : 'bg-gray-200'}`}>
                      <div className="flex items-center mb-2">
                        <div className={`w-8 h-8 rounded-full mr-3 flex items-center justify-center ${message.sender === 'AI' ? 'bg-indigo-600' : 'bg-blue-600'}`}>
                          <span className="font-medium text-white text-sm">
                            {message.sender === 'AI' ? 'AI' : 'ME'}
                          </span>
                        </div>
                        <div>
                          <span className="text-sm font-medium text-gray-900">{message.sender}</span>
                          <span className="text-xs text-gray-500 ml-2">Today</span>
                        </div>
                      </div>
                      <div className="text-base text-gray-800 ml-11">{message.content}</div>
                      
                      {message.suggestedTodos && (
                        <div className="mt-3 border-t border-gray-200 pt-3 ml-11">
                          <div className="text-sm font-medium text-gray-900 mb-2">Suggested tasks:</div>
                          <div className="space-y-2">
                            {message.suggestedTodos.map(todo => (
                              <div key={todo.id} className="flex items-center justify-between bg-white p-3 rounded-md border border-gray-200">
                                <div className="flex items-center">
                                  <PlusCircle size={16} className="mr-2 text-gray-500" />
                                  <span className="text-base text-gray-900">{todo.text}</span>
                                </div>
                                <div className="flex space-x-2">
                                  <button 
                                    className="p-1.5 text-green-600 hover:bg-green-50 rounded-full"
                                    onClick={() => acceptSuggestedTodo(selectedTicket.id, todo)}
                                  >
                                    <CheckCircle size={18} />
                                  </button>
                                  <button className="p-1.5 text-red-600 hover:bg-red-50 rounded-full">
                                    <XCircle size={18} />
                                  </button>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                
                <div className="flex">
                  <input
                    type="text"
                    placeholder="Write a message..."
                    className="flex-1 text-base border border-gray-300 rounded-l-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') addMessage(selectedTicket.id);
                    }}
                  />
                  <button 
                    className="bg-indigo-600 text-white px-4 py-2 rounded-r-md font-medium"
                    onClick={() => addMessage(selectedTicket.id)}
                  >
                    Send
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default function Home() {
  return <CoachRAG />;
}
