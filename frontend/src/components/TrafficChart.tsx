import * as React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from './ui/card';
import { Eye, GitFork } from 'lucide-react';

interface TrafficData {
  repository: string;
  views: number;
  unique_views: number;
  clones: number;
  unique_clones: number;
  views_history: Array<{
    timestamp: string;
    count: number;
    uniques: number;
  }>;
  clones_history: Array<{
    timestamp: string;
    count: number;
    uniques: number;
  }>;
  updated_at: string;
}

interface TrafficChartProps {
  data: TrafficData | null;
  loading?: boolean;
  error?: string | null;
}

export function TrafficChart({ data, loading, error }: TrafficChartProps) {
  if (loading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="h-[300px] flex items-center justify-center">
            <p className="text-sm text-muted-foreground">Loading traffic data...</p>
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

  if (!data) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="h-[300px] flex items-center justify-center">
            <p className="text-sm text-muted-foreground">No traffic data available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Combine views and clones data for the chart
  const chartData = data.views_history.map(view => {
    const clone = data.clones_history.find(
      clone => new Date(clone.timestamp).toDateString() === new Date(view.timestamp).toDateString()
    ) || { count: 0, uniques: 0 };

    return {
      date: new Date(view.timestamp).toLocaleDateString(),
      views: view.count,
      unique_views: view.uniques,
      clones: clone.count,
      unique_clones: clone.uniques
    };
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Repository Traffic</CardTitle>
        <CardDescription>Views and clones over time for {data.repository}</CardDescription>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-2">
          <div className="flex items-center gap-2">
            <Eye className="h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium">{data.views}</p>
              <p className="text-xs text-muted-foreground">Total Views</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Eye className="h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium">{data.unique_views}</p>
              <p className="text-xs text-muted-foreground">Unique Views</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <GitFork className="h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium">{data.clones}</p>
              <p className="text-xs text-muted-foreground">Total Clones</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <GitFork className="h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium">{data.unique_clones}</p>
              <p className="text-xs text-muted-foreground">Unique Clones</p>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[300px] mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="views"
                stroke="#8884d8"
                name="Views"
              />
              <Line
                type="monotone"
                dataKey="unique_views"
                stroke="#82ca9d"
                name="Unique Views"
              />
              <Line
                type="monotone"
                dataKey="clones"
                stroke="#ffc658"
                name="Clones"
              />
              <Line
                type="monotone"
                dataKey="unique_clones"
                stroke="#ff7300"
                name="Unique Clones"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
