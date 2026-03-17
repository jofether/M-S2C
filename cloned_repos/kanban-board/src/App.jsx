import React, { useState } from 'react';
import TaskCard from './components/TaskCard';
import Column from './components/Column';

function App() {
  const [tasks, setTasks] = useState({
    backlog: [
      { id: '1', title: 'Research market trends', priority: 'high', assignee: 'Sarah', dueDate: '2026-02-25' },
      { id: '2', title: 'Competitor analysis', priority: 'medium', assignee: 'Mike', dueDate: '2026-03-05' },
      { id: '3', title: 'User interview sessions', priority: 'high', assignee: 'Emma', dueDate: '2026-03-10' },
      { id: '4', title: 'Create wireframes', priority: 'medium', assignee: 'John', dueDate: '2026-03-15' },
    ],
    todo: [
      { id: '5', title: 'Setup development environment', priority: 'high', assignee: 'Alex', dueDate: '2026-02-18' },
      { id: '6', title: 'Design system documentation', priority: 'medium', assignee: 'Lisa', dueDate: '2026-02-20' },
      { id: '7', title: 'Database schema design', priority: 'high', assignee: 'David', dueDate: '2026-02-22' },
    ],
    inProgress: [
      { id: '8', title: 'Frontend architecture setup', priority: 'high', assignee: 'Emma', dueDate: '2026-02-19' },
      { id: '9', title: 'API endpoint development', priority: 'high', assignee: 'Mike', dueDate: '2026-02-21' },
      { id: '10', title: 'Authentication system', priority: 'high', assignee: 'Alex', dueDate: '2026-02-23' },
    ],
    review: [
      { id: '11', title: 'Code review: Auth module', priority: 'medium', assignee: 'Sarah', dueDate: '2026-02-17' },
      { id: '12', title: 'Security audit', priority: 'high', assignee: 'John', dueDate: '2026-02-19' },
      { id: '13', title: 'Performance optimization', priority: 'medium', assignee: 'David', dueDate: '2026-02-20' },
    ],
    done: [
      { id: '14', title: 'Project kickoff meeting', priority: 'medium', assignee: 'Sarah', dueDate: '2026-02-16' },
      { id: '15', title: 'Repository setup', priority: 'medium', assignee: 'Lisa', dueDate: '2026-02-16' },
      { id: '16', title: 'Team onboarding', priority: 'low', assignee: 'Emma', dueDate: '2026-02-16' },
    ],
  });

  const [draggedTask, setDraggedTask] = useState(null);
  const [newTaskInput, setNewTaskInput] = useState({});

  const columns = [
    { id: 'backlog', title: 'Backlog', color: 'from-slate-400 to-slate-500', icon: '📋' },
    { id: 'todo', title: 'To Do', color: 'from-blue-400 to-blue-500', icon: '✓' },
    { id: 'inProgress', title: 'In Progress', color: 'from-indigo-400 to-indigo-500', icon: '🔄' },
    { id: 'review', title: 'Review', color: 'from-amber-400 to-amber-500', icon: '👀' },
    { id: 'done', title: 'Done', color: 'from-emerald-400 to-emerald-500', icon: '✅' },
  ];

  const handleDragStart = (e, task, sourceColumn) => {
    setDraggedTask({ task, sourceColumn });
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e, targetColumn) => {
    e.preventDefault();
    if (!draggedTask) return;

    const { task, sourceColumn } = draggedTask;

    if (sourceColumn !== targetColumn) {
      setTasks((prev) => ({
        ...prev,
        [sourceColumn]: prev[sourceColumn].filter((t) => t.id !== task.id),
        [targetColumn]: [...prev[targetColumn], task],
      }));
    }
    setDraggedTask(null);
  };

  const handleAddTask = (columnId) => {
    const title = newTaskInput[columnId]?.trim();
    if (!title) return;

    const newTask = {
      id: Date.now().toString(),
      title,
      priority: 'medium',
      assignee: 'Unassigned',
      dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    };

    setTasks((prev) => ({
      ...prev,
      [columnId]: [...prev[columnId], newTask],
    }));

    setNewTaskInput((prev) => ({
      ...prev,
      [columnId]: '',
    }));
  };

  const handleDeleteTask = (columnId, taskId) => {
    setTasks((prev) => ({
      ...prev,
      [columnId]: prev[columnId].filter((t) => t.id !== taskId),
    }));
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 font-sans overflow-hidden">
      {/* Header */}
      <header className="px-8 py-6 bg-gradient-to-r from-slate-800 to-slate-700 border-b border-slate-600 flex-shrink-0 shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">📊 Project Board</h1>
            <p className="text-slate-400 text-sm mt-1">Manage your tasks and workflow efficiently</p>
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <span className="px-3 py-1 rounded-full bg-slate-700 text-xs font-medium">Active Sprint</span>
            <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-medium">On Track</span>
          </div>
        </div>
      </header>

      {/* Main Board */}
      <main className="flex-1 overflow-x-auto overflow-y-hidden p-12">
        <div className="flex h-full gap-1 min-w-max">
          {columns.map((column) => (
            <Column
              key={column.id}
              column={column}
              tasks={tasks[column.id]}
              onDragStart={handleDragStart}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onAddTask={handleAddTask}
              onDeleteTask={handleDeleteTask}
              newTaskInput={newTaskInput}
              setNewTaskInput={setNewTaskInput}
            />
          ))}
          
          {/* Spacer to ensure last column has margin */}
          <div className="w-2 flex-shrink-0"></div>
        </div>
      </main>
    </div>
  );
}

export default App;