# main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import json

app = FastAPI()

# Cấu hình CORS để cho phép Angular frontend kết nối
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong môi trường production, hãy chỉ định chính xác origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Lưu trữ các kết nối websocket đang hoạt động
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

    # Thông báo cho tất cả người dùng về người dùng mới
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

            # Xác định loại tin nhắn
            if message_data["type"] == "chat":
                # Gửi tin nhắn đến người nhận cụ thể
                if "recipient_id" in message_data and message_data["recipient_id"]:
                    recipient_id = message_data["recipient_id"]
                    forward_message = json.dumps({
                        "type": "chat",
                        "sender_id": client_id,
                        "content": message_data["content"],
                        "timestamp": message_data.get("timestamp", "")
                    })
                    await manager.send_personal_message(forward_message, recipient_id)
                # Hoặc phát tán tin nhắn đến tất cả
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
        # Thông báo cho tất cả người dùng về người dùng rời đi
        user_left_message = json.dumps({
            "type": "user_left",
            "user_id": client_id,
            "users": manager.get_active_users()
        })
        await manager.broadcast(user_left_message)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)