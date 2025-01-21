import { io, Socket } from 'socket.io-client';

export interface MindMapNode {
  _id: string;
  mindmapId: string;
  label: string;
  position: { x: number; y: number };
  createdAt: string;
  updatedAt: string;
  createdBy: string;
}

export interface MindMapEdge {
  _id: string;
  mindmapId: string;
  sourceId: string;
  targetId: string;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
}

export interface MindMapState {
  nodes: MindMapNode[];
  edges: MindMapEdge[];
}

class WebSocketService {
  private socket: Socket | null = null;
  private mindmapId: string | null = null;
  private userId: string | null = null;

  connect(url: string = 'http://localhost:5000'): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.socket = io(url);

        this.socket.on('connect', () => {
          console.log('WebSocket connected');
          resolve();
        });

        this.socket.on('connect_error', (error) => {
          console.error('WebSocket connection error:', error);
          reject(error);
        });

        this.setupEventListeners();
      } catch (error) {
        console.error('Failed to create WebSocket connection:', error);
        reject(error);
      }
    });
  }

  private stateCallback?: (state: MindMapState) => void;
  private userJoinedCallback?: (userId: string) => void;
  private userLeftCallback?: (userId: string) => void;
  private nodeCreatedCallback?: (node: MindMapNode) => void;
  private nodeUpdatedCallback?: (update: Partial<MindMapNode> & { nodeId: string }) => void;
  private nodeDeletedCallback?: (nodeId: string) => void;
  private edgeCreatedCallback?: (edge: MindMapEdge) => void;
  private edgeDeletedCallback?: (edgeId: string) => void;

  onMindmapState(callback: (state: MindMapState) => void) {
    this.stateCallback = callback;
  }

  onUserJoined(callback: (userId: string) => void) {
    this.userJoinedCallback = callback;
  }

  onUserLeft(callback: (userId: string) => void) {
    this.userLeftCallback = callback;
  }

  onNodeCreated(callback: (node: MindMapNode) => void) {
    this.nodeCreatedCallback = callback;
  }

  onNodeUpdated(callback: (update: Partial<MindMapNode> & { nodeId: string }) => void) {
    this.nodeUpdatedCallback = callback;
  }

  onNodeDeleted(callback: (nodeId: string) => void) {
    this.nodeDeletedCallback = callback;
  }

  onEdgeCreated(callback: (edge: MindMapEdge) => void) {
    this.edgeCreatedCallback = callback;
  }

  onEdgeDeleted(callback: (edgeId: string) => void) {
    this.edgeDeletedCallback = callback;
  }

  private setupEventListeners() {
    if (!this.socket) return;

    this.socket.on('mindmap_state', (state: MindMapState) => {
      console.log('Received mindmap state:', state);
      this.stateCallback?.(state);
    });

    this.socket.on('user_joined', (data: { userId: string; timestamp: string }) => {
      console.log('User joined:', data);
      this.userJoinedCallback?.(data.userId);
    });

    this.socket.on('user_left', (data: { userId: string; timestamp: string }) => {
      console.log('User left:', data);
      this.userLeftCallback?.(data.userId);
    });

    this.socket.on('node_created', (node: MindMapNode) => {
      console.log('Node created:', node);
      this.nodeCreatedCallback?.(node);
    });

    this.socket.on('node_updated', (update: Partial<MindMapNode> & { nodeId: string }) => {
      console.log('Node updated:', update);
      this.nodeUpdatedCallback?.(update);
    });

    this.socket.on('node_deleted', (data: { nodeId: string }) => {
      console.log('Node deleted:', data);
      this.nodeDeletedCallback?.(data.nodeId);
    });

    this.socket.on('edge_created', (edge: MindMapEdge) => {
      console.log('Edge created:', edge);
      this.edgeCreatedCallback?.(edge);
    });

    this.socket.on('edge_deleted', (data: { edgeId: string }) => {
      console.log('Edge deleted:', data);
      this.edgeDeletedCallback?.(data.edgeId);
    });
  }

  joinMindmap(mindmapId: string, userId: string) {
    if (!this.socket) return;
    this.mindmapId = mindmapId;
    this.userId = userId;
    this.socket.emit('join_mindmap', { mindmapId, userId });
  }

  leaveMindmap() {
    if (!this.socket || !this.mindmapId || !this.userId) return;
    this.socket.emit('leave_mindmap', { mindmapId: this.mindmapId, userId: this.userId });
    this.mindmapId = null;
    this.userId = null;
  }

  addNode(label: string, position: { x: number; y: number }) {
    if (!this.socket || !this.mindmapId || !this.userId) return;
    this.socket.emit('node_added', {
      mindmapId: this.mindmapId,
      userId: this.userId,
      label,
      position
    });
  }

  updateNode(nodeId: string, updates: Partial<{ label: string; position: { x: number; y: number } }>) {
    if (!this.socket || !this.mindmapId || !this.userId) return;
    this.socket.emit('node_updated', {
      mindmapId: this.mindmapId,
      userId: this.userId,
      nodeId,
      ...updates
    });
  }

  deleteNode(nodeId: string) {
    if (!this.socket || !this.mindmapId || !this.userId) return;
    this.socket.emit('node_deleted', {
      mindmapId: this.mindmapId,
      userId: this.userId,
      nodeId
    });
  }

  addEdge(sourceId: string, targetId: string) {
    if (!this.socket || !this.mindmapId || !this.userId) return;
    this.socket.emit('edge_added', {
      mindmapId: this.mindmapId,
      userId: this.userId,
      sourceId,
      targetId
    });
  }

  deleteEdge(edgeId: string) {
    if (!this.socket || !this.mindmapId || !this.userId) return;
    this.socket.emit('edge_deleted', {
      mindmapId: this.mindmapId,
      userId: this.userId,
      edgeId
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }
}

export const websocketService = new WebSocketService();
