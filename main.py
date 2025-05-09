
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

    async def broadcast(self, message: str, exclude_client_id: str = None):
        for client_id, connection in self.active_connections.items():
            if client_id != exclude_client_id:
                await connection.send_text(message)

    def get_active_users(self):
        return list(self.active_connections.keys())


manager = ConnectionManager()


@app.get("/")
async def get():
    return {"message": "WebSocket Server is running"}


@app.get("/users")
async def get_users():
    return {"users": manager.get_active_users()}


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    user_message = json.dumps({
        "type": "user_joined",
        "user_id": client_id,
        "users": manager.get_active_users()
    })
    await manager.broadcast(user_message)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data["type"] == "chat":
                if "recipient_id" in message_data and message_data["recipient_id"]:
                    recipient_id = message_data["recipient_id"]
                    forward_message = json.dumps({
                        "type": "chat",
                        "sender_id": client_id,
                        "content": message_data["content"],
                        "timestamp": message_data.get("timestamp", "")
                    })
                    await manager.send_personal_message(forward_message, recipient_id)
                else:
                    broadcast_message = json.dumps({
                        "type": "chat",
                        "sender_id": client_id,
                        "content": message_data["content"],
                        "timestamp": message_data.get("timestamp", "")
                    })
                    await manager.broadcast(broadcast_message, client_id)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        user_left_message = json.dumps({
            "type": "user_left",
            "user_id": client_id,
            "users": manager.get_active_users()
        })
        await manager.broadcast(user_left_message)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)