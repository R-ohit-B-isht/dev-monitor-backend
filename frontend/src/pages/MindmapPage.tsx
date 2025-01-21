import * as React from 'react';
import { useEffect, useState } from 'react';
import { RelationshipGraph } from '../components/views/RelationshipGraph';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Plus, Trash2, Users } from 'lucide-react';
import { websocketService, MindMapNode, MindMapEdge, MindMapState } from '../services/websocket';
import { Breadcrumb } from '../components/Breadcrumb';

export function MindmapPage() {
  const [nodes, setNodes] = useState<MindMapNode[]>([]);
  const [edges, setEdges] = useState<MindMapEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [newNodeLabel, setNewNodeLabel] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [connectedUsers, setConnectedUsers] = useState<string[]>([]);

  useEffect(() => {
    const initializeWebSocket = async () => {
      try {
        await websocketService.connect();
        const mindmapId = 'default'; // You might want to make this dynamic
        const userId = 'current'; // Get from auth context
        websocketService.joinMindmap(mindmapId, userId);

        // Set up event listeners
        websocketService.onMindmapState((state: MindMapState) => {
          setNodes(state.nodes);
          setEdges(state.edges);
          setLoading(false);
        });

        websocketService.onUserJoined((userId: string) => {
          setConnectedUsers(prev => [...prev, userId]);
        });

        websocketService.onUserLeft((userId: string) => {
          setConnectedUsers(prev => prev.filter(id => id !== userId));
        });

        websocketService.onNodeCreated((node: MindMapNode) => {
          setNodes(prev => [...prev, node]);
        });

        websocketService.onNodeUpdated((update: Partial<MindMapNode> & { nodeId: string }) => {
          setNodes(prev => prev.map(node => 
            node._id === update.nodeId ? { ...node, ...update } : node
          ));
        });

        websocketService.onNodeDeleted((nodeId: string) => {
          setNodes(prev => prev.filter(node => node._id !== nodeId));
          if (selectedNode === nodeId) {
            setSelectedNode(null);
          }
        });

        websocketService.onEdgeCreated((edge: MindMapEdge) => {
          setEdges(prev => [...prev, edge]);
        });

        websocketService.onEdgeDeleted((edgeId: string) => {
          setEdges(prev => prev.filter(edge => edge._id !== edgeId));
        });

      } catch (err) {
        console.error('Failed to initialize WebSocket:', err);
        setError('Failed to connect to real-time service');
      }
    };

    initializeWebSocket();

    return () => {
      websocketService.disconnect();
    };
  }, [selectedNode]);

  const handleAddNode = () => {
    if (!newNodeLabel.trim()) return;

    const position = {
      x: Math.random() * 500,
      y: Math.random() * 500
    };

    websocketService.addNode(newNodeLabel, position);
    setNewNodeLabel('');
  };

  const handleDeleteNode = (nodeId: string) => {
    websocketService.deleteNode(nodeId);
    if (selectedNode === nodeId) {
      setSelectedNode(null);
    }
  };

  const handleNodeClick = (nodeId: string) => {
    if (selectedNode && selectedNode !== nodeId) {
      // Create edge between nodes
      websocketService.addEdge(selectedNode, nodeId);
      setSelectedNode(null);
    } else {
      setSelectedNode(nodeId);
    }
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <Breadcrumb items={[{ label: 'Mindmap' }]} />
        <div className="flex items-center gap-2">
          <div className="flex items-center text-sm text-muted-foreground">
            <Users className="h-4 w-4 mr-1" />
            {connectedUsers.length} connected
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 border border-red-200 rounded-lg bg-red-50 text-red-800">
          {error}
        </div>
      )}

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Add Node</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <Input
              value={newNodeLabel}
              onChange={(e) => setNewNodeLabel(e.target.value)}
              placeholder="Enter node label"
              className="flex-1"
              onKeyPress={(e) => e.key === 'Enter' && handleAddNode()}
            />
            <Button onClick={handleAddNode}>
              <Plus className="h-4 w-4 mr-1" />
              Add Node
            </Button>
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <p className="text-gray-500">Loading mindmap...</p>
        </div>
      ) : (
        <div className="mt-6">
          <RelationshipGraph
            tasks={nodes.map(node => ({
              _id: node._id,
              title: node.label,
              status: 'In-Progress',
              integration: 'github',
              createdAt: node.createdAt,
              updatedAt: node.updatedAt,
              description: '',
              assignee: '',
              priority: 'medium',
              dueDate: null,
              tags: []
            }))}
            relationships={edges.map(edge => ({
              _id: edge._id,
              sourceTaskId: edge.sourceId,
              targetTaskId: edge.targetId,
              type: 'relates-to',
              createdAt: edge.createdAt,
              updatedAt: edge.updatedAt
            }))}
            onTaskClick={(node) => handleNodeClick(node._id)}

          />
        </div>
      )}
    </div>
  );
}
