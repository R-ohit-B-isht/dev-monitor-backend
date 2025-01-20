import * as React from 'react';
import { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { api, ValueStreamMetrics, ValueStreamTask } from '../services/api';
import { Breadcrumb } from '../components/Breadcrumb';
import { Clock, GitMerge, Code, GitPullRequest } from 'lucide-react';

export function ValueStreamAnalysisPage() {
  const [metrics, setMetrics] = useState<ValueStreamMetrics | null>(null);
  const [tasks, setTasks] = useState<ValueStreamTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await api.getValueStreamMetrics('current');
        setMetrics(data.metrics);
        setTasks(data.tasks);
      } catch (err) {
        console.error('Failed to fetch value stream metrics:', err);
        setError('Failed to load value stream metrics');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const formatDuration = (milliseconds: number): string => {
    const hours = Math.floor(milliseconds / (1000 * 60 * 60));
    const minutes = Math.floor((milliseconds % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  };

  if (loading) {
    return <div>Loading value stream metrics...</div>;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  const maxDuration = Math.max(
    metrics?.avgIdeaToCode || 0,
    metrics?.avgCodeToReview || 0,
    metrics?.avgReviewToMerge || 0,
    metrics?.avgMergeToDeploy || 0
  );

  return (
    <div className="p-4 sm:p-6">
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/' },
          { label: 'Value Stream Analysis' }
        ]}
      />

      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl sm:text-2xl font-bold">Value Stream Analysis</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-6 sm:mb-8">
        {/* Idea to Code */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Idea to Code
            </CardTitle>
            <Code className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Progress
                value={(metrics?.avgIdeaToCode || 0) / maxDuration * 100}
                className="h-2"
              />
              <p className="text-2xl font-bold">
                {formatDuration(metrics?.avgIdeaToCode || 0)}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Code to Review */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Code to Review
            </CardTitle>
            <GitPullRequest className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Progress
                value={(metrics?.avgCodeToReview || 0) / maxDuration * 100}
                className="h-2"
              />
              <p className="text-2xl font-bold">
                {formatDuration(metrics?.avgCodeToReview || 0)}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Review to Merge */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Review to Merge
            </CardTitle>
            <GitMerge className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Progress
                value={(metrics?.avgReviewToMerge || 0) / maxDuration * 100}
                className="h-2"
              />
              <p className="text-2xl font-bold">
                {formatDuration(metrics?.avgReviewToMerge || 0)}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Merge to Deploy */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Merge to Deploy
            </CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Progress
                value={(metrics?.avgMergeToDeploy || 0) / maxDuration * 100}
                className="h-2"
              />
              <p className="text-2xl font-bold">
                {formatDuration(metrics?.avgMergeToDeploy || 0)}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Tasks */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Tasks</CardTitle>
          <CardDescription>
            Value stream metrics for recently completed tasks
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {tasks.slice(0, 5).map((task) => (
              <div
                key={task._id}
                className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 border rounded-lg gap-4"
              >
                <div>
                  <p className="font-medium">{task.title}</p>
                  <p className="text-sm text-gray-500">
                    Status: {task.status}
                  </p>
                </div>
                <div className="flex flex-wrap gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Idea to Code</p>
                    <p className="font-medium">{formatDuration(task.ideaToCode)}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Code to Review</p>
                    <p className="font-medium">{formatDuration(task.codeToReview)}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Review to Merge</p>
                    <p className="font-medium">{formatDuration(task.reviewToMerge)}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Merge to Deploy</p>
                    <p className="font-medium">{formatDuration(task.mergeToDeploy)}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
