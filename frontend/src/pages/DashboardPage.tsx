import * as React from 'react';
import { useEffect, useState } from 'react';
import { Card } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { api } from '../services/api';

export function DashboardPage() {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await api.getMonitoringMetrics();
        setMetrics(data);
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
        <p className="text-gray-500">Loading metrics...</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Focus Time Card */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-2">Focus Time</h3>
          <Progress value={metrics?.focusTimePercentage || 0} className="mb-2" />
          <p className="text-sm text-gray-500">
            {Math.round((metrics?.focusTimeSeconds || 0) / 3600)} hours today
          </p>
        </Card>

        {/* Productivity Score Card */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-2">Productivity Score</h3>
          <div className="text-3xl font-bold mb-2">
            {Math.round(metrics?.productivityScore || 0)}%
          </div>
          <p className="text-sm text-gray-500">
            Based on focus time and activity
          </p>
        </Card>

        {/* Activity Summary Card */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-2">Activity Summary</h3>
          <div className="text-3xl font-bold mb-2">
            {metrics?.totalActivities || 0}
          </div>
          <p className="text-sm text-gray-500">
            Total activities tracked today
          </p>
        </Card>
      </div>
    </div>
  );
}
