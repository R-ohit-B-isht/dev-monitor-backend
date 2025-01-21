import * as React from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from './ui/card';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
// Removed unused import - formatDuration not needed

interface AppFocusData {
  appName: string;
  focusTime: number;
  eventCount: number;
  percentage: number;
}

interface FocusBreakdownChartProps {
  data: AppFocusData[];
  className?: string;
}

export function FocusBreakdownChart({ data, className = '' }: FocusBreakdownChartProps) {
  const chartData = data.map(app => ({
    name: app.appName,
    focusTime: app.focusTime / 3600, // Convert to hours
    percentage: app.percentage
  }));

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Focus Time Breakdown</CardTitle>
        <CardDescription>Time spent in different applications</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <XAxis 
                dataKey="name"
                tick={{ fontSize: 12 }}
                interval={0}
                angle={-45}
                textAnchor="end"
              />
              <YAxis
                label={{ 
                  value: 'Hours',
                  angle: -90,
                  position: 'insideLeft',
                  style: { textAnchor: 'middle' }
                }}
              />
              <Tooltip
                formatter={(value: number) => [
                  `${value.toFixed(2)} hours (${(value * 100 / chartData.reduce((acc, curr) => acc + curr.focusTime, 0)).toFixed(1)}%)`,
                  'Focus Time'
                ]}
              />
              <Bar
                dataKey="focusTime"
                fill="var(--primary)"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
