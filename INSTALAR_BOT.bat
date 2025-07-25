@echo off
chcp 65001 > nul
color 0A
title Instalador do Bot Tibia - Versão 2.0

echo.
echo ╔════════════════════════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                                                ║
echo ║                          🏰 BOT TIBIA INDETECTÁVEL - INSTALADOR 🏰                          ║
echo ║                                                                                                ║
echo ║                                      Versão 2.0                                               ║
echo ║                                                                                                ║
echo ╚════════════════════════════════════════════════════════════════════════════════════════════════╝
echo.
echo ⚠️  IMPORTANTE: Execute como Administrador para melhor compatibilidade
echo.
echo 📋 Este instalador irá:
echo    • Verificar se Python, Node.js e Git estão instalados
echo    • Instalar dependências do backend (Python)
echo    • Instalar dependências do frontend (Node.js)
echo    • Configurar o ambiente do bot
echo    • Criar atalhos para execução
echo.
pause

:CHECK_PYTHON
echo.
echo 🔍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    echo.
    echo 📥 Por favor, instale o Python primeiro:
    echo    1. Acesse: https://www.python.org/downloads/
    echo    2. Baixe a versão mais recente
    echo    3. ⚠️  IMPORTANTE: Marque "Add Python to PATH" durante a instalação
    echo    4. Execute este instalador novamente
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Python encontrado
    python --version
)

:CHECK_NODE
echo.
echo 🔍 Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js não encontrado!
    echo.
    echo 📥 Por favor, instale o Node.js primeiro:
    echo    1. Acesse: https://nodejs.org/
    echo    2. Baixe a versão LTS (recomendada)
    echo    3. Execute a instalação normalmente
    echo    4. Execute este instalador novamente
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Node.js encontrado
    node --version
)

:CHECK_YARN
echo.
echo 🔍 Verificando Yarn...
yarn --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Yarn não encontrado. Instalando...
    npm install -g yarn
    if %errorlevel% neq 0 (
        echo ❌ Erro ao instalar Yarn
        echo 💡 Tentando usar npm diretamente...
        set USE_NPM=1
    ) else (
        echo ✅ Yarn instalado com sucesso
        yarn --version
    )
) else (
    echo ✅ Yarn encontrado
    yarn --version
)

:INSTALL_BACKEND
echo.
echo 📦 Instalando dependências do backend...
cd backend
echo    • Instalando bibliotecas Python...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependências do backend
    echo 💡 Tentando com --user...
    pip install --user -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Falha na instalação das dependências do backend
        echo 📞 Verifique sua conexão com a internet e tente novamente
        pause
        exit /b 1
    )
)
echo ✅ Dependências do backend instaladas
cd ..

:INSTALL_FRONTEND
echo.
echo 📦 Instalando dependências do frontend...
cd frontend
if defined USE_NPM (
    echo    • Usando npm...
    npm install
) else (
    echo    • Usando yarn...
    yarn install
)
if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependências do frontend
    echo 💡 Tentando com npm...
    npm install
    if %errorlevel% neq 0 (
        echo ❌ Falha na instalação das dependências do frontend
        echo 📞 Verifique sua conexão com a internet e tente novamente
        pause
        exit /b 1
    )
)
echo ✅ Dependências do frontend instaladas
cd ..

:CREATE_SHORTCUTS
echo.
echo 🔗 Criando atalhos de execução...

echo @echo off > EXECUTAR_BOT.bat
echo chcp 65001 ^> nul >> EXECUTAR_BOT.bat
echo color 0A >> EXECUTAR_BOT.bat
echo title Bot Tibia - Executando >> EXECUTAR_BOT.bat
echo. >> EXECUTAR_BOT.bat
echo echo ╔════════════════════════════════════════════════════════════════════════════════════════════════╗ >> EXECUTAR_BOT.bat
echo echo ║                            🏰 BOT TIBIA INDETECTÁVEL - EXECUTANDO 🏰                         ║ >> EXECUTAR_BOT.bat
echo echo ╚════════════════════════════════════════════════════════════════════════════════════════════════╝ >> EXECUTAR_BOT.bat
echo echo. >> EXECUTAR_BOT.bat
echo echo ⚠️  IMPORTANTE: >> EXECUTAR_BOT.bat
echo echo    • Certifique-se de que o Tibia está aberto >> EXECUTAR_BOT.bat
echo echo    • Configure o bot na interface web que abrirá >> EXECUTAR_BOT.bat
echo echo    • Mantenha esta janela aberta enquanto usa o bot >> EXECUTAR_BOT.bat
echo echo. >> EXECUTAR_BOT.bat
echo echo 🚀 Iniciando backend... >> EXECUTAR_BOT.bat
echo start /B python backend/server.py >> EXECUTAR_BOT.bat
echo echo ⏳ Aguarde 5 segundos... >> EXECUTAR_BOT.bat
echo timeout /t 5 /nobreak ^> nul >> EXECUTAR_BOT.bat
echo echo 🌐 Iniciando frontend... >> EXECUTAR_BOT.bat
echo cd frontend >> EXECUTAR_BOT.bat
echo if defined USE_NPM ^( >> EXECUTAR_BOT.bat
echo     npm start >> EXECUTAR_BOT.bat
echo ^) else ^( >> EXECUTAR_BOT.bat
echo     yarn start >> EXECUTAR_BOT.bat
echo ^) >> EXECUTAR_BOT.bat

