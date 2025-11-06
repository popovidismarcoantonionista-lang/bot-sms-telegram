# 🎯 INTEGRAÇÃO APEX SEGUIDORES

## 📋 O QUE É?

**Apex Seguidores** é um painel SMM que oferece:
- 📱 Seguidores Instagram, TikTok, Twitter
- ❤️ Curtidas em posts
- 👁️ Visualizações de vídeos
- 💬 Comentários
- 📊 E muito mais!

## 🔧 COMO INTEGRAR

### 1️⃣ Obter API Key

1. Acesse: **https://apexseguidores.com**
2. Crie uma conta ou faça login
3. Vá em **"API"** no menu
4. Copie sua **API Key**

### 2️⃣ Adicionar ao Projeto

**Arquivo criado:** `apex_seguidores.py`

**Adicionar ao config.py:**
```python
APEX_API_KEY = os.getenv('APEX_API_KEY')
```

**Adicionar ao .env e Railway:**
```
APEX_API_KEY=sua_chave_aqui
```

### 3️⃣ Usar no Bot

**Importar:**
```python
from apex_seguidores import apex_api
```

**Listar serviços:**
```python
# Todos os serviços
services = apex_api.get_services()

# Por categoria
instagram_services = apex_api.get_services_by_category('instagram')
tiktok_services = apex_api.get_services_by_category('tiktok')
```

**Criar pedido:**
```python
order = apex_api.create_order(
    service_id=123,  # ID do serviço
    link='https://instagram.com/seu_perfil',
    quantity=1000  # 1000 seguidores
)

if order:
    order_id = order['order_id']
    print(f"Pedido criado: {order_id}")
```

**Verificar status:**
```python
status = apex_api.check_order_status(order_id)

if status:
    print(f"Status: {status['status']}")
    print(f"Resta: {status['remains']}")
```

## 💰 SISTEMA DE PREÇOS

A Apex cobra por 1000 unidades. Exemplos:

- **Instagram Seguidores:** R$ 5,00 / 1000
- **TikTok Curtidas:** R$ 3,00 / 1000
- **YouTube Views:** R$ 8,00 / 1000

**Cálculo de preço:**
```python
service_rate = 5.00  # R$ 5 por 1000
quantity = 500  # Usuario quer 500 seguidores

price = (service_rate / 1000) * quantity
# R$ 2,50
```

## 🤖 ADICIONAR AO BOT

**Novo comando:** `/social`

```python
async def social_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comprar serviços de redes sociais"""
    user = update.effective_user
    db_user = db.get_or_create_user(telegram_id=user.id)

    text = f"""
📱 *Serviços de Redes Sociais*

Seu saldo: R$ {db_user.balance:.2f}

Escolha a rede social:
"""

    keyboard = [
        [InlineKeyboardButton("📸 Instagram", callback_data="social_instagram")],
        [InlineKeyboardButton("🎵 TikTok", callback_data="social_tiktok")],
        [InlineKeyboardButton("🐦 Twitter", callback_data="social_twitter")],
        [InlineKeyboardButton("▶️ YouTube", callback_data="social_youtube")],
        [InlineKeyboardButton("◀️ Voltar", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
```

## 📊 CATEGORIAS APEX

As principais categorias são:

- **Instagram:** Seguidores, Curtidas, Comentários, Views
- **TikTok:** Seguidores, Curtidas, Views, Shares
- **YouTube:** Inscritos, Views, Curtidas, Comentários
- **Twitter:** Seguidores, Retweets, Curtidas
- **Facebook:** Curtidas de página, Seguidores, Reações

## ⚠️ IMPORTANTE

1. **Saldo Apex:** Você precisa ter saldo na conta Apex
2. **Preços variam:** Consulte sempre via API
3. **Mínimo/Máximo:** Cada serviço tem limites
4. **Tempo de entrega:** Varia por serviço (instantâneo a 24h)

## 🎯 FLUXO SUGERIDO

```
[Usuário] /social
    ↓
[Bot] Escolha rede social
    ↓
[Usuário] Clica "Instagram"
    ↓
[Bot] Mostra serviços: Seguidores, Curtidas, etc
    ↓
[Usuário] Escolhe "Seguidores"
    ↓
[Bot] "Cole o link do perfil"
    ↓
[Usuário] Cola link
    ↓
[Bot] "Quantos seguidores? (min-max)"
    ↓
[Usuário] Digite quantidade
    ↓
[Bot] Calcula preço e cobra do saldo
    ↓
[Apex] Processa pedido
    ↓
[Bot] "✅ Pedido criado! ID: 12345"
```

Criado: 06/11/2025 19:01
