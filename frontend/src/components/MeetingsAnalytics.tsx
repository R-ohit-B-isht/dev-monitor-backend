import * as React from 'react';
import { useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from './ui/card';
import { Progress } from './ui/progress';
import { Calendar, Clock, RefreshCw } from 'lucide-react';

interface Meeting {
  id: string;
  title: string;
  start: string;
  end: string;
  duration: number;
  isRecurring: boolean;
  recurrencePattern?: string;
}

interface MeetingMetrics {
  totalMeetingTime: number;
  meetingCount: number;
  idleTime: number;
  overlapTime: number;
  meetings: Meeting[];
  recurringMeetings: {
    count: number;
    patterns: Record<string, number>;
  };
}

interface MeetingsAnalyticsProps {
  metrics: MeetingMetrics;
  className?: string;
}

export function MeetingsAnalytics({ metrics, className = '' }: MeetingsAnalyticsProps) {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());

  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const dailyLimit = 4 * 3600; // 4 hours daily meeting limit
  const meetingPercentage = (metrics.totalMeetingTime / dailyLimit) * 100;
  const overlapPercentage = (metrics.overlapTime / metrics.totalMeetingTime) * 100;

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Meeting Timeline */}
      <Card>
        <CardHeader>
          <CardTitle>Meeting Timeline</CardTitle>
          <CardDescription>Your meeting schedule for the day</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="relative h-24 bg-secondary/20 rounded-lg">
            {metrics.meetings.map((meeting) => {
              const startTime = new Date(meeting.start);
              const endTime = new Date(meeting.end);
              const startPercentage = ((startTime.getHours() * 60 + startTime.getMinutes()) / (24 * 60)) * 100;
              const duration = (endTime.getTime() - startTime.getTime()) / (24 * 60 * 60 * 1000) * 100;
              
              return (
                <div
                  key={meeting.id}
                  className="absolute h-6 rounded bg-primary/60 cursor-pointer hover:bg-primary/80 transition-colors"
                  style={{
                    left: `${startPercentage}%`,
                    width: `${duration}%`,
                    top: '50%',
                    transform: 'translateY(-50%)'
                  }}
                  title={`${meeting.title}\n${startTime.toLocaleTimeString()} - ${endTime.toLocaleTimeString()}`}
                />
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Meeting Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Meeting Load
            </CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Progress
                value={Math.min(meetingPercentage, 100)}
                className="h-2"
              />
              <p className="text-sm text-muted-foreground">
                {formatDuration(metrics.totalMeetingTime)} of {formatDuration(dailyLimit)}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Meeting Overlap
            </CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Progress
                value={Math.min(overlapPercentage, 100)}
                className="h-2"
              />
              <p className="text-sm text-muted-foreground">
                {formatDuration(metrics.overlapTime)} overlap time
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Recurring Meetings
            </CardTitle>
            <RefreshCw className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-2xl font-bold">
                {metrics.recurringMeetings.count}
              </p>
              <div className="text-sm text-muted-foreground">
                {Object.entries(metrics.recurringMeetings.patterns).map(([pattern, count]) => (
                  <div key={pattern} className="flex justify-between">
                    <span>{pattern}</span>
                    <span>{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
