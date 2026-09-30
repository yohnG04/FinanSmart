from decimal import Decimal, InvalidOperation

from flask import Flask, jsonify, request

app = Flask(__name__)


def generate_recommendation(category_name, spent, limit):
    percentage = (spent / limit) * Decimal("100")

    if percentage < Decimal("70"):
        return (
            f"Vas bien. Has utilizado el {percentage:.1f}% "
            f"de tu presupuesto de {category_name}."
        )

    if percentage < Decimal("100"):
        return (
            f"Atención: has utilizado el {percentage:.1f}% "
            f"de tu presupuesto de {category_name}. "
            "Reduce los gastos no esenciales."
        )

    exceeded_amount = spent - limit

    return (
        f"Superaste tu presupuesto de {category_name} "
        f"en ${exceeded_amount:,.2f}. "
        "Revisa tus últimos gastos y ajusta tus próximas compras."
    )


@app.route("/api/v2/recommendations/", methods=["POST"])
def recommendations():
    data = request.get_json(silent=True)

    if not data:
        return jsonify(
            {
                "error": "invalid_request",
                "detail": "Se requiere un cuerpo JSON válido.",
            }
        ), 400

    required_fields = ["category_name", "spent", "limit"]
    missing_fields = [
        field for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return jsonify(
            {
                "error": "missing_fields",
                "detail": (
                    "Faltan campos obligatorios: "
                    + ", ".join(missing_fields)
                ),
            }
        ), 400

    category_name = str(data["category_name"]).strip()

    if not category_name:
        return jsonify(
            {
                "error": "invalid_category",
                "detail": "category_name no puede estar vacío.",
            }
        ), 400

    try:
        spent = Decimal(str(data["spent"]))
        limit = Decimal(str(data["limit"]))
    except (InvalidOperation, TypeError, ValueError):
        return jsonify(
            {
                "error": "invalid_amount",
                "detail": "spent y limit deben ser valores numéricos.",
            }
        ), 400

    if spent < 0:
        return jsonify(
            {
                "error": "invalid_spent",
                "detail": "spent no puede ser negativo.",
            }
        ), 400

    if limit <= 0:
        return jsonify(
            {
                "error": "invalid_limit",
                "detail": "limit debe ser mayor que cero.",
            }
        ), 400

    try:
        recommendation = generate_recommendation(
            category_name=category_name,
            spent=spent,
            limit=limit,
        )
    except Exception:
        return jsonify(
            {
                "error": "internal_error",
                "detail": "No fue posible generar la recomendación.",
            }
        ), 500

    return jsonify(
        {
            "category_name": category_name,
            "spent": str(spent),
            "limit": str(limit),
            "recommendation": recommendation,
        }
    ), 200


@app.route("/health/", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
