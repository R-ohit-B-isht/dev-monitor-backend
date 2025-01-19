import * as React from 'react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Activity, GitGraph } from 'lucide-react';
import { ViewToggle, ViewType } from '../components/ViewToggle';
import { FilterPanel, Filters } from '../components/FilterPanel';
import { BoardView } from '../components/views/BoardView';
import { ListView } from '../components/views/ListView';
import { TableView } from '../components/views/TableView';
import { RelationshipGraph } from '../components/views/RelationshipGraph';
import { Breadcrumb } from '../components/Breadcrumb';
import { Task } from '../types/Task';
import { api, Relationship } from '../services/api';

export function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filters, setFilters] = useState<Filters>({});
  const [currentView, setCurrentView] = useState<ViewType>('board');
  const [showRelationships, setShowRelationships] = useState(false);
  const [relationships, setRelationships] = useState<Relationship[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const filterParams: Record<string, string> = {};
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== '') {
            if (key === 'excludeMeetings') {
              filterParams[key] = value ? 'true' : 'false';
            } else {
              filterParams[key] = value.toString();
            }
          }
        });

        const [tasksResponse, relationshipsResponse] = await Promise.all([
          fetch(`http://localhost:5000/tasks?${new URLSearchParams(filterParams)}`),
          fetch('http://localhost:5000/relationships')
        ]);
        const tasksData = await tasksResponse.json();
        const relationshipsData = await relationshipsResponse.json();
        setTasks(tasksData);
        setRelationships(relationshipsData);
      } catch (err) {
        setError('Failed to load data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filters]);

  return (
    <div className="p-6">
      <Breadcrumb items={[{ label: 'Tasks' }]} />
      
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div className="flex items-center gap-4">
          <FilterPanel
            filters={filters}
            onChangeFilters={setFilters}
          />
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => navigate('/monitoring')}
            >
              <Activity className="h-4 w-4 mr-2" />
              Monitoring
            </Button>
            <Button
              variant="outline"
              onClick={() => setShowRelationships(!showRelationships)}
            >
              <GitGraph className="h-4 w-4 mr-2" />
              {showRelationships ? 'Hide' : 'Show'} Relationships
            </Button>
          </div>
        </div>
        {!showRelationships && (
          <ViewToggle
            currentView={currentView}
            onViewChange={setCurrentView}
          />
        )}
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <p className="text-gray-500">Loading data...</p>
        </div>
      ) : error ? (
        <div className="flex items-center justify-center h-64">
          <p className="text-red-500">{error}</p>
        </div>
      ) : showRelationships ? (
        <RelationshipGraph
          tasks={tasks}
          relationships={relationships}
          onTaskClick={(task) => console.log('Task clicked:', task)}
        />
      ) : (
        <>
          {currentView === 'board' && (
            <BoardView tasks={tasks} onTaskClick={(task) => console.log('Task clicked:', task)} />
          )}
          {currentView === 'list' && (
            <ListView tasks={tasks} onTaskClick={(task) => console.log('Task clicked:', task)} />
          )}
          {currentView === 'table' && (
            <TableView tasks={tasks} onTaskClick={(task) => console.log('Task clicked:', task)} />
          )}
        </>
      )}
    </div>
  );
}
