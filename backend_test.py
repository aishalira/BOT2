#!/usr/bin/env python3
"""
Comprehensive Backend Test Suite for Tibia Bot Indetectável v2.0
Tests all API endpoints, bot functionality, and system integration
"""

import asyncio
import json
import time
import uuid
import requests
import websocket
from datetime import datetime
from typing import Dict, List, Any
import threading
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class TibiaBotTester:
    """Comprehensive test suite for Tibia Bot backend"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 30
        self.test_results = []
        self.websocket_messages = []
        self.websocket_connected = False
        
    def log_test(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}: {message}")
        
        if details:
            for key, value in details.items():
                print(f"    {key}: {value}")
    
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/health")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check",
                    True,
                    "Health endpoint responding correctly",
                    {
                        "status_code": response.status_code,
                        "response": data
                    }
                )
                return True
            else:
                self.log_test(
                    "Health Check",
                    False,
                    f"Health endpoint returned status {response.status_code}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Health Check",
                False,
                f"Health endpoint failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_bot_config_get(self):
        """Test getting bot configuration"""
        try:
            response = self.session.get(f"{API_BASE}/bot/config")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Get Bot Config",
                    True,
                    "Successfully retrieved bot configuration",
                    {
                        "status_code": response.status_code,
                        "has_default_config": "default_config" in data
                    }
                )
                return True, data
            else:
                self.log_test(
                    "Get Bot Config",
                    False,
                    f"Failed to get config, status: {response.status_code}",
                    {"status_code": response.status_code}
                )
                return False, None
                
        except Exception as e:
            self.log_test(
                "Get Bot Config",
                False,
                f"Get config failed: {str(e)}",
                {"error": str(e)}
            )
            return False, None
    
    def test_bot_config_save(self):
        """Test saving bot configuration"""
        try:
            # Create test configuration
            test_config = {
                "name": "Configuração de Teste",
                "auto_heal": True,
                "auto_food": True,
                "auto_attack": True,
                "auto_walk": False,
                "auto_loot": True,
                "heal_spell": "exura",
                "heal_at_hp": 70,
                "heal_mana_spell": "exura gran",
                "heal_at_mp": 50,
                "attack_spell": "exori",
                "food_type": "ham",
                "food_at": 90,
                "food_hotkey": "F1",
                "waypoints": [
                    {"name": "Ponto 1", "x": 1000, "y": 1000, "description": "Ponto inicial"},
                    {"name": "Ponto 2", "x": 1050, "y": 1050, "description": "Ponto de caça"}
                ],
                "waypoint_mode": "loop",
                "waypoint_delay": 1000,
                "target_creatures": ["rat", "rotworm", "cyclops"],
                "loot_items": ["gold coin", "platinum coin", "crystal coin"],
                "discard_items": ["leather armor", "studded armor"],
                "loot_all_and_filter": True,
                "loot_range": 3,
                "anti_idle": True,
                "emergency_logout_hp": 10,
                "enabled": False
            }
            
            response = self.session.post(f"{API_BASE}/bot/config", json=test_config)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Save Bot Config",
                    True,
                    "Successfully saved bot configuration",
                    {
                        "status_code": response.status_code,
                        "config_id": data.get("config_id"),
                        "message": data.get("message")
                    }
                )
                return True, data.get("config_id")
            else:
                self.log_test(
                    "Save Bot Config",
                    False,
                    f"Failed to save config, status: {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                return False, None
                
        except Exception as e:
            self.log_test(
                "Save Bot Config",
                False,
                f"Save config failed: {str(e)}",
                {"error": str(e)}
            )
            return False, None
    
    def test_bot_status(self):
        """Test bot status endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/bot/status")
            
            if response.status_code == 200:
                data = response.json()
                status_data = data.get("data", {})
                
                # Verify required fields
                required_fields = ["is_running", "is_paused", "session_id", "stats", "game_state"]
                missing_fields = [field for field in required_fields if field not in status_data]
                
                if not missing_fields:
                    self.log_test(
                        "Bot Status",
                        True,
                        "Bot status endpoint working correctly",
                        {
                            "status_code": response.status_code,
                            "is_running": status_data.get("is_running"),
                            "is_paused": status_data.get("is_paused"),
                            "session_id": status_data.get("session_id")
                        }
                    )
                    return True, status_data
                else:
                    self.log_test(
                        "Bot Status",
                        False,
                        f"Missing required fields: {missing_fields}",
                        {"missing_fields": missing_fields}
                    )
                    return False, None
            else:
                self.log_test(
                    "Bot Status",
                    False,
                    f"Status endpoint returned {response.status_code}",
                    {"status_code": response.status_code}
                )
                return False, None
                
        except Exception as e:
            self.log_test(
                "Bot Status",
                False,
                f"Status check failed: {str(e)}",
                {"error": str(e)}
            )
            return False, None
    
    def test_bot_start(self):
        """Test starting the bot"""
        try:
            response = self.session.post(f"{API_BASE}/bot/start")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Start Bot",
                    True,
                    "Bot started successfully",
                    {
                        "status_code": response.status_code,
                        "session_id": data.get("session_id"),
                        "is_running": data.get("is_running"),
                        "message": data.get("message")
                    }
                )
                return True, data.get("session_id")
            else:
                # Bot might already be running or config missing
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                self.log_test(
                    "Start Bot",
                    response.status_code in [200, 400],  # 400 might be expected if already running
                    f"Bot start response: {data.get('message', response.text)}",
                    {
                        "status_code": response.status_code,
                        "response": data
                    }
                )
                return response.status_code == 200, data.get("session_id")
                
        except Exception as e:
            self.log_test(
                "Start Bot",
                False,
                f"Start bot failed: {str(e)}",
                {"error": str(e)}
            )
            return False, None
    
    def test_bot_pause(self):
        """Test pausing/resuming the bot"""
        try:
            response = self.session.post(f"{API_BASE}/bot/pause")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Pause/Resume Bot",
                    True,
                    f"Bot pause/resume successful: {data.get('message')}",
                    {
                        "status_code": response.status_code,
                        "is_paused": data.get("is_paused"),
                        "is_running": data.get("is_running")
                    }
                )
                return True
            else:
                self.log_test(
                    "Pause/Resume Bot",
                    False,
                    f"Pause failed with status {response.status_code}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Pause/Resume Bot",
                False,
                f"Pause operation failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_bot_stop(self):
        """Test stopping the bot"""
        try:
            response = self.session.post(f"{API_BASE}/bot/stop")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Stop Bot",
                    True,
                    "Bot stopped successfully",
                    {
                        "status_code": response.status_code,
                        "is_running": data.get("is_running"),
                        "message": data.get("message")
                    }
                )
                return True
            else:
                self.log_test(
                    "Stop Bot",
                    False,
                    f"Stop failed with status {response.status_code}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Stop Bot",
                False,
                f"Stop operation failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_current_position(self):
        """Test getting current position"""
        try:
            response = self.session.get(f"{API_BASE}/bot/current-position")
            
            if response.status_code == 200:
                data = response.json()
                position_data = data.get("data", {})
                
                if "x" in position_data and "y" in position_data:
                    self.log_test(
                        "Current Position",
                        True,
                        "Position retrieved successfully",
                        {
                            "status_code": response.status_code,
                            "x": position_data.get("x"),
                            "y": position_data.get("y"),
                            "message": position_data.get("message")
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Current Position",
                        False,
                        "Position data missing x or y coordinates",
                        {"response": data}
                    )
                    return False
            else:
                self.log_test(
                    "Current Position",
                    False,
                    f"Position request failed with status {response.status_code}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Current Position",
                False,
                f"Position request failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_waypoint_management(self):
        """Test waypoint addition and deletion"""
        try:
            # Test adding waypoint
            test_waypoint = {
                "name": "Ponto de Teste",
                "x": 1100,
                "y": 1100,
                "description": "Waypoint criado durante teste"
            }
            
            response = self.session.post(f"{API_BASE}/bot/waypoint", json=test_waypoint)
            
            if response.status_code == 200:
                data = response.json()
                waypoint_id = data.get("waypoint", {}).get("id")
                
                self.log_test(
                    "Add Waypoint",
                    True,
                    "Waypoint added successfully",
                    {
                        "status_code": response.status_code,
                        "waypoint_id": waypoint_id,
                        "total_waypoints": data.get("total_waypoints")
                    }
                )
                
                # Test deleting waypoint if we got an ID
                if waypoint_id:
                    delete_response = self.session.delete(f"{API_BASE}/bot/waypoint/{waypoint_id}")
                    
                    if delete_response.status_code == 200:
                        delete_data = delete_response.json()
                        self.log_test(
                            "Delete Waypoint",
                            True,
                            "Waypoint deleted successfully",
                            {
                                "status_code": delete_response.status_code,
                                "remaining_waypoints": delete_data.get("remaining_waypoints")
                            }
                        )
                        return True
                    else:
                        self.log_test(
                            "Delete Waypoint",
                            False,
                            f"Delete failed with status {delete_response.status_code}",
                            {"status_code": delete_response.status_code}
                        )
                        return False
                else:
                    self.log_test(
                        "Delete Waypoint",
                        False,
                        "No waypoint ID returned from add operation",
                        {}
                    )
                    return False
            else:
                self.log_test(
                    "Add Waypoint",
                    False,
                    f"Add waypoint failed with status {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Waypoint Management",
                False,
                f"Waypoint operations failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_bot_sessions(self):
        """Test getting bot session history"""
        try:
            response = self.session.get(f"{API_BASE}/bot/sessions")
            
            if response.status_code == 200:
                data = response.json()
                sessions = data.get("sessions", [])
                
                self.log_test(
                    "Bot Sessions",
                    True,
                    "Session history retrieved successfully",
                    {
                        "status_code": response.status_code,
                        "total_sessions": data.get("total"),
                        "sessions_count": len(sessions)
                    }
                )
                return True
            else:
                self.log_test(
                    "Bot Sessions",
                    False,
                    f"Sessions request failed with status {response.status_code}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Bot Sessions",
                False,
                f"Sessions request failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_bot_statistics(self):
        """Test getting bot statistics"""
        try:
            response = self.session.get(f"{API_BASE}/bot/statistics")
            
            if response.status_code == 200:
                data = response.json()
                current_stats = data.get("current_session", {})
                historical_stats = data.get("historical", {})
                
                self.log_test(
                    "Bot Statistics",
                    True,
                    "Statistics retrieved successfully",
                    {
                        "status_code": response.status_code,
                        "has_current_session": bool(current_stats),
                        "has_historical": bool(historical_stats)
                    }
                )
                return True
            else:
                self.log_test(
                    "Bot Statistics",
                    False,
                    f"Statistics request failed with status {response.status_code}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Bot Statistics",
                False,
                f"Statistics request failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_bot_commands(self):
        """Test bot command endpoint"""
        try:
            # Test get_position command
            command = {"command": "get_position"}
            response = self.session.post(f"{API_BASE}/bot/command", json=command)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Bot Commands - Get Position",
                    True,
                    "Get position command executed successfully",
                    {
                        "status_code": response.status_code,
                        "message": data.get("message"),
                        "has_data": "data" in data
                    }
                )
                
                # Test reset_stats command
                reset_command = {"command": "reset_stats"}
                reset_response = self.session.post(f"{API_BASE}/bot/command", json=reset_command)
                
                if reset_response.status_code == 200:
                    reset_data = reset_response.json()
                    self.log_test(
                        "Bot Commands - Reset Stats",
                        True,
                        "Reset stats command executed successfully",
                        {
                            "status_code": reset_response.status_code,
                            "message": reset_data.get("message")
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Bot Commands - Reset Stats",
                        False,
                        f"Reset stats failed with status {reset_response.status_code}",
                        {"status_code": reset_response.status_code}
                    )
                    return False
            else:
                self.log_test(
                    "Bot Commands - Get Position",
                    False,
                    f"Command failed with status {response.status_code}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Bot Commands",
                False,
                f"Command execution failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def on_websocket_message(self, ws, message):
        """Handle WebSocket messages"""
        try:
            data = json.loads(message)
            self.websocket_messages.append(data)
            print(f"WebSocket message received: {data.get('type', 'unknown')}")
        except Exception as e:
            print(f"Error parsing WebSocket message: {e}")
    
    def on_websocket_error(self, ws, error):
        """Handle WebSocket errors"""
        print(f"WebSocket error: {error}")
    
    def on_websocket_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        self.websocket_connected = False
        print("WebSocket connection closed")
    
    def on_websocket_open(self, ws):
        """Handle WebSocket open"""
        self.websocket_connected = True
        print("WebSocket connection opened")
        
        # Send ping message
        ws.send(json.dumps({"type": "ping"}))
        
        # Request status
        ws.send(json.dumps({"type": "get_status"}))
    
    def test_websocket_connection(self):
        """Test WebSocket real-time communication"""
        try:
            # Convert HTTP URL to WebSocket URL
            ws_url = BACKEND_URL.replace('http://', 'ws://').replace('https://', 'wss://')
            ws_url = f"{ws_url}/api/bot/ws"
            
            print(f"Connecting to WebSocket: {ws_url}")
            
            # Create WebSocket connection
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=self.on_websocket_message,
                on_error=self.on_websocket_error,
                on_close=self.on_websocket_close,
                on_open=self.on_websocket_open
            )
            
            # Run WebSocket in a separate thread
            ws_thread = threading.Thread(target=ws.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
            # Wait for connection and messages
            time.sleep(3)
            
            if self.websocket_connected and self.websocket_messages:
                self.log_test(
                    "WebSocket Connection",
                    True,
                    "WebSocket connection and messaging working",
                    {
                        "connected": self.websocket_connected,
                        "messages_received": len(self.websocket_messages),
                        "message_types": [msg.get('type') for msg in self.websocket_messages]
                    }
                )
                return True
            else:
                self.log_test(
                    "WebSocket Connection",
                    False,
                    "WebSocket connection failed or no messages received",
                    {
                        "connected": self.websocket_connected,
                        "messages_received": len(self.websocket_messages)
                    }
                )
                return False
                
        except Exception as e:
            self.log_test(
                "WebSocket Connection",
                False,
                f"WebSocket test failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_tibia_bot_core(self):
        """Test core TibiaBot functionality"""
        try:
            # Import and test TibiaBot classes
            import sys
            sys.path.append('/app/backend')
            
            from tibia_bot import TibiaBot, TibiaDetector, TibiaAutomation
            
            # Test TibiaBot instantiation
            bot = TibiaBot()
            
            # Test basic methods
            status = bot.get_status()
            position = bot.get_current_position()
            
            # Test detector
            detector = TibiaDetector()
            screenshot = detector.capture_screen()
            
            # Test automation
            automation = TibiaAutomation()
            
            self.log_test(
                "TibiaBot Core Classes",
                True,
                "Core bot classes instantiated and basic methods working",
                {
                    "bot_created": bot is not None,
                    "status_method": status is not None,
                    "position_method": position is not None,
                    "detector_created": detector is not None,
                    "screenshot_captured": screenshot is not None,
                    "automation_created": automation is not None
                }
            )
            return True
            
        except Exception as e:
            self.log_test(
                "TibiaBot Core Classes",
                False,
                f"Core bot functionality test failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 80)
        print("TIBIA BOT INDETECTÁVEL v2.0 - BACKEND TEST SUITE")
        print("=" * 80)
        print(f"Testing backend at: {BACKEND_URL}")
        print(f"API base URL: {API_BASE}")
        print("=" * 80)
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("Bot Configuration (Get)", self.test_bot_config_get),
            ("Bot Configuration (Save)", self.test_bot_config_save),
            ("Bot Status", self.test_bot_status),
            ("Bot Start", self.test_bot_start),
            ("Bot Pause/Resume", self.test_bot_pause),
            ("Current Position", self.test_current_position),
            ("Waypoint Management", self.test_waypoint_management),
            ("Bot Sessions", self.test_bot_sessions),
            ("Bot Statistics", self.test_bot_statistics),
            ("Bot Commands", self.test_bot_commands),
            ("Bot Stop", self.test_bot_stop),
            ("WebSocket Connection", self.test_websocket_connection),
            ("TibiaBot Core", self.test_tibia_bot_core)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n--- Running: {test_name} ---")
            try:
                result = test_func()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL | {test_name}: Unexpected error - {str(e)}")
                failed += 1
            
            time.sleep(0.5)  # Brief pause between tests
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {passed + failed}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Backend is working correctly.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Check the details above.")
        
        print("=" * 80)
        
        return {
            "total": passed + failed,
            "passed": passed,
            "failed": failed,
            "success_rate": passed / (passed + failed) * 100,
            "results": self.test_results
        }

def main():
    """Main test execution"""
    tester = TibiaBotTester()
    results = tester.run_all_tests()
    
    # Save detailed results to file
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed test results saved to: /app/backend_test_results.json")
    
    return results["failed"] == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)