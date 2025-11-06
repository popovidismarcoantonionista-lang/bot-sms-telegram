# 🎯 Integração PIX Cópia e Cola - Pluggy.ai

## ✅ O que seu bot JÁ TEM

Analisei seu repositório e encontrei:

- ✅ **bot.py** (27KB) - Bot principal funcionando
- ✅ **pluggy_checker.py** - Verificação de transações Pluggy
- ✅ **sms_activate.py** - API SMS-Activate configurada
- ✅ **database.py** - Banco de dados com transações
- ✅ **webhook_server.py** - Servidor de webhooks
- ✅ **Sistema de saldo** - Já funcional
- ✅ **Categorias de serviço** - Básico, Padrão, Premium

## 🆕 O que vamos ADICIONAR

- 🆕 **Geração automática de código Pix cópia e cola**
- 🆕 **Verificação automática de pagamento** (background, a cada 30s)
- 🆕 **Notificação instantânea** quando pagamento confirmar
- 🆕 **Interface amigável** com botões interativos

---

## 📦 INSTALAÇÃO RÁPIDA

### 1️⃣ Baixe os arquivos

📥 [**BAIXAR PACOTE COMPLETO DE INTEGRAÇÃO**](https://pub-b70cb36a6853407fa468c5d6dec16633.r2.dev/196744/generic/file_upload/request/e976be129e1ea315b97fe103c70d3624)

O pacote contém:
- `pluggy_payment.py` - Novo módulo de pagamentos
- `config_additions.txt` - Adições para config.py
- `env_additions.txt` - Novas variáveis de ambiente
- `bot_integration.py` - Código para integrar no bot.py
- `database_additions.py` - Funções para database.py
- `INTEGRATION_GUIDE.md` - Guia completo

### 2️⃣ Obtenha as credenciais Pluggy

1. Acesse: **https://dashboard.pluggy.ai**
2. Faça login ou crie conta
3. Vá em **API Keys** e copie:
   - `PLUGGY_API_KEY`
   - `PLUGGY_CLIENT_ID` (você já deve ter)
   - `PLUGGY_CLIENT_SECRET` (você já deve ter)

4. **Criar Recipient** (recebedor Pix):

```bash
curl --request POST \
  --url https://api.pluggy.ai/payments/recipients \
  --header 'X-API-KEY: sua_api_key' \
  --header 'content-type: application/json' \
  --data '{
    "name": "Bot SMS Telegram",
    "documentNumber": "seu_cpf_ou_cnpj",
    "accountNumber": "sua_conta",
    "bankCode": "codigo_banco",
    "type": "INDIVIDUAL"
  }'
```

Guarde o **`id`** retornado - esse é seu `PLUGGY_RECIPIENT_ID`

### 3️⃣ Atualizar .env

Adicione ao seu `.env`:

```env
# Pluggy Payment API
PLUGGY_API_KEY=sua_api_key_aqui
PLUGGY_RECIPIENT_ID=uuid_do_recebedor_aqui
PLUGGY_WEBHOOK_URL=https://seu-dominio.railway.app/webhook/pluggy
```

### 4️⃣ Adicionar pluggy_payment.py

Copie o arquivo `pluggy_payment.py` do pacote para a raiz do projeto.

### 5️⃣ Atualizar config.py

Adicione no `config.py` (depois das outras variáveis Pluggy):

```python
# Pluggy Payment API
PLUGGY_API_KEY = os.getenv('PLUGGY_API_KEY')
PLUGGY_RECIPIENT_ID = os.getenv('PLUGGY_RECIPIENT_ID')
PLUGGY_WEBHOOK_URL = os.getenv('PLUGGY_WEBHOOK_URL', '')
```

### 6️⃣ Atualizar database.py

Adicione as funções do arquivo `database_additions.py` ao final do seu `database.py`.

### 7️⃣ Atualizar bot.py

No arquivo `bot.py`:

**a) Adicione o import no topo:**
```python
from pluggy_payment import pluggy_payment
```

