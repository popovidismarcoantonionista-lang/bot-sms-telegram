# 🚂 Guia Completo de Deploy no Railway

## 📋 Pré-requisitos (Todos Prontos!)

- ✅ Repositório GitHub: **bot-sms-telegram**
- ✅ Arquivo **.env** configurado com todas as credenciais
- ✅ **Dockerfile** presente
- ✅ **requirements.txt** presente
- ✅ **Procfile** presente

---

## 🎯 Passo a Passo - Deploy no Railway

### 【 PASSO 1 】 Criar Conta no Railway

1. Acesse: **https://railway.app**
2. Clique em **"Login"** ou **"Start a New Project"**
3. Escolha uma opção de login:
   - ✨ **Login com GitHub** (RECOMENDADO)
   - 📧 Login com Email
4. Autorize o Railway a acessar seus repositórios

💡 **VANTAGEM:** $5 de crédito grátis por mês no plano gratuito

---

### 【 PASSO 2 】 Criar Novo Projeto

1. No dashboard do Railway, clique em **"New Project"**
2. Selecione **"Deploy from GitHub repo"**
3. Você verá uma lista dos seus repositórios
4. Procure e selecione:
   ```
   📦 popovidismarcoantonionista-lang/bot-sms-telegram
   ```
5. Clique no repositório para selecioná-lo

---

### 【 PASSO 3 】 Configuração Automática

O Railway detectará automaticamente:
- ✅ **Dockerfile** (para build da imagem)
- ✅ **requirements.txt** (dependências Python)
- ✅ **Procfile** (comando de start)
- ✅ **.env** (variáveis de ambiente)

⚡ **O Railway começará o build automaticamente!**

---

### 【 PASSO 4 】 Aguardar o Build

1. Você verá o log de build em tempo real
2. Processo de build:
   - Installing dependencies...
   - Building Docker image...
   - Starting application...
3. Status: **Building** → **Deploying** → **Running**

⏱️ **Tempo estimado:** 2-5 minutos

---

### 【 PASSO 5 】 Verificar Variáveis de Ambiente (Opcional)

O .env já está no repositório, mas você pode verificar:

1. Clique na sua aplicação
2. Vá em **"Variables"** ou **"Settings"**
3. Verifique se as variáveis estão carregadas:
   - `TELEGRAM_BOT_TOKEN`
   - `APEX_API_KEY`
   - `DATABASE_URL`
   - etc.

---

### 【 PASSO 6 】 Verificar Logs

1. Na dashboard do projeto
2. Clique em **"Deployments"**
3. Clique no deployment mais recente
4. Veja os logs em tempo real:
   ```
   Bot iniciando...
   Conectando ao Telegram...
   Bot ativo e aguardando mensagens...
   ```

✅ **Se aparecer "Bot started successfully", está funcionando!**

---

### 【 PASSO 7 】 Testar o Bot no Telegram

1. Abra o **Telegram**
2. Procure: **@smstemporariobaratobot**
3. Ou acesse: **https://t.me/smstemporariobaratobot**
4. Envie: `/start`
5. O bot deve responder!

**📱 Teste outros comandos:**
- `/balance` - Ver saldo
- `/services` - Ver serviços
- `/order` - Fazer pedido
- `/help` - Ajuda

---

## 🔧 Configurações Importantes do Railway

### 💾 Banco de Dados
- Seu bot usa SQLite (arquivo local)
- ✅ Já configurado no .env: `DATABASE_URL=sqlite:///bot_database.db`

### 🔄 Auto-Restart
- O Railway reinicia automaticamente se o bot cair
- ✅ Configurado automaticamente

### 📊 Monitoramento
- CPU Usage
- Memory Usage
- Network Traffic
- Acesse em "Metrics" no dashboard

### 💳 Billing
- **Plano Gratuito:** $5/mês de crédito
- Cobrado apenas pelo uso real
- Bot leve: **~$0.50-2/mês**

---

## ⚠️ Troubleshooting - Problemas Comuns

### ❌ PROBLEMA 1: Build falhou

**Solução:**
1. Verifique os logs de build
2. Certifique-se que requirements.txt está correto
3. Tente "Redeploy" no Railway

