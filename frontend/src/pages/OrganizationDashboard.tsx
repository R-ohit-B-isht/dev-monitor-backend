import * as React from 'react';
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { DateRangeFilter } from '../components/DateRangeFilter';
import { ActivityFeed } from '../components/ActivityFeed';
import { Breadcrumb } from '../components/Breadcrumb';
import { api } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { GitBranch, GitPullRequest, Shield, Users } from 'lucide-react';

interface RepositoryMetrics {
  repository: string;
  activity: {
    commits: number;
    pull_requests: number;
    reviews: number;
    comments: number;
  };
  performance: {
    avg_review_time: number;
    merge_success_rate: number;
    deployment_frequency: number;
  };
  security: {
    open_alerts: number;
    fixed_alerts: number;
    high_severity: number;
  };
  collaboration: {
    unique_contributors: number;
    review_coverage: number;
    comment_ratio: number;
  };
}

interface OrganizationMetrics {
  metrics: RepositoryMetrics[];
  totals: {
    total_repositories: number;
    total_activity: number;
    total_contributors: number;
    total_security_alerts: number;
    avg_deployment_frequency: number;
    timeframe: {
      start: string;
      end: string;
      days: number;
    };
  };
}

export function OrganizationDashboard() {
  const [metrics, setMetrics] = useState<OrganizationMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startDate, setStartDate] = useState(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000));
  const [endDate, setEndDate] = useState(new Date());

  useEffect(() => {
    fetchMetrics();
  }, [startDate, endDate]);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const days = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));
      const data = await api.getOrganizationMetrics(days);
      setMetrics(data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch organization metrics:', err);
      setError('Failed to load organization metrics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading organization metrics...</div>;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  if (!metrics) {
    return null;
  }

  const activityData = metrics.metrics.map(repo => ({
    name: repo.repository.split('/')[1],
    commits: repo.activity.commits,
    'pull requests': repo.activity.pull_requests,
    reviews: repo.activity.reviews,
    comments: repo.activity.comments
  }));

  return (
    <div className="p-6">
      <Breadcrumb
        items={[
          { label: 'Dashboard', href: '/' },
          { label: 'Organization Overview' }
        ]}
      />

      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Organization Overview</h1>
        <DateRangeFilter
          startDate={startDate}
          endDate={endDate}
          onStartDateChange={setStartDate}
          onEndDateChange={setEndDate}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Repositories
            </CardTitle>
            <GitBranch className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.totals.total_repositories}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Total Activity
            </CardTitle>
            <GitPullRequest className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.totals.total_activity}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Contributors
            </CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.totals.total_contributors}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">
              Security Alerts
            </CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.totals.total_security_alerts}</div>
          </CardContent>
        </Card>
      </div>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Repository Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={activityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="commits" fill="#8884d8" />
                <Bar dataKey="pull requests" fill="#82ca9d" />
                <Bar dataKey="reviews" fill="#ffc658" />
                <Bar dataKey="comments" fill="#ff7300" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {metrics.metrics.map((repo) => (
          <Card key={repo.repository}>
            <CardHeader>
              <CardTitle>{repo.repository}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium mb-2">Performance</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-muted-foreground">Merge Success Rate</div>
                      <div className="text-lg font-medium">
                        {repo.performance.merge_success_rate.toFixed(1)}%
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Deployment Frequency</div>
                      <div className="text-lg font-medium">
                        {repo.performance.deployment_frequency.toFixed(2)}/day
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium mb-2">Security</h4>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <div className="text-sm text-muted-foreground">Open Alerts</div>
                      <div className="text-lg font-medium">{repo.security.open_alerts}</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Fixed Alerts</div>
                      <div className="text-lg font-medium">{repo.security.fixed_alerts}</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">High Severity</div>
                      <div className="text-lg font-medium">{repo.security.high_severity}</div>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium mb-2">Collaboration</h4>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <div className="text-sm text-muted-foreground">Contributors</div>
                      <div className="text-lg font-medium">
                        {repo.collaboration.unique_contributors}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Review Coverage</div>
                      <div className="text-lg font-medium">
                        {repo.collaboration.review_coverage.toFixed(1)}%
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Comment Ratio</div>
                      <div className="text-lg font-medium">
                        {repo.collaboration.comment_ratio.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
