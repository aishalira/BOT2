#!/usr/bin/env python3
"""
Simplified Backend Test for Tibia Bot - Focus on API endpoints
"""

import requests
import json
import time
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://654a1bcc-4f86-4793-bc65-07e3165a568e.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_api_endpoints():
    """Test all API endpoints"""
    session = requests.Session()
    session.timeout = 10
    results = []
    
    def log_test(name, success, message, details=None):
        result = {
            'test': name,
            'success': success,
            'message': message,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {name}: {message}")
        if details:
            for key, value in details.items():
                print(f"    {key}: {value}")
    
    print("=" * 60)
    print("TIBIA BOT BACKEND API TESTS")
    print("=" * 60)
    print(f"Testing: {API_BASE}")
    print("=" * 60)
    
    # Test 1: Health Check
    try:
        response = session.get(f"{API_BASE}/health")
        success = response.status_code == 200
        data = response.json() if success else {}
        log_test("Health Check", success, 
                "API health endpoint working" if success else f"Health check failed: {response.status_code}",
                {"status_code": response.status_code, "response": data})
    except Exception as e:
        log_test("Health Check", False, f"Health check error: {str(e)}")
    
    # Test 2: Get Bot Config
    try:
        response = session.get(f"{API_BASE}/bot/config")
        success = response.status_code == 200
        data = response.json() if success else {}
        log_test("Get Bot Config", success,
                "Bot config retrieval working" if success else f"Config get failed: {response.status_code}",
                {"status_code": response.status_code, "has_default": "default_config" in data})
    except Exception as e:
        log_test("Get Bot Config", False, f"Config get error: {str(e)}")
    
    # Test 3: Save Bot Config
    try:
        test_config = {
            "name": "Test Configuration",
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
            "waypoints": [],
            "waypoint_mode": "loop",
            "waypoint_delay": 1000,
            "target_creatures": ["rat", "rotworm"],
            "loot_items": ["gold coin", "platinum coin"],
            "discard_items": ["leather armor"],
            "loot_all_and_filter": True,
            "loot_range": 3,
            "anti_idle": True,
            "emergency_logout_hp": 10,
            "enabled": False
        }
        
        response = session.post(f"{API_BASE}/bot/config", json=test_config)
        success = response.status_code == 200
        data = response.json() if success else {}
        log_test("Save Bot Config", success,
                "Bot config save working" if success else f"Config save failed: {response.status_code}",
                {"status_code": response.status_code, "config_id": data.get("config_id")})
    except Exception as e:
        log_test("Save Bot Config", False, f"Config save error: {str(e)}")
    
    # Test 4: Bot Status
    try:
        response = session.get(f"{API_BASE}/bot/status")
        success = response.status_code == 200
        data = response.json() if success else {}
        status_data = data.get("data", {})
        log_test("Bot Status", success,
                "Bot status endpoint working" if success else f"Status failed: {response.status_code}",
                {"status_code": response.status_code, 
                 "is_running": status_data.get("is_running"),
                 "session_id": status_data.get("session_id")})
    except Exception as e:
        log_test("Bot Status", False, f"Status error: {str(e)}")
    
    # Test 5: Start Bot
    try:
        response = session.post(f"{API_BASE}/bot/start")
        success = response.status_code == 200
        data = response.json() if success else {}
        log_test("Start Bot", success,
                "Bot start working" if success else f"Start failed: {response.status_code}",
                {"status_code": response.status_code, 
                 "session_id": data.get("session_id"),
                 "message": data.get("message")})
    except Exception as e:
        log_test("Start Bot", False, f"Start error: {str(e)}")
    
    # Test 6: Pause Bot
    try:
        response = session.post(f"{API_BASE}/bot/pause")
        success = response.status_code == 200
        data = response.json() if success else {}
        log_test("Pause Bot", success,
                "Bot pause working" if success else f"Pause failed: {response.status_code}",
                {"status_code": response.status_code, 
                 "is_paused": data.get("is_paused")})
    except Exception as e:
        log_test("Pause Bot", False, f"Pause error: {str(e)}")
    
    # Test 7: Current Position
    try:
        response = session.get(f"{API_BASE}/bot/current-position")
        success = response.status_code == 200
        data = response.json() if success else {}
        position_data = data.get("data", {})
        log_test("Current Position", success,
                "Position endpoint working" if success else f"Position failed: {response.status_code}",
                {"status_code": response.status_code,
                 "x": position_data.get("x"),
                 "y": position_data.get("y")})
    except Exception as e:
        log_test("Current Position", False, f"Position error: {str(e)}")
    
    # Test 8: Add Waypoint
    try:
        waypoint = {
            "name": "Test Waypoint",
            "x": 1000,
            "y": 1000,
            "description": "Test waypoint"
        }
        response = session.post(f"{API_BASE}/bot/waypoint", json=waypoint)
        success = response.status_code == 200
        data = response.json() if success else {}
        waypoint_id = data.get("waypoint", {}).get("id") if success else None
        log_test("Add Waypoint", success,
                "Waypoint add working" if success else f"Add waypoint failed: {response.status_code}",
                {"status_code": response.status_code,
                 "waypoint_id": waypoint_id,
                 "total_waypoints": data.get("total_waypoints")})
        
        # Test 9: Delete Waypoint (if we got an ID)
        if success and waypoint_id:
            try:
                delete_response = session.delete(f"{API_BASE}/bot/waypoint/{waypoint_id}")
                delete_success = delete_response.status_code == 200
                delete_data = delete_response.json() if delete_success else {}
                log_test("Delete Waypoint", delete_success,
                        "Waypoint delete working" if delete_success else f"Delete waypoint failed: {delete_response.status_code}",
                        {"status_code": delete_response.status_code,
                         "remaining_waypoints": delete_data.get("remaining_waypoints")})
            except Exception as e:
                log_test("Delete Waypoint", False, f"Delete waypoint error: {str(e)}")
        else:
            log_test("Delete Waypoint", False, "Skipped - no waypoint ID from add test")
            
    except Exception as e:
        log_test("Add Waypoint", False, f"Add waypoint error: {str(e)}")
        log_test("Delete Waypoint", False, "Skipped - add waypoint failed")
    
    # Test 10: Bot Sessions
    try:
        response = session.get(f"{API_BASE}/bot/sessions")
        success = response.status_code == 200
        data = response.json() if success else {}
        log_test("Bot Sessions", success,
                "Sessions endpoint working" if success else f"Sessions failed: {response.status_code}",
                {"status_code": response.status_code,
                 "total": data.get("total"),
                 "sessions_count": len(data.get("sessions", []))})
    except Exception as e:
        log_test("Bot Sessions", False, f"Sessions error: {str(e)}")
    
    # Test 11: Bot Statistics
    try:
        response = session.get(f"{API_BASE}/bot/statistics")
        success = response.status_code == 200
        data = response.json() if success else {}
        log_test("Bot Statistics", success,
                "Statistics endpoint working" if success else f"Statistics failed: {response.status_code}",
                {"status_code": response.status_code,
                 "has_current_session": "current_session" in data,
                 "has_historical": "historical" in data})
    except Exception as e:
        log_test("Bot Statistics", False, f"Statistics error: {str(e)}")
    
    # Test 12: Bot Commands
    try:
        command = {"command": "get_position"}
        response = session.post(f"{API_BASE}/bot/command", json=command)
        success = response.status_code == 200
        data = response.json() if success else {}
        log_test("Bot Commands", success,
                "Commands endpoint working" if success else f"Commands failed: {response.status_code}",
                {"status_code": response.status_code,
                 "message": data.get("message")})
    except Exception as e:
        log_test("Bot Commands", False, f"Commands error: {str(e)}")
    
    # Test 13: Stop Bot
    try:
        response = session.post(f"{API_BASE}/bot/stop")
        success = response.status_code == 200
        data = response.json() if success else {}
        log_test("Stop Bot", success,
                "Bot stop working" if success else f"Stop failed: {response.status_code}",
                {"status_code": response.status_code,
                 "message": data.get("message")})
    except Exception as e:
        log_test("Stop Bot", False, f"Stop error: {str(e)}")
    
    # Test 14: Core Bot Classes
    try:
        import sys
        sys.path.append('/app/backend')
        from tibia_bot import TibiaBot, TibiaDetector, TibiaAutomation
        
        bot = TibiaBot()
        detector = TibiaDetector()
        automation = TibiaAutomation()
        
        # Test basic methods
        status = bot.get_status()
        position = bot.get_current_position()
        screenshot = detector.capture_screen()
        
        log_test("Core Bot Classes", True,
                "Core bot classes working correctly",
                {"bot_created": bot is not None,
                 "detector_created": detector is not None,
                 "automation_created": automation is not None,
                 "status_method": status is not None,
                 "position_method": position is not None,
                 "screenshot_method": screenshot is not None})
    except Exception as e:
        log_test("Core Bot Classes", False, f"Core classes error: {str(e)}")
    
    # Summary
    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed / len(results) * 100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Backend is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check details above.")
    
    print("=" * 60)
    
    # Save results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "success_rate": passed / len(results) * 100,
            "results": results
        }, f, indent=2, default=str)
    
    return failed == 0

if __name__ == "__main__":
    success = test_api_endpoints()
    exit(0 if success else 1)