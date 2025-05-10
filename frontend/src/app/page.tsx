"use client";

import React from "react";
import { ChevronDown, ChevronRight, MessageSquare, CheckCircle, AlertCircle, Clock, Calendar, XCircle, CheckSquare, Square, PlusCircle } from 'lucide-react';

interface Todo {
  id: number | string;
  text: string;
  completed: boolean;
}

interface SuggestedTodo {
  id: string;
  text: string;
  completed: boolean;
}

interface Message {
  id: number | string;
  sender: string;
  content: string;
  suggestedTodos?: SuggestedTodo[];
}

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

const CoachRAG = () => {
  const [tickets, setTickets] = React.useState<Ticket[]>([
    {
      id: 'LIFE-123',
      title: 'Plan Summer Vacation',
      description: 'Research and organize a 2-week family vacation to Europe in July',
      status: 'in-progress',
      priority: 'high',
      assignee: 'Me',
      dueDate: '2025-06-01',
      tags: ['travel', 'family'],
      todos: [
        { id: 1, text: 'Research flight options', completed: true },
        { id: 2, text: 'Book accommodations', completed: true },
        { id: 3, text: 'Create daily itinerary', completed: false },
        { id: 4, text: 'Purchase travel insurance', completed: false }
      ],
      messages: [
        { id: 1, sender: 'AI', content: 'I recommend focusing on 2-3 cities maximum for a more relaxed experience.' },
        { id: 2, sender: 'Me', content: 'Good point, we were trying to fit in too many destinations.' },
        { id: 3, sender: 'AI', content: 'Consider adding these items to your checklist:', suggestedTodos: [
          { id: 'st1', text: 'Check passport expiration dates', completed: false },
          { id: 'st2', text: 'Research local transportation options', completed: false }
        ]}
      ]
    },
    {
      id: 'LIFE-124',
      title: 'Home Renovation Project',
      description: 'Plan and execute kitchen remodel including new cabinets, countertops, and appliances',
      status: 'backlog',
      priority: 'medium',
      assignee: 'Me',
      dueDate: '2025-08-15',
      tags: ['home', 'renovation'],
      todos: [
        { id: 1, text: 'Get quotes from contractors', completed: false },
        { id: 2, text: 'Create budget spreadsheet', completed: false },
        { id: 3, text: 'Select appliance models', completed: false }
      ],
      messages: []
    },
    {
      id: 'LIFE-125',
      title: 'Train for Half Marathon',
      description: 'Prepare for the city half marathon in September with a structured training plan',
      status: 'todo',
      priority: 'low',
      assignee: 'Me',
      dueDate: '2025-09-20',
      tags: ['fitness', 'health'],
      todos: [
        { id: 1, text: 'Research training programs', completed: false },
        { id: 2, text: 'Buy new running shoes', completed: false }
      ],
      messages: []
    }
  ]);

  const [selectedTicket, setSelectedTicket] = React.useState<Ticket>(tickets[0]);
  const [expandedTicket, setExpandedTicket] = React.useState<string | null>(tickets[0].id);
  const [newTodo, setNewTodo] = React.useState('');
  const [newMessage, setNewMessage] = React.useState('');

  const toggleTicketExpand = (ticketId: string) => {
    if (expandedTicket === ticketId) {
      setExpandedTicket(null);
    } else {
      setExpandedTicket(ticketId);
      const ticket = tickets.find(t => t.id === ticketId);
      if (ticket) setSelectedTicket(ticket);
    }
  };

  const toggleTodo = (ticketId: string, todoId: number | string) => {
    setTickets(tickets.map(ticket => {
      if (ticket.id === ticketId) {
        return {
          ...ticket,
          todos: ticket.todos.map(todo => 
            todo.id === todoId ? { ...todo, completed: !todo.completed } : todo
          )
        };
      }
      return ticket;
    }));
    
    // Also update selected ticket if it's the one being modified
    if (selectedTicket.id === ticketId) {
      setSelectedTicket({
        ...selectedTicket,
        todos: selectedTicket.todos.map(todo => 
          todo.id === todoId ? { ...todo, completed: !todo.completed } : todo
        )
      });
    }
  };

  const addTodo = (ticketId: string) => {
    if (!newTodo.trim()) return;
    
    const updatedTickets = tickets.map(ticket => {
      if (ticket.id === ticketId) {
        return {
          ...ticket,
          todos: [
            ...ticket.todos,
            { id: Date.now(), text: newTodo, completed: false }
          ]
        };
      }
      return ticket;
    });
    
    setTickets(updatedTickets);
    
    // Update selected ticket if it's the one being modified
    if (selectedTicket.id === ticketId) {
      setSelectedTicket({
        ...selectedTicket,
        todos: [
          ...selectedTicket.todos,
          { id: Date.now(), text: newTodo, completed: false }
        ]
      });
    }
    
    setNewTodo('');
  };

  const addMessage = (ticketId: string) => {
    if (!newMessage.trim()) return;
    
    const updatedTickets = tickets.map(ticket => {
      if (ticket.id === ticketId) {
        return {
          ...ticket,
          messages: [
            ...ticket.messages,
            { id: Date.now(), sender: 'Me', content: newMessage }
          ]
        };
      }
      return ticket;
    });
    
    setTickets(updatedTickets);
    
    // Update selected ticket if it's the one being modified
    if (selectedTicket.id === ticketId) {
      setSelectedTicket({
        ...selectedTicket,
        messages: [
          ...selectedTicket.messages,
          { id: Date.now(), sender: 'Me', content: newMessage }
        ]
      });
    }
    
    setNewMessage('');
    
    // Simulate AI response after a brief delay
    setTimeout(() => {
      const aiResponse = { 
        id: Date.now() + 1, 
        sender: 'AI', 
        content: `I've noted your message about "${newMessage}". How can I help with this task?` 
      };
      
      const updatedTicketsWithAI = tickets.map(ticket => {
        if (ticket.id === ticketId) {
          return {
            ...ticket,
            messages: [...ticket.messages, { id: Date.now(), sender: 'Me', content: newMessage }, aiResponse]
          };
        }
        return ticket;
      });
      
      setTickets(updatedTicketsWithAI);
      
      if (selectedTicket.id === ticketId) {
        setSelectedTicket({
          ...selectedTicket,
          messages: [...selectedTicket.messages, { id: Date.now(), sender: 'Me', content: newMessage }, aiResponse]
        });
      }
    }, 1000);
  };

  const acceptSuggestedTodo = (ticketId: string, suggestedTodo: SuggestedTodo) => {
    const updatedTickets = tickets.map(ticket => {
      if (ticket.id === ticketId) {
        return {
          ...ticket,
          todos: [
            ...ticket.todos,
            { ...suggestedTodo, id: Date.now() }
          ]
        };
      }
      return ticket;
    });
    
    setTickets(updatedTickets);
    
    if (selectedTicket.id === ticketId) {
      setSelectedTicket({
        ...selectedTicket,
        todos: [
          ...selectedTicket.todos,
          { ...suggestedTodo, id: Date.now() }
        ]
      });
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
      case 'todo': return 'bg-gray-100 text-gray-800';
      case 'done': return 'bg-green-100 text-green-800';
      case 'backlog': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const completedTodos = selectedTicket.todos.filter(todo => todo.completed).length;
  const totalTodos = selectedTicket.todos.length;
  const progress = totalTodos ? Math.round((completedTodos / totalTodos) * 100) : 0;

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 text-white p-4 flex flex-col">
        <div className="text-xl font-bold mb-8">LifeCoach</div>
        
        <div className="flex items-center space-x-2 p-2 bg-gray-800 rounded mb-4">
          <div className="w-2 h-2 rounded-full bg-green-400"></div>
          <span>My Life Goals</span>
        </div>
        
        <nav className="flex-1">
          <ul>
            <li className="mb-1">
              <a href="#" className="flex items-center p-2 rounded hover:bg-gray-800 bg-gray-700">
                <MessageSquare size={16} className="mr-2" />
                <span>Projects</span>
              </a>
            </li>
            <li className="mb-1">
              <a href="#" className="flex items-center p-2 rounded hover:bg-gray-800">
                <CheckCircle size={16} className="mr-2" />
                <span>My Tasks</span>
              </a>
            </li>
          </ul>
        </nav>
        
        <div className="mt-auto">
          <div className="flex items-center p-2">
            <div className="w-8 h-8 rounded-full bg-blue-500 mr-2 flex items-center justify-center">
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
            <h1 className="text-xl font-semibold">My Life Projects</h1>
            <div className="flex space-x-2">
              <button className="px-3 py-1 bg-gray-100 rounded-md text-sm">Filter</button>
              <button className="px-3 py-1 bg-indigo-600 text-white rounded-md text-sm">New Project</button>
            </div>
          </div>
        </header>

        {/* Ticket List and Detail View */}
        <div className="flex-1 flex overflow-hidden">
          {/* Ticket List */}
          <div className="w-1/2 overflow-y-auto p-4 border-r border-gray-200">
            {tickets.map(ticket => (
              <div key={ticket.id} className="mb-4 bg-white rounded-lg shadow">
                <div 
                  className="p-4 cursor-pointer flex items-center"
                  onClick={() => toggleTicketExpand(ticket.id)}
                >
                  {expandedTicket === ticket.id ? 
                    <ChevronDown size={18} className="mr-2 text-gray-500" /> : 
                    <ChevronRight size={18} className="mr-2 text-gray-500" />
                  }
                  <div className="flex-1">
                    <div className="flex items-center">
                      <span className="text-xs text-gray-500 font-mono mr-2">{ticket.id}</span>
                      <h3 className="font-medium">{ticket.title}</h3>
                    </div>
                    <div className="flex items-center mt-1 text-sm text-gray-600">
                      <span className={`px-2 py-0.5 rounded-full text-xs ${getStatusColor(ticket.status)}`}>
                        {ticket.status}
                      </span>
                      <div className="ml-2 flex items-center">
                        {getPriorityIcon(ticket.priority)}
                        <span className="ml-1 text-xs">{ticket.priority}</span>
                      </div>
                      <div className="ml-auto flex items-center">
                        <span className="text-xs">{`${ticket.todos.filter(t => t.completed).length}/${ticket.todos.length}`}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                {expandedTicket === ticket.id && (
                  <div className="px-4 pb-4">
                    <div className="mb-3 text-sm text-gray-600">
                      {ticket.description}
                    </div>
                    
                    <div className="mb-3">
                      <h4 className="text-sm font-medium mb-2">To-Do List</h4>
                      <ul className="space-y-1">
                        {ticket.todos.map(todo => (
                          <li key={todo.id} className="flex items-center">
                            <button 
                              className="mr-2 text-gray-400 hover:text-indigo-600"
                              onClick={() => toggleTodo(ticket.id, todo.id)}
                            >
                              {todo.completed ? <CheckSquare size={16} /> : <Square size={16} />}
                            </button>
                            <span className={`text-sm ${todo.completed ? 'line-through text-gray-400' : ''}`}>
                              {todo.text}
                            </span>
                          </li>
                        ))}
                      </ul>
                      <div className="flex mt-2">
                        <input
                          type="text"
                          placeholder="Add new todo"
                          className="flex-1 text-sm border border-gray-300 rounded-l-md p-1 focus:outline-none focus:ring focus:border-indigo-300"
                          value={newTodo}
                          onChange={(e) => setNewTodo(e.target.value)}
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') addTodo(ticket.id);
                          }}
                        />
                        <button 
                          className="bg-indigo-600 text-white px-2 rounded-r-md"
                          onClick={() => addTodo(ticket.id)}
                        >
                          +
                        </button>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-medium mb-2">Messages</h4>
                      <div className="space-y-2 max-h-60 overflow-y-auto mb-2">
                        {ticket.messages.map(message => (
                          <div key={message.id} className={`p-2 rounded-lg ${message.sender === 'AI' ? 'bg-indigo-50' : 'bg-gray-100'}`}>
                            <div className="flex items-center mb-1">
                              <span className={`text-xs font-medium ${message.sender === 'AI' ? 'text-indigo-600' : 'text-gray-700'}`}>
                                {message.sender}
                              </span>
                            </div>
                            <div className="text-sm">{message.content}</div>
                            {message.suggestedTodos && (
                              <div className="mt-2 border-t border-gray-200 pt-2">
                                <div className="text-xs font-medium mb-1">Suggested tasks:</div>
                                {message.suggestedTodos.map(todo => (
                                  <div key={todo.id} className="flex items-center justify-between bg-white p-1 rounded mb-1">
                                    <span className="text-sm">{todo.text}</span>
                                    <div className="flex space-x-1">
                                      <button 
                                        className="p-1 text-green-600 hover:bg-green-50 rounded"
                                        onClick={() => acceptSuggestedTodo(ticket.id, todo)}
                                      >
                                        <CheckCircle size={14} />
                                      </button>
                                      <button className="p-1 text-red-600 hover:bg-red-50 rounded">
                                        <XCircle size={14} />
                                      </button>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                      <div className="flex">
                        <input
                          type="text"
                          placeholder="Write a message..."
                          className="flex-1 text-sm border border-gray-300 rounded-l-md p-2 focus:outline-none focus:ring focus:border-indigo-300"
                          value={newMessage}
                          onChange={(e) => setNewMessage(e.target.value)}
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') addMessage(ticket.id);
                          }}
                        />
                        <button 
                          className="bg-indigo-600 text-white px-3 rounded-r-md"
                          onClick={() => addMessage(ticket.id)}
                        >
                          Send
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Detail View */}
          <div className="w-1/2 overflow-y-auto p-4 bg-white">
            <div className="flex items-center mb-4">
              <div className="flex-1">
                <div className="flex items-center">
                  <span className="text-xs text-gray-500 font-mono mr-2">{selectedTicket.id}</span>
                  <h2 className="text-xl font-semibold">{selectedTicket.title}</h2>
                </div>
                <div className="flex items-center mt-1">
                  <span className={`px-2 py-0.5 rounded-full text-xs ${getStatusColor(selectedTicket.status)}`}>
                    {selectedTicket.status}
                  </span>
                </div>
              </div>
              <button className="px-3 py-1 bg-indigo-600 text-white rounded-md">
                Edit
              </button>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg mb-4">
              <h3 className="text-sm font-medium mb-2">Description</h3>
              <p className="text-sm text-gray-700">{selectedTicket.description}</p>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-medium mb-2">Details</h3>
                <ul className="space-y-2">
                  <li className="flex items-center text-sm">
                    <span className="w-20 text-gray-500">Priority:</span>
                    <div className="flex items-center">
                      {getPriorityIcon(selectedTicket.priority)}
                      <span className="ml-1 capitalize">{selectedTicket.priority}</span>
                    </div>
                  </li>
                  <li className="flex items-center text-sm">
                    <span className="w-20 text-gray-500">Assignee:</span>
                    <div className="flex items-center">
                      <div className="w-6 h-6 rounded-full bg-blue-500 mr-1 flex items-center justify-center">
                        <span className="font-medium text-white text-xs">ME</span>
                      </div>
                      <span>{selectedTicket.assignee}</span>
                    </div>
                  </li>
                  <li className="flex items-center text-sm">
                    <span className="w-20 text-gray-500">Due:</span>
                    <div className="flex items-center">
                      <Calendar size={14} className="mr-1 text-gray-400" />
                      <span>{selectedTicket.dueDate}</span>
                    </div>
                  </li>
                  <li className="flex items-center text-sm">
                    <span className="w-20 text-gray-500">Tags:</span>
                    <div className="flex flex-wrap gap-1">
                      {selectedTicket.tags.map((tag, index) => (
                        <span key={index} className="px-2 py-0.5 bg-gray-200 rounded-full text-xs">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </li>
                </ul>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-medium mb-2">Progress</h3>
                <div className="mb-2">
                  <div className="flex justify-between text-xs mb-1">
                    <span>{completedTodos} of {totalTodos} tasks completed</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-indigo-600 h-2 rounded-full" 
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                </div>
                
                <h4 className="text-xs font-medium mt-4 mb-1">Activity</h4>
                <div className="text-xs text-gray-500">
                  <div className="flex items-center">
                    <div className="w-4 h-4 rounded-full bg-blue-500 mr-1 flex items-center justify-center">
                      <span className="font-medium text-white text-xs">M</span>
                    </div>
                    <span>You updated this ticket 3 hours ago</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg mb-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium">To-Do List</h3>
                <span className="text-xs text-gray-500">{completedTodos}/{totalTodos}</span>
              </div>
              
              <ul className="space-y-1 mb-3">
                {selectedTicket.todos.map(todo => (
                  <li key={todo.id} className="flex items-center bg-white p-2 rounded shadow-sm">
                    <button 
                      className="mr-2 text-gray-400 hover:text-indigo-600"
                      onClick={() => toggleTodo(selectedTicket.id, todo.id)}
                    >
                      {todo.completed ? <CheckSquare size={16} /> : <Square size={16} />}
                    </button>
                    <span className={`text-sm ${todo.completed ? 'line-through text-gray-400' : ''}`}>
                      {todo.text}
                    </span>
                  </li>
                ))}
              </ul>
              
              <div className="flex">
                <input
                  type="text"
                  placeholder="Add new todo"
                  className="flex-1 text-sm border border-gray-300 rounded-l-md p-2 focus:outline-none focus:ring focus:border-indigo-300"
                  value={newTodo}
                  onChange={(e) => setNewTodo(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') addTodo(selectedTicket.id);
                  }}
                />
                <button 
                  className="bg-indigo-600 text-white px-3 rounded-r-md"
                  onClick={() => addTodo(selectedTicket.id)}
                >
                  Add
                </button>
              </div>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium mb-2">Messages</h3>
              <div className="space-y-3 max-h-60 overflow-y-auto mb-3">
                {selectedTicket.messages.map(message => (
                  <div key={message.id} className={`p-3 rounded-lg ${message.sender === 'AI' ? 'bg-indigo-50' : 'bg-gray-100'}`}>
                    <div className="flex items-center mb-1">
                      <div className={`w-6 h-6 rounded-full mr-2 flex items-center justify-center ${message.sender === 'AI' ? 'bg-indigo-500' : 'bg-blue-500'}`}>
                        <span className="font-medium text-white text-xs">
                          {message.sender === 'AI' ? 'AI' : 'ME'}
                        </span>
                      </div>
                      <span className="text-sm font-medium">{message.sender}</span>
                      <span className="text-xs text-gray-500 ml-2">Today</span>
                    </div>
                    <div className="text-sm pl-8">{message.content}</div>
                    
                    {message.suggestedTodos && (
                      <div className="mt-3 border-t border-gray-200 pt-2 pl-8">
                        <div className="text-xs font-medium mb-2">Suggested tasks:</div>
                        <div className="space-y-2">
                          {message.suggestedTodos.map(todo => (
                            <div key={todo.id} className="flex items-center justify-between bg-white p-2 rounded shadow-sm">
                              <div className="flex items-center">
                                <PlusCircle size={14} className="mr-2 text-gray-400" />
                                <span className="text-sm">{todo.text}</span>
                              </div>
                              <div className="flex space-x-2">
                                <button 
                                  className="p-1 text-green-600 hover:bg-green-50 rounded"
                                  onClick={() => acceptSuggestedTodo(selectedTicket.id, todo)}
                                >
                                  <CheckCircle size={16} />
                                </button>
                                <button className="p-1 text-red-600 hover:bg-red-50 rounded">
                                  <XCircle size={16} />
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
                  className="flex-1 text-sm border border-gray-300 rounded-l-md p-2 focus:outline-none focus:ring focus:border-indigo-300"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') addMessage(selectedTicket.id);
                  }}
                />
                <button 
                  className="bg-indigo-600 text-white px-3 rounded-r-md"
                  onClick={() => addMessage(selectedTicket.id)}
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default function Home() {
  return <CoachRAG />;
}
