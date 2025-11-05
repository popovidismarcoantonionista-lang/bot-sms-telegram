# 🚀 GUIA DE DEPLOY CORRIGIDO - Bot SMS

## ✅ PROBLEMA IDENTIFICADO E CORRIGIDO

O bot não respondia porque estava configurado como "web service" mas deveria ser "worker service" (background).

## 📋 PASSOS PARA DEPLOY CORRETO

### Opção 1: Render.com (RECOMENDADO - FREE 24/7)

1. **Acesse**: https://render.com
2. **Login** com GitHub
3. **New + → Background Worker** (NÃO Web Service!)
4. **Selecione**: `bot-sms-telegram` repository
5. **Configure**:
   - **Name**: `bot-sms-telegram`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot_sms_telegram.py`
   - **Instance Type**: FREE

6. **Environment Variables** (adicione cada uma):
```
TELEGRAM_TOKEN=7958563749:AAGUWtp2ISNcegnOHAr1Hfqu_dpigJPJR8s
SMS_ACTIVATE_API_KEY=58f78469017177b5defd637edA3983d1
PLUGGY_CLIENT_ID=3d15ed55-b74a-4b7c-8bcc-430e80cf01ab
PLUGGY_CLIENT_SECRET=ccef002e-7935-452b-ace8-dde1db125e81
```

7. **Create Background Worker**
8. **Aguarde 2-3 minutos** → Bot online! ✅

---

### Opção 2: Railway.app (Alternativa FREE)

1. **Acesse**: https://railway.app
2. **Login** com GitHub
3. **New Project → Deploy from GitHub repo**
4. **Selecione**: `bot-sms-telegram`
5. **Settings → Environment Variables** (adicione as mesmas variáveis acima)
6. **Deploy automático!** ✅

---

### Opção 3: Heroku (Clássico)

```bash
# Instalar Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Criar app
heroku create bot-sms-telegram

# Adicionar variáveis
heroku config:set TELEGRAM_TOKEN="7958563749:AAGUWtp2ISNcegnOHAr1Hfqu_dpigJPJR8s"
heroku config:set SMS_ACTIVATE_API_KEY="58f78469017177b5defd637edA3983d1"
heroku config:set PLUGGY_CLIENT_ID="3d15ed55-b74a-4b7c-8bcc-430e80cf01ab"
heroku config:set PLUGGY_CLIENT_SECRET="ccef002e-7935-452b-ace8-dde1db125e81"

# Deploy
git push heroku main
```

---

## ✅ VERIFICAR SE BOT ESTÁ ONLINE

1. Abra Telegram
2. Busque: `@seu_bot`
3. Digite: `/start`
4. Se responder = **BOT FUNCIONANDO!** 🎉

---

## 🔧 TROUBLESHOOTING

### Bot não responde no Telegram?

**Verifique:**
1. ✅ Serviço está como "Background Worker" (não Web Service)
2. ✅ Todas as 4 variáveis de ambiente foram adicionadas
3. ✅ Logs mostram "🚀 Bot iniciado!"
4. ✅ Token do Telegram está correto

**Logs no Render:**
- Dashboard → Seu worker → "Logs"
- Deve mostrar: `🚀 Bot iniciado!`

**Reiniciar bot:**
- Dashboard → Settings → Manual Deploy → "Clear build cache & deploy"

---

## 💳 PAGAMENTOS AUTOMÁTICOS

O webhook está pronto em `webhook_server.py` mas precisa:

1. **Deploy separado** do webhook (como Web Service)
2. **URL pública** para o Pluggy chamar
3. **Configurar** no painel do Pluggy

### Deploy do Webhook (Render):

1. **New + → Web Service**
2. **Same repository**: `bot-sms-telegram`
3. **Build**: `pip install -r requirements.txt`
4. **Start**: `gunicorn webhook_server:app`
5. **Environment**: mesmas variáveis
6. **Deploy!**

Após deploy, você terá uma URL tipo:
`https://bot-sms-telegram-webhook.onrender.com`

Configure no Pluggy para chamar:
`https://sua-url.onrender.com/webhook/pluggy/{user_id}`

---

## 📊 MONITORAMENTO

### Ver logs em tempo real:
```bash
# Render
Dashboard → Logs → Live logs

# Railway  
Dashboard → Deployments → View Logs

# Heroku
heroku logs --tail -a bot-sms-telegram
```

---

## ⚡ TESTE RÁPIDO

Após deploy, teste:

```
/start → Deve mostrar boas-vindas
/saldo → Deve mostrar R$ 0,00
/comprar → Deve mostrar categorias
/ajuda → Deve mostrar comandos
```

Se todos responderem = **BOT 100% FUNCIONAL!** ✅

---

## 🎯 RESUMO

✅ Arquivos corrigidos no GitHub
✅ render.yaml agora usa "worker"
✅ Procfile corrigido
✅ Webhook de pagamentos criado
✅ Requirements atualizado

**Próximo passo**: Fazer deploy no Render como **Background Worker**!

---

Repositório: https://github.com/popovidismarcoantonionista-lang/bot-sms-telegram