### ❌ PROBLEMA 2: Bot não responde no Telegram

**Solução:**
1. Verifique os logs: "Telegram bot token is invalid"?
2. Confirme `TELEGRAM_BOT_TOKEN` no .env
3. Teste o token:
   ```bash
   curl https://api.telegram.org/bot<TOKEN>/getMe
   ```

### ❌ PROBLEMA 3: Apex API erro

**Solução:**
1. Verifique `APEX_API_KEY` no .env
2. **Adicione créditos no Apex** (saldo atual: R$ 0,00)
3. Teste API:
   ```bash
   curl -X POST https://apexseguidores.com/api/v2 \
     -d "action=balance&key=SEU_API_KEY"
   ```

### ❌ PROBLEMA 4: Deployment crashando

**Solução:**
1. Verifique logs: "ModuleNotFoundError"?
2. Adicione módulo faltante no `requirements.txt`
3. Push para GitHub e redeploy automático

---

## 🎯 Comandos Úteis do Railway CLI (Opcional)

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Linkar projeto
railway link

# Ver logs em tempo real
railway logs

# Abrir dashboard
railway open

# Redeploy
railway up
```

---

## ✅ Checklist Final

### 📋 PREPARAÇÃO
- [ ] Conta Railway criada
- [ ] Repositório GitHub conectado
- [ ] Projeto criado no Railway

### 📋 DEPLOYMENT
- [ ] Build completado com sucesso
- [ ] Aplicação rodando (status: Running)
- [ ] Logs mostrando "Bot started"

### 📋 TESTES
- [ ] Bot responde no Telegram
- [ ] Comandos funcionando
- [ ] Apex API integrada

### 📋 PÓS-DEPLOY
- [ ] **Adicionar créditos no Apex** (IMPORTANTE!)
- [ ] Configurar Pluggy PIX (se usar)
- [ ] Testar fluxo completo de compra

---

## 🔗 Links Importantes

- 🚂 **Railway:** https://railway.app
- 📦 **Repositório:** https://github.com/popovidismarcoantonionista-lang/bot-sms-telegram
- 🤖 **Bot Telegram:** https://t.me/smstemporariobaratobot
- 💎 **Apex Seguidores:** https://apexseguidores.com

---

## 📊 Credenciais Configuradas

Todas as credenciais já estão no arquivo `.env`:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=7958563749:AAGUWtp2ISNcegnOHAr1Hfqu_dpigJPJR8s
TELEGRAM_ADMIN_ID=7958563749

# Apex Seguidores
APEX_API_KEY=207d62f08e4f76b9a8384facc27272e4

# Database
DATABASE_URL=sqlite:///bot_database.db

# ... e outras configurações
```

---

## 💰 Adicionar Créditos no Apex

⚠️ **ATENÇÃO:** Saldo atual é R$ 0,00

**Passos:**
1. Acesse: https://apexseguidores.com
2. Faça login com sua conta
3. Vá em "Adicionar Fundos" ou "Add Funds"
4. Escolha o método de pagamento (PIX, cartão, etc)
5. Adicione créditos (mínimo recomendado: **R$ 20**)

**Serviços disponíveis (35 no total):**
- Instagram Seguidores 🥇 - R$ 30,00/1000
- Instagram Seguidores 🥉 - R$ 14,00/1000
- Instagram Seguidores 🥈 - R$ 20,00/1000
- E muitos outros...

---

## 🎊 Pronto!

Seu bot está configurado e pronto para deploy no Railway!

**Resumo:**
1. ✅ Acesse **railway.app**
2. ✅ Login com GitHub
3. ✅ Deploy do repositório **bot-sms-telegram**
4. ✅ Aguarde 2-5 minutos
5. ✅ Teste no Telegram
6. 💰 Adicione créditos no Apex

**Custo mensal estimado:** $0.50-2.00 (você tem $5 grátis!)

---

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs no Railway
2. Confira as variáveis de ambiente
3. Teste as APIs individualmente
4. Consulte este guia novamente

**Boa sorte com seu bot! 🚀**
