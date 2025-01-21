import * as React from 'react';
import { Button } from './ui/button';
import { Calendar } from 'lucide-react';
import { format } from 'date-fns';

interface DateRangeFilterProps {
  startDate: Date;
  endDate: Date;
  onStartDateChange: (date: Date) => void;
  onEndDateChange: (date: Date) => void;
  className?: string;
}

export function DateRangeFilter({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  className = ''
}: DateRangeFilterProps) {
  return (
    <div className={`flex flex-col sm:flex-row items-start sm:items-center gap-4 ${className}`}>
      <div className="flex items-center gap-2">
        <Calendar className="h-4 w-4 text-muted-foreground" />
        <input
          type="date"
          value={format(startDate, 'yyyy-MM-dd')}
          onChange={(e) => onStartDateChange(new Date(e.target.value))}
          className="px-3 py-1 rounded-md border text-sm bg-background"
        />
        <span className="text-muted-foreground">to</span>
        <input
          type="date"
          value={format(endDate, 'yyyy-MM-dd')}
          onChange={(e) => onEndDateChange(new Date(e.target.value))}
          className="px-3 py-1 rounded-md border text-sm bg-background"
        />
      </div>
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            const end = new Date();
            const start = new Date();
            start.setDate(end.getDate() - 7);
            onStartDateChange(start);
            onEndDateChange(end);
          }}
        >
          Last 7 days
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            const end = new Date();
            const start = new Date();
            start.setDate(end.getDate() - 30);
            onStartDateChange(start);
            onEndDateChange(end);
          }}
        >
          Last 30 days
        </Button>
      </div>
    </div>
  );
}
