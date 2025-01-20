import { useCallback, useEffect, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Panel,
  MiniMap,
  useReactFlow,
  ConnectionMode,
  ReactFlowProvider,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Task } from '../../../types/Task';
import { Relationship } from '../../../services/api';
import { ErrorBoundary } from '../../ErrorBoundry';
import { Button } from '../../ui/button';
import { ZoomIn, ZoomOut, Maximize } from 'lucide-react';

interface RelationshipGraphProps {
  task: Task;
  relationships: Relationship[];
  allTasks: Task[];
}

export function RelationshipGraph({ task, relationships, allTasks }: RelationshipGraphProps) {
  // Convert tasks and relationships to nodes and edges
  const getInitialNodes = useCallback(() => {
    const nodes: Node[] = [];
    const addedTaskIds = new Set<string>();

    // Add central task node
    nodes.push({
      id: task._id,
      data: { label: task.title, status: task.status },
      position: { x: 0, y: 0 },
      type: 'default',
      style: {
        background: '#fff',
        border: '1px solid #e2e8f0',
        borderRadius: '8px',
        padding: '10px',
      },
    });
    addedTaskIds.add(task._id);

    // Add related task nodes in a circular layout
    relationships.forEach((rel, index) => {
      const relatedTask = allTasks.find(t => t._id === rel.targetTaskId);
      if (!relatedTask || addedTaskIds.has(rel.targetTaskId)) return;

      const angle = (2 * Math.PI * index) / relationships.length;
      const radius = 200;
      const x = Math.cos(angle) * radius;
      const y = Math.sin(angle) * radius;

      nodes.push({
        id: relatedTask._id,
        data: { label: relatedTask.title, status: relatedTask.status },
        position: { x, y },
        type: 'default',
        style: {
          background: '#fff',
          border: '1px solid #e2e8f0',
          borderRadius: '8px',
          padding: '10px',
        },
      });
      addedTaskIds.add(relatedTask._id);
    });

    return nodes;
  }, [task, relationships, allTasks]);

  const getInitialEdges = useCallback(() => {
    return relationships
      .filter(rel => rel._id && rel.sourceTaskId && rel.targetTaskId) // Filter out invalid relationships
      .map((rel): Edge => ({
        id: rel._id!, // Safe to use ! after filter
        source: rel.sourceTaskId,
        target: rel.targetTaskId,
        label: rel.type,
        type: 'smoothstep',
        animated: rel.type === 'blocks',
        style: { stroke: rel.type === 'blocks' ? '#ef4444' : '#94a3b8' }
      }));
  }, [relationships]);

  const memoizedNodes = useCallback(getInitialNodes, [task, relationships, allTasks]);
  const memoizedEdges = useCallback(getInitialEdges, [relationships]);

  const initialNodes = useCallback(() => memoizedNodes(), [memoizedNodes, getInitialNodes]);
  const initialEdges = useCallback(() => memoizedEdges(), [memoizedEdges, getInitialEdges]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes());
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges());

  useEffect(() => {
    setNodes(initialNodes());
    setEdges(initialEdges());
  }, [initialNodes, initialEdges, setNodes, setEdges, relationships, allTasks]);

  const nodeTypes = useMemo(() => ({
    default: ({ data }: { data: { label: string; status: string } }) => {
      const getStatusColor = (status: string) => {
        switch (status) {
          case 'To-Do':
            return 'bg-yellow-100 border-yellow-300';
          case 'In-Progress':
            return 'bg-blue-100 border-blue-300';
          case 'Done':
            return 'bg-green-100 border-green-300';
          default:
            return 'bg-white';
        }
      };

      return (
        <div className={`px-4 py-2 shadow-lg rounded-lg border hover:shadow-xl transition-shadow ${getStatusColor(data.status)}`}>
          <div className="font-medium text-center">{data.label}</div>
          <div className="mt-2 text-xs text-center opacity-75">{data.status}</div>
        </div>
      );
    },
  }), []);

  // Removed custom edge component in favor of built-in smoothstep edges

  // Error handling is now managed by ErrorBoundary

  const Flow = () => {
    const { fitView, zoomIn, zoomOut } = useReactFlow();
    return (
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-right"
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    );
  };

  return (
    <div className="w-full h-[calc(100vh-12rem)] border rounded-lg overflow-hidden relative">
      <ErrorBoundary fallback={<div className="p-4 text-destructive">Failed to render relationship graph</div>}>
        <ReactFlowProvider>
          <Flow />
        </ReactFlowProvider>
      </ErrorBoundary>
    </div>
  );
}
