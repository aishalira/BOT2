# # 🏰 Bot Tibia Indetectável v2.0

## 📋 Descrição

Um bot completo e indetectável para Tibia, desenvolvido com tecnologias modernas e interface web intuitiva. Ideal para uso em servidores OT onde bots são permitidos e para fins educacionais/pesquisa no Tibia Global.

## ✨ Características Principais

### 🎯 Funcionalidades Completas
- **Auto-Cura Inteligente**: Detecta HP/MP e usa magias automaticamente
- **Auto-Ataque**: Detecta criaturas e ataca automaticamente
- **Auto-Loot**: Sistema inteligente para Free Account (pega tudo + descarta indesejados)
- **Waypoints**: Sistema de navegação automática com 3 modos
- **Anti-Idle**: Ações aleatórias para evitar desconexão
- **Logout de Emergência**: Para automaticamente em HP baixo

### 🛡️ Tecnologia Anti-Detecção
- **Movimentos Humanizados**: Usa curvas Bézier para movimento natural do mouse
- **Delays Aleatórios**: Tempos variáveis entre ações
- **Micro-Pausas**: Simulação de comportamento humano
- **Detecção Inteligente**: OCR + análise de cores para máxima precisão

### 🌐 Interface Moderna
- **Web Interface**: Acesso via navegador, responsiva e intuitiva
- **Tempo Real**: WebSocket para atualizações instantâneas
- **Dashboard Completo**: Estatísticas, monitoramento, histórico
- **Configuração Fácil**: Todos os parâmetros ajustáveis

## 🚀 Instalação Super Fácil

### 1️⃣ Pré-requisitos
```
✅ Windows 10+
✅ Python 3.8+     → https://www.python.org/downloads/
✅ Node.js 16+      → https://nodejs.org/
```

### 2️⃣ Instalação Automática
```batch
1. Baixe e extraia o arquivo ZIP
2. Execute: INSTALAR_BOT.bat (como administrador)
3. Aguarde a instalação terminar
```

### 3️⃣ Uso
```batch
1. Abra o Tibia e entre com seu personagem
2. Execute: EXECUTAR_BOT.bat
3. Configure na interface web
4. Clique "Iniciar" e aproveite!
```

## 📁 Estrutura do Projeto

```
TibiaBotIndetectavel_v2.0/
├── 📄 LEIA-ME_PRIMEIRO.txt          # Instruções iniciais
├── 📄 MANUAL_INSTALACAO.md          # Manual completo
├── 📄 GUIA_RAPIDO.md               # Guia rápido
├── 🔧 INSTALAR_BOT.bat             # Instalador automático
├── ▶️ EXECUTAR_BOT.bat              # Executar bot
├── ⏹️ PARAR_BOT.bat                 # Parar bot
├── 🔍 VERIFICAR_INSTALACAO.bat      # Verificar instalação
├── 📁 backend/                      # Servidor Python
│   ├── server.py                    # API FastAPI
│   ├── tibia_bot.py                # Core do bot
│   └── requirements.txt            # Dependências Python
└── 📁 frontend/                     # Interface React
    ├── src/App.js                  # Interface principal
    ├── package.json                # Dependências Node.js
    └── ...
```

## 🎮 Funcionalidades Detalhadas

### Auto-Cura
- Detecta HP/MP via OCR e análise de cores
- Configurable threshold (padrão: 70% HP, 50% MP)
- Suporte a diferentes magias de cura
- Cura de HP e MP independentes

### Auto-Ataque
- Detecção de criaturas por template matching
- Lista configurável de alvos
- Ataque automático da criatura mais próxima
- Suporte a diferentes magias de ataque

### Auto-Loot
- **Modo Free Account**: Pega tudo + descarta indesejados
- **Modo Premium**: Loot seletivo
- Lista configurável de itens desejados/indesejados
- Gerenciamento inteligente de inventário

### Sistema de Waypoints
- **🔄 Loop Contínuo**: Anda infinitamente pelos pontos
- **↔️ Ida e Volta**: Vai até o final e volta
- **1️⃣ Uma Vez**: Passa por todos apenas uma vez
- Captura de posição com um clique
- Delay configurável entre waypoints

