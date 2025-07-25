import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Componente principal da aplicação
const App = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [botStatus, setBotStatus] = useState({
    is_running: false,
    is_paused: false,
    session_id: null,
    stats: {
      time_running: 0,
      heals_used: 0,
      food_used: 0,
      attacks_made: 0,
      creatures_killed: 0,
      items_looted: 0,
      items_discarded: 0
    },
    game_state: {
      hp_percent: 100,
      mp_percent: 100,
      is_alive: true,
      target_creature: null
    }
  });
  
  const [config, setConfig] = useState({
    name: 'Meu Bot Tibia',
    auto_heal: true,
    auto_food: true,
    auto_attack: true,
    auto_walk: false,
    auto_loot: true,
    heal_spell: 'exura',
    heal_at_hp: 70,
    heal_mana_spell: 'exura gran',
    heal_at_mp: 50,
    attack_spell: 'exori',
    food_hotkey: 'F1',
    waypoints: [],
    waypoint_mode: 'loop',
    waypoint_delay: 1000,
    target_creatures: ['rat', 'rotworm', 'cyclops'],
    loot_items: ['gold coin', 'platinum coin', 'crystal coin'],
    discard_items: ['leather armor', 'studded armor', 'chain armor'],
    loot_all_and_filter: true,
    anti_idle: true,
    emergency_logout_hp: 10
  });
  
  const [sessions, setSessions] = useState([]);
  const [notification, setNotification] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);

  // Conectar WebSocket para atualizações em tempo real
  useEffect(() => {
    connectWebSocket();
    loadInitialData();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    const wsUrl = `${BACKEND_URL}/api/bot/ws`.replace('http', 'ws');
    wsRef.current = new WebSocket(wsUrl);
    
    wsRef.current.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket conectado');
    };
    
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'stats_update') {
        setBotStatus(data.data);
      }
    };
    
    wsRef.current.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket desconectado');
      
      // Tentar reconectar após 3 segundos
      setTimeout(() => {
        connectWebSocket();
      }, 3000);
    };
    
    wsRef.current.onerror = (error) => {
      console.error('Erro no WebSocket:', error);
    };
  };

  const loadInitialData = async () => {
    try {
      // Carregar configuração
      const configResponse = await axios.get(`${API}/bot/config`);
      if (configResponse.data && !configResponse.data.message) {
        setConfig(configResponse.data);
      }
      
      // Carregar status do bot
      const statusResponse = await axios.get(`${API}/bot/status`);
      if (statusResponse.data.data) {
        setBotStatus(statusResponse.data.data);
      }
      
      // Carregar sessões
      const sessionsResponse = await axios.get(`${API}/bot/sessions`);
      setSessions(sessionsResponse.data.sessions || []);
      
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      showNotification('Erro ao carregar dados iniciais', 'error');
    }
  };

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  const saveConfig = async () => {
    try {
      await axios.post(`${API}/bot/config`, config);
      showNotification('Configuração salva com sucesso!', 'success');
    } catch (error) {
      console.error('Erro ao salvar configuração:', error);
      showNotification('Erro ao salvar configuração', 'error');
    }
  };

  const startBot = async () => {
    try {
      const response = await axios.post(`${API}/bot/start`);
      showNotification(response.data.message, 'success');
    } catch (error) {
      console.error('Erro ao iniciar bot:', error);
      showNotification('Erro ao iniciar bot: ' + error.response?.data?.detail, 'error');
    }
  };

  const stopBot = async () => {
    try {
      const response = await axios.post(`${API}/bot/stop`);
      showNotification(response.data.message, 'success');
    } catch (error) {
      console.error('Erro ao parar bot:', error);
      showNotification('Erro ao parar bot', 'error');
    }
  };

  const pauseBot = async () => {
    try {
      const response = await axios.post(`${API}/bot/pause`);
      showNotification(response.data.message, 'success');
    } catch (error) {
      console.error('Erro ao pausar bot:', error);
      showNotification('Erro ao pausar bot', 'error');
    }
  };

  const capturePosition = async () => {
    try {
      const response = await axios.get(`${API}/bot/current-position`);
      const position = response.data.data;
      
      const waypointName = prompt('Nome do waypoint:');
      if (waypointName) {
        const newWaypoint = {
          name: waypointName,
          x: position.x,
          y: position.y,
          description: `Capturado em ${new Date().toLocaleString()}`
        };
        
        await axios.post(`${API}/bot/waypoint`, newWaypoint);
        
        setConfig(prev => ({
          ...prev,
          waypoints: [...prev.waypoints, { ...newWaypoint, id: Date.now() }]
        }));
        
        showNotification(`Waypoint "${waypointName}" adicionado em (${position.x}, ${position.y})`, 'success');
      }
    } catch (error) {
      console.error('Erro ao capturar posição:', error);
      showNotification('Erro ao capturar posição', 'error');
    }
  };

  const deleteWaypoint = async (waypointId) => {
    try {
      await axios.delete(`${API}/bot/waypoint/${waypointId}`);
      
      setConfig(prev => ({
        ...prev,
        waypoints: prev.waypoints.filter(wp => wp.id !== waypointId)
      }));
      
      showNotification('Waypoint removido com sucesso!', 'success');
    } catch (error) {
      console.error('Erro ao remover waypoint:', error);
      showNotification('Erro ao remover waypoint', 'error');
    }
  };

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const formatArrayInput = (value) => {
    if (Array.isArray(value)) {
      return value.join(', ');
    }
    return value || '';
  };

  const parseArrayInput = (value) => {
    return value.split(',').map(item => item.trim()).filter(item => item);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Notificação */}
      {notification && (
        <div className={`fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
          notification.type === 'success' ? 'bg-green-600' : 
          notification.type === 'error' ? 'bg-red-600' : 'bg-blue-600'
        }`}>
          <div className="flex items-center">
            <span className="mr-2">
              {notification.type === 'success' ? '✓' : 
               notification.type === 'error' ? '✗' : 'ℹ'}
            </span>
            {notification.message}
          </div>
        </div>
      )}

      {/* Header */}
      <header className="bg-gray-800 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-yellow-400">🏰 Tibia Bot Indetectável</h1>
              <div className={`ml-4 px-2 py-1 rounded-full text-xs ${
                isConnected ? 'bg-green-600' : 'bg-red-600'
              }`}>
                {isConnected ? 'Conectado' : 'Desconectado'}
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-sm">
                <span className="text-gray-400">Status:</span>
                <span className={`ml-2 ${
                  botStatus.is_running ? 
                    (botStatus.is_paused ? 'text-yellow-400' : 'text-green-400') : 
                    'text-red-400'
                }`}>
                  {botStatus.is_running ? 
                    (botStatus.is_paused ? 'Pausado' : 'Rodando') : 
                    'Parado'}
                </span>
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={startBot}
                  disabled={botStatus.is_running && !botStatus.is_paused}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded-lg transition-colors"
                >
                  ▶️ Iniciar
                </button>
                
                <button
                  onClick={pauseBot}
                  disabled={!botStatus.is_running}
                  className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 rounded-lg transition-colors"
                >
                  ⏸️ {botStatus.is_paused ? 'Retomar' : 'Pausar'}
                </button>
                
                <button
                  onClick={stopBot}
                  disabled={!botStatus.is_running}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 rounded-lg transition-colors"
                >
                  ⏹️ Parar
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navegação */}
      <nav className="bg-gray-800 border-t border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'dashboard', label: '📊 Dashboard', icon: '📊' },
              { id: 'config', label: '⚙️ Configurações', icon: '⚙️' },
              { id: 'waypoints', label: '🗺️ Waypoints', icon: '🗺️' },
              { id: 'sessions', label: '📈 Sessões', icon: '📈' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-yellow-400 text-yellow-400'
                    : 'border-transparent text-gray-400 hover:text-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Conteúdo Principal */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Dashboard */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-600 rounded-lg">
                    <span className="text-2xl">⏱️</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm text-gray-400">Tempo Ativo</p>
                    <p className="text-2xl font-bold">{formatTime(botStatus.stats.time_running)}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-green-600 rounded-lg">
                    <span className="text-2xl">💚</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm text-gray-400">Curas Usadas</p>
                    <p className="text-2xl font-bold">{botStatus.stats.heals_used}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-red-600 rounded-lg">
                    <span className="text-2xl">⚔️</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm text-gray-400">Ataques</p>
                    <p className="text-2xl font-bold">{botStatus.stats.attacks_made}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-yellow-600 rounded-lg">
                    <span className="text-2xl">🏆</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm text-gray-400">Criaturas Mortas</p>
                    <p className="text-2xl font-bold">{botStatus.stats.creatures_killed}</p>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Game State */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Estado do Jogo</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-400">HP</span>
                    <span className="text-sm font-medium">{botStatus.game_state.hp_percent.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-red-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${botStatus.game_state.hp_percent}%` }}
                    ></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-400">MP</span>
                    <span className="text-sm font-medium">{botStatus.game_state.mp_percent.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${botStatus.game_state.mp_percent}%` }}
                    ></div>
                  </div>
                </div>
              </div>
              
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center">
                  <span className="text-sm text-gray-400">Status:</span>
                  <span className={`ml-2 ${botStatus.game_state.is_alive ? 'text-green-400' : 'text-red-400'}`}>
                    {botStatus.game_state.is_alive ? 'Vivo' : 'Morto'}
                  </span>
                </div>
                
                <div className="flex items-center">
                  <span className="text-sm text-gray-400">Alvo:</span>
                  <span className="ml-2">
                    {botStatus.game_state.target_creature || 'Nenhum'}
                  </span>
                </div>
              </div>
            </div>
            
            {/* Estatísticas Detalhadas */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Estatísticas da Sessão</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-yellow-400">{botStatus.stats.items_looted}</p>
                  <p className="text-sm text-gray-400">Itens Coletados</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-400">{botStatus.stats.items_discarded}</p>
                  <p className="text-sm text-gray-400">Itens Descartados</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-400">{botStatus.stats.food_used}</p>
                  <p className="text-sm text-gray-400">Comida Usada</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-400">0</p>
                  <p className="text-sm text-gray-400">EXP Ganha</p>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Configurações */}
        {activeTab === 'config' && (
          <div className="space-y-6">
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Configurações Básicas</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Nome do Bot
                  </label>
                  <input
                    type="text"
                    value={config.name}
                    onChange={(e) => setConfig({...config, name: e.target.value})}
                    className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    HP de Logout de Emergência
                  </label>
                  <input
                    type="number"
                    value={config.emergency_logout_hp}
                    onChange={(e) => setConfig({...config, emergency_logout_hp: parseInt(e.target.value)})}
                    className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
            
            {/* Configurações de Cura */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Configurações de Cura</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="flex items-center mb-4">
                    <input
                      type="checkbox"
                      checked={config.auto_heal}
                      onChange={(e) => setConfig({...config, auto_heal: e.target.checked})}
                      className="mr-2"
                    />
                    <span>Ativar Auto-Cura</span>
                  </label>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">
                        Magia de Cura
                      </label>
                      <input
                        type="text"
                        value={config.heal_spell}
                        onChange={(e) => setConfig({...config, heal_spell: e.target.value})}
                        className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">
                        Curar quando HP estiver em (%)
                      </label>
                      <input
                        type="number"
                        value={config.heal_at_hp}
                        onChange={(e) => setConfig({...config, heal_at_hp: parseInt(e.target.value)})}
                        className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>
                
                <div>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">
                        Magia de Mana
                      </label>
                      <input
                        type="text"
                        value={config.heal_mana_spell}
                        onChange={(e) => setConfig({...config, heal_mana_spell: e.target.value})}
                        className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">
                        Curar mana quando MP estiver em (%)
                      </label>
                      <input
                        type="number"
                        value={config.heal_at_mp}
                        onChange={(e) => setConfig({...config, heal_at_mp: parseInt(e.target.value)})}
                        className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Configurações de Ataque */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Configurações de Ataque</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="flex items-center mb-4">
                    <input
                      type="checkbox"
                      checked={config.auto_attack}
                      onChange={(e) => setConfig({...config, auto_attack: e.target.checked})}
                      className="mr-2"
                    />
                    <span>Ativar Auto-Ataque</span>
                  </label>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                      Magia de Ataque
                    </label>
                    <input
                      type="text"
                      value={config.attack_spell}
                      onChange={(e) => setConfig({...config, attack_spell: e.target.value})}
                      className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Criaturas para Atacar (separadas por vírgula)
                  </label>
                  <textarea
                    value={formatArrayInput(config.target_creatures)}
                    onChange={(e) => setConfig({...config, target_creatures: parseArrayInput(e.target.value)})}
                    className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent h-24"
                    placeholder="rat, rotworm, cyclops, dragon"
                  />
                </div>
              </div>
            </div>
            
            {/* Configurações de Loot */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Configurações de Loot</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="flex items-center mb-4">
                    <input
                      type="checkbox"
                      checked={config.auto_loot}
                      onChange={(e) => setConfig({...config, auto_loot: e.target.checked})}
                      className="mr-2"
                    />
                    <span>Ativar Auto-Loot</span>
                  </label>
                  
                  <label className="flex items-center mb-4">
                    <input
                      type="checkbox"
                      checked={config.loot_all_and_filter}
                      onChange={(e) => setConfig({...config, loot_all_and_filter: e.target.checked})}
                      className="mr-2"
                    />
                    <span>Lootar Tudo e Filtrar (Free Account)</span>
                  </label>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                      Itens para Coletar (separados por vírgula)
                    </label>
                    <textarea
                      value={formatArrayInput(config.loot_items)}
                      onChange={(e) => setConfig({...config, loot_items: parseArrayInput(e.target.value)})}
                      className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent h-24"
                      placeholder="gold coin, platinum coin, crystal coin"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Itens para Descartar (separados por vírgula)
                  </label>
                  <textarea
                    value={formatArrayInput(config.discard_items)}
                    onChange={(e) => setConfig({...config, discard_items: parseArrayInput(e.target.value)})}
                    className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent h-24"
                    placeholder="leather armor, studded armor, chain armor"
                  />
                </div>
              </div>
            </div>
            
            {/* Configurações de Comida */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Configurações de Comida</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="flex items-center mb-4">
                    <input
                      type="checkbox"
                      checked={config.auto_food}
                      onChange={(e) => setConfig({...config, auto_food: e.target.checked})}
                      className="mr-2"
                    />
                    <span>Ativar Auto-Comida</span>
                  </label>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Hotkey da Comida
                  </label>
                  <input
                    type="text"
                    value={config.food_hotkey}
                    onChange={(e) => setConfig({...config, food_hotkey: e.target.value})}
                    className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
            
            {/* Outras Configurações */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Outras Configurações</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="flex items-center mb-4">
                    <input
                      type="checkbox"
                      checked={config.anti_idle}
                      onChange={(e) => setConfig({...config, anti_idle: e.target.checked})}
                      className="mr-2"
                    />
                    <span>Ativar Anti-Idle</span>
                  </label>
                </div>
                
                <div>
                  <label className="flex items-center mb-4">
                    <input
                      type="checkbox"
                      checked={config.auto_walk}
                      onChange={(e) => setConfig({...config, auto_walk: e.target.checked})}
                      className="mr-2"
                    />
                    <span>Ativar Auto-Walk (Waypoints)</span>
                  </label>
                </div>
              </div>
            </div>
            
            {/* Botão Salvar */}
            <div className="flex justify-end">
              <button
                onClick={saveConfig}
                className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-medium transition-colors"
              >
                💾 Salvar Configurações
              </button>
            </div>
          </div>
        )}
        
        {/* Waypoints */}
        {activeTab === 'waypoints' && (
          <div className="space-y-6">
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">Gerenciar Waypoints</h3>
                <button
                  onClick={capturePosition}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
                >
                  📍 Capturar Posição Atual
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Modo de Movimento
                  </label>
                  <select
                    value={config.waypoint_mode}
                    onChange={(e) => setConfig({...config, waypoint_mode: e.target.value})}
                    className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  >
                    <option value="loop">🔄 Loop Contínuo</option>
                    <option value="back_and_forth">↔️ Ida e Volta</option>
                    <option value="once">1️⃣ Uma Vez</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Delay entre Waypoints (ms)
                  </label>
                  <input
                    type="number"
                    value={config.waypoint_delay}
                    onChange={(e) => setConfig({...config, waypoint_delay: parseInt(e.target.value)})}
                    className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent"
                  />
                </div>
                
                <div className="flex items-end">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={config.auto_walk}
                      onChange={(e) => setConfig({...config, auto_walk: e.target.checked})}
                      className="mr-2"
                    />
                    <span>🚶 Ativar Auto Walk</span>
                  </label>
                </div>
              </div>
              
              <div className="space-y-4">
                <h4 className="font-medium">Waypoints Configurados ({config.waypoints.length})</h4>
                
                {config.waypoints.length === 0 ? (
                  <div className="text-center py-8 text-gray-400">
                    <p>Nenhum waypoint configurado</p>
                    <p className="text-sm">Clique em "Capturar Posição Atual" para adicionar waypoints</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {config.waypoints.map((waypoint, index) => (
                      <div key={waypoint.id || index} className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                        <div className="flex items-center">
                          <span className="text-yellow-400 mr-3">#{index + 1}</span>
                          <div>
                            <h5 className="font-medium">{waypoint.name}</h5>
                            <p className="text-sm text-gray-400">
                              Posição: ({waypoint.x}, {waypoint.y})
                            </p>
                            {waypoint.description && (
                              <p className="text-xs text-gray-500">{waypoint.description}</p>
                            )}
                          </div>
                        </div>
                        
                        <button
                          onClick={() => deleteWaypoint(waypoint.id || index)}
                          className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm transition-colors"
                        >
                          🗑️ Remover
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
        
        {/* Sessões */}
        {activeTab === 'sessions' && (
          <div className="space-y-6">
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Histórico de Sessões</h3>
              
              {sessions.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  <p>Nenhuma sessão encontrada</p>
                  <p className="text-sm">As sessões aparecerão aqui após você usar o bot</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {sessions.map((session, index) => (
                    <div key={session.session_id || index} className="p-4 bg-gray-700 rounded-lg">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium">Sessão {index + 1}</h4>
                        <span className="text-sm text-gray-400">
                          {new Date(session.created_at).toLocaleString('pt-BR')}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-400">Tempo:</span>
                          <span className="ml-2">{formatTime(session.time_running)}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Curas:</span>
                          <span className="ml-2">{session.heals_used}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Ataques:</span>
                          <span className="ml-2">{session.attacks_made}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Criaturas:</span>
                          <span className="ml-2">{session.creatures_killed}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Itens:</span>
                          <span className="ml-2">{session.items_looted}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Descartados:</span>
                          <span className="ml-2">{session.items_discarded}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Comida:</span>
                          <span className="ml-2">{session.food_used}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">EXP:</span>
                          <span className="ml-2">{session.exp_gained}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;