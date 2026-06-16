from flask import Flask, request, jsonify
from core import TransactionService, AccountService

app = Flask(__name__)

# 🔐 TOKEN SIMULADO
ADMIN_TOKEN = "SECURE123"


class SecurityMiddleware:
    @staticmethod
    def validate_admin(headers):
        token = headers.get("Authorization")
        return token == ADMIN_TOKEN


@app.route("/")
def home():
    return jsonify({"msg": "API Running 🚀"})


# 🔍 GET ACCOUNT
@app.route("/api/v1/accounts/detail", methods=["GET"])
def get_account():
    account_id = request.args.get("id")

    if not account_id:
        return jsonify({"error": "Missing ID"}), 400

    data, status = AccountService.get_account(account_id)
    return jsonify(data), status


# 💸 TRANSFERENCIA
@app.route("/api/v1/transactions/transfer", methods=["POST"])
def transfer():
    payload = request.get_json()

    origin = payload.get("desde")
    destiny = payload.get("hacia")
    amount = payload.get("monto")

    if not origin or not destiny or amount is None:
        return jsonify({"error": "Datos incompletos"}), 422

    data, status = TransactionService.transfer(origin, destiny, amount)
    return jsonify(data), status


# 🔐 ADMIN
@app.route("/api/v1/accounts/admin/bypass-status", methods=["POST"])
def admin_status():
    if not SecurityMiddleware.validate_admin(request.headers):
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json()

    acc_id = payload.get("id")
    status_new = payload.get("status")

    if not acc_id or not status_new:
        return jsonify({"error": "Datos incompletos"}), 422

    data, status = AccountService.change_status(acc_id, status_new)
    return jsonify(data), status