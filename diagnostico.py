#!/usr/bin/env python3
"""
DIAGNÓSTICO DO BOT - Verifica todos os problemas possíveis
"""

import asyncio
import sys
import os

print("🔍 INICIANDO DIAGNÓSTICO...")
print("=" * 70)

# 1. VERIFICAR DEPENDÊNCIAS
print("\n📦 Verificando dependências...")
dependencias = {
    "telegram": "python-telegram-bot",
    "aiosqlite": "aiosqlite",
    "dotenv": "python-dotenv"
}

missing = []
for module, package in dependencias.items():
    try:
        if module == "telegram":
            import telegram
            print(f"  ✅ {package}: {telegram.__version__}")
        elif module == "aiosqlite":
            import aiosqlite
            print(f"  ✅ {package}: instalado")
        elif module == "dotenv":
            from dotenv import load_dotenv
            print(f"  ✅ {package}: instalado")
    except ImportError:
        missing.append(package)
        print(f"  ❌ {package}: NÃO INSTALADO")

if missing:
    print(f"\n❌ INSTALE AS DEPENDÊNCIAS:")
    print(f"   pip install {' '.join(missing)}")
    sys.exit(1)

# 2. CARREGAR .ENV
print("\n⚙️  Verificando .env...")
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

if not TOKEN:
    print("  ❌ TELEGRAM_BOT_TOKEN não encontrado no .env")
    print("\n💡 Crie um arquivo .env com:")
    print("   TELEGRAM_BOT_TOKEN=seu_token_aqui")
    sys.exit(1)

print(f"  ✅ Token encontrado: {TOKEN[:15]}...")

# 3. TESTAR CONEXÃO COM TELEGRAM
print("\n📡 Testando conexão com Telegram...")

async def test_connection():
    try:
        from telegram import Bot
        bot = Bot(token=TOKEN)

        # Testar getMe
        me = await bot.get_me()
        print(f"  ✅ Conectado ao bot: @{me.username}")
        print(f"  📱 Nome: {me.first_name}")
        print(f"  🆔 ID: {me.id}")
        return True
    except Exception as e:
        print(f"  ❌ Erro na conexão: {e}")
        return False

# Executar teste
resultado = asyncio.run(test_connection())

if not resultado:
    print("\n❌ NÃO CONSEGUIU CONECTAR AO TELEGRAM")
    print("\n💡 Possíveis causas:")
    print("   1. Token inválido ou expirado")
    print("   2. Sem conexão com internet")
    print("   3. Firewall bloqueando")
    sys.exit(1)

# 4. TESTAR DATABASE
print("\n💾 Testando database...")

async def test_database():
    try:
        import aiosqlite

        # Criar database de teste
        conn = await aiosqlite.connect(":memory:")

        # Criar tabela
        await conn.execute("""
            CREATE TABLE test (
                id INTEGER PRIMARY KEY,
                value TEXT
            )
        """)

        # Inserir dado
        await conn.execute("INSERT INTO test (value) VALUES (?)", ("teste",))
        await conn.commit()

        # Ler dado
        cursor = await conn.execute("SELECT value FROM test")
        row = await cursor.fetchone()

        await conn.close()

        if row and row[0] == "teste":
            print("  ✅ Database funcional")
            return True
        else:
            print("  ❌ Erro ao ler do database")
            return False

    except Exception as e:
        print(f"  ❌ Erro no database: {e}")
        return False

resultado_db = asyncio.run(test_database())

if not resultado_db:
    print("\n❌ PROBLEMA NO DATABASE")
    sys.exit(1)

# 5. VERIFICAR ARQUIVOS
print("\n📂 Verificando arquivos necessários...")

arquivos_necessarios = {
    "bot.py": "ou bot_FIXED.py",
    "config.py": "ou config_FIXED.py",
    "database.py": "ou database_FIXED.py"
}

for arquivo, alternativa in arquivos_necessarios.items():
    arquivo_fixed = arquivo.replace(".py", "_FIXED.py")

    if os.path.exists(arquivo):
        print(f"  ✅ {arquivo}")
    elif os.path.exists(arquivo_fixed):
        print(f"  ⚠️  {arquivo} não encontrado, mas {arquivo_fixed} existe")
        print(f"     Execute: mv {arquivo_fixed} {arquivo}")
    else:
        print(f"  ❌ {arquivo} NÃO ENCONTRADO")

print("\n" + "=" * 70)
print("✅ DIAGNÓSTICO COMPLETO")
print("\n💡 Se todos os testes passaram mas o bot não responde:")
print("   1. O bot está rodando? Execute: python bot.py")
print("   2. Você enviou /start no Telegram?")
print("   3. Verifique os logs do bot")
