import json
import threading
import os

DATA_FILE = "accounts.json"
lock = threading.Lock()


class AccountRepository:

    @staticmethod
    def init_data():
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w") as f:
                json.dump({
                    "ACC-001": {"titular": "Carlos Mendoza", "saldo": 500000.0, "estado": "ACTIVA", "historial": []},
                    "ACC-002": {"titular": "Ana Gomez", "saldo": 12000.0, "estado": "ACTIVA", "historial": []},
                    "ACC-003": {"titular": "Juan Perez", "saldo": 1000000.0, "estado": "BLOQUEADA", "historial": []}
                }, f, indent=4)

    @staticmethod
    def load_data():
        AccountRepository.init_data()
        with open(DATA_FILE, "r") as f:
            return json.load(f)

    @staticmethod
    def save_data(data):
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)


class TransactionService:

    @staticmethod
    def validate_amount(amount):
        if not isinstance(amount, (int, float)):
            return {"error": "Monto inválido"}, 400
        if amount <= 0:
            return {"error": "Monto debe ser mayor a 0"}, 400
        return None

    @staticmethod
    def transfer(origin, destiny, amount):
        error = TransactionService.validate_amount(amount)
        if error:
            return error

        with lock:
            db = AccountRepository.load_data()

            if origin not in db or destiny not in db:
                return {"error": "Cuentas no encontradas"}, 404

            if db[origin]["estado"] != "ACTIVA" or db[destiny]["estado"] != "ACTIVA":
                return {"error": "Cuenta bloqueada"}, 403

            if db[origin]["saldo"] < amount:
                return {"error": "Fondos insuficientes"}, 400

            db[origin]["saldo"] -= amount
            db[destiny]["saldo"] += amount

            db[origin]["historial"].append({
                "tipo": "DEBITO",
                "monto": amount,
                "target": destiny
            })

            db[destiny]["historial"].append({
                "tipo": "CREDITO",
                "monto": amount,
                "target": origin
            })

            AccountRepository.save_data(db)

        return {"status": "SUCCESS"}, 200


class AccountService:

    @staticmethod
    def get_account(account_id):
        db = AccountRepository.load_data()
        if account_id in db:
            return db[account_id], 200
        return {"error": "Not Found"}, 404

    @staticmethod
    def change_status(account_id, new_status):
        with lock:
            db = AccountRepository.load_data()

            if account_id not in db:
                return {"error": "Not Found"}, 404

            db[account_id]["estado"] = new_status
            AccountRepository.save_data(db)

        return {"status": "CHANGED"}, 200