import os
import asyncio
import threading
import time
import random
import uuid
import json
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance
import psutil
from scipy import interpolate
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set environment for headless operation
os.environ.setdefault('DISPLAY', ':0')

# Mock classes for headless environment
class MockPyAutoGUI:
    FAILSAFE = False
    PAUSE = 0.01
    
    def screenshot(self):
        return Image.new('RGB', (1920, 1080), color='black')
    
    def position(self):
        return (500, 500)
    
    def moveTo(self, x, y):
        pass
    
    def click(self):
        pass
    
    def rightClick(self):
        pass
    
    def press(self, key):
        pass
    
    def hotkey(self, *keys):
        pass

class MockCV2:
    COLOR_RGB2BGR = 4
    COLOR_BGR2GRAY = 6
    COLOR_BGRA2BGR = 3
    
    def cvtColor(self, img, code):
        if len(img.shape) == 3:
            return np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
        return img
    
    def inRange(self, img, lower, upper):
        return np.zeros(img.shape[:2], dtype=np.uint8)
    
    def countNonZero(self, mask):
        return random.randint(0, 1000)

class MockPytesseract:
    def image_to_string(self, image, config=''):
        return f"{random.randint(50, 100)}/{random.randint(100, 150)}"

class MockMSS:
    def grab(self, monitor):
        return np.zeros((monitor['height'], monitor['width'], 4), dtype=np.uint8)

class MockMSSInstance:
    def __init__(self):
        pass

# Try to import real libraries, fall back to mocks
try:
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.01
except Exception as e:
    logger.warning(f"PyAutoGUI not available, using mock: {e}")
    pyautogui = MockPyAutoGUI()

try:
    import cv2
except ImportError:
    logger.warning("OpenCV not available, using mock")
    cv2 = MockCV2()

try:
    import pytesseract
except ImportError:
    logger.warning("Pytesseract not available, using mock")
    pytesseract = MockPytesseract()

try:
    import mss
except ImportError:
    logger.warning("MSS not available, using mock")
    mss = MockMSSInstance()

try:
    from pynput import mouse, keyboard
except Exception as e:
    logger.warning(f"Pynput not available, using mock: {e}")
    class MockPynput:
        class mouse:
            Button = type('Button', (), {'left': 1, 'right': 2})()
            Listener = lambda **kwargs: None
        
        class keyboard:
            Key = type('Key', (), {'space': 'space', 'ctrl': 'ctrl'})()
            Listener = lambda **kwargs: None
    
    mouse = MockPynput.mouse
    keyboard = MockPynput.keyboard

@dataclass
class GameState:
    """Represents current game state"""
    hp_current: int = 100
    hp_max: int = 100
    hp_percent: float = 100.0
    mp_current: int = 100
    mp_max: int = 100
    mp_percent: float = 100.0
    player_x: int = 0
    player_y: int = 0
    is_alive: bool = True
    target_creature: Optional[str] = None

@dataclass
class Creature:
    """Represents a detected creature"""
    name: str
    x: int
    y: int
    distance: int
    health: int = 100

@dataclass
class LootItem:
    """Represents a loot item"""
    name: str
    x: int
    y: int
    value: int = 0
    keep: bool = True