echo @echo off > PARAR_BOT.bat
echo chcp 65001 ^> nul >> PARAR_BOT.bat
echo color 0C >> PARAR_BOT.bat
echo title Bot Tibia - Parando >> PARAR_BOT.bat
echo echo 🛑 Parando Bot Tibia... >> PARAR_BOT.bat
echo taskkill /F /IM python.exe /T 2^>nul >> PARAR_BOT.bat
echo taskkill /F /IM node.exe /T 2^>nul >> PARAR_BOT.bat
echo echo ✅ Bot parado com sucesso! >> PARAR_BOT.bat
echo timeout /t 3 /nobreak ^> nul >> PARAR_BOT.bat

echo @echo off > VERIFICAR_INSTALACAO.bat
echo chcp 65001 ^> nul >> VERIFICAR_INSTALACAO.bat
echo color 0B >> VERIFICAR_INSTALACAO.bat
echo title Bot Tibia - Verificação >> VERIFICAR_INSTALACAO.bat
echo echo 🔍 Verificando instalação... >> VERIFICAR_INSTALACAO.bat
echo echo. >> VERIFICAR_INSTALACAO.bat
echo python --version ^|^| echo ❌ Python não encontrado >> VERIFICAR_INSTALACAO.bat
echo node --version ^|^| echo ❌ Node.js não encontrado >> VERIFICAR_INSTALACAO.bat
echo echo. >> VERIFICAR_INSTALACAO.bat
echo echo 📁 Verificando arquivos... >> VERIFICAR_INSTALACAO.bat
echo if exist backend\\server.py ^(echo ✅ Backend encontrado^) else ^(echo ❌ Backend não encontrado^) >> VERIFICAR_INSTALACAO.bat
echo if exist frontend\\package.json ^(echo ✅ Frontend encontrado^) else ^(echo ❌ Frontend não encontrado^) >> VERIFICAR_INSTALACAO.bat
echo if exist backend\\requirements.txt ^(echo ✅ Requirements encontrado^) else ^(echo ❌ Requirements não encontrado^) >> VERIFICAR_INSTALACAO.bat
echo echo. >> VERIFICAR_INSTALACAO.bat
echo echo 🎯 Se todos os itens estão ✅, a instalação está OK! >> VERIFICAR_INSTALACAO.bat
echo pause >> VERIFICAR_INSTALACAO.bat

echo ✅ Atalhos criados

:FINISH
echo.
echo ╔════════════════════════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                                                ║
echo ║                          🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO! 🎉                             ║
echo ║                                                                                                ║
echo ╚════════════════════════════════════════════════════════════════════════════════════════════════╝
echo.
echo 📋 Próximos passos:
echo.
echo    1. 🎮 Abra o Tibia e entre com seu personagem
echo    2. 🚀 Clique duplo em "EXECUTAR_BOT.bat"
echo    3. 🌐 Aguarde a interface web abrir automaticamente
echo    4. ⚙️  Configure o bot na aba "Configurações"
echo    5. ▶️  Clique em "Iniciar" para começar a usar
echo.
echo 🔧 Arquivos importantes:
echo    • EXECUTAR_BOT.bat - Inicia o bot
echo    • PARAR_BOT.bat - Para o bot completamente
echo    • VERIFICAR_INSTALACAO.bat - Verifica se tudo está OK
echo.
echo 📖 Consulte o manual "MANUAL_INSTALACAO.md" para mais detalhes
echo.
echo 🆘 Em caso de problemas:
echo    • Execute "VERIFICAR_INSTALACAO.bat"
echo    • Verifique se o Tibia está aberto
echo    • Certifique-se de que tem conexão com a internet
echo.
echo ✨ Divirta-se e bom jogo! ✨
echo.
pause