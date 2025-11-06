# 🎯 INTEGRAÇÃO PIX SIMPLES - SEM CNPJ

## ✅ Como Funciona

1. Usuário solicita depósito
2. Bot gera ID único (ex: SMS12345671699999999)
3. Bot mostra sua chave PIX e o ID
4. Usuário faz PIX manual colocando o ID na descrição
5. Pluggy verifica depósitos automaticamente (você já tem!)
6. Bot detecta o ID na descrição e credita o saldo

## 📝 Adicione ao bot.py

```python
# Import no topo
from simple_pix_payment import simple_pix

# Na função depositar (quando usuário escolhe valor):

async def process_deposit_simple(self, query, user, valor):
    """Processa depósito via PIX estático"""

    # Gerar instruções
    instrucoes = simple_pix.gerar_instrucoes_pix(
        valor=valor,
        user_id=user.id,
        descricao=f"Depósito Bot SMS"
    )

    # Salvar no banco (pendente)
    db.create_pending_payment(
        telegram_id=user.id,
        payment_id=instrucoes['payment_id'],
        amount=valor,
        pix_code=instrucoes['pix_key']
    )

    # Formatar e enviar mensagem
    mensagem = simple_pix.formatar_mensagem_pix(instrucoes)

    keyboard = [
        [InlineKeyboardButton("✅ Já Paguei", callback_data=f"check_deposit")],
        [InlineKeyboardButton("◀️ Voltar", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        mensagem,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

    # Iniciar verificação automática (já existe no pluggy_checker!)
    asyncio.create_task(
        self.auto_verify_deposit(query.message.chat_id, user.id, instrucoes['payment_id'], valor)
    )
```

## 🔄 Verificação Automática

O `pluggy_checker.py` que você JÁ TEM vai:
1. Buscar transações recentes
2. Procurar pela descrição com o payment_id
3. Creditar automaticamente quando encontrar

Está tudo pronto! 🎉
