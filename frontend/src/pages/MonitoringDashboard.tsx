import * as React from "react";
import { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Button } from '../components/ui/button';
import { Clock, Award, Activity, Brain, FileDown } from 'lucide-react';
import { Breadcrumb } from '../components/Breadcrumb';
import { api, MonitoringMetrics, Achievement } from '../services/api';
import { MeetingTimeCard } from '../components/MeetingTimeCard';
import { ReportPanel } from '../components/ReportPanel';

export function MonitoringDashboard() {
  const [metrics, setMetrics] = useState<MonitoringMetrics | null>(null);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string>('');

  const fetchData = async () => {
    try {
      const [metricsData, achievementsData] = await Promise.all([
        api.getMonitoringMetrics(),
        api.getAchievements()
      ]);
      setMetrics(metricsData);
      setAchievements(achievementsData.achievements);
    } catch (err) {
      setError('Failed to load monitoring data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  if (loading) {
    return <div>Loading monitoring data...</div>;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  return (
    <div className="p-4 sm:p-6">
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/' },
          { label: 'Monitoring' }
        ]}
      />

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4 sm:mb-6">
        <h1 className="text-xl sm:text-2xl font-bold">Devin's Activity Monitor</h1>
        <ReportPanel engineerId="current" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-6 sm:mb-8">
        {/* Meeting Time */}
        <MeetingTimeCard
          engineerId="current"
          sessionId={currentSessionId}
          onDiscardIdleTime={async () => {
            if (!currentSessionId) return;
            try {
              await api.discardIdleTime(currentSessionId);
              // Refresh metrics
              fetchData();
            } catch (error) {
              console.error('Failed to discard idle time:', error);
              setError('Failed to discard idle time');
            }
          }}
        />

        {/* Productivity Score */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between p-3 sm:p-4 pb-2">
            <CardTitle className="text-sm font-medium">
              Productivity Score
            </CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent className="p-3 sm:p-4 pt-2">
            <div className="space-y-2">
              <Progress
                value={metrics?.productivityScore || 0}
                className="h-2.5"
              />
              <p className="text-xl sm:text-2xl font-bold">
                {Math.round(metrics?.productivityScore || 0)}%
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Focus Time */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between p-3 sm:p-4 pb-2">
            <CardTitle className="text-sm font-medium">
              Focus Time
            </CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent className="p-3 sm:p-4 pt-2">
            <div className="space-y-2">
              <Progress
                value={metrics?.focusTimePercentage || 0}
                className="h-2.5"
              />
              <p className="text-xl sm:text-2xl font-bold">
                {formatDuration(metrics?.focusTimeSeconds || 0)}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Activity Count */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between p-3 sm:p-4 pb-2">
            <CardTitle className="text-sm font-medium">
              Activities
            </CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent className="p-3 sm:p-4 pt-2">
            <div className="space-y-2">
              <Progress
                value={(metrics?.focusActivityRatio || 0) * 100}
                className="h-2.5"
              />
              <p className="text-xl sm:text-2xl font-bold">
                {metrics?.focusActivities || 0}/{metrics?.totalActivities || 0}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Achievements */}
      <Card className="mb-6 sm:mb-8">
        <CardHeader className="p-4 sm:p-6">
          <CardTitle className="text-lg sm:text-xl">Recent Achievements</CardTitle>
          <CardDescription>
            Badges and milestones earned during work sessions
          </CardDescription>
        </CardHeader>
        <CardContent className="p-4 sm:p-6 pt-0">
          <div className="space-y-4">
            {achievements.slice(0, 5).map((achievement, index) => (
              <div
                key={index}
                className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 border rounded-lg"
              >
                <div className="flex items-center gap-4">
                  <Award className="h-5 w-5 text-yellow-500 flex-shrink-0" />
                  <div>
                    <p className="font-medium">{achievement.badge}</p>
                    <p className="text-sm text-gray-500">
                      {new Date(achievement.earnedAt).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <Badge variant="secondary" className="whitespace-nowrap">
                  Score: {Math.round(achievement.metadata.productivityScore)}%
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
