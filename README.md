# 🤖 Bot SMS Telegram - Sistema Completo

Bot Telegram profissional para venda de números SMS temporários com pagamento automático via PIX usando Pluggy.ai.

## ✨ Funcionalidades

### 💰 Pagamentos Automáticos
- ✅ Integração com Pluggy.ai para verificação de PIX
- ✅ Crédito automático após confirmação de pagamento
- ✅ Sistema de ID único para cada usuário
- ✅ Notificações automáticas de depósitos

### 📱 SMS Temporários
- ✅ Integração com SMS-Activate
- ✅ Múltiplas categorias de preços
- ✅ Suporte a diversos serviços (WhatsApp, Instagram, Google, etc)
- ✅ Sistema de reembolso (50% em cancelamentos)

### 🔒 Segurança & Performance
- ✅ PostgreSQL para persistência de dados
- ✅ Variáveis de ambiente para credenciais
- ✅ Logs estruturados
- ✅ Worker assíncrono para verificação de pagamentos

## 🚀 Instalação Rápida

### 1. Clonar o Repositório
```bash
git clone https://github.com/popovidismarcoantonionista-lang/bot-sms-telegram.git
cd bot-sms-telegram
```

### 2. Configurar Variáveis de Ambiente
```bash
cp .env.example .env
nano .env  # Edite com suas credenciais
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Inicializar Banco de Dados
```bash
python -c "from database import db; db.init_db()"
```

### 5. Executar o Bot
```bash
# Terminal 1 - Bot principal
python bot.py

# Terminal 2 - Worker de verificação
python worker.py
```

## 🐳 Deploy com Docker

```bash
# Build e iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down
```

## ⚙️ Configuração

### Credenciais Necessárias

1. **Telegram Bot Token**
   - Obtenha com [@BotFather](https://t.me/BotFather)
   - Comando: `/newbot`

2. **Pluggy.ai**
   - Crie conta em [dashboard.pluggy.ai](https://dashboard.pluggy.ai)
   - Obtenha Client ID e Secret
   - Configure Item ID conectando sua conta Mercado Pago

3. **SMS-Activate**
   - Crie conta em [sms-activate.org](https://sms-activate.org)
   - Obtenha API Key no perfil

4. **PostgreSQL (Neon.tech)**
   - Crie projeto em [neon.tech](https://neon.tech)
   - Copie a Connection String

### Variáveis de Ambiente (.env)

```env
# Telegram
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_ADMIN_ID=seu_telegram_id

# Pluggy
PLUGGY_CLIENT_ID=seu_client_id
PLUGGY_CLIENT_SECRET=seu_secret
PLUGGY_ENVIRONMENT=production
PLUGGY_ITEM_ID=seu_item_id

# SMS-Activate
SMS_ACTIVATE_API_KEY=sua_key

# Database
DATABASE_URL=postgresql://user:pass@host/db

# PIX
PIX_KEY=sua_chave_pix
PIX_NAME=Seu Nome
```

## 📊 Estrutura do Projeto

```
bot-sms-telegram/
├── bot.py                 # Bot principal
├── worker.py              # Worker de verificação de depósitos
├── config.py              # Configurações centralizadas
├── database.py            # Modelos e operações do banco
├── pluggy_checker.py      # Cliente Pluggy para verificação PIX
├── sms_activate.py        # Cliente SMS-Activate
├── requirements.txt       # Dependências Python
├── Dockerfile             # Container Docker
├── docker-compose.yml     # Orquestração Docker
├── .env.example           # Template de configuração
└── README.md              # Esta documentação
```

## 🎯 Comandos do Bot

### Usuários
- `/start` - Iniciar bot e ver menu
- `/saldo` - Ver saldo atual
- `/depositar` - Instruções para depósito PIX
- `/comprar` - Comprar número SMS
- `/historico` - Ver histórico de transações
- `/ajuda` - Obter ajuda e FAQ

### Admin (apenas dono)
- `/admin` - Painel administrativo com estatísticas

## 💵 Categorias de Preços

| Categoria | Preço | Serviços |
|-----------|-------|----------|
| 💚 Básico | R$ 0.60 | WhatsApp, Telegram, Discord |
| 💙 Padrão | R$ 1.00 | Instagram, Facebook, Twitter, TikTok |
| 💜 Premium | R$ 2.50 | Google, Microsoft, Amazon, PayPal |

## 🔧 Manutenção

### Ver Logs
```bash
tail -f logs/bot.log
```

### Backup do Banco
```bash
pg_dump $DATABASE_URL > backup.sql
```

### Atualizar Código
```bash
git pull origin main
docker-compose restart
```

## 🐛 Troubleshooting

### Bot não inicia
- Verifique se o TOKEN está correto
- Confirme que todas as variáveis de ambiente estão configuradas

### Depósitos não são detectados
- Verifique se o Worker está rodando
- Confirme que PLUGGY_ITEM_ID está correto
- Verifique logs do worker

### SMS não chega
- Verifique saldo do SMS-Activate
- Confirme que o serviço tem números disponíveis
- Alguns serviços podem demorar até 20 minutos

## 📝 Licença

Este projeto é privado e proprietário.

## 👨‍💻 Suporte

Em caso de dúvidas ou problemas, entre em contato através do Telegram.

---

**Desenvolvido com ❤️ para automação de SMS temporários**
