import * as React from "react";
import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { Filter } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './ui/dialog';
import { Checkbox } from './ui/checkbox';

export interface Filters {
  status?: string;
  integration?: string;
  priority?: string;
  search?: string;
  excludeMeetings?: boolean;
}

interface FilterPanelProps {
  filters: Filters;
  onChangeFilters: (filters: Filters) => void;
}

export function FilterPanel({ filters, onChangeFilters }: FilterPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [localFilters, setLocalFilters] = useState(filters);

  const handleApplyFilters = () => {
    onChangeFilters(localFilters);
    setIsOpen(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" />
          Filters
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Filter Tasks</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          {/* Status Filter */}
          <div className="grid gap-2">
            <label className="text-sm font-medium">Status</label>
            <Select
              value={localFilters.status}
              onValueChange={(value) =>
                setLocalFilters({ ...localFilters, status: value })
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Select status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="To-Do">To-Do</SelectItem>
                <SelectItem value="In-Progress">In Progress</SelectItem>
                <SelectItem value="Done">Done</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Integration Filter */}
          <div className="grid gap-2">
            <label className="text-sm font-medium">Integration</label>
            <Select
              value={localFilters.integration}
              onValueChange={(value) =>
                setLocalFilters({ ...localFilters, integration: value })
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Select integration" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="github">GitHub</SelectItem>
                <SelectItem value="jira">Jira</SelectItem>
                <SelectItem value="linear">Linear</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Priority Filter */}
          <div className="grid gap-2">
            <label className="text-sm font-medium">Priority</label>
            <Select
              value={localFilters.priority}
              onValueChange={(value) =>
                setLocalFilters({ ...localFilters, priority: value })
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Select priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Search Filter */}
          <div className="grid gap-2">
            <label className="text-sm font-medium">Search</label>
            <Input
              placeholder="Search tasks..."
              value={localFilters.search || ''}
              onChange={(e) =>
                setLocalFilters({ ...localFilters, search: e.target.value })
              }
            />
          </div>

          {/* Exclude Meetings */}
          <div className="flex items-center space-x-2">
            <Checkbox
              id="excludeMeetings"
              checked={localFilters.excludeMeetings}
              onCheckedChange={(checked) =>
                setLocalFilters({
                  ...localFilters,
                  excludeMeetings: checked as boolean,
                })
              }
            />
            <label
              htmlFor="excludeMeetings"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
              Exclude meeting tasks
            </label>
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <Button
            variant="outline"
            onClick={() => {
              setLocalFilters(filters);
              setIsOpen(false);
            }}
          >
            Cancel
          </Button>
          <Button onClick={handleApplyFilters}>Apply Filters</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