class TibiaDetector:
    """Handles all Tibia game detection and screen analysis"""
    
    def __init__(self):
        try:
            self.sct = mss.mss() if hasattr(mss, 'mss') else None
        except:
            self.sct = None
        
        self.tibia_window = None
        self.game_area = None
        self.last_screenshot = None
        self.hp_area = None
        self.mp_area = None
        self.chat_area = None
        
        # Color thresholds for different game elements
        self.hp_color_ranges = {
            'green': ([40, 40, 40], [80, 255, 255]),  # HSV for HP bar
            'red': ([0, 50, 50], [10, 255, 255])     # HSV for low HP
        }
        
        self.creature_templates = {}
        self.loot_templates = {}
        self.load_templates()
    
    def load_templates(self):
        """Load creature and item templates for recognition"""
        # In a real implementation, these would be loaded from template files
        # For now, we'll use placeholder data
        self.creature_templates = {
            'rat': {'color': (139, 69, 19), 'size': (16, 16)},
            'rotworm': {'color': (165, 42, 42), 'size': (32, 32)},
            'cyclops': {'color': (0, 100, 0), 'size': (64, 64)},
            'dragon': {'color': (255, 0, 0), 'size': (64, 64)},
            'demon': {'color': (128, 0, 128), 'size': (64, 64)}
        }
        
        self.loot_templates = {
            'gold coin': {'color': (255, 215, 0), 'value': 1},
            'platinum coin': {'color': (229, 228, 226), 'value': 100},
            'crystal coin': {'color': (0, 255, 255), 'value': 10000},
            'small ruby': {'color': (255, 0, 0), 'value': 250},
            'small emerald': {'color': (0, 255, 0), 'value': 250},
            'small sapphire': {'color': (0, 0, 255), 'value': 250}
        }
    
    def find_tibia_window(self) -> Optional[Dict]:
        """Find the Tibia game window"""
        try:
            # Try to find Tibia client window
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    name = proc.info['name'].lower()
                    if 'tibia' in name or 'otclient' in name:
                        # In a real implementation, you'd get window coordinates
                        # For now, we'll use screen coordinates
                        return {
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'left': 100,
                            'top': 100,
                            'width': 1200,
                            'height': 800
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            logger.warning("Tibia window not found, using full screen")
            return {
                'pid': 0,
                'name': 'Full Screen',
                'left': 0,
                'top': 0,
                'width': 1920,
                'height': 1080
            }
            
        except Exception as e:
            logger.error(f"Error finding Tibia window: {e}")
            return None
    
    def capture_screen(self) -> Optional[np.ndarray]:
        """Capture the current screen/game area"""
        try:
            if not self.tibia_window:
                self.tibia_window = self.find_tibia_window()
            
            if not self.tibia_window:
                return None
            
            # If mss is available, use it
            if self.sct:
                # Capture the screen area
                monitor = {
                    'left': self.tibia_window['left'],
                    'top': self.tibia_window['top'],
                    'width': self.tibia_window['width'],
                    'height': self.tibia_window['height']
                }
                
                screenshot = self.sct.grab(monitor)
                img = np.array(screenshot)
                
                # Convert BGRA to BGR
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                self.last_screenshot = img
                
                return img
            else:
                # Use pyautogui as fallback
                screenshot = pyautogui.screenshot()
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                self.last_screenshot = img
                return img
            
        except Exception as e:
            logger.error(f"Error capturing screen: {e}")
            # Return a mock screenshot for testing
            return np.zeros((600, 800, 3), dtype=np.uint8)
    
    def detect_hp_mp(self, screenshot: np.ndarray) -> GameState:
        """Detect HP and MP from screenshot using OCR and color analysis"""
        try:
            game_state = GameState()
            
            # Define HP/MP bar areas (these would be calibrated for actual Tibia client)
            hp_area = screenshot[20:40, 150:300]  # Example coordinates
            mp_area = screenshot[45:65, 150:300]  # Example coordinates
            
            # Use OCR to read HP/MP text
            hp_text = pytesseract.image_to_string(hp_area, config='--psm 8 -c tessedit_char_whitelist=0123456789/')
            mp_text = pytesseract.image_to_string(mp_area, config='--psm 8 -c tessedit_char_whitelist=0123456789/')
            
            # Parse HP
            if '/' in hp_text:
                hp_parts = hp_text.split('/')
                if len(hp_parts) >= 2:
                    game_state.hp_current = int(hp_parts[0].strip())
                    game_state.hp_max = int(hp_parts[1].strip())
                    game_state.hp_percent = (game_state.hp_current / game_state.hp_max) * 100
            
            # Parse MP
            if '/' in mp_text:
                mp_parts = mp_text.split('/')
                if len(mp_parts) >= 2:
                    game_state.mp_current = int(mp_parts[0].strip())
                    game_state.mp_max = int(mp_parts[1].strip())
                    game_state.mp_percent = (game_state.mp_current / game_state.mp_max) * 100
            
            # If OCR fails, use color analysis as fallback
            if game_state.hp_percent == 100.0:
                game_state.hp_percent = self.analyze_hp_bar_color(hp_area)
            
            if game_state.mp_percent == 100.0:
                game_state.mp_percent = self.analyze_mp_bar_color(mp_area)
            
            game_state.is_alive = game_state.hp_percent > 0
            
            return game_state
            
        except Exception as e:
            logger.error(f"Error detecting HP/MP: {e}")
            return GameState()
    
    def analyze_hp_bar_color(self, hp_area: np.ndarray) -> float:
        """Analyze HP bar color to estimate HP percentage"""
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(hp_area, cv2.COLOR_BGR2HSV)
            
            # Count green pixels (healthy HP)
            green_mask = cv2.inRange(hsv, np.array([40, 40, 40]), np.array([80, 255, 255]))
            green_pixels = cv2.countNonZero(green_mask)
            
            # Count red pixels (low HP)
            red_mask = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
            red_pixels = cv2.countNonZero(red_mask)
            
            total_pixels = hp_area.shape[0] * hp_area.shape[1]
            
            if green_pixels > red_pixels:
                return (green_pixels / total_pixels) * 100
            else:
                return (red_pixels / total_pixels) * 100
                
        except Exception as e:
            logger.error(f"Error analyzing HP bar color: {e}")
            return 100.0
    
    def analyze_mp_bar_color(self, mp_area: np.ndarray) -> float:
        """Analyze MP bar color to estimate MP percentage"""
        try:
            # Convert to HSV
            hsv = cv2.cvtColor(mp_area, cv2.COLOR_BGR2HSV)
            
            # Count blue pixels (MP)
            blue_mask = cv2.inRange(hsv, np.array([100, 50, 50]), np.array([130, 255, 255]))
            blue_pixels = cv2.countNonZero(blue_mask)
            
            total_pixels = mp_area.shape[0] * mp_area.shape[1]
            
            return (blue_pixels / total_pixels) * 100
            
        except Exception as e:
            logger.error(f"Error analyzing MP bar color: {e}")
            return 100.0
    
    def detect_creatures(self, screenshot: np.ndarray, target_list: List[str]) -> List[Creature]:
        """Detect creatures on screen using template matching"""
        creatures = []
        
        try:
            # Game area where creatures appear (center of screen typically)
            game_area = screenshot[100:600, 300:900]
            
            for creature_name in target_list:
                if creature_name in self.creature_templates:
                    template = self.creature_templates[creature_name]
                    
                    # In a real implementation, you'd use template matching
                    # For demo, we'll simulate creature detection
                    if random.random() < 0.15:  # 15% chance to detect each creature
                        x = random.randint(300, 850)
                        y = random.randint(150, 550)
                        distance = random.randint(1, 7)
                        
                        creatures.append(Creature(
                            name=creature_name,
                            x=x,
                            y=y,
                            distance=distance,
                            health=random.randint(50, 100)
                        ))
            
            # Sort by distance (closest first)
            creatures.sort(key=lambda c: c.distance)
            
            return creatures
            
        except Exception as e:
            logger.error(f"Error detecting creatures: {e}")
            return []
    
    def detect_loot(self, screenshot: np.ndarray, loot_list: List[str]) -> List[LootItem]:
        """Detect loot items on screen"""
        loot_items = []
        
        try:
            # Area around player where loot appears
            loot_area = screenshot[200:500, 400:800]
            
            for item_name in loot_list:
                if item_name in self.loot_templates:
                    template = self.loot_templates[item_name]
                    
                    # Simulate loot detection
                    if random.random() < 0.08:  # 8% chance to detect each item
                        x = random.randint(400, 750)
                        y = random.randint(250, 450)
                        
                        loot_items.append(LootItem(
                            name=item_name,
                            x=x,
                            y=y,
                            value=template['value'],
                            keep=True
                        ))
            
            return loot_items
            
        except Exception as e:
            logger.error(f"Error detecting loot: {e}")
            return []
    
    def get_current_position(self) -> Tuple[int, int]:
        """Get current player position (for waypoint system)"""
        try:
            # In a real implementation, this would read from memory or analyze minimap
            # For demo, we'll return simulated coordinates
            return (random.randint(1000, 1100), random.randint(1000, 1100))
            
        except Exception as e:
            logger.error(f"Error getting current position: {e}")
            return (1000, 1000)

class TibiaAutomation:
    """Handles all automation actions (mouse, keyboard, spells)"""
    
    def __init__(self):
        self.last_action_time = 0
        self.human_delays = {
            'min_action_delay': 0.1,
            'max_action_delay': 0.8,
            'typing_delay': (0.05, 0.15),
            'mouse_move_duration': (0.3, 1.2),
            'micro_pause_chance': 0.15,
            'micro_pause_duration': (0.05, 0.3)
        }
        
    def human_delay(self, min_delay: float = None, max_delay: float = None):
        """Generate human-like delay with micro-pauses"""
        if min_delay is None:
            min_delay = self.human_delays['min_action_delay']
        if max_delay is None:
            max_delay = self.human_delays['max_action_delay']
        
        # Base delay
        delay = random.uniform(min_delay, max_delay)
        
        # Add micro-pause chance
        if random.random() < self.human_delays['micro_pause_chance']:
            micro_pause = random.uniform(*self.human_delays['micro_pause_duration'])
            delay += micro_pause
        
        time.sleep(delay)
    
    def bezier_mouse_move(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], duration: float = None):
        """Move mouse using Bezier curve for natural movement"""
        if duration is None:
            duration = random.uniform(*self.human_delays['mouse_move_duration'])
        
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        # Create control points for Bezier curve
        control_x = random.uniform(min(x1, x2), max(x1, x2))
        control_y = random.uniform(min(y1, y2), max(y1, y2))
        
        # Generate points along Bezier curve
        steps = int(duration * 60)  # 60 steps per second
        for i in range(steps + 1):
            t = i / steps
            
            # Bezier curve formula
            x = (1-t)**2 * x1 + 2*(1-t)*t * control_x + t**2 * x2
            y = (1-t)**2 * y1 + 2*(1-t)*t * control_y + t**2 * y2
            
            pyautogui.moveTo(int(x), int(y))
            time.sleep(duration / steps)
    
    def cast_spell(self, spell: str):
        """Cast a spell with human-like typing"""
        try:
            self.human_delay(0.1, 0.3)
            
            # Type spell with human-like delays
            for char in spell:
                pyautogui.press(char)
                time.sleep(random.uniform(*self.human_delays['typing_delay']))
            
            pyautogui.press('enter')
            logger.info(f"Cast spell: {spell}")
            
        except Exception as e:
            logger.error(f"Error casting spell {spell}: {e}")
    
    def use_hotkey(self, hotkey: str):
        """Use a hotkey (e.g., F1, F2, etc.)"""
        try:
            self.human_delay(0.1, 0.2)
            pyautogui.press(hotkey)
            logger.info(f"Used hotkey: {hotkey}")
            
        except Exception as e:
            logger.error(f"Error using hotkey {hotkey}: {e}")
    
    def click_position(self, x: int, y: int, button: str = 'left'):
        """Click at specific position with human-like movement"""
        try:
            current_pos = pyautogui.position()
            
            # Move mouse with bezier curve
            self.bezier_mouse_move(current_pos, (x, y))
            
            # Click with slight delay
            self.human_delay(0.1, 0.2)
            
            if button == 'left':
                pyautogui.click()
            elif button == 'right':
                pyautogui.rightClick()
            
            logger.info(f"Clicked at ({x}, {y}) with {button} button")
            
        except Exception as e:
            logger.error(f"Error clicking at ({x}, {y}): {e}")
    
    def attack_creature(self, creature: Creature, attack_spell: str):
        """Attack a creature"""
        try:
            # Right-click on creature to attack
            self.click_position(creature.x, creature.y, 'right')
            
            # Wait a moment then cast attack spell
            self.human_delay(0.2, 0.4)
            self.cast_spell(attack_spell)
            
            logger.info(f"Attacked {creature.name} with {attack_spell}")
            
        except Exception as e:
            logger.error(f"Error attacking {creature.name}: {e}")
    
    def loot_item(self, item: LootItem):
        """Loot an item"""
        try:
            # Right-click on item to loot
            self.click_position(item.x, item.y, 'right')
            
            logger.info(f"Looted {item.name}")
            
        except Exception as e:
            logger.error(f"Error looting {item.name}: {e}")
    
    def move_to_position(self, x: int, y: int):
        """Move character to specific position"""
        try:
            # Click to move
            self.click_position(x, y)
            
            logger.info(f"Moving to position ({x}, {y})")
            
        except Exception as e:
            logger.error(f"Error moving to ({x}, {y}): {e}")
    
    def use_food(self, food_hotkey: str = 'F1'):
        """Use food item"""
        try:
            self.use_hotkey(food_hotkey)
            logger.info(f"Used food with hotkey {food_hotkey}")
            
        except Exception as e:
            logger.error(f"Error using food: {e}")
    
    def drop_item(self, item_name: str):
        """Drop an item (for inventory management)"""
        try:
            # In a real implementation, this would find the item in inventory
            # and drag it to the ground
            logger.info(f"Dropped {item_name}")
            
        except Exception as e:
            logger.error(f"Error dropping {item_name}: {e}")
    
    def anti_idle_action(self):
        """Perform random anti-idle action"""
        try:
            actions = [
                lambda: pyautogui.press('space'),
                lambda: pyautogui.press('ctrl'),
                lambda: pyautogui.moveTo(pyautogui.position()[0] + random.randint(-10, 10), 
                                       pyautogui.position()[1] + random.randint(-10, 10))
            ]
            
            action = random.choice(actions)
            action()
            
            logger.info("Performed anti-idle action")
            
        except Exception as e:
            logger.error(f"Error in anti-idle action: {e}")

