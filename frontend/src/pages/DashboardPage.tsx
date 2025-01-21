import * as React from 'react';
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { api } from '../services/api';
import { DateRangeFilter } from '../components/DateRangeFilter';
import { ContributionChart } from '../components/ContributionChart';
import { TrafficChart } from '../components/TrafficChart';
import { getTrafficStats, TrafficData } from '../services/api';

export function DashboardPage() {
  const [metrics, setMetrics] = useState<any>(null);
  const [contributions, setContributions] = useState<any>(null);
  const [trafficData, setTrafficData] = useState<TrafficData | null>(null);
  const [loading, setLoading] = useState(true);
  const [trafficLoading, setTrafficLoading] = useState(true);
  const [trafficError, setTrafficError] = useState<string | null>(null);
  const [startDate, setStartDate] = useState(() => {
    const date = new Date();
    date.setDate(date.getDate() - 30);
    return date;
  });
  const [endDate, setEndDate] = useState(() => new Date());

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricsData, contributionsData] = await Promise.all([
          api.getMonitoringMetrics(startDate, endDate),
          api.getContributions('current', startDate, endDate)
        ]);
        setMetrics(metricsData);
        setContributions(contributionsData);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    const fetchTrafficData = async () => {
      setTrafficLoading(true);
      setTrafficError(null);
      try {
        const data = await getTrafficStats('R-ohit-B-isht/dev-monitor-frontend');
        setTrafficData(data);
      } catch (error) {
        console.error('Failed to fetch traffic data:', error);
        setTrafficError('Failed to load traffic data');
      } finally {
        setTrafficLoading(false);
      }
    };

    fetchData();
    fetchTrafficData();
  }, [startDate, endDate]);

  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
        <p className="text-gray-500">Loading metrics...</p>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <h1 className="text-xl sm:text-2xl font-bold">Dashboard</h1>
        <DateRangeFilter
          startDate={startDate}
          endDate={endDate}
          onStartDateChange={setStartDate}
          onEndDateChange={setEndDate}
        />
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
        {/* Focus Time Card */}
        <Card className="p-4 sm:p-6">
          <h3 className="text-base sm:text-lg font-semibold mb-2">Focus Time</h3>
          <Progress value={metrics?.focusTimePercentage || 0} className="mb-2 h-2.5" />
          <p className="text-sm text-gray-500">
            {Math.round((metrics?.focusTimeSeconds || 0) / 3600)} hours today
          </p>
        </Card>

        {/* Productivity Score Card */}
        <Card className="p-4 sm:p-6">
          <h3 className="text-base sm:text-lg font-semibold mb-2">Productivity Score</h3>
          <div className="text-2xl sm:text-3xl font-bold mb-2">
            {Math.round(metrics?.productivityScore || 0)}%
          </div>
          <p className="text-sm text-gray-500">
            Based on focus time and activity
          </p>
        </Card>

        {/* Activity Summary Card */}
        <Card className="p-4 sm:p-6">
          <h3 className="text-base sm:text-lg font-semibold mb-2">Activity Summary</h3>
          <div className="text-2xl sm:text-3xl font-bold mb-2">
            {metrics?.totalActivities || 0}
          </div>
          <p className="text-sm text-gray-500">
            Total activities tracked today
          </p>
        </Card>
      </div>

      {/* Contribution Chart */}
      <div className="mt-8">
        {loading ? (
          <Card className="p-6">
            <div className="h-[200px] flex items-center justify-center">
              <p className="text-sm text-muted-foreground">Loading contribution data...</p>
            </div>
          </Card>
        ) : contributions ? (
          <ContributionChart
            months={contributions.months}
            totalContributions={contributions.totalContributions}
          />
        ) : (
          <Card className="p-6">
            <div className="h-[200px] flex items-center justify-center">
              <p className="text-sm text-destructive">Failed to load contribution data</p>
            </div>
          </Card>
        )}
      </div>

      {/* Traffic Chart */}
      <div className="mt-8">
        <TrafficChart
          data={trafficData}
          loading={trafficLoading}
          error={trafficError}
        />
      </div>
    </div>
  );
}
