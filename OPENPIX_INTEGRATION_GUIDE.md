# 🚀 INTEGRAÇÃO PIX CÓPIA E COLA - OpenPix

## ✅ POR QUE OPENPIX?

✅ **100% Gratuito** até 1000 transações/mês
✅ **Mais simples** que Pluggy para pagamentos
✅ **Gera código Pix** cópia e cola instantaneamente
✅ **Webhook automático** para notificações
✅ **QR Code visual** incluído
✅ **Documentação excelente** em português

## 📦 PASSO A PASSO

### 1️⃣ Criar Conta OpenPix

1. Acesse: **https://app.openpix.com.br**
2. Clique em "Criar Conta"
3. Preencha seus dados:
   - Nome: Marco Antonio Nista Popovidis
   - CPF: 092.675.711-33
   - Email: seu_email@exemplo.com

### 2️⃣ Obter APP ID

1. Faça login no dashboard
2. Vá em **API/Plugins** → **API Keys**
3. Copie o **App ID**
4. Formato: `Q2xpZW50...` (começa com letras)

### 3️⃣ Configurar Chave PIX

1. No dashboard OpenPix
2. Vá em **Configurações** → **Chaves Pix**
3. Adicione sua chave PIX do Recargapay:
   - Tipo: CPF
   - Chave: 092.675.711-33

### 4️⃣ Configurar Webhook (Opcional mas Recomendado)

1. **API/Plugins** → **Webhooks**
2. URL: `https://seu-bot.railway.app/webhook/openpix`
3. Eventos: Marcar "charge.completed"
4. Salvar

### 5️⃣ Adicionar ao Repositório

Arquivo criado: **openpix_payment.py**

**Adicione ao config.py:**
```python
OPENPIX_APP_ID = os.getenv('OPENPIX_APP_ID')
```

**Adicione ao .env (e no Railway):**
```
OPENPIX_APP_ID=seu_app_id_aqui
```

### 6️⃣ Usar no bot.py

**Import:**
```python
from openpix_payment import openpix_api
```

**Gerar cobrança:**
```python
# Valor em centavos (5000 = R$ 50,00)
cobranca = openpix_api.criar_cobranca_pix(
    valor=5000,
    descricao="Depósito Bot SMS",
    user_id=user.id,
    expira_em_segundos=1800  # 30 minutos
)

if cobranca:
    pix_code = cobranca['brcode']  # Código cópia e cola
    qr_image = cobranca['qrcode_image']  # URL da imagem QR
    correlation_id = cobranca['correlation_id']  # Para rastrear
```

## 🎯 VANTAGENS DA OPENPIX

| Feature | OpenPix | Pluggy Payments |
|---------|---------|-----------------|
| Gratuito | ✅ Até 1000/mês | ⚠️ Pago |
| Gera Pix | ✅ Direto | ❌ Precisa recipient |
| Webhook | ✅ Simples | ✅ Sim |
| QR Code | ✅ Imagem pronta | ⚠️ Só texto |
| Setup | ✅ 5 minutos | ⚠️ Complexo |
| Docs PT-BR | ✅ Completa | ⚠️ Inglês |

## 📊 COMPARAÇÃO DE APIS PIX

### OpenPix (RECOMENDADO) ⭐
- ✅ Grátis 1000 trans/mês
- ✅ Setup 5 min
- ✅ Webhook incluído
- 🌐 https://openpix.com.br

### Asaas
- ⚠️ R$ 0,60/cobrança
- ✅ Muito completa
- ✅ Gestão financeira
- 🌐 https://asaas.com

### Gerencianet
- ⚠️ R$ 0,49/cobrança
- ✅ Popular
- ✅ Muito estável
- 🌐 https://gerencianet.com.br

## 🔧 MINHA RECOMENDAÇÃO

**MELHOR SOLUÇÃO PARA SEU BOT:**

1. **OpenPix** → Gerar códigos Pix cópia e cola
2. **Pluggy** → Manter para verificar saldo bancário (você já tem!)
3. **SMS-Activate** → Números SMS (você já tem!)

Criado: 06/11/2025 17:25
