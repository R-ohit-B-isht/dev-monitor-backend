import * as React from 'react';
import { useState, useMemo } from 'react';
import { Task } from '../../types/Task';
import { Badge } from '../../components/ui/badge';
import { statusStyles } from '../TaskCard';
import { cn } from '../../lib/utils';
import { Github, Trello, LineChart, ArrowUpDown } from 'lucide-react';
import { Button } from '../../components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../../components/ui/table";

const integrationIcons = {
  github: <Github className="h-4 w-4" />,
  jira: <Trello className="h-4 w-4" />,
  linear: <LineChart className="h-4 w-4" />
};

interface TableViewProps {
  tasks: Task[];
  onTaskClick: (task: Task) => void;
}

type SortField = 'title' | 'status' | 'priority' | 'updatedAt' | 'integration';
type SortDirection = 'asc' | 'desc';

export function TableView({ tasks, onTaskClick }: TableViewProps) {
  const [sortField, setSortField] = useState<SortField>('updatedAt');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const sortedTasks = useMemo(() => {
    return [...tasks].sort((a, b) => {
      const direction = sortDirection === 'asc' ? 1 : -1;
      
      if (sortField === 'updatedAt') {
        return direction * (new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());
      }
      
      const aValue = a[sortField] || '';
      const bValue = b[sortField] || '';
      
      return direction * String(aValue).localeCompare(String(bValue));
    });
  }, [tasks, sortField, sortDirection]);

  const renderSortButton = (field: SortField, label: string) => (
    <Button
      variant="ghost"
      onClick={() => handleSort(field)}
      className="hover:bg-muted/50 h-8 px-2"
    >
      {label}
      <ArrowUpDown className="ml-2 h-4 w-4" />
    </Button>
  );

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>{renderSortButton('title', 'Title')}</TableHead>
            <TableHead>{renderSortButton('status', 'Status')}</TableHead>
            <TableHead>{renderSortButton('priority', 'Priority')}</TableHead>
            <TableHead>{renderSortButton('integration', 'Integration')}</TableHead>
            <TableHead>Created</TableHead>
            <TableHead>{renderSortButton('updatedAt', 'Updated')}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedTasks.map((task) => (
            <TableRow
              key={task._id}
              className="cursor-pointer hover:bg-muted/50"
              onClick={() => onTaskClick(task)}
            >
              <TableCell className="font-medium">{task.title}</TableCell>
              <TableCell>
                <Badge 
                  variant="secondary"
                  className={cn(
                    "transition-colors",
                    statusStyles[task.status]
                  )}
                >
                  {task.status}
                </Badge>
              </TableCell>
              <TableCell>
                {task.priority && (
                  <Badge variant="outline">
                    {task.priority}
                  </Badge>
                )}
              </TableCell>
              <TableCell>
                <div className="flex items-center">
                  {integrationIcons[task.integration]}
                  <span className="ml-2">{task.integration}</span>
                </div>
              </TableCell>
              <TableCell>{new Date(task.createdAt).toLocaleDateString()}</TableCell>
              <TableCell>{new Date(task.updatedAt).toLocaleDateString()}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
