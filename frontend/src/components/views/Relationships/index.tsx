import { useState, useEffect } from 'react';
import { RelationshipGraph } from './RelationshipGraph';
import { Card, CardHeader, CardTitle, CardContent } from '../../ui/card';
import { Button } from '../../ui/button';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '../../ui/collapsible';
import { ChevronDown, ChevronRight } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../ui/select';

import { Label } from '../../ui/label';
// Badge import removed as it's not used directly
import { Link2, Unlink, GitMerge, GitBranch, Copy, ArrowDown, ArrowUp } from 'lucide-react';
import { Task } from '@/types/Task';
import { api, Relationship } from '../../../services/api';
import { ApiErrorResponse } from '../../../types/ApiError';

interface RelationshipsProps {
  task: Task;
  allTasks: Task[];
}

export function Relationships({ task, allTasks }: RelationshipsProps) {
  const [relationships, setRelationships] = useState<Relationship[]>([]);
  const [selectedType, setSelectedType] = useState<Relationship['type']>('relates-to');
  const [selectedTaskId, setSelectedTaskId] = useState<string>('');
  const [isOpen, setIsOpen] = useState(() => {
    const savedState = localStorage.getItem('relationshipCardCollapsed');
    return savedState ? JSON.parse(savedState) : false;
  });

  useEffect(() => {
    localStorage.setItem('relationshipCardCollapsed', JSON.stringify(isOpen));
  }, [isOpen]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRelationships = async () => {
      try {
        setLoading(true);
        setError(null);
        const loadedRelationships = await api.getRelationships({ sourceTaskId: task._id });
        setRelationships(loadedRelationships);
      } catch (err) {
        console.error('Error loading relationships:', err);
        setError('Failed to load relationships');
      } finally {
        setLoading(false);
      }
    };

    fetchRelationships();
  }, [task._id]);

  const relationshipTypes = [
    { value: 'blocks', label: 'Blocks', icon: <GitMerge className="h-4 w-4" /> },
    { value: 'blocked-by', label: 'Blocked By', icon: <GitBranch className="h-4 w-4" /> },
    { value: 'relates-to', label: 'Relates To', icon: <Link2 className="h-4 w-4" /> },
    { value: 'duplicates', label: 'Duplicates', icon: <Copy className="h-4 w-4" /> },
    { value: 'parent-of', label: 'Parent Of', icon: <ArrowDown className="h-4 w-4" /> },
    { value: 'child-of', label: 'Child Of', icon: <ArrowUp className="h-4 w-4" /> },
  ];

  const addRelationship = async () => {
    if (!selectedTaskId || !selectedType) return;

    try {
      await api.createRelationship({
        sourceTaskId: task._id,
        targetTaskId: selectedTaskId,
        type: selectedType,
      });

      // Refresh relationships list
      const updatedRelationships = await api.getRelationships({ sourceTaskId: task._id });
      setRelationships(updatedRelationships);

      // Reset selection
      setSelectedTaskId('');
      setSelectedType('relates-to');
    } catch (err: unknown) {
      const apiError = err as ApiErrorResponse;
      console.error('Error creating relationship:', apiError);
      const errorMessage = apiError.response?.data?.error || apiError.error || 'Failed to create relationship';
      setError(errorMessage);

      // Log detailed error information
      if (apiError.response) {
        console.error('Response data:', apiError.response.data);
        console.error('Response status:', apiError.response.status);
        console.error('Response headers:', apiError.response.headers);
      }
    }
  };

  const removeRelationship = async (relationshipId: string) => {
    try {
      await api.deleteRelationship(relationshipId);

      // Refresh relationships list
      const updatedRelationships = await api.getRelationships({ sourceTaskId: task._id });
      setRelationships(updatedRelationships);
    } catch (err) {
      console.error('Error deleting relationship:', err);
      setError('Failed to delete relationship');
    }
  };

  const getRelatedTask = (taskId: string) => {
    return allTasks.find(t => t._id === taskId);
  };

  const getRelationshipIcon = (type: Relationship['type']) => {
    switch (type) {
      case 'blocks':
        return <GitMerge className="h-4 w-4" />;
      case 'blocked-by':
        return <GitBranch className="h-4 w-4" />;
      case 'relates-to':
        return <Link2 className="h-4 w-4" />;
      case 'duplicates':
        return <Copy className="h-4 w-4" />;
      case 'parent-of':
        return <ArrowDown className="h-4 w-4" />;
      case 'child-of':
        return <ArrowUp className="h-4 w-4" />;
      default:
        return <Link2 className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Task Relationships</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <p className="text-muted-foreground">Loading relationships...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Task Relationships</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-destructive space-y-2">
            <p>{error}</p>
            <Button
              variant="outline"
              onClick={() => {
                setError(null);
                setLoading(true);
                api.getRelationships({ sourceTaskId: task._id })
                  .then(setRelationships)
                  .catch(err => {
                    console.error('Error reloading relationships:', err);
                    setError('Failed to load relationships');
                  })
                  .finally(() => setLoading(false));
              }}
            >
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const mainContent = (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <Card className="w-full">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle>Task Relationships</CardTitle>
          <CollapsibleTrigger asChild>
            <Button variant="ghost" size="sm" className="w-9 p-0">
              {isOpen ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </Button>
          </CollapsibleTrigger>
        </CardHeader>
        <CollapsibleContent>
          <CardContent>
            <div className="space-y-6">
              {/* Add Relationship Form */}
              <div className="space-y-4">
                <div className="grid gap-4">
              <div className="space-y-2">
                <Label>Relationship Type</Label>
                <Select
                  value={selectedType}
                  onValueChange={(value) => setSelectedType(value as Relationship['type'])}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {relationshipTypes.map(type => (
                      <SelectItem key={type.value} value={type.value}>
                        <div className="flex items-center">
                          {type.icon}
                          <span className="ml-2">{type.label}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Related Task</Label>
                <Select
                  value={selectedTaskId}
                  onValueChange={setSelectedTaskId}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a task" />
                  </SelectTrigger>
                  <SelectContent>
                    {allTasks
                      .filter(t => t._id !== task._id)
                      .map(t => (
                        <SelectItem key={t._id} value={t._id}>
                          {t.title}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Button
              onClick={addRelationship}
              disabled={!selectedTaskId || !selectedType}
              className="w-full"
            >
              <Link2 className="h-4 w-4 mr-2" />
              Add Relationship
            </Button>
          </div>

          {/* Existing Relationships */}
          <div className="space-y-4">
            <Label>Existing Relationships</Label>
            <div className="space-y-2">
              {relationships.map(relationship => {
                const relatedTask = getRelatedTask(relationship.targetTaskId);
                if (!relatedTask) return null;

                return (
                  <div
                    key={relationship._id}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div className="flex items-center gap-2">
                      {getRelationshipIcon(relationship.type)}
                      <span className="font-medium">{relatedTask.title}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Select
                        value={relationship.type}
                        onValueChange={async (value) => {
                          try {
                            await api.updateRelationship(relationship._id!, value as Relationship['type']);
                            const updatedRelationships = await api.getRelationships({ sourceTaskId: task._id });
                            setRelationships(updatedRelationships);
                          } catch (err) {
                            console.error('Error updating relationship:', err);
                            setError('Failed to update relationship');
                          }
                        }}
                      >
                        <SelectTrigger className="h-8 w-[130px]">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {relationshipTypes.map(type => (
                            <SelectItem key={type.value} value={type.value}>
                              <div className="flex items-center">
                                {type.icon}
                                <span className="ml-2">{type.label}</span>
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => removeRelationship(relationship._id!)}
                      >
                        <Unlink className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                );
              })}
              {relationships.length === 0 && (
                <div className="text-center text-muted-foreground py-4">
                  No relationships defined
                </div>
              )}
            </div>
          </div>

          {/* Visualization */}
          <RelationshipGraph
            task={task}
            relationships={relationships}
            allTasks={allTasks}
          />
            </div>
          </CardContent>
        </CollapsibleContent>
      </Card>
    </Collapsible>
  );

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Task Relationships</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <p className="text-muted-foreground">Loading relationships...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Task Relationships</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-destructive space-y-2">
            <p>{error}</p>
            <Button
              variant="outline"
              onClick={() => {
                setError(null);
                setLoading(true);
                api.getRelationships({ sourceTaskId: task._id })
                  .then(setRelationships)
                  .catch(err => {
                    console.error('Error reloading relationships:', err);
                    setError('Failed to load relationships');
                  })
                  .finally(() => setLoading(false));
              }}
            >
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return mainContent;
}