### Monitoramento
- **Dashboard em Tempo Real**: HP/MP, estatísticas, status
- **Histórico de Sessões**: Todas as sessões salvas
- **Estatísticas Detalhadas**: Tempo, curas, ataques, loot
- **Indicadores Visuais**: Barras de HP/MP, status do bot

## 🛡️ Segurança e Uso Responsável

### ⚠️ Aviso Legal
- Este bot é destinado para uso **educacional** e em **servidores OT**
- Para Tibia Global: Use por sua **conta e risco**
- Não nos responsabilizamos por punições ou banimentos
- Respeite os termos de serviço do jogo

### 🔒 Dicas de Segurança
- 🔄 **Varie os horários** de uso
- ⏰ **Não use 24h por dia**
- 🎭 **Simule comportamento humano**
- 📊 **Monitore sempre** o bot
- 🎯 **Use em locais seguros**

## 🔧 Configuração Recomendada

### Para Iniciantes
```
✅ Auto-Cura: Habilitado (70% HP)
✅ Auto-Ataque: Habilitado (exori)
✅ Auto-Loot: Habilitado + Filtro
✅ Criaturas: rat, rotworm, cyclops
✅ Itens: gold coin, platinum coin
✅ Anti-Idle: Habilitado
✅ Logout Emergência: 10% HP
```

### Para Avançados
- Configure waypoints personalizados
- Ajuste delays para seu estilo
- Personalize listas de loot
- Use modo premium se aplicável

## 🆘 Suporte e Troubleshooting

### Problemas Comuns
- **❌ Bot não inicia**: Execute `VERIFICAR_INSTALACAO.bat`
- **❌ Interface não abre**: Aguarde 30s, acesse `http://localhost:3000`
- **❌ Não funciona no jogo**: Certifique-se que Tibia está em modo janela
- **❌ Python não reconhecido**: Reinstale marcando "Add to PATH"

### Antes de Pedir Ajuda
1. ✅ Leia `MANUAL_INSTALACAO.md`
2. ✅ Execute `VERIFICAR_INSTALACAO.bat`
3. ✅ Verifique se Tibia está aberto
4. ✅ Certifique-se que tem internet

## 📊 Especificações Técnicas

### Backend
- **FastAPI**: API REST moderna e rápida
- **Python 3.8+**: Linguagem principal
- **PyAutoGUI**: Automação de mouse/teclado
- **OpenCV**: Processamento de imagens
- **Tesseract**: OCR para detecção de texto
- **WebSocket**: Comunicação tempo real

### Frontend
- **React 19**: Interface moderna e responsiva
- **Tailwind CSS**: Estilização avançada
- **Axios**: Comunicação HTTP
- **WebSocket**: Atualizações tempo real

### Banco de Dados
- **MongoDB**: Armazenamento de configurações e sessões
- **Motor**: Driver assíncrono para MongoDB

## 🏆 Vantagens Competitivas

1. **🎯 Fácil de Usar**: Instalação em 1 clique, interface intuitiva
2. **🛡️ Indetectável**: Movimentos humanizados, delays aleatórios
3. **🌐 Interface Moderna**: Web-based, responsiva, tempo real
4. **📚 Bem Documentado**: Manual completo, guias, troubleshooting
5. **🔧 Configurável**: Todos os parâmetros ajustáveis
6. **📊 Monitoramento**: Estatísticas detalhadas, histórico completo
7. **🚀 Tecnologia Atual**: Stack moderno, código limpo

## 🎉 Conclusão

O **Bot Tibia Indetectável v2.0** representa o que há de mais avançado em automação para Tibia. Com interface moderna, funcionalidades completas e instalação super fácil, é a escolha perfeita para quem busca qualidade e simplicidade.

**Divirta-se e bom jogo!** 🏰⚔️

---

*© 2025 Bot Tibia Indetectável - Versão 2.0*
*Desenvolvido com ❤️ para a comunidade Tibia*
