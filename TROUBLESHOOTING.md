# 🔧 GUIA DE TROUBLESHOOTING

## ❌ Bot não responde? Siga este guia:

### 1️⃣ VERIFICAÇÃO RÁPIDA

Execute o diagnóstico:
```bash
python diagnostico.py
```

Se todos os testes passarem, vá para o passo 2.

---

### 2️⃣ TESTE COM BOT MINIMALISTA

```bash
python bot_minimal.py
```

**Se este bot funcionar:**
- ✅ Token está OK
- ✅ Internet está OK
- ❌ Problema está no código do bot principal

**Se este bot NÃO funcionar:**
- Problema está no token ou internet

---

### 3️⃣ VERIFICAR TOKEN

1. Abra o Telegram
2. Busque por `@BotFather`
3. Envie `/mybots`
4. Selecione seu bot
5. Clique em "API Token"
6. Copie o token
7. Cole no arquivo `.env`:
   ```
   TELEGRAM_BOT_TOKEN=seu_token_aqui
   ```

---

### 4️⃣ VERIFICAR DEPENDÊNCIAS

```bash
pip install -r requirements.txt --upgrade
```

---

### 5️⃣ CRIAR ARQUIVO .env

Se não existir, crie:
```bash
cp .env.example .env
```

Depois edite o `.env` com suas credenciais.

---

### 6️⃣ USAR ARQUIVOS CORRIGIDOS

```bash
# Se existirem os arquivos _FIXED:
mv bot_FIXED.py bot.py
mv database_FIXED.py database.py
mv config_FIXED.py config.py

# Executar
python bot.py
```

---

### 7️⃣ VERIFICAR SE O BOT ESTÁ RODANDO

```bash
# Verificar processos
ps aux | grep bot.py

# Se estiver rodando em duplicata, mate os processos:
pkill -f bot.py

# Execute novamente
python bot.py
```

---

### 8️⃣ LOGS E DEBUG

Adicione no início do bot.py:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Execute e veja os logs detalhados.

---

### 9️⃣ PROBLEMAS COMUNS

| Problema | Solução |
|----------|---------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `TOKEN inválido` | Verificar token no BotFather |
| `Database locked` | Fechar todas as instâncias do bot |
| `No module named 'telegram'` | `pip install python-telegram-bot==20.7` |
| Bot não recebe mensagens | Verificar se o polling está ativo |
| `Conflict: terminated by other getUpdates` | Só uma instância pode rodar |

---

### 🔟 CHECKLIST FINAL

- [ ] Token correto no .env
- [ ] Dependências instaladas
- [ ] Apenas 1 instância rodando
- [ ] Enviou /start no Telegram
- [ ] Internet funcionando
- [ ] Python 3.8+ instalado

---

## 🆘 AINDA NÃO FUNCIONA?

Execute linha por linha:

```bash
# 1. Limpar tudo
pkill -f bot.py
rm bot_database.db

# 2. Reinstalar dependências
pip uninstall python-telegram-bot -y
pip install python-telegram-bot==20.7

# 3. Testar minimalista
python bot_minimal.py
```

Se o bot_minimal funcionar, o problema é no código principal.

---

**Última atualização:** 08/11/2025 17:38
