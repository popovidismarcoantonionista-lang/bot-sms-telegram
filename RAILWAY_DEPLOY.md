# 🚂 DEPLOY NO RAILWAY - GUIA COMPLETO

## 📋 Pré-requisitos

1. Conta no Railway ([railway.app](https://railway.app))
2. Conta no GitHub
3. Token do bot do Telegram

---

## 🚀 DEPLOY EM 5 MINUTOS

### **Método 1: Deploy Direto (MAIS FÁCIL)**

1. **Acesse o Railway:**
   - Vá para [railway.app](https://railway.app)
   - Faça login com GitHub

2. **Clique em "New Project"**

3. **Selecione "Deploy from GitHub repo"**

4. **Escolha o repositório:**
   ```
   popovidismarcoantonionista-lang/bot-sms-telegram
   ```

5. **Configure as Variáveis de Ambiente:**
   - Clique em "Variables"
   - Adicione as seguintes variáveis:

   ```env
   TELEGRAM_BOT_TOKEN=7548957030:AAF8208JFkZRdsEEdt7LTnZu0CCsqZNgqKc
   ADMIN_IDS=8126278368
   SMS_ACTIVATE_API_KEY=82c74f0d322857ed7A7ee311dAdf20cc
   PLUGGY_CLIENT_ID=08a122f1-1549-4a55-a3ea-c24114c44359
   PLUGGY_API_KEY=
   APEX_API_KEY=a7832009d1e84ea9c461959b2f771e10
   REFERRAL_BONUS=5.0
   REFERRAL_PERCENTAGE=5.0
   ```

6. **Deploy Automático:**
   - Railway vai detectar o `railway.json` e fazer deploy automaticamente
   - Aguarde 2-3 minutos

7. **Verificar Logs:**
   - Clique em "Deployments"
   - Veja os logs em tempo real
   - Procure por: "✅ Bot iniciado com sucesso!"

8. **Testar:**
   - Abra o Telegram
   - Envie `/start` para seu bot
   - Deve receber resposta instantânea

---

### **Método 2: Deploy via CLI do Railway**

```bash
# 1. Instalar Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Clonar repositório
git clone https://github.com/popovidismarcoantonionista-lang/bot-sms-telegram.git
cd bot-sms-telegram

# 4. Inicializar projeto Railway
railway init

# 5. Adicionar variáveis de ambiente
railway variables set TELEGRAM_BOT_TOKEN="seu_token"
railway variables set ADMIN_IDS="seu_id"
railway variables set SMS_ACTIVATE_API_KEY="sua_key"

# 6. Deploy
railway up

# 7. Ver logs
railway logs
```

---

## 📊 VARIÁVEIS DE AMBIENTE NECESSÁRIAS

| Variável | Obrigatório | Exemplo |
|----------|------------|---------|
| `TELEGRAM_BOT_TOKEN` | ✅ Sim | `123456:ABC-DEF...` |
| `ADMIN_IDS` | ✅ Sim | `123456789` |
| `SMS_ACTIVATE_API_KEY` | ✅ Sim | `abc123...` |
| `PLUGGY_CLIENT_ID` | ⚠️ Opcional | `uuid-here` |
| `PLUGGY_API_KEY` | ⚠️ Opcional | `key-here` |
| `APEX_API_KEY` | ⚠️ Opcional | `key-here` |
| `REFERRAL_BONUS` | ⚠️ Opcional | `5.0` |
| `REFERRAL_PERCENTAGE` | ⚠️ Opcional | `5.0` |

---

## 🔧 CONFIGURAÇÃO DO RAILWAY

### **railway.json** (já está no repositório)
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "python bot.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### **Procfile** (já está no repositório)
```
worker: python bot.py
```

---

## ✅ CHECKLIST DE DEPLOY

- [ ] Repositório está no GitHub
- [ ] Arquivos corretos (_FIXED renomeados)
- [ ] Token do bot válido
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy iniciado no Railway
- [ ] Logs mostram "Bot iniciado"
- [ ] Bot responde no Telegram

---

## 🐛 TROUBLESHOOTING RAILWAY

### **1. Build falhou**
```bash
# Verificar se requirements.txt está correto
cat requirements.txt

# Verificar versão do Python
python --version
```

**Solução:** Certifique-se que `runtime.txt` tem `python-3.11.0`

---

### **2. Bot não inicia**
Verifique os logs:
```bash
railway logs
```

**Erros comuns:**
- `ModuleNotFoundError` → requirements.txt incompleto
- `TOKEN inválido` → Variável TELEGRAM_BOT_TOKEN errada
- `Database locked` → Use aiosqlite (já configurado)

---

### **3. Deploy OK mas bot não responde**

**Verificar:**
1. Logs mostram "Bot conectado: @seu_bot"?
2. Variável TELEGRAM_BOT_TOKEN está correta?
3. Você enviou /start no Telegram?

**Testar localmente:**
```bash
# Baixar logs do Railway
railway logs > logs.txt

# Ver últimas linhas
tail -50 logs.txt
```

---

### **4. Bot trava depois de um tempo**

**Causa:** Webhook ativo ou múltiplas instâncias

**Solução:**
```bash
# Desabilitar webhook
curl https://api.telegram.org/bot<TOKEN>/deleteWebhook

# Verificar no Railway
railway ps
```

---

### **5. Database não persiste**

Railway reseta o filesystem a cada deploy.

**Solução:** Use Railway Database (PostgreSQL):

```bash
# Adicionar PostgreSQL
railway add postgresql

# Instalar psycopg2
pip install psycopg2-binary

# Atualizar database.py para usar PostgreSQL
```

---

## 📈 MONITORAMENTO

### **Ver logs em tempo real:**
```bash
railway logs --follow
```

### **Status do serviço:**
```bash
railway status
```

### **Métricas:**
- Acesse Railway Dashboard
- Veja CPU, Memory, Network

---

## 💰 CUSTOS

**Railway Free Plan:**
- ✅ $5 de crédito grátis/mês
- ✅ 500 horas de execução
- ✅ Suficiente para 1 bot pequeno

**Dica:** Bot Telegram usa MUITO pouco recurso (~10MB RAM)

---

## 🔄 ATUALIZAÇÕES AUTOMÁTICAS

Railway faz deploy automático a cada push no GitHub:

```bash
# Local
git add .
git commit -m "Atualização"
git push

# Railway detecta e faz redeploy automaticamente
```

---

## 🆘 SUPORTE

**Logs não ajudaram?**

1. Vá para [railway.app/help](https://railway.app/help)
2. Ou Discord: [discord.gg/railway](https://discord.gg/railway)

---

## 📱 TESTE FINAL

Depois do deploy:

```bash
# 1. Ver logs
railway logs

# 2. Procure por esta linha:
# "✅ Bot conectado: @seu_bot"

# 3. Abra o Telegram
# 4. Envie: /start
# 5. Deve responder em 1 segundo
```

---

## ⚡ DEPLOY RÁPIDO (1 COMANDO)

```bash
railway login && railway init && railway variables set TELEGRAM_BOT_TOKEN="SEU_TOKEN" && railway up
```

---

**🎉 Pronto! Seu bot está no ar 24/7 no Railway!**

---

## 🔗 Links Úteis

- [Railway Docs](https://docs.railway.app)
- [Repositório](https://github.com/popovidismarcoantonionista-lang/bot-sms-telegram)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

**Última atualização:** {datetime.now().strftime("%d/%m/%Y %H:%M")}
