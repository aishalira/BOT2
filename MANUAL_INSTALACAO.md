# 🏰 Manual de Instalação - Bot Tibia Indetectável v2.0

## 📖 Índice
1. [Requisitos do Sistema](#requisitos-do-sistema)
2. [Instalação Rápida](#instalação-rápida)
3. [Instalação Detalhada](#instalação-detalhada)
4. [Configuração do Bot](#configuração-do-bot)
5. [Como Usar](#como-usar)
6. [Problemas Comuns](#problemas-comuns)
7. [Dicas de Segurança](#dicas-de-segurança)

---

## 🖥️ Requisitos do Sistema

### Mínimos:
- ✅ Windows 10 ou superior
- ✅ 4GB de RAM
- ✅ 2GB de espaço livre
- ✅ Conexão com internet
- ✅ Tibia client instalado

### Programas Necessários:
- 🐍 **Python 3.8+** - [Download](https://www.python.org/downloads/)
- 🟢 **Node.js 16+** - [Download](https://nodejs.org/)
- 📱 **Git** - [Download](https://git-scm.com/download/win)

---

## ⚡ Instalação Rápida

### Método 1: Automático (Recomendado)
1. **Baixe** todos os arquivos do bot
2. **Clique duplo** em `INSTALAR_BOT.bat`
3. **Aguarde** a instalação terminar
4. **Execute** `EXECUTAR_BOT.bat`

### Método 2: Manual
```bash
# 1. Instalar dependências do backend
cd backend
pip install -r requirements.txt

# 2. Instalar dependências do frontend
cd ../frontend
yarn install

# 3. Executar (em terminais separados)
python ../backend/server.py
yarn start
```

---

## 🔧 Instalação Detalhada

### Passo 1: Preparar o Ambiente

#### 1.1 - Instalar Python
1. Acesse: https://www.python.org/downloads/
2. Baixe a versão mais recente
3. **⚠️ IMPORTANTE**: Marque "Add Python to PATH"
4. Clique "Install Now"
5. Aguarde a instalação

#### 1.2 - Instalar Node.js
1. Acesse: https://nodejs.org/
2. Baixe a versão LTS (recomendada)
3. Execute a instalação normalmente
4. Aguarde a instalação

#### 1.3 - Instalar Git (Opcional)
1. Acesse: https://git-scm.com/download/win
2. Baixe e instale normalmente
3. Use configurações padrão

### Passo 2: Instalar o Bot

#### 2.1 - Método Automático
```batch
# Execute como administrador
INSTALAR_BOT.bat
```

#### 2.2 - Método Manual
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
yarn install
# ou npm install
```

### Passo 3: Verificar Instalação
```batch
# Execute para verificar
VERIFICAR_INSTALACAO.bat
```

---

## ⚙️ Configuração do Bot

### Primeira Configuração

1. **Execute** `EXECUTAR_BOT.bat`
2. **Aguarde** a interface web abrir
3. Vá para a aba **"⚙️ Configurações"**

### Configurações Básicas

#### 🩺 Cura Automática
- **Ativar Auto-Cura**: ✅ Habilitado
- **Magia de Cura**: `exura` (ou sua magia)
- **Curar em HP**: `70%` (recomendado)
- **Magia de Mana**: `exura gran`
- **Curar em MP**: `50%`

#### ⚔️ Ataque Automático
- **Ativar Auto-Ataque**: ✅ Habilitado
- **Magia de Ataque**: `exori` (ou sua magia)
- **Criaturas Alvo**: `rat, rotworm, cyclops`

#### 💰 Loot Automático
- **Ativar Auto-Loot**: ✅ Habilitado
- **Lootar Tudo e Filtrar**: ✅ Habilitado (Free Account)
- **Itens Desejados**: `gold coin, platinum coin, crystal coin`
- **Itens para Descartar**: `leather armor, studded armor`

#### 🍖 Comida Automática
- **Ativar Auto-Comida**: ✅ Habilitado
- **Hotkey da Comida**: `F1` (configure no Tibia)

### Configurações Avançadas

#### 🗺️ Waypoints (Opcional)
1. **Posicione** seu char no primeiro local
2. **Clique** em "📍 Capturar Posição Atual"
3. **Digite** um nome para o waypoint
4. **Repita** para outros locais
5. **Configure** o modo:
   - 🔄 **Loop**: Anda infinitamente
   - ↔️ **Ida e Volta**: Vai e volta
   - 1️⃣ **Uma Vez**: Passa uma vez

#### 🛡️ Segurança
- **HP de Emergência**: `10%` (logout automático)
- **Anti-Idle**: ✅ Habilitado
- **Delays Humanizados**: Automático

---

## 🎮 Como Usar

### Preparação

1. **Abra o Tibia** e entre com seu personagem
2. **Posicione** o char no local desejado
3. **Configure** hotkeys de comida no Tibia
4. **Deixe** o jogo visível (não minimize)

### Execução

1. **Execute** `EXECUTAR_BOT.bat`
2. **Aguarde** a interface web abrir
3. **Configure** o bot se necessário
4. **Clique** em "▶️ Iniciar"
5. **Monitore** as estatísticas em tempo real

### Monitoramento

#### 📊 Dashboard
- **Tempo Ativo**: Quanto tempo o bot está rodando
- **Estatísticas**: Curas, ataques, criaturas mortas
- **Estado do Jogo**: HP/MP atual do personagem

#### 📈 Sessões
- **Histórico**: Todas as sessões anteriores
- **Estatísticas**: Desempenho por sessão
- **Análise**: Eficiência do bot

---

## 🆘 Problemas Comuns

### ❌ "Python não é reconhecido"
**Solução**:
1. Reinstale o Python
2. Marque "Add Python to PATH"
3. Reinicie o computador

### ❌ "Node não é reconhecido"
**Solução**:
1. Reinstale o Node.js
2. Use a versão LTS
3. Reinicie o computador

### ❌ Bot não funciona no jogo
**Possíveis causas**:
1. **Tibia não está aberto**
2. **Jogo está em fullscreen** (use modo janela)
3. **Coordenadas incorretas** (reinicie o bot)
4. **Permissões insuficientes** (execute como admin)

### ❌ Interface não carrega
**Solução**:
1. Aguarde 30 segundos após iniciar
2. Acesse manualmente: `http://localhost:3000`
3. Verifique se ambos os serviços estão rodando
4. Reinicie o bot

### ❌ Erro de instalação
**Solução**:
1. Execute como administrador
2. Verifique conexão com internet
3. Desative antivírus temporariamente
4. Limpe cache do npm: `npm cache clean --force`

### ❌ Bot não detecta HP/MP
**Solução**:
1. Certifique-se que o Tibia está visível
2. Use resolução padrão
3. Não altere a interface do cliente
4. Reinicie o bot

---

## 🛡️ Dicas de Segurança

### Para Tibia Global
- ⚠️ **Use por sua conta e risco**
- 🔄 **Varie os horários** de uso
- ⏰ **Não use 24h por dia**
- 🎭 **Simule comportamento humano**
- 📊 **Monitore sempre** o bot

### Para OTs (Servers Privados)
- ✅ **Geralmente permitido**
- 📋 **Verifique as regras** do servidor
- 🤝 **Comunique-se** com administradores
- 🔧 **Ajuste configurações** conforme necessário

### Configurações Recomendadas
- 🐌 **Delays altos**: Mais seguro
- 🎯 **Locais seguros**: Evite PK
- 💰 **Loot moderado**: Não seja ganancioso
- 🔄 **Rotas variadas**: Mude waypoints

---

## 📞 Suporte

### Antes de Pedir Ajuda
1. ✅ **Execute** `VERIFICAR_INSTALACAO.bat`
2. 📖 **Leia** este manual completamente
3. 🔍 **Verifique** a seção "Problemas Comuns"
4. 📋 **Colete** logs de erro

### Informações Úteis
- 💻 **Versão do Windows**
- 🐍 **Versão do Python** (`python --version`)
- 🟢 **Versão do Node.js** (`node --version`)
- 🎮 **Cliente do Tibia** (oficial/OT)
- 📄 **Mensagem de erro** completa

---

## 🔄 Atualizações

### Como Atualizar
1. **Baixe** a versão mais recente
2. **Substitua** os arquivos antigos
3. **Execute** `INSTALAR_BOT.bat` novamente
4. **Mantenha** suas configurações salvas

### Backup das Configurações
- 📁 **Configurações**: Salvas automaticamente no banco
- 📊 **Sessões**: Mantidas no histórico
- 🗺️ **Waypoints**: Exportáveis/importáveis

---

## ✨ Recursos Especiais

### 🤖 Inteligência Artificial
- **Movimentos Humanizados**: Curvas Bézier
- **Delays Aleatórios**: Simula comportamento humano
- **Detecção Inteligente**: OCR + Análise de cores
- **Anti-Detecção**: Padrões não repetitivos

### 🌐 Interface Moderna
- **Tempo Real**: WebSocket para updates instantâneos
- **Responsive**: Funciona em qualquer tela
- **Intuitivo**: Fácil de usar mesmo para iniciantes
- **Completo**: Todas as funcionalidades em um lugar

### 📊 Estatísticas Avançadas
- **Análise de Desempenho**: Eficiência por sessão
- **Histórico Completo**: Todas as sessões salvas
- **Monitoramento**: Estado do jogo em tempo real
- **Relatórios**: Estatísticas detalhadas

---

## 🎯 Conclusão

Este bot foi desenvolvido para ser:
- 🟢 **Fácil** de instalar e usar
- 🛡️ **Seguro** e indetectável
- 🔧 **Completo** em funcionalidades
- 📚 **Bem documentado** e suportado

**Divirta-se e bom jogo!** 🏰⚔️

---

*© 2025 Bot Tibia Indetectável - Versão 2.0*