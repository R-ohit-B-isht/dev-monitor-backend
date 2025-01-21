import * as React from 'react';
import { TaskCard } from './TaskCard';
import { Task } from '../types/Task';

interface TaskColumnProps {
  title: string;
  tasks: Task[];
  onTaskClick: (task: Task) => void;
}

export function TaskColumn({ title, tasks, onTaskClick }: TaskColumnProps) {
  return (
    <div className="flex-1 flex-col min-w-[280px] sm:min-w-[300px] bg-card/50 backdrop-blur-sm rounded-lg p-4 border border-border shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">{title}</h2>
        <span className="text-sm text-muted-foreground bg-card/50 px-2 py-0.5 rounded-full">
          {tasks.length}
        </span>
      </div>
      <div className="space-y-3 min-h-[200px]">
        {tasks.map((task) => (
          <TaskCard
            key={task._id}
            task={task}
            onClick={() => onTaskClick(task)}
          />
        ))}
        {tasks.length === 0 && (
          <div className="flex items-center justify-center h-32 border-2 border-dashed border-border rounded-lg bg-card/50">
            <p className="text-sm text-muted-foreground">No tasks yet</p>
          </div>
        )}
      </div>
    </div>
  );
}
