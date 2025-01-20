import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { cn } from '../lib/utils';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from './ui/tooltip';

interface Contribution {
  date: string;
  count: number;
  intensity: number;
}

interface Month {
  year: number;
  month: number;
  name: string;
  days: number;
  contributions: Contribution[];
}

interface ContributionChartProps {
  months: Month[];
  totalContributions: number;
}

const intensityColors: Record<number, string> = {
  0: 'bg-zinc-100 dark:bg-zinc-800 group-hover:bg-zinc-200 dark:group-hover:bg-zinc-700',
  1: 'bg-emerald-100 dark:bg-emerald-900/30 group-hover:bg-emerald-200 dark:group-hover:bg-emerald-800/40',
  2: 'bg-emerald-200 dark:bg-emerald-800/40 group-hover:bg-emerald-300 dark:group-hover:bg-emerald-700/50',
  3: 'bg-emerald-300 dark:bg-emerald-700/50 group-hover:bg-emerald-400 dark:group-hover:bg-emerald-600/60',
  4: 'bg-emerald-400 dark:bg-emerald-600/60 group-hover:bg-emerald-500 dark:group-hover:bg-emerald-500/70'
} as const;

export function ContributionChart({ months, totalContributions }: ContributionChartProps) {
  const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium">
          {totalContributions.toLocaleString()} contributions in the last year
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className="select-none">Less</span>
            <div className="flex gap-1">
              {Object.values(intensityColors).map((color, i) => (
                <div
                  key={i}
                  className={cn('w-3 h-3 rounded-sm transition-colors', color)}
                  role="presentation"
                />
              ))}
            </div>
            <span className="select-none">More</span>
          </div>
          
          <div className="relative overflow-x-auto scrollbar-thin scrollbar-thumb-muted-foreground/20 scrollbar-track-transparent">
            <div className="flex min-w-[800px] pb-4">
              {/* Weekday labels */}
              <div className="flex flex-col gap-2 pr-3 pt-6 text-xs text-muted-foreground sticky left-0 bg-background/80 backdrop-blur-sm">
                {weekdays.map((day, i) => (
                  <div key={i} className="h-3 text-right font-medium hover:text-primary transition-colors">
                    {i % 2 === 0 ? day : ''}
                  </div>
                ))}
              </div>
              
              {/* Months grid */}
              <div className="flex gap-2">
                {months.map((month, monthIndex) => (
                  <div key={monthIndex} className="flex flex-col">
                    <div className="h-6 text-xs text-muted-foreground text-center sticky top-0 bg-background/80 backdrop-blur-sm px-1 font-medium hover:text-primary transition-colors">
                      {month.name}
                    </div>
                    <div className="grid grid-rows-7 grid-flow-col gap-1">
                      {Array.from({ length: month.days }).map((_, day) => {
                        const contribution = month.contributions[day];
                        return (
                          <TooltipProvider key={day}>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <div
                                  className={cn(
                                    'w-3 h-3 rounded-sm transition-all duration-200 cursor-pointer hover:ring-2 hover:ring-primary/50 hover:ring-offset-1 hover:scale-105',
                                    intensityColors[contribution?.intensity || 0]
                                  )}
                                  role="gridcell"
                                  aria-label={`${contribution?.count || 0} contributions on ${new Date(contribution?.date || '').toLocaleDateString(undefined, {
                                    weekday: 'long',
                                    year: 'numeric',
                                    month: 'long',
                                    day: 'numeric'
                                  })}`}
                                />
                              </TooltipTrigger>
                              <TooltipContent>
                                <p className="text-sm">
                                  <span className="font-medium">
                                    {contribution?.count || 0} contributions
                                  </span>
                                  <br />
                                  {new Date(contribution?.date).toLocaleDateString(undefined, {
                                    weekday: 'long',
                                    year: 'numeric',
                                    month: 'long',
                                    day: 'numeric'
                                  })}
                                </p>
                              </TooltipContent>
                            </Tooltip>
                          </TooltipProvider>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
