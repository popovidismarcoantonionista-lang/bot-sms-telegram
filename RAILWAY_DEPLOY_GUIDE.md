# 🚂 GUIA COMPLETO DE DEPLOY NO RAILWAY

## 📋 PRÉ-REQUISITOS

Antes de começar, você precisa ter:
- ✅ Conta no [Railway](https://railway.app)
- ✅ Conta no [Neon.tech](https://neon.tech) (PostgreSQL gratuito)
- ✅ Token do Telegram Bot (via @BotFather)
- ✅ API Key do SMS-Activate
- ✅ Credenciais do Pluggy.ai

---

## 🚀 PASSO A PASSO COMPLETO

### **1. Criar Banco de Dados PostgreSQL (Neon.tech)**

1. Acesse [neon.tech](https://neon.tech) e faça login
2. Clique em **"Create Project"**
3. Escolha uma região (de preferência US East)
4. Copie a **Connection String**:
   ```
   postgresql://user:password@host/dbname?sslmode=require
   ```
5. Guarde essa string, vamos usar no Railway

---

### **2. Fazer Deploy no Railway**

#### **Opção 1: Deploy via GitHub (RECOMENDADO)**

1. Acesse [railway.app](https://railway.app)
2. Faça login com GitHub
3. Clique em **"New Project"**
4. Escolha **"Deploy from GitHub repo"**
5. Selecione: `popovidismarcoantonionista-lang/bot-sms-telegram`
6. Railway vai detectar automaticamente o Python

#### **Opção 2: Deploy via CLI**

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Fazer login
railway login

# No diretório do bot
railway init
railway up
```

---

### **3. Configurar Variáveis de Ambiente no Railway**

No painel do Railway, vá em **"Variables"** e adicione:

```env
# Telegram
TELEGRAM_BOT_TOKEN=seu_token_do_botfather
TELEGRAM_ADMIN_ID=seu_telegram_user_id

# Pluggy.ai
PLUGGY_CLIENT_ID=seu_client_id
PLUGGY_CLIENT_SECRET=seu_client_secret
PLUGGY_ENVIRONMENT=production
PLUGGY_ITEM_ID=seu_item_id

# SMS-Activate
SMS_ACTIVATE_API_KEY=sua_api_key

# Database (cole a string do Neon.tech)
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require

# PIX
PIX_KEY=sua_chave_pix@email.com
PIX_NAME=Seu Nome Completo

# Opcional
DEBUG=false
CHECK_PAYMENT_INTERVAL=30
MIN_DEPOSIT=1.00
MAX_DEPOSIT=1000.00
```

**⚠️ IMPORTANTE:** Depois de adicionar as variáveis, clique em **"Deploy"** ou espere o redeploy automático.

---

### **4. Verificar Deploy**

1. No Railway, vá em **"Deployments"**
2. Clique no deploy mais recente
3. Veja os **Logs** em tempo real
4. Procure por:
   ```
   ✅ "Starting bot..."
   ✅ "Database initialized successfully"
   ```

Se aparecer erro, copie e me envie!

---

## 🔍 TROUBLESHOOTING RAILWAY

### **Problema: "ModuleNotFoundError"**
**Solução:** Verifique se `requirements.txt` está correto
```bash
# Localmente, teste:
pip install -r requirements.txt
```

### **Problema: "Config validation error"**
**Solução:** Verifique se TODAS as variáveis de ambiente estão configuradas no Railway

### **Problema: Bot não responde**
**Possíveis causas:**
1. ❌ TELEGRAM_BOT_TOKEN inválido
2. ❌ Bot não está rodando (veja logs no Railway)
3. ❌ Erro no banco de dados

**Debug:**
1. Vá em Railway → Seu projeto → **Logs**
2. Procure por erros em vermelho
3. Cole os erros aqui para eu ajudar

### **Problema: "Database connection failed"**
**Solução:**
1. Verifique se DATABASE_URL está correto
2. Certifique-se que tem `?sslmode=require` no final
3. Teste a conexão no Neon.tech dashboard

---

## 📊 MONITORAMENTO

### **Ver Logs em Tempo Real:**
```bash
# Via CLI
railway logs
```

Ou pelo dashboard: **Railway → Seu Projeto → Logs**

### **Restart do Bot:**
```bash
# Via CLI
railway restart

# Ou no dashboard: Settings → Restart
```

---

## 💰 CUSTOS

- **Railway:** $5/mês (500 horas gratuitas no trial)
- **Neon.tech:** GRATUITO (até 3GB)
- **Total:** ~$5/mês (ou grátis no trial)

---

## 🎯 CHECKLIST FINAL

Antes de considerar concluído:

- [ ] PostgreSQL criado no Neon.tech
- [ ] Projeto criado no Railway
- [ ] Todas as variáveis de ambiente configuradas
- [ ] Deploy realizado com sucesso
- [ ] Logs sem erros
- [ ] Bot respondendo no Telegram (`/start`)
- [ ] Testado comando `/comprar`

---

## 📞 PRÓXIMOS PASSOS APÓS DEPLOY

1. **Teste o Bot:**
   - Envie `/start` no Telegram
   - Verifique se responde

2. **Configure PIX:**
   - Certifique-se que a chave PIX está correta
   - Teste um depósito pequeno (R$ 1,00)

3. **Monitore:**
   - Verifique logs no Railway
   - Acompanhe transações no banco

---

**🆘 Precisa de ajuda?**
Se algo der errado, me envie:
1. Screenshot dos logs do Railway
2. Mensagem de erro completa
3. Resposta do bot (se houver)

Boa sorte com o deploy! 🚀
