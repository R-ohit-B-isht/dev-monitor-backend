import * as React from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from './ui/card';
import { Badge } from './ui/badge';
import { GitPullRequest, GitMerge, MessageSquare, GitCommit } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { Activity } from '../services/api';

interface ActivityFeedProps {
  activities: Activity[];
  loading?: boolean;
  error?: string | null;
}

type EventType = 'review' | 'merge' | 'comment' | 'commit';

const eventIcons: Record<EventType, JSX.Element> = {
  'review': <GitPullRequest className="h-4 w-4" />,
  'merge': <GitMerge className="h-4 w-4" />,
  'comment': <MessageSquare className="h-4 w-4" />,
  'commit': <GitCommit className="h-4 w-4" />
};

const eventColors: Record<EventType, string> = {
  'review': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
  'merge': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
  'comment': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
  'commit': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300'
};

export function ActivityFeed({ activities, loading, error }: ActivityFeedProps) {
  if (loading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="h-[300px] flex items-center justify-center">
            <p className="text-sm text-muted-foreground">Loading activity feed...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="h-[300px] flex items-center justify-center">
            <p className="text-sm text-destructive">{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Activity Feed</CardTitle>
        <CardDescription>Recent collaboration events and updates</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity) => (
            <div
              key={activity._id}
              className="flex items-start gap-4 p-4 border rounded-lg"
            >
              <div className="mt-1">
                {eventIcons[activity.eventType as EventType] || <GitCommit className="h-4 w-4" />}
              </div>
              <div className="flex-1 space-y-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-medium">
                      {activity.title || `${activity.eventType} on ${activity.repository}`}
                    </h4>
                    <Badge
                      variant="secondary"
                      className={eventColors[activity.eventType as EventType]}
                    >
                      {activity.eventType}
                    </Badge>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                  </span>
                </div>
                {activity.description && (
                  <p className="text-sm text-muted-foreground">
                    {activity.description}
                  </p>
                )}
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  {activity.commentCount !== undefined && (
                    <span className="flex items-center gap-1">
                      <MessageSquare className="h-3 w-3" />
                      {activity.commentCount} comments
                    </span>
                  )}
                  {(activity.additions !== undefined || activity.deletions !== undefined) && (
                    <span>
                      {activity.additions !== undefined && `+${activity.additions}`}
                      {activity.additions !== undefined && activity.deletions !== undefined && ', '}
                      {activity.deletions !== undefined && `-${activity.deletions}`}
                    </span>
                  )}
                  {activity.reviewers && activity.reviewers.length > 0 && (
                    <span>
                      Reviewers: {activity.reviewers.join(', ')}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
