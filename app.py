# app.py - Servidor Flask para consultar API JPS solo para Nuevos Tiempos
from flask import Flask, request, jsonify
import requests  # Para hacer solicitudes HTTP a la API JPS

app = Flask(__name__)

# Endpoint: GET /get_result?sorteo=XXXX
# Recibe número de sorteo, consulta API JPS, parsea y devuelve JSON limpio
@app.route('/get_result', methods=['GET'])
def get_result():
    sorteo = request.args.get('sorteo')  # Obtiene sorteo de query param
    if not sorteo:
        return jsonify({"error": "No se proporcionó número de sorteo"}), 400
    
    url = f"https://integration.jps.go.cr/api/App/nuevostiempos/{sorteo}"
    
    try:
        # Consulta la API JPS
        response = requests.get(url, timeout=10)  # Timeout de 10s para evitar hangs
        response.raise_for_status()  # Lanza error si no 200 OK
        
        data = response.json()  # Parsea JSON
        
        # Extracción de datos (basado en estructura de API: numero, fecha, premio, etc.)
        # Si no existe campo, usa defaults
        numero_ganador = data.get('numero', None)
        
        # Hora: Extrae de 'fecha' (formato ISO: YYYY-MM-DDTHH:MM:SS)
        fecha = data.get('fecha', '')
        hora = ''
        if fecha and 'T' in fecha:
            hora = fecha.split('T')[1][:5]  # HH:MM
        
        # Descripción: Construye de 'premio' si existe, else vacío
        premio = data.get('premio', '')
        descripcion = f"Premio: {premio}" if premio else ''
        
        # Si no hay número ganador (sorteo futuro o sin resultados), maneja
        if numero_ganador is None:
            return jsonify({"error": "No hay resultados disponibles para este sorteo aún"}), 404
        
        # Devuelve JSON limpio
        result = {
            "numero_ganador": numero_ganador,
            "hora": hora,
            "descripcion": descripcion
        }
        return jsonify(result)
    
    except requests.exceptions.RequestException as e:
        # Manejo de errores: API no responde, timeout, etc.
        return jsonify({"error": f"Error al consultar API JPS: {str(e)}"}), 500

if __name__ == '__main__':

    app.run(debug=True)  # Para local; en Render usa gunicorn
