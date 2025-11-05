from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Database simples
DATABASE_FILE = "database.json"

def carregar_database():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    return {}

def salvar_database(db):
    with open(DATABASE_FILE, 'w') as f:
        json.dump(db, f, indent=2)

def atualizar_saldo(user_id, valor):
    db = carregar_database()
    user_id_str = str(user_id)
    if user_id_str in db:
        db[user_id_str]["saldo"] += valor
        salvar_database(db)
        return True
    return False

@app.route('/webhook/pluggy/<user_id>', methods=['POST'])
def webhook_pluggy(user_id):
    """Webhook para receber confirmação de pagamento do Pluggy"""
    try:
        data = request.json

        # Verificar se pagamento foi aprovado
        if data.get('status') == 'COMPLETED' or data.get('status') == 'approved':
            valor = float(data.get('amount', 0))

            if atualizar_saldo(user_id, valor):
                print(f"✅ Saldo de R$ {valor:.2f} creditado para usuário {user_id}")
                return jsonify({"status": "success", "message": "Saldo creditado"}), 200

        return jsonify({"status": "pending"}), 200

    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
