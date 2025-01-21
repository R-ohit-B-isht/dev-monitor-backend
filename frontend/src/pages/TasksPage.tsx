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

  console.log('Current tasks:', tasks); // Debug log

  const handleTaskClick = (task: Task) => {
    navigate(`/tasks/${task._id}`);
  };

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

        try {
          const [tasksData, relationshipsData] = await Promise.all([
            api.getTasks(filterParams),
            api.getRelationships()
          ]);
          console.log('API Response - Tasks:', tasksData); // Debug log
          console.log('API Response - Relationships:', relationshipsData); // Debug log
          
          if (Array.isArray(tasksData)) {
            setTasks(tasksData);
          } else {
            console.error('Tasks data is not an array:', tasksData);
            setError('Invalid tasks data format');
            setTasks([]);
          }
          
          if (Array.isArray(relationshipsData)) {
            setRelationships(relationshipsData);
          } else {
            console.error('Relationships data is not an array:', relationshipsData);
            setRelationships([]);
          }
        } catch (err) {
          console.error('Error fetching data:', err);
          setError('Failed to load data');
          setTasks([]);
          setRelationships([]);
        }
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
    <div className="p-4 sm:p-6">
      <Breadcrumb items={[{ label: 'Tasks' }]} />
      
      <div className="flex flex-col gap-4 mb-4 sm:mb-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <FilterPanel
            filters={filters}
            onChangeFilters={setFilters}
          />
          {!showRelationships && (
            <ViewToggle
              currentView={currentView}
              onViewChange={setCurrentView}
            />
          )}
        </div>
        
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            className="w-full sm:w-auto"
            onClick={() => navigate('/monitoring')}
          >
            <Activity className="h-4 w-4 mr-2" />
            Monitoring
          </Button>
          <Button
            variant="outline"
            className="w-full sm:w-auto"
            onClick={() => setShowRelationships(!showRelationships)}
          >
            <GitGraph className="h-4 w-4 mr-2" />
            {showRelationships ? 'Hide' : 'Show'} Relationships
          </Button>
        </div>
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
          onTaskClick={handleTaskClick}
        />
      ) : (
        <>
          {currentView === 'board' && (
            <BoardView tasks={tasks} onTaskClick={handleTaskClick} />
          )}
          {currentView === 'list' && (
            <ListView tasks={tasks} onTaskClick={handleTaskClick} />
          )}
          {currentView === 'table' && (
            <TableView tasks={tasks} onTaskClick={handleTaskClick} />
          )}
        </>
      )}


    </div>
  );
}
