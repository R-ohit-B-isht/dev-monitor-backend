import * as React from "react";
import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './ui/dialog';
import { Button } from './ui/button';
import { Calendar } from './ui/calendar';
import { Checkbox } from './ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { FileDown, Calendar as CalendarIcon } from 'lucide-react';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { format } from 'date-fns';
import { api } from '../services/api';
import type { DateRange } from 'react-day-picker';
import type { CheckedState } from "@radix-ui/react-checkbox";

interface ReportPanelProps {
  engineerId?: string;
}

export const ReportPanel: React.FC<ReportPanelProps> = ({ engineerId = 'current' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState<DateRange | undefined>();
  const [reportType, setReportType] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  const [fileFormat, setFileFormat] = useState<'json' | 'csv'>('csv');
  const [includeAchievements, setIncludeAchievements] = useState(true);
  const [includeMeetings, setIncludeMeetings] = useState(true);
  const [availableMetrics, setAvailableMetrics] = useState<Array<{
    id: string;
    name: string;
    type: string;
  }>>([]);

  React.useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const summary = await api.getReportSummary();
        setAvailableMetrics(summary.metrics);
      } catch (error) {
        console.error('Failed to fetch report metrics:', error);
      }
    };
    fetchMetrics();
  }, []);

  const handleGenerateReport = async () => {
    setLoading(true);
    try {
      const response = await api.generateReport({
        startDate: dateRange?.from?.toISOString(),
        endDate: dateRange?.to?.toISOString(),
        type: reportType,
        format: fileFormat,
        engineerId,
        includeAchievements,
        includeMeetings
      });

      if (fileFormat === 'csv') {
        // Handle CSV download
        const blob = new Blob([response], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `monitoring_report_${reportType}_${format(new Date(), 'yyyy-MM-dd')}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }

      setIsOpen(false);
    } catch (error) {
      console.error('Failed to generate report:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline">
          <FileDown className="h-4 w-4 mr-2" />
          Generate Report
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Generate Monitoring Report</DialogTitle>
          <DialogDescription>
            Customize and download your monitoring report
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          {/* Date Range Picker */}
          <div className="grid gap-2">
            <label className="text-sm font-medium">Date Range</label>
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="outline" className="justify-start text-left font-normal">
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {dateRange?.from ? (
                    dateRange.to ? (
                      <>
                        {format(dateRange.from, "LLL dd, y")} -{" "}
                        {format(dateRange.to, "LLL dd, y")}
                      </>
                    ) : (
                      format(dateRange.from, "LLL dd, y")
                    )
                  ) : (
                    <span>Pick a date range</span>
                  )}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  initialFocus
                  mode="range"
                  selected={dateRange}
                  onSelect={setDateRange}
                  numberOfMonths={2}
                />
              </PopoverContent>
            </Popover>
          </div>

          {/* Report Type */}
          <div className="grid gap-2">
            <label className="text-sm font-medium">Report Type</label>
            <Select value={reportType} onValueChange={(value: any) => setReportType(value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select report type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* File Format */}
          <div className="grid gap-2">
            <label className="text-sm font-medium">File Format</label>
            <Select value={fileFormat} onValueChange={(value: any) => setFileFormat(value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select file format" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="csv">CSV</SelectItem>
                <SelectItem value="json">JSON</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Include Options */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Include in Report</label>
            <div className="flex flex-col gap-2">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="achievements"
                  checked={includeAchievements}
                  onCheckedChange={(checked: CheckedState) => setIncludeAchievements(!!checked)}
                />
                <label htmlFor="achievements" className="text-sm">
                  Achievements
                </label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="meetings"
                  checked={includeMeetings}
                  onCheckedChange={(checked: CheckedState) => setIncludeMeetings(!!checked)}
                />
                <label htmlFor="meetings" className="text-sm">
                  Meeting Data
                </label>
              </div>
            </div>
          </div>

          {/* Available Metrics */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Available Metrics</label>
            <div className="text-sm text-muted-foreground">
              {availableMetrics.map((metric) => (
                <div key={metric.id} className="flex items-center gap-2">
                  <span className="w-32">{metric.name}</span>
                  <span className="text-xs bg-secondary px-2 py-0.5 rounded">
                    {metric.type}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={() => setIsOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleGenerateReport} disabled={loading}>
            {loading ? "Generating..." : "Generate Report"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
