import * as React from 'react';
import { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from './ui/card';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Video, Clock } from 'lucide-react';
import { api, MeetingTimeMetrics } from '../services/api';

interface MeetingTimeCardProps {
  engineerId: string;
  sessionId: string;
  onDiscardIdleTime: () => void;
}

export function MeetingTimeCard({ engineerId, sessionId, onDiscardIdleTime }: MeetingTimeCardProps) {
  const [metrics, setMetrics] = useState<MeetingTimeMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMeetingTime = async () => {
      try {
        const data = await api.getMeetingTime(engineerId);
        setMetrics(data);
      } catch (error) {
        console.error('Failed to fetch meeting time:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMeetingTime();
  }, [engineerId]);

  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  if (loading) {
    return <div>Loading meeting metrics...</div>;
  }

  const dailyLimit = 4 * 3600; // 4 hours daily meeting limit
  const meetingPercentage = ((metrics?.totalMeetingTime || 0) / dailyLimit) * 100;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium">
          Meeting Time
        </CardTitle>
        <Video className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="space-y-2">
            <Progress
              value={Math.min(meetingPercentage, 100)}
              className="h-2"
            />
            <div className="flex items-center justify-between text-sm">
              <p className="text-muted-foreground">
                {metrics?.meetingCount || 0} meetings today
              </p>
              <p className="font-medium">
                {formatDuration(metrics?.totalMeetingTime || 0)}
              </p>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center text-sm text-muted-foreground">
              <Clock className="mr-1 h-4 w-4" />
              {meetingPercentage > 75 ? (
                <span className="text-red-500 font-medium">High meeting load</span>
              ) : (
                <span>Daily target: 4h max</span>
              )}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={onDiscardIdleTime}
            >
              Discard Idle Time
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
