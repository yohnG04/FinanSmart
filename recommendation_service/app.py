from decimal import Decimal, InvalidOperation
from gettext import translation
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)
LOCALE_DIR = Path(__file__).resolve().parent / 'locale'


def translated(language):
    lang = 'en' if language == 'en' else 'es'
    return translation('flask', localedir=str(LOCALE_DIR), languages=[lang], fallback=True).gettext


def generate_recommendation(category_name, spent, limit, language='es'):
    _ = translated(language)
    percentage = (spent / limit) * Decimal('100')
    if percentage < Decimal('70'):
        return _('Vas bien. Has utilizado el {pct:.1f}% de tu presupuesto de {category}.').format(pct=percentage, category=category_name)
    if percentage < Decimal('100'):
        return _('Atención: has utilizado el {pct:.1f}% de tu presupuesto de {category}. Reduce los gastos no esenciales.').format(pct=percentage, category=category_name)
    return _('Superaste tu presupuesto de {category} en ${amount:,.2f}. Revisa tus últimos gastos y ajusta tus próximas compras.').format(category=category_name, amount=spent-limit)


@app.route('/api/v2/recommendations/', methods=['POST'])
def recommendations():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error='invalid_request', detail='Se requiere un cuerpo JSON válido.'), 400
    language = 'en' if data.get('language') == 'en' else 'es'
    _ = translated(language)
    missing_fields = [field for field in ('category_name', 'spent', 'limit') if field not in data]
    if missing_fields:
        return jsonify(error='missing_fields', detail=_('Faltan campos obligatorios: ') + ', '.join(missing_fields)), 400
    category_name = data['category_name']
    if not isinstance(category_name, str) or not category_name.strip():
        return jsonify(error='invalid_category', detail=_('category_name no puede estar vacío.')), 400
    category_name = category_name.strip()[:100]
    try:
        spent = Decimal(str(data['spent']))
        limit = Decimal(str(data['limit']))
        if not spent.is_finite() or not limit.is_finite():
            raise ValueError()
    except (InvalidOperation, TypeError, ValueError):
        return jsonify(error='invalid_amount', detail=_('spent y limit deben ser valores numéricos finitos.')), 400
    if spent < 0:
        return jsonify(error='invalid_spent', detail=_('spent no puede ser negativo.')), 400
    if limit <= 0:
        return jsonify(error='invalid_limit', detail=_('limit debe ser mayor que cero.')), 400
    return jsonify(
        category_name=category_name, spent=str(spent), limit=str(limit),
        recommendation=generate_recommendation(category_name, spent, limit, language),
    ), 200


@app.route('/health/', methods=['GET'])
def health():
    return jsonify(status='ok'), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
