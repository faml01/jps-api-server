# app.py - Servidor Flask con bypass 403 para API JPS
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Headers para simular un navegador real (bypass 403)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Referer': 'https://www.jps.go.cr/',
    'Origin': 'https://www.jps.go.cr'
}

@app.route('/get_result', methods=['GET'])
def get_result():
    sorteo = request.args.get('sorteo')
    if not sorteo:
        return jsonify({"error": "Falta número de sorteo"}), 400
    
    url = f"https://integration.jps.go.cr/api/App/nuevostiempos/{sorteo}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()

        numero_ganador = data.get('numero')
        fecha = data.get('fecha', '')
        hora = fecha.split('T')[1][:5] if fecha and 'T' in fecha else ''
        premio = data.get('premio', '')
        descripcion = f"Premio: {premio}" if premio else ''

        if not numero_ganador:
            return jsonify({"error": "Sorteo sin resultados aún"}), 404

        return jsonify({
            "numero_ganador": numero_ganador,
            "hora": hora,
            "descripcion": descripcion
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API JPS: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
