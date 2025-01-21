import React, { useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Task } from '../../types/Task';
import { Relationship } from '../../services/api';

interface RelationshipGraphProps {
  tasks: Task[];
  relationships: Relationship[];
  onTaskClick: (task: Task) => void;
}

const nodeWidth = 250;
const nodeHeight = 80;

export function RelationshipGraph({ tasks, relationships, onTaskClick }: RelationshipGraphProps) {
  // Convert tasks to nodes
  const nodes: Node[] = useMemo(() => {
    return tasks.map((task, index) => ({
      id: task._id,
      type: 'default',
      data: { label: task.title, task },
      position: {
        x: (index % 3) * (nodeWidth + 100) + 50,
        y: Math.floor(index / 3) * (nodeHeight + 100) + 50
      },
      style: {
        width: nodeWidth,
        background: task.status === 'Done' ? '#dcfce7' : task.status === 'In-Progress' ? '#fef9c3' : '#f3f4f6',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        padding: '12px'
      }
    }));
  }, [tasks]);

  // Convert relationships to edges
  const edges: Edge[] = useMemo(() => {
    return relationships.map((rel): Edge => ({
      id: rel._id!,
      source: rel.sourceTaskId,
      target: rel.targetTaskId,
      label: rel.type,
      type: 'smoothstep',
      animated: rel.type === 'blocks',
      style: { stroke: rel.type === 'blocks' ? '#ef4444' : '#94a3b8' }
    }));
  }, [relationships]);

  const onNodeClick = (_: React.MouseEvent, node: Node) => {
    const task = (node.data as { task: Task }).task;
    onTaskClick(task);
  };

  return (
    <div className="w-full h-[calc(100vh-12rem)]">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodeClick={onNodeClick}
        fitView
        attributionPosition="bottom-right"
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}
