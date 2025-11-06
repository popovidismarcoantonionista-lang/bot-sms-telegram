#!/usr/bin/env python3
"""
Script de Diagnóstico do Bot SMS Telegram
Verifica configurações e conexões antes de rodar o bot
"""

import os
import sys
from pathlib import Path

print("🔍 DIAGNÓSTICO DO BOT SMS TELEGRAM\n")
print("="*50)

# 1. Check Python version
print("\n1️⃣  VERIFICANDO PYTHON:")
print(f"   Versão: {sys.version}")
if sys.version_info < (3, 8):
    print("   ❌ ERRO: Python 3.8+ é necessário!")
else:
    print("   ✅ Versão OK")

# 2. Check .env file
print("\n2️⃣  VERIFICANDO ARQUIVO .env:")
env_path = Path('.env')
if env_path.exists():
    print("   ✅ Arquivo .env encontrado")

    # Load and check required vars
    from dotenv import load_dotenv
    load_dotenv()

    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_ADMIN_ID',
        'PLUGGY_CLIENT_ID',
        'PLUGGY_CLIENT_SECRET',
        'PLUGGY_ITEM_ID',
        'SMS_ACTIVATE_API_KEY',
        'DATABASE_URL',
        'PIX_KEY'
    ]

    print("\n   Variáveis de ambiente:")
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show partial value for security
            if 'TOKEN' in var or 'KEY' in var or 'SECRET' in var:
                display = value[:10] + "..." if len(value) > 10 else "***"
            else:
                display = value
            print(f"   ✅ {var}: {display}")
        else:
            print(f"   ❌ {var}: NÃO CONFIGURADO")
            missing.append(var)

    if missing:
        print(f"\n   ⚠️  FALTAM {len(missing)} variáveis obrigatórias!")
        print(f"   Configure: {', '.join(missing)}")
    else:
        print("\n   ✅ Todas as variáveis configuradas!")

else:
    print("   ❌ Arquivo .env NÃO encontrado!")
    print("   Execute: cp .env.example .env")
    sys.exit(1)

# 3. Check dependencies
print("\n3️⃣  VERIFICANDO DEPENDÊNCIAS:")
required_packages = [
    'telegram',
    'sqlalchemy',
    'requests',
    'dotenv',
    'flask'
]

for package in required_packages:
    try:
        __import__(package.replace('-', '_'))
        print(f"   ✅ {package}")
    except ImportError:
        print(f"   ❌ {package} não instalado")
        print(f"      Execute: pip install -r requirements.txt")

# 4. Test Telegram Token
print("\n4️⃣  TESTANDO TOKEN DO TELEGRAM:")
try:
    import requests
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token:
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get('ok'):
                bot_data = bot_info.get('result', {})
                print(f"   ✅ Token válido!")
                print(f"   Bot: @{bot_data.get('username', 'unknown')}")
                print(f"   Nome: {bot_data.get('first_name', 'unknown')}")
            else:
                print(f"   ❌ Token inválido!")
        else:
            print(f"   ❌ Erro HTTP {response.status_code}")
    else:
        print("   ❌ TELEGRAM_BOT_TOKEN não configurado")
except Exception as e:
    print(f"   ❌ Erro ao testar token: {e}")

# 5. Test Database Connection
print("\n5️⃣  TESTANDO CONEXÃO COM BANCO DE DADOS:")
try:
    from sqlalchemy import create_engine
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            print(f"   ✅ Conexão com banco OK")
            print(f"   URL: {db_url.split('@')[0]}@***")
    else:
        print("   ❌ DATABASE_URL não configurado")
except Exception as e:
    print(f"   ❌ Erro ao conectar: {e}")

# 6. Test SMS-Activate API
print("\n6️⃣  TESTANDO API SMS-ACTIVATE:")
try:
    api_key = os.getenv('SMS_ACTIVATE_API_KEY')
    if api_key:
        url = f"https://api.sms-activate.org/stubs/handler_api.php?api_key={api_key}&action=getBalance"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            result = response.text
            if result.startswith('ACCESS_BALANCE:'):
                balance = result.split(':')[1]
                print(f"   ✅ API OK - Saldo: ${balance}")
            else:
                print(f"   ❌ Resposta inesperada: {result}")
        else:
            print(f"   ❌ Erro HTTP {response.status_code}")
    else:
        print("   ❌ SMS_ACTIVATE_API_KEY não configurado")
except Exception as e:
    print(f"   ❌ Erro ao testar API: {e}")

# 7. Test Pluggy API
print("\n7️⃣  TESTANDO API PLUGGY:")
try:
    client_id = os.getenv('PLUGGY_CLIENT_ID')
    client_secret = os.getenv('PLUGGY_CLIENT_SECRET')

    if client_id and client_secret:
        env = os.getenv('PLUGGY_ENVIRONMENT', 'production')
        base_url = 'https://api.pluggy.ai' if env == 'production' else 'https://api.sandbox.pluggy.ai'

        response = requests.post(
            f"{base_url}/auth",
            json={"clientId": client_id, "clientSecret": client_secret},
            timeout=10
        )

        if response.status_code == 200:
            print(f"   ✅ Autenticação Pluggy OK")
            print(f"   Ambiente: {env}")
        else:
            print(f"   ❌ Erro na autenticação: {response.status_code}")
    else:
        print("   ❌ Credenciais Pluggy não configuradas")
except Exception as e:
    print(f"   ❌ Erro ao testar Pluggy: {e}")

print("\n" + "="*50)
print("\n✅ DIAGNÓSTICO COMPLETO!")
print("\nSe todos os itens estão OK, execute: python bot.py")
print("Se houver erros, corrija as configurações acima.\n")