**b) Substitua a função `depositar_command`** pela versão do arquivo `bot_integration.py`

**c) Adicione as novas funções:**
- `process_deposit`
- `verificar_pagamento_automatico`
- `verificar_pagamento_manual`

**d) Atualize `button_callback`** para incluir os novos callbacks de depósito e verificação

---

## 🧪 TESTAR

### Em modo Sandbox:

```bash
# No .env
PLUGGY_ENVIRONMENT=sandbox

# Rodar bot
python bot.py
```

### Comandos para testar:

1. `/start` - Ver menu principal
2. `/depositar` - Testar geração de Pix
3. Escolher valor (ex: R$ 10,00)
4. Copiar código Pix gerado
5. Clicar em "✅ Já Paguei"

**No sandbox**, você pode simular pagamentos diretamente no dashboard Pluggy.

---

## 🚀 PRODUÇÃO

Quando estiver pronto:

```env
PLUGGY_ENVIRONMENT=production
```

E configure um **Recipient real** com suas informações bancárias.

---

## 📊 FLUXO VISUAL

```
[Usuário] /depositar
    ↓
[Bot] Mostra opções: R$ 10, 20, 50, 100, Outro
    ↓
[Usuário] Clica "R$ 50,00"
    ↓
[Bot Pluggy API] Gera Payment Request
    ↓
[Bot] Recebe pixQrCode
    ↓
[Bot → Usuário] Envia código Pix cópia e cola
    ↓
[Background] Verifica a cada 30s (max 20min)
    ↓
[Pluggy API] Status = COMPLETED
    ↓
[Bot] Credita R$ 50 no saldo
    ↓
[Bot → Usuário] "✅ PAGAMENTO CONFIRMADO!"
```

---

## 📸 Exemplo de Mensagem ao Usuário

```
🎯 Pagamento PIX Gerado!

💰 Valor: R$ 50,00
📝 Descrição: Depósito Bot SMS - User 123456
🆔 ID: pay_abc123xyz
📊 Status: Aguardando Pagamento

📋 Código Pix Cópia e Cola:
┌─────────────────────────────┐
│ 00020126580014br.gov.bcb... │
└─────────────────────────────┘

👆 Toque no código acima para copiar

📱 Instruções:
1. Copie o código Pix acima
2. Abra seu app bancário
3. Escolha "Pix" > "Copia e Cola"
4. Cole o código e confirme
5. Clique em "✅ Já Paguei" abaixo

⏰ Verificação automática ativa
Seu saldo será creditado em até 2 minutos!

[✅ Já Paguei - Verificar] [❌ Cancelar]
```

---

## ⚠️ IMPORTANTE

1. **Nunca commit o arquivo `.env`** com credenciais reais
2. **Use sandbox** primeiro para testes
3. **Valor mínimo PIX**: R$ 1,00
4. **Timeout de verificação**: 20 minutos
5. **Recipient**: Deve estar ativo no Pluggy

---

## 🆘 TROUBLESHOOTING

### Erro: "pixQrCode não gerado"
- Verifique se PLUGGY_RECIPIENT_ID está correto
- Confirme que a API_KEY está válida
- Teste no dashboard Pluggy primeiro

### Erro: "Recipient not found"
- Crie um recipient primeiro via API
- Verifique o ID no dashboard

### Pagamento não detectado
- Aguarde até 2 minutos
- Verifique logs do pluggy_checker
- Confirme que PLUGGY_ITEM_ID está correto

---

## 📞 Suporte

Se tiver problemas, verifique:
1. Logs do bot: `tail -f bot.log`
2. Dashboard Pluggy: https://dashboard.pluggy.ai
3. Docs Pluggy: https://docs.pluggy.ai

---

Criado via Rube AI - {datetime.now().strftime("%d/%m/%Y %H:%M")}
