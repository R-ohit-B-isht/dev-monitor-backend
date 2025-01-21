import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Task } from '../types/Task';
import { api } from '../services/api';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/views/Skeleton';
import { Breadcrumb } from '../components/Breadcrumb';
import { ArrowLeft, ArrowRight, Clock, Github, Trello, LineChart, XCircle } from 'lucide-react';
import { Relationships } from '../components/views/Relationships';
import { cn } from '../lib/utils';
import { statusStyles } from '../components/TaskCard';

const integrationIcons = {
  github: <Github className="h-4 w-4" />,
  jira: <Trello className="h-4 w-4" />,
  linear: <LineChart className="h-4 w-4" />
};

export function TaskDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [allTasks, setAllTasks] = useState<Task[]>([]);

  // Fetch all tasks for relationships
  useEffect(() => {
    const fetchAllTasks = async () => {
      try {
        const tasks = await api.getTasks();
        setAllTasks(tasks);
      } catch (error) {
        console.error('Error loading all tasks:', error);
      }
    };

    fetchAllTasks();
  }, []);


  useEffect(() => {
    const fetchTask = async () => {
      try {
        const response = await api.getTask(id!);
        setTask(response);
      } catch (error: unknown) {
        console.error('Error loading task details:', error);
        setError('Failed to load task details');
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
  }, [id]);

  if (loading) return (
    <div className="p-6 max-w-4xl mx-auto">
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/' },
          { label: 'Loading...' }
        ]}
      />
      <div className="flex items-center gap-4 mb-6">
        <Skeleton className="h-10 w-24" /> {/* Back button */}
      </div>
      <Card>
        <CardHeader className="space-y-2">
          <Skeleton className="h-8 w-3/4" /> {/* Title */}
          <div className="flex gap-2">
            <Skeleton className="h-6 w-20" /> {/* Status badge */}
            <Skeleton className="h-6 w-24" /> {/* Priority badge */}
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6">
            <div className="space-y-2">
              <Skeleton className="h-5 w-24" /> {/* Description label */}
              <Skeleton className="h-20 w-full" /> {/* Description content */}
            </div>
            <div className="space-y-2">
              <Skeleton className="h-5 w-20" /> {/* Timeline label */}
              <div className="space-y-2">
                <Skeleton className="h-6 w-48" />
                <Skeleton className="h-6 w-48" />
              </div>
            </div>
          </div>

          {/* Task Relationships */}
          <div className="mt-6">
            <Skeleton className="h-[400px] rounded-lg" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
  if (error || !task) {
    const message = error || 'Task not found';
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <Breadcrumb
          items={[
            { label: 'Dashboard', href: '/' },
            { label: 'Error' }
          ]}
        />
        <div className="flex items-center gap-4 mb-6">
          <Button
            variant="outline"
            onClick={() => navigate('/')}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
        </div>
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center justify-center text-center p-6">
              <div className="rounded-full bg-red-100 p-3 mb-4">
                <XCircle className="h-6 w-6 text-red-600" />
              </div>
              <h3 className="text-lg font-semibold text-red-900 mb-2">Error Loading Task</h3>
              <p className="text-red-600">{message}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-4 md:p-6 max-w-4xl mx-auto">
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/' },
          { label: task.title }
        ]}
      />
      <div className="flex items-center gap-4 mb-6">
        <Button
          variant="outline"
          onClick={() => navigate(-1)}
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        <div className="h-4 w-px bg-border" />

      </div>
      <Card className="transition-all duration-200 hover:shadow-lg">
        <CardHeader className="space-y-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-xl font-bold">{task.title}</CardTitle>
            {integrationIcons[task.integration]}
          </div>
          <div className="flex flex-wrap gap-2">
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
              <Badge variant="outline">Priority: {task.priority}</Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6">
            <div className="space-y-2">
              <h3 className="font-medium">Description</h3>
              <p className="text-sm text-gray-500">{task.description || 'No description provided'}</p>
            </div>

            <div className="space-y-2">
              <h3 className="font-medium">Timeline</h3>
              <div className="grid gap-2 text-sm text-gray-500">
                <div className="flex items-center">
                  <Clock className="h-4 w-4 mr-2" />
                  <span>Created: {new Date(task.createdAt).toLocaleString()}</span>
                </div>
                <div className="flex items-center">
                  <Clock className="h-4 w-4 mr-2" />
                  <span>Updated: {new Date(task.updatedAt).toLocaleString()}</span>
                </div>
              </div>
            </div>
            <div className="grid sm:grid-cols-2 gap-4">
              {task.devinSessionUrl && (
                <div className="space-y-2">
                  <h3 className="font-medium">Devin Session</h3>
                  <a
                    href={task.devinSessionUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-blue-500 hover:text-blue-600 transition-colors"
                  >
                    View Session
                    <ArrowRight className="ml-1 h-4 w-4" />
                  </a>
                </div>
              )}

              {task.sourceUrl && (
                <div className="space-y-2">
                  <h3 className="font-medium">Source</h3>
                  <a
                    href={task.sourceUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-blue-500 hover:text-blue-600 transition-colors"
                  >
                    View Original Issue
                    <ArrowRight className="ml-1 h-4 w-4" />
                  </a>
                </div>
              )}
            </div>
            {/* Optional links section removed until Task interface is updated */}
            <div className="grid sm:grid-cols-2 gap-4"></div>
          </div>

          {/* Task Relationships */}
          {task && (
            <div className="mt-6">
              <Relationships
                task={task}
                allTasks={allTasks}
              />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );


}
