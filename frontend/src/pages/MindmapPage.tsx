import * as React from 'react';
import { useEffect, useState } from 'react';
import { RelationshipGraph } from '../components/views/RelationshipGraph';
import { Task } from '../types/Task';
import { Relationship } from '../services/api';
import { Breadcrumb } from '../components/Breadcrumb';

interface MindmapNode extends Task {
  position?: { x: number; y: number };
}

interface MindmapEdge extends Relationship {
  sourceId: string;
  targetId: string;
}

export function MindmapPage() {
  const [nodes, setNodes] = useState<MindmapNode[]>([]);
  const [edges, setEdges] = useState<MindmapEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMindmap = async () => {
      setLoading(true);
      setError(null);
      try {
        const [nodesResponse, edgesResponse] = await Promise.all([
          fetch('http://localhost:5000/mindmap/nodes'),
          fetch('http://localhost:5000/mindmap/edges')
        ]);
        
        const nodesData = await nodesResponse.json();
        const edgesData = await edgesResponse.json();

        // Convert mindmap nodes to task format for RelationshipGraph
        const formattedNodes = nodesData.map((node: any) => ({
          _id: node._id,
          title: node.label,
          status: 'In-Progress',
          integration: 'github',
          createdAt: node.createdAt,
          updatedAt: node.updatedAt,
          position: node.position
        }));

        // Convert mindmap edges to relationship format
        const formattedEdges = edgesData.map((edge: any) => ({
          _id: edge._id,
          sourceTaskId: edge.sourceId,
          targetTaskId: edge.targetId,
          type: 'relates-to',
          createdAt: edge.createdAt,
          updatedAt: edge.updatedAt
        }));

        setNodes(formattedNodes);
        setEdges(formattedEdges);
      } catch (err) {
        setError('Failed to load mindmap data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchMindmap();
  }, []);

  return (
    <div className="p-6">
      <Breadcrumb items={[{ label: 'Mindmap' }]} />
      
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <p className="text-gray-500">Loading mindmap...</p>
        </div>
      ) : error ? (
        <div className="flex items-center justify-center h-64">
          <p className="text-red-500">{error}</p>
        </div>
      ) : (
        <div className="mt-6">
          <RelationshipGraph
            tasks={nodes}
            relationships={edges}
            onTaskClick={(node) => console.log('Node clicked:', node)}
          />
        </div>
      )}
    </div>
  );
}
