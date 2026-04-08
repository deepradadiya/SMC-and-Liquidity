"""
WebSocket connection manager for real-time updates
"""

import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
import asyncio

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Store active connections by type
        self.connections: Dict[str, Set[WebSocket]] = {
            'signals': set(),
            'prices': set(),
            'alerts': set(),
            'general': set()
        }
        
    async def connect(self, websocket: WebSocket, connection_type: str = 'general'):
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        if connection_type not in self.connections:
            self.connections[connection_type] = set()
            
        self.connections[connection_type].add(websocket)
        logger.info(f"WebSocket connected: {connection_type} (total: {len(self.connections[connection_type])})")
        
    def disconnect(self, websocket: WebSocket, connection_type: str = 'general'):
        """Remove WebSocket connection"""
        if connection_type in self.connections:
            self.connections[connection_type].discard(websocket)
            logger.info(f"WebSocket disconnected: {connection_type} (total: {len(self.connections[connection_type])})")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_type(self, message: dict, connection_type: str):
        """Broadcast message to all connections of a specific type"""
        if connection_type not in self.connections:
            return
            
        disconnected = set()
        
        for websocket in self.connections[connection_type].copy():
            try:
                await websocket.send_text(json.dumps(message))
            except WebSocketDisconnect:
                disconnected.add(websocket)
            except Exception as e:
                logger.error(f"Error broadcasting to {connection_type}: {e}")
                disconnected.add(websocket)
        
        # Remove disconnected websockets
        for websocket in disconnected:
            self.connections[connection_type].discard(websocket)
    
    async def broadcast_signal(self, signal_data: dict):
        """Broadcast new trading signal"""
        message = {
            'type': 'signal',
            'data': signal_data,
            'timestamp': signal_data.get('timestamp')
        }
        await self.broadcast_to_type(message, 'signals')
        await self.broadcast_to_type(message, 'general')
    
    async def broadcast_price_update(self, price_data: dict):
        """Broadcast price update"""
        message = {
            'type': 'price_update',
            'data': price_data,
            'timestamp': price_data.get('timestamp')
        }
        await self.broadcast_to_type(message, 'prices')
        await self.broadcast_to_type(message, 'general')
    
    async def broadcast_alert(self, alert_data: dict):
        """Broadcast alert notification"""
        message = {
            'type': 'alert',
            'data': alert_data,
            'timestamp': alert_data.get('timestamp')
        }
        await self.broadcast_to_type(message, 'alerts')
        await self.broadcast_to_type(message, 'general')
    
    def get_connection_count(self, connection_type: str = None) -> int:
        """Get number of active connections"""
        if connection_type:
            return len(self.connections.get(connection_type, set()))
        else:
            return sum(len(conns) for conns in self.connections.values())
    
    def get_connection_stats(self) -> dict:
        """Get connection statistics"""
        return {
            connection_type: len(connections)
            for connection_type, connections in self.connections.items()
        }

# Global WebSocket manager instance
websocket_manager = WebSocketManager()