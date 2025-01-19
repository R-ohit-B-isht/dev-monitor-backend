import * as React from 'react';
import { Task } from '../../types/Task';
import { TaskCard } from '../TaskCard';

interface ListViewProps {
  tasks: Task[];
  onTaskClick: (task: Task) => void;
}

export function ListView({ tasks, onTaskClick }: ListViewProps) {
  return (
    <div className="space-y-4 max-w-3xl mx-auto">
      {tasks.map((task) => (
        <TaskCard
          key={task._id}
          task={task}
          onClick={() => onTaskClick(task)}
        />
      ))}
      {tasks.length === 0 && (
        <div className="text-center text-gray-500 py-8">
          No tasks found
        </div>
      )}
    </div>
  );
}
