# 🤖 Bot SMS Telegram - VERSÃO MELHORADA

Bot de vendas de SMS para Telegram com integração SMS Activate e Pluggy

## 🆕 NOVAS FUNCIONALIDADES

### ✨ Sistema de Referral (Indicação)
**Ganhe créditos indicando amigos!**
- 🎁 Bônus de R$ 5,00 para o novo usuário
- 💰 Bônus de R$ 10,00 para quem indicou
- 📊 Ganhe comissão de 5% em todas as compras dos indicados
- 📈 Acompanhe suas indicações no dashboard

**Como usar:**
1. Digite `/referral` para ver seu código
2. Compartilhe com amigos
3. Eles usam `/start SEUCODIGO`
4. Ambos ganham bônus instantâneo!

### 🎯 Sistema de Níveis
**Evolua e ganhe mais benefícios!**

| Nível | Gasto Mínimo | Cashback | Benefícios |
|-------|-------------|----------|------------|
| 🥉 **Bronze** | R$ 0 | 0% | Acesso básico |
| 🥈 **Silver** | R$ 100 | 2% | Prioridade no atendimento |
| 🥇 **Gold** | R$ 500 | 5% | Atendimento VIP + Bônus |
| 💎 **Platinum** | R$ 1000 | 10% | Premium 24/7 + Ofertas exclusivas |

### 💰 Sistema de Cashback
- Receba de volta uma % do valor de cada compra
- % aumenta conforme seu nível
- Cashback é creditado automaticamente

### 🎁 Sistema de Cupons
**Descontos especiais!**
- Use cupons para ter descontos nas compras
- Admin pode criar cupons personalizados
- Limite de uso por usuário
- Validade configurável

**Comandos:**
- `/cupom CODIGO` - Usar um cupom

### 📊 Dashboard Administrativo Avançado
**Para administradores:**
- Estatísticas em tempo real
- Gráficos de vendas
- Gerenciamento de cupons
- Visualização de indicações
- Relatório de níveis dos usuários

---

## 🚀 Como Usar as Novas Funcionalidades

### Para Usuários:

**1. Sistema de Indicação:**
```
/referral - Ver seu código de indicação
/referral_stats - Ver estatísticas de suas indicações
```

**2. Sistema de Níveis:**
```
/nivel - Ver seu nível atual e progresso
/beneficios - Ver benefícios do seu nível
```

**3. Cupons de Desconto:**
```
/cupom CODIGO - Usar um cupom na próxima compra
```

### Para Administradores:

**1. Gerenciar Cupons:**
```
/criar_cupom CODIGO DESCONTO% [MAX_USOS] [DIAS_VALIDADE]
Exemplo: /criar_cupom PROMO10 10 100 30
```

**2. Dashboard Avançado:**
```
/admin_dashboard - Estatísticas completas
/admin_niveis - Ver distribuição de níveis
/admin_cupons - Gerenciar cupons ativos
```

---

## 📦 Instalação

### Pré-requisitos
- Python 3.8+
- pip
- Conta no Telegram (BotFather)
- API Keys (SMS-Activate, Pluggy, etc)

### Instalação Rápida
```bash
git clone https://github.com/popovidismarcoantonionista-lang/bot-sms-telegram.git
cd bot-sms-telegram
pip install -r requirements.txt
cp .env.example .env
# Edite o .env com suas credenciais
python bot.py
```

### Deploy Automático (Railway)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

---

## 🔧 Configuração

Edite o arquivo `.env`:

```env
# Bot Token
TELEGRAM_BOT_TOKEN=seu_token

# APIs
SMS_ACTIVATE_API_KEY=sua_key
PLUGGY_API_KEY=sua_key

# Configurações de Referral
REFERRAL_BONUS=5.0
REFERRAL_PERCENTAGE=5.0

# Admin
ADMIN_IDS=seu_telegram_id
```

---

## 📊 Estrutura do Projeto

```
bot-sms-telegram/
├── bot.py                    # Bot principal
├── config.py                 # Configurações
├── database.py               # Banco de dados
├── referral_system.py        # 🆕 Sistema de indicação
├── loyalty_system.py         # 🆕 Sistema de níveis
├── coupon_system.py          # 🆕 Sistema de cupons
├── sms_activate.py           # Integração SMS
├── pluggy_payment.py         # Pagamentos
└── requirements.txt          # Dependências
```

---

## 🎮 Comandos Disponíveis

### Usuário:
- `/start` - Iniciar bot
- `/saldo` - Ver saldo
- `/comprar` - Comprar número SMS
- `/referral` - Ver código de indicação
- `/nivel` - Ver nível atual
- `/cupom CODIGO` - Usar cupom

### Admin:
- `/admin` - Painel administrativo
- `/criar_cupom` - Criar cupom de desconto
- `/admin_dashboard` - Dashboard completo
- `/broadcast` - Enviar mensagem para todos

---

## 📈 Roadmap

- [x] Sistema de Referral
- [x] Sistema de Níveis
- [x] Sistema de Cashback
- [x] Sistema de Cupons
- [ ] Multi-idioma (EN, ES)
- [ ] Autenticação 2FA para admins
- [ ] Sistema de pacotes promocionais
- [ ] Avaliações de serviços
- [ ] Suporte a mais serviços SMS

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

---

## 📄 Licença

MIT License

---

## 💬 Suporte

- Issues: [GitHub Issues](https://github.com/popovidismarcoantonionista-lang/bot-sms-telegram/issues)
- Telegram: [@seubot](https://t.me/seubot)

---

**Desenvolvido com ❤️ usando Python e python-telegram-bot**

**Última atualização:** 08/11/2025
