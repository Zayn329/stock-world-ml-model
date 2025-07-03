from fastapi import WebSocket
from typing import Dict, List
import json
import asyncio
import structlog

logger = structlog.get_logger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, List[str]] = {}  # client_id -> [topics]
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = []
        logger.info("WebSocket client connected", client_id=client_id)
    
    def disconnect(self, client_id: str):
        """Disconnect a WebSocket client"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.subscriptions:
            del self.subscriptions[client_id]
        logger.info("WebSocket client disconnected", client_id=client_id)
    
    async def send_personal_message(self, message: str, client_id: str):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception as e:
                logger.error("Failed to send message to client", 
                           client_id=client_id, error=str(e))
                self.disconnect(client_id)
    
    async def send_json_to_client(self, data: dict, client_id: str):
        """Send JSON data to a specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(data)
            except Exception as e:
                logger.error("Failed to send JSON to client", 
                           client_id=client_id, error=str(e))
                self.disconnect(client_id)
    
    async def broadcast_message(self, message: str):
        """Broadcast a message to all connected clients"""
        disconnected_clients = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error("Failed to broadcast to client", 
                           client_id=client_id, error=str(e))
                disconnected_clients.append(client_id)
        
        # Remove disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def broadcast_json(self, data: dict):
        """Broadcast JSON data to all connected clients"""
        disconnected_clients = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.error("Failed to broadcast JSON to client", 
                           client_id=client_id, error=str(e))
                disconnected_clients.append(client_id)
        
        # Remove disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    def subscribe_to_topic(self, client_id: str, topic: str):
        """Subscribe a client to a topic"""
        if client_id in self.subscriptions:
            if topic not in self.subscriptions[client_id]:
                self.subscriptions[client_id].append(topic)
                logger.info("Client subscribed to topic", 
                          client_id=client_id, topic=topic)
    
    def unsubscribe_from_topic(self, client_id: str, topic: str):
        """Unsubscribe a client from a topic"""
        if client_id in self.subscriptions:
            if topic in self.subscriptions[client_id]:
                self.subscriptions[client_id].remove(topic)
                logger.info("Client unsubscribed from topic", 
                          client_id=client_id, topic=topic)
    
    async def broadcast_to_topic(self, topic: str, data: dict):
        """Broadcast data to all clients subscribed to a topic"""
        disconnected_clients = []
        for client_id, topics in self.subscriptions.items():
            if topic in topics and client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_json({
                        "topic": topic,
                        "data": data
                    })
                except Exception as e:
                    logger.error("Failed to send topic message", 
                               client_id=client_id, topic=topic, error=str(e))
                    disconnected_clients.append(client_id)
        
        # Remove disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)
    
    def get_topic_subscribers(self, topic: str) -> List[str]:
        """Get list of clients subscribed to a topic"""
        return [client_id for client_id, topics in self.subscriptions.items() 
                if topic in topics]