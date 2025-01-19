import * as React from "react";
import { Button } from './ui/button';
import { LayoutGrid, List, Table } from 'lucide-react';

export type ViewType = 'board' | 'list' | 'table';

interface ViewToggleProps {
  currentView: ViewType;
  onViewChange: (view: ViewType) => void;
}

export function ViewToggle({ currentView, onViewChange }: ViewToggleProps) {
  return (
    <div className="flex gap-2">
      <Button
        variant={currentView === 'board' ? 'default' : 'outline'}
        size="sm"
        onClick={() => onViewChange('board')}
      >
        <LayoutGrid className="h-4 w-4 mr-2" />
        Board
      </Button>
      <Button
        variant={currentView === 'list' ? 'default' : 'outline'}
        size="sm"
        onClick={() => onViewChange('list')}
      >
        <List className="h-4 w-4 mr-2" />
        List
      </Button>
      <Button
        variant={currentView === 'table' ? 'default' : 'outline'}
        size="sm"
        onClick={() => onViewChange('table')}
      >
        <Table className="h-4 w-4 mr-2" />
        Table
      </Button>
    </div>
  );
}
