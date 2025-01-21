import * as React from 'react';
import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from './ui/dialog';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Task } from '../types/Task';
import { api } from '../services/api';
import { Github, Trello, LineChart, Clock, Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';
import { statusStyles } from './TaskCard';

const integrationIcons = {
  github: <Github className="h-4 w-4" />,
  jira: <Trello className="h-4 w-4" />,
  linear: <LineChart className="h-4 w-4" />
};

interface TaskDetailDialogProps {
  taskId: string | null;
  isOpen: boolean;
  onClose: () => void;
}

export function TaskDetailDialog({ taskId, isOpen, onClose }: TaskDetailDialogProps) {
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!taskId || !isOpen) return;
    
    const fetchTask = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.getTask(taskId);
        setTask(data);
      } catch (err) {
        setError('Failed to load task details');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
  }, [taskId, isOpen]);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-gray-500" />
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <p className="text-red-500">{error}</p>
          </div>
        ) : task ? (
          <>
            <DialogHeader>
              <div className="flex items-center justify-between">
                <DialogTitle>{task.title}</DialogTitle>
                <div className="flex items-center space-x-2">
                  {integrationIcons[task.integration]}
                </div>
              </div>
              {task.description && (
                <DialogDescription className="mt-2">
                  {task.description}
                </DialogDescription>
              )}
            </DialogHeader>

            <div className="space-y-4 py-4">
              {/* Status and Priority */}
              <div className="flex items-center gap-2">
                <Badge 
                  variant="secondary"
                  className={cn(
                    "transition-colors",
                    statusStyles[task.status]
                  )}
                >
                  {task.status}
                </Badge>
                {task.priority && (
                  <Badge variant="outline">
                    Priority: {task.priority}
                  </Badge>
                )}
              </div>

              {/* Timestamps */}
              <div className="space-y-2 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  <span>Created: {new Date(task.createdAt).toLocaleString()}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  <span>Updated: {new Date(task.updatedAt).toLocaleString()}</span>
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={onClose}>
                Close
              </Button>
            </DialogFooter>
          </>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
