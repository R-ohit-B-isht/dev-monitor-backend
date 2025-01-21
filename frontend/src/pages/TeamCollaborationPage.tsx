import * as React from 'react';
import { useState, useEffect } from 'react';
import { ActivityFeed } from '../components/ActivityFeed';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { GitPullRequest, GitMerge, MessageSquare, Users } from 'lucide-react';
import { Breadcrumb } from '../components/Breadcrumb';
import { api, Activity, CollaborationStats } from '../services/api';

export function TeamCollaborationPage() {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [stats, setStats] = useState<CollaborationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [repository, setRepository] = useState('R-ohit-B-isht/dev-monitor-frontend');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [activitiesData, statsData] = await Promise.all([
          api.getActivityFeed({ repository }),
          api.getCollaborationStats({ repository })
        ]);
        setActivities(activitiesData.activities);
        setStats(statsData);
      } catch (err) {
        console.error('Failed to fetch collaboration data:', err);
        setError('Failed to load collaboration data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [repository]);

  return (
    <div className="p-6">
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/' },
          { label: 'Team Collaboration' }
        ]}
      />

      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Team Collaboration</h1>
        <div className="flex items-center gap-4">
          <input
            type="text"
            placeholder="Enter repository (owner/repo)"
            value={repository}
            onChange={(e) => setRepository(e.target.value)}
            className="px-3 py-2 border rounded-md text-sm"
          />
          <Button
            onClick={() => setLoading(true)}
            disabled={loading}
          >
            Refresh
          </Button>
        </div>
      </div>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">
                Reviews
              </CardTitle>
              <GitPullRequest className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_reviews}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">
                Comments
              </CardTitle>
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_comments}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">
                Code Changes
              </CardTitle>
              <GitMerge className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                +{stats.total_additions || 0}, -{stats.total_deletions || 0}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">
                Reviewers
              </CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.reviewer_count}</div>
            </CardContent>
          </Card>
        </div>
      )}

      <ActivityFeed
        activities={activities}
        loading={loading}
        error={error}
      />
    </div>
  );
}
