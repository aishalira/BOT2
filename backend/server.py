import os
import asyncio
import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
import logging
from dotenv import load_dotenv

from tibia_bot import TibiaBot

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'tibia_bot_database')

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Initialize FastAPI
app = FastAPI(title="Tibia Bot Indetectável", version="2.0.0")
api_router = APIRouter(prefix="/api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class BotConfig(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    auto_heal: bool = True
    auto_food: bool = True
    auto_attack: bool = True
    auto_walk: bool = False
    auto_loot: bool = True
    heal_spell: str = "exura"
    heal_at_hp: int = 70
    heal_mana_spell: str = "exura gran"
    heal_at_mp: int = 50
    attack_spell: str = "exori"
    food_type: str = "ham"
    food_at: int = 90
    food_hotkey: str = "F1"
    waypoints: List[Dict[str, Any]] = []
    waypoint_mode: str = "loop"  # loop, back_and_forth, once
    waypoint_delay: int = 1000  # milliseconds between waypoints
    target_creatures: List[str] = ["rat", "rotworm", "cyclops"]
    loot_items: List[str] = ["gold coin", "platinum coin", "crystal coin"]
    discard_items: List[str] = ["leather armor", "studded armor", "chain armor"]
    loot_all_and_filter: bool = True  # True for free acc, False for premium
    loot_range: int = 3  # Squares from player
    anti_idle: bool = True
    emergency_logout_hp: int = 10
    enabled: bool = False

class BotStats(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    exp_gained: int = 0
    time_running: int = 0
    heals_used: int = 0
    food_used: int = 0
    attacks_made: int = 0
    creatures_killed: int = 0
    items_looted: int = 0
    items_discarded: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Waypoint(BaseModel):
    name: str
    x: int
    y: int
    description: Optional[str] = ""

class BotCommand(BaseModel):
    command: str
    data: Optional[Dict[str, Any]] = None

# Global bot instance
bot = TibiaBot()

# WebSocket endpoint
@api_router.websocket("/bot/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    bot.websocket_connections.add(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message.get("type") == "get_status":
                status = bot.get_status()
                await websocket.send_text(json.dumps({
                    "type": "status_update",
                    "data": status
                }))
                
    except WebSocketDisconnect:
        bot.websocket_connections.discard(websocket)

# API Routes
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@api_router.post("/bot/config")
async def save_bot_config(config: BotConfig):
    """Save bot configuration"""
    try:
        config.id = str(uuid.uuid4())
        config_dict = config.dict()
        
        # Save to database
        await db.bot_configs.insert_one(config_dict)
        
        # Update bot configuration
        bot.config = config
        
        logger.info(f"Bot configuration saved: {config.name}")
        
        return {
            "message": "Configuração salva com sucesso!",
            "config_id": config.id,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error saving bot config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bot/config")
async def get_bot_config():
    """Get latest bot configuration"""
    try:
        config = await db.bot_configs.find_one(sort=[("_id", -1)])
        if config:
            config.pop("_id", None)
            return config
        
        # Return default config if none found
        return {
            "message": "Nenhuma configuração encontrada",
            "default_config": BotConfig(name="Configuração Padrão").dict()
        }
        
    except Exception as e:
        logger.error(f"Error getting bot config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/bot/start")
async def start_bot():
    """Start the bot"""
    try:
        if bot.is_running:
            return {
                "message": "Bot já está rodando",
                "is_running": True,
                "session_id": bot.session_id
            }
        
        # Load config if not set
        if not bot.config:
            config_data = await db.bot_configs.find_one(sort=[("_id", -1)])
            if config_data:
                config_data.pop("_id", None)
                bot.config = BotConfig(**config_data)
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="Nenhuma configuração encontrada. Configure o bot primeiro."
                )
        
        # Start bot
        success = bot.start()
        
        if success:
            logger.info(f"Bot started successfully with session: {bot.session_id}")
            return {
                "message": "Bot iniciado com sucesso!",
                "session_id": bot.session_id,
                "is_running": True,
                "timestamp": datetime.utcnow()
            }
        else:
            raise HTTPException(status_code=500, detail="Falha ao iniciar o bot")
            
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/bot/stop")
async def stop_bot():
    """Stop the bot"""
    try:
        # Save session stats before stopping
        if bot.stats:
            stats_dict = bot.stats.copy()
            stats_dict['ended_at'] = datetime.utcnow()
            await db.bot_sessions.insert_one(stats_dict)
        
        # Stop bot
        bot.stop()
        
        logger.info("Bot stopped successfully")
        
        return {
            "message": "Bot parado com sucesso!",
            "is_running": False,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/bot/pause")
async def pause_bot():
    """Pause/resume the bot"""
    try:
        is_paused = bot.pause()
        
        status = "pausado" if is_paused else "retomado"
        logger.info(f"Bot {status}")
        
        return {
            "message": f"Bot {status} com sucesso!",
            "is_paused": is_paused,
            "is_running": bot.is_running,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error pausing bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bot/status")
async def get_bot_status():
    """Get current bot status"""
    try:
        status = bot.get_status()
        return {
            "status": "success",
            "data": status,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting bot status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bot/sessions")
async def get_bot_sessions():
    """Get bot session history"""
    try:
        sessions = []
        async for session in db.bot_sessions.find().sort("created_at", -1).limit(20):
            session.pop("_id", None)
            sessions.append(session)
        
        return {
            "sessions": sessions,
            "total": len(sessions),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting bot sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bot/current-position")
async def get_current_position():
    """Get current player position"""
    try:
        position = bot.get_current_position()
        return {
            "status": "success",
            "data": position,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting current position: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/bot/waypoint")
async def add_waypoint(waypoint: Waypoint):
    """Add a waypoint to the current configuration"""
    try:
        if not bot.config:
            raise HTTPException(
                status_code=400, 
                detail="Nenhuma configuração carregada"
            )
        
        # Add waypoint to current config
        waypoint_dict = waypoint.dict()
        waypoint_dict['id'] = str(uuid.uuid4())
        
        bot.config.waypoints.append(waypoint_dict)
        
        # Save updated config
        config_dict = bot.config.dict()
        await db.bot_configs.insert_one(config_dict)
        
        logger.info(f"Waypoint added: {waypoint.name} at ({waypoint.x}, {waypoint.y})")
        
        return {
            "message": "Waypoint adicionado com sucesso!",
            "waypoint": waypoint_dict,
            "total_waypoints": len(bot.config.waypoints),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error adding waypoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/bot/waypoint/{waypoint_id}")
async def delete_waypoint(waypoint_id: str):
    """Delete a waypoint"""
    try:
        if not bot.config:
            raise HTTPException(
                status_code=400, 
                detail="Nenhuma configuração carregada"
            )
        
        # Find and remove waypoint
        waypoints = bot.config.waypoints
        original_count = len(waypoints)
        
        bot.config.waypoints = [wp for wp in waypoints if wp.get('id') != waypoint_id]
        
        if len(bot.config.waypoints) == original_count:
            raise HTTPException(
                status_code=404, 
                detail="Waypoint não encontrado"
            )
        
        # Save updated config
        config_dict = bot.config.dict()
        await db.bot_configs.insert_one(config_dict)
        
        logger.info(f"Waypoint deleted: {waypoint_id}")
        
        return {
            "message": "Waypoint removido com sucesso!",
            "remaining_waypoints": len(bot.config.waypoints),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error deleting waypoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bot/statistics")
async def get_bot_statistics():
    """Get detailed bot statistics"""
    try:
        # Get current session stats
        current_stats = bot.stats
        
        # Get historical data
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_sessions": {"$sum": 1},
                    "total_time": {"$sum": "$time_running"},
                    "total_creatures": {"$sum": "$creatures_killed"},
                    "total_items": {"$sum": "$items_looted"},
                    "total_heals": {"$sum": "$heals_used"},
                    "total_attacks": {"$sum": "$attacks_made"}
                }
            }
        ]
        
        historical_stats = await db.bot_sessions.aggregate(pipeline).to_list(1)
        historical = historical_stats[0] if historical_stats else {}
        
        return {
            "current_session": current_stats,
            "historical": historical,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting bot statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/bot/command")
async def send_bot_command(command: BotCommand):
    """Send command to bot"""
    try:
        if command.command == "emergency_stop":
            bot.stop()
            return {"message": "Parada de emergência executada"}
        
        elif command.command == "reset_stats":
            bot.stats = {
                'session_id': bot.session_id,
                'exp_gained': 0,
                'time_running': 0,
                'heals_used': 0,
                'food_used': 0,
                'attacks_made': 0,
                'creatures_killed': 0,
                'items_looted': 0,
                'items_discarded': 0,
                'created_at': datetime.utcnow()
            }
            return {"message": "Estatísticas resetadas"}
        
        elif command.command == "get_position":
            position = bot.get_current_position()
            return {"message": "Posição obtida", "data": position}
        
        else:
            raise HTTPException(status_code=400, detail="Comando não reconhecido")
            
    except Exception as e:
        logger.error(f"Error executing bot command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)