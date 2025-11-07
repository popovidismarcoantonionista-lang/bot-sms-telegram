# 🎯 GUIA DE CONFIGURAÇÃO - APEX SEGUIDORES

## ✅ Problema Corrigido

O arquivo `.env.example` foi atualizado para incluir a configuração do Apex Seguidores!

**Commit:** [ff7c1a7](https://github.com/popovidismarcoantonionista-lang/bot-sms-telegram/commit/ff7c1a7e2fb92ed2431edd94efd7d9d5371d28f1)

## 📋 Configuração no Servidor (Railway/Render/Outro)

### Opção 1: Adicionar variável de ambiente na plataforma

**No Railway:**
1. Acesse seu projeto no Railway
2. Vá em **Variables**
3. Adicione a nova variável:
   - **Name:** `APEX_API_KEY`
   - **Value:** `207d62f08e4f76b9a8384facc27272e4`
4. Clique em **Add** e depois em **Deploy**

**No Render:**
1. Acesse seu serviço no Render
2. Vá em **Environment**
3. Adicione a variável:
   - **Key:** `APEX_API_KEY`
   - **Value:** `207d62f08e4f76b9a8384facc27272e4`
4. Salve e o serviço irá fazer redeploy automaticamente

### Opção 2: Atualizar arquivo .env no repositório

⚠️ **ATENÇÃO:** Nunca commite o arquivo `.env` com chaves reais no GitHub!

Se você estiver usando o arquivo `.env` localmente:

1. Copie o `.env.example` para `.env`:
```bash
cp .env.example .env
```

2. Edite o `.env` e substitua:
```bash
APEX_API_KEY=207d62f08e4f76b9a8384facc27272e4
```

3. Certifique-se que `.env` está no `.gitignore` (já está ✅)

## 🔍 Como Testar

Após configurar, teste a integração do Apex:

```python
from apex_seguidores import apex_api

# Verificar saldo
balance = apex_api.get_balance()
print(f"Saldo Apex: R$ {balance:.2f}")

# Listar serviços
services = apex_api.get_services()
print(f"Serviços disponíveis: {len(services)}")

# Filtrar por categoria (Instagram)
instagram_services = apex_api.get_services_by_category('instagram')
for service in instagram_services[:5]:
    print(apex_api.format_service_info(service))
```

## 📱 Serviços Disponíveis no Apex

A API Apex Seguidores oferece serviços para várias redes sociais:

- **Instagram:** Seguidores, curtidas, visualizações, comentários
- **TikTok:** Seguidores, curtidas, visualizações
- **YouTube:** Inscritos, visualizações, curtidas
- **Twitter:** Seguidores, retweets, curtidas
- **Facebook:** Curtidas, seguidores, compartilhamentos
- E muito mais!

## 🛠️ Funcionalidades Implementadas

O módulo `apex_seguidores.py` já está pronto com:

✅ `get_services()` - Lista todos os serviços disponíveis
✅ `get_balance()` - Consulta saldo da conta
✅ `create_order()` - Cria pedidos de serviços
✅ `check_order_status()` - Verifica status de pedidos
✅ `get_services_by_category()` - Filtra serviços por categoria
✅ `format_service_info()` - Formata informações para exibição

## 🚀 Próximos Passos

1. ✅ Adicione a variável `APEX_API_KEY` no seu servidor
2. 🔄 Faça redeploy do bot
3. 🧪 Teste as funcionalidades de redes sociais
4. 📊 Monitore os pedidos através do dashboard Apex

## 📞 Suporte

- **Apex Seguidores:** https://apexseguidores.com/api
- **Documentação:** https://apexseguidores.com/docs
- **Bot Telegram:** @smstemporariobaratobot

---

**Sua API KEY:** `207d62f08e4f76b9a8384facc27272e4`

⚠️ **Importante:** Mantenha sua API KEY em segredo!
