from flask import Blueprint, current_app
from flask_socketio import SocketIO, join_room, leave_room
from flask_socketio import emit as socketio_emit
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from .utils.anonymization import hash_engineer_id

websocket_bp = Blueprint("websocket", __name__)
socketio = SocketIO()

def get_db():
    client = MongoClient(current_app.config["MONGODB_URI"])
    return client[current_app.config["MONGODB_DB"]]

def init_websocket(app):
    """Initialize WebSocket with Flask app"""
    socketio.init_app(app, cors_allowed_origins="*")
    
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')
    
    @socketio.on('join_mindmap')
    def handle_join_mindmap(data):
        """Handle client joining a mindmap room"""
        room = f"mindmap_{data['mindmapId']}"
        join_room(room)
        
        # Get current mindmap state
        db = get_db()
        nodes = list(db.mindmap_nodes.find({'mindmapId': data['mindmapId']}))
        edges = list(db.mindmap_edges.find({'mindmapId': data['mindmapId']}))
        
        # Convert ObjectId to string
        for node in nodes:
            node['_id'] = str(node['_id'])
        for edge in edges:
            edge['_id'] = str(edge['_id'])
            
        socketio_emit('mindmap_state', {
            'nodes': nodes,
            'edges': edges
        }, to=room)
        
        # Notify others
        socketio_emit('user_joined', {
            'userId': hash_engineer_id(data.get('userId', 'anonymous')),
            'timestamp': datetime.utcnow().isoformat()
        }, to=room)
    
    @socketio.on('leave_mindmap')
    def handle_leave_mindmap(data):
        """Handle client leaving a mindmap room"""
        room = f"mindmap_{data['mindmapId']}"
        leave_room(room)
        socketio_emit('user_left', {
            'userId': hash_engineer_id(data.get('userId', 'anonymous')),
            'timestamp': datetime.utcnow().isoformat()
        }, to=room)
    
    @socketio.on('node_added')
    def handle_node_added(data):
        """Handle new node creation"""
        db = get_db()
        room = f"mindmap_{data['mindmapId']}"
        
        node = {
            'mindmapId': data['mindmapId'],
            'label': data['label'],
            'position': data['position'],
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'createdBy': hash_engineer_id(data.get('userId', 'anonymous'))
        }
        
        result = db.mindmap_nodes.insert_one(node)
        node['_id'] = str(result.inserted_id)
        
        socketio_emit('node_created', node, to=room)
    
    @socketio.on('node_updated')
    def handle_node_updated(data):
        """Handle node updates"""
        db = get_db()
        room = f"mindmap_{data['mindmapId']}"
        
        node_id = ObjectId(data['nodeId'])
        updates = {
            'label': data.get('label'),
            'position': data.get('position'),
            'updatedAt': datetime.utcnow(),
            'updatedBy': hash_engineer_id(data.get('userId', 'anonymous'))
        }
        
        # Remove None values
        updates = {k: v for k, v in updates.items() if v is not None}
        
        db.mindmap_nodes.update_one(
            {'_id': node_id},
            {'$set': updates}
        )
        
        socketio_emit('node_updated', {
            'nodeId': str(node_id),
            **updates
        }, to=room)
    
    @socketio.on('node_deleted')
    def handle_node_deleted(data):
        """Handle node deletion"""
        db = get_db()
        room = f"mindmap_{data['mindmapId']}"
        
        node_id = ObjectId(data['nodeId'])
        db.mindmap_nodes.delete_one({'_id': node_id})
        
        # Delete associated edges
        db.mindmap_edges.delete_many({
            '$or': [
                {'sourceId': str(node_id)},
                {'targetId': str(node_id)}
            ]
        })
        
        socketio_emit('node_deleted', {
            'nodeId': str(node_id)
        }, to=room)
    
    @socketio.on('edge_added')
    def handle_edge_added(data):
        """Handle new edge creation"""
        db = get_db()
        room = f"mindmap_{data['mindmapId']}"
        
        edge = {
            'mindmapId': data['mindmapId'],
            'sourceId': data['sourceId'],
            'targetId': data['targetId'],
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
            'createdBy': hash_engineer_id(data.get('userId', 'anonymous'))
        }
        
        result = db.mindmap_edges.insert_one(edge)
        edge['_id'] = str(result.inserted_id)
        
        socketio_emit('edge_created', edge, to=room)
    
    @socketio.on('edge_deleted')
    def handle_edge_deleted(data):
        """Handle edge deletion"""
        db = get_db()
        room = f"mindmap_{data['mindmapId']}"
        
        edge_id = ObjectId(data['edgeId'])
        db.mindmap_edges.delete_one({'_id': edge_id})
        
        socketio_emit('edge_deleted', {
            'edgeId': str(edge_id)
        }, to=room)
    
    return socketio