class TibiaBot:
    """Main bot class that orchestrates all functionality"""
    
    def __init__(self):
        self.detector = TibiaDetector()
        self.automation = TibiaAutomation()
        
        # Bot state
        self.is_running = False
        self.is_paused = False
        self.session_id = str(uuid.uuid4())
        
        # Configuration
        self.config = None
        
        # Statistics
        self.stats = {
            'session_id': self.session_id,
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
        
        # Waypoint system
        self.current_waypoint_index = 0
        self.waypoint_direction = 1
        self.last_waypoint_time = 0
        
        # WebSocket connections for real-time updates
        self.websocket_connections = set()
        
        # Game state
        self.game_state = GameState()
        
    def update_stats(self, stat_name: str, value: int = 1):
        """Update bot statistics"""
        if stat_name in self.stats:
            self.stats[stat_name] += value
    
    async def broadcast_stats(self):
        """Broadcast current stats to all connected websockets"""
        if self.websocket_connections:
            stats_data = {
                "type": "stats_update",
                "data": {
                    **self.stats,
                    "is_running": self.is_running,
                    "is_paused": self.is_paused,
                    "game_state": {
                        "hp_percent": self.game_state.hp_percent,
                        "mp_percent": self.game_state.mp_percent,
                        "is_alive": self.game_state.is_alive,
                        "target_creature": self.game_state.target_creature
                    }
                }
            }
            
            disconnected = set()
            for websocket in self.websocket_connections:
                try:
                    await websocket.send_text(json.dumps(stats_data))
                except:
                    disconnected.add(websocket)
            
            # Remove disconnected websockets
            self.websocket_connections -= disconnected
    
    async def main_loop(self):
        """Main bot execution loop"""
        logger.info("Bot main loop started")
        start_time = time.time()
        
        while self.is_running:
            try:
                if self.is_paused:
                    await asyncio.sleep(1)
                    continue
                
                # Update running time
                self.stats['time_running'] = int(time.time() - start_time)
                
                # Capture screen
                screenshot = self.detector.capture_screen()
                if screenshot is None:
                    await asyncio.sleep(1)
                    continue
                
                # Detect game state
                self.game_state = self.detector.detect_hp_mp(screenshot)
                
                # Emergency logout
                if self.game_state.hp_percent <= self.config.emergency_logout_hp:
                    logger.warning("Emergency logout triggered!")
                    self.is_running = False
                    break
                
                # Auto heal
                if (self.config.auto_heal and 
                    self.game_state.hp_percent <= self.config.heal_at_hp):
                    self.automation.cast_spell(self.config.heal_spell)
                    self.update_stats('heals_used')
                
                # Auto mana
                if (self.config.auto_heal and 
                    self.game_state.mp_percent <= self.config.heal_at_mp):
                    self.automation.cast_spell(self.config.heal_mana_spell)
                    self.update_stats('heals_used')
                
                # Auto food
                if self.config.auto_food and random.random() < 0.05:  # 5% chance per cycle
                    self.automation.use_food()
                    self.update_stats('food_used')
                
                # Auto attack
                if self.config.auto_attack:
                    creatures = self.detector.detect_creatures(screenshot, self.config.target_creatures)
                    if creatures:
                        target = creatures[0]  # Attack closest creature
                        self.automation.attack_creature(target, self.config.attack_spell)
                        self.update_stats('attacks_made')
                        
                        # Chance to kill creature
                        if random.random() < 0.3:
                            self.update_stats('creatures_killed')
                            self.game_state.target_creature = None
                        else:
                            self.game_state.target_creature = target.name
                
                # Auto loot
                if self.config.auto_loot:
                    loot_items = self.detector.detect_loot(screenshot, self.config.loot_items)
                    for item in loot_items:
                        self.automation.loot_item(item)
                        self.update_stats('items_looted')
                        
                        # If using loot all and filter, might need to discard
                        if (self.config.loot_all_and_filter and 
                            item.name in self.config.discard_items):
                            self.automation.drop_item(item.name)
                            self.update_stats('items_discarded')
                
                # Auto walk (waypoints)
                if self.config.auto_walk and self.config.waypoints:
                    await self.execute_waypoint_movement()
                
                # Anti-idle
                if self.config.anti_idle and random.random() < 0.02:  # 2% chance per cycle
                    self.automation.anti_idle_action()
                
                # Broadcast stats
                await self.broadcast_stats()
                
                # Random delay between main loop iterations
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
            except Exception as e:
                logger.error(f"Error in bot main loop: {e}")
                await asyncio.sleep(1)
        
        logger.info("Bot main loop ended")
    
    async def execute_waypoint_movement(self):
        """Execute waypoint-based movement"""
        try:
            current_time = time.time() * 1000  # Convert to milliseconds
            
            if current_time - self.last_waypoint_time < self.config.waypoint_delay:
                return
            
            waypoints = self.config.waypoints
            if not waypoints:
                return
            
            # Get current waypoint
            current_waypoint = waypoints[self.current_waypoint_index]
            
            # Move to waypoint
            self.automation.move_to_position(current_waypoint['x'], current_waypoint['y'])
            
            logger.info(f"Walking to waypoint: {current_waypoint['name']} "
                       f"({current_waypoint['x']}, {current_waypoint['y']})")
            
            # Update waypoint index based on mode
            if self.config.waypoint_mode == "loop":
                self.current_waypoint_index = (self.current_waypoint_index + 1) % len(waypoints)
            
            elif self.config.waypoint_mode == "back_and_forth":
                self.current_waypoint_index += self.waypoint_direction
                
                # Change direction at endpoints
                if self.current_waypoint_index >= len(waypoints) - 1:
                    self.waypoint_direction = -1
                elif self.current_waypoint_index <= 0:
                    self.waypoint_direction = 1
                
                # Clamp to valid range
                self.current_waypoint_index = max(0, min(self.current_waypoint_index, len(waypoints) - 1))
            
            elif self.config.waypoint_mode == "once":
                if self.current_waypoint_index < len(waypoints) - 1:
                    self.current_waypoint_index += 1
                else:
                    # Reached end, disable auto walk
                    self.config.auto_walk = False
                    logger.info("Waypoint sequence completed - disabling auto walk")
            
            self.last_waypoint_time = current_time
            
        except Exception as e:
            logger.error(f"Error in waypoint movement: {e}")
    
    def get_current_position(self) -> Dict[str, Any]:
        """Get current player position"""
        try:
            x, y = self.detector.get_current_position()
            return {
                'x': x,
                'y': y,
                'message': 'Posição capturada com sucesso!',
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error getting current position: {e}")
            return {
                'x': 1000,
                'y': 1000,
                'message': 'Erro ao capturar posição',
                'timestamp': datetime.utcnow()
            }
    
    def start(self):
        """Start the bot"""
        if self.is_running:
            return False
        
        self.is_running = True
        self.is_paused = False
        self.session_id = str(uuid.uuid4())
        
        # Reset stats
        self.stats = {
            'session_id': self.session_id,
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
        
        # Start main loop in background
        asyncio.create_task(self.main_loop())
        
        logger.info(f"Bot started with session ID: {self.session_id}")
        return True
    
    def stop(self):
        """Stop the bot"""
        self.is_running = False
        self.is_paused = False
        logger.info("Bot stopped")
        return True
    
    def pause(self):
        """Pause/resume the bot"""
        self.is_paused = not self.is_paused
        status = "paused" if self.is_paused else "resumed"
        logger.info(f"Bot {status}")
        return self.is_paused
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        return {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'session_id': self.session_id,
            'stats': self.stats,
            'game_state': {
                'hp_percent': self.game_state.hp_percent,
                'mp_percent': self.game_state.mp_percent,
                'is_alive': self.game_state.is_alive,
                'target_creature': self.game_state.target_creature
            }
        }