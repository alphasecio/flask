from flask import Flask, render_template, request, jsonify, send_file
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import json
import os

app = Flask(__name__)

def obtener_datos_nit(driver, nit):
    try:
        nit_input = WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="Nit"]'))
        )
        nit_input.send_keys(Keys.CONTROL + "a")
        nit_input.send_keys(Keys.BACKSPACE)
        nit_input.send_keys(nit)
        nit_input.send_keys(Keys.ENTER)

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//a[@class="text-end pe-2"]'))
            ).click()

            time.sleep(1)

            datos = {}
            campos = [
                ("Empresa", '//h1[@class="intro__nombre intro__nombre--xs"]'),
                ("Identificación", '//p[text()="Identificación"]/following-sibling::p'),
                ("Fecha_Matricula", '//p[text()="Fecha de Matrícula"]/following-sibling::p'),
                ("Camara_Comercio", '//p[text()="Cámara de Comercio"]/following-sibling::p'),
                ("Estado_Matricula", '//p[text()="Estado de la matrícula"]/following-sibling::p'),
                ("Fecha_Vigencia", '//p[text()="Fecha de Vigencia"]/following-sibling::p'),
                ("Fecha_Renovación", '//p[text="Fecha de renovación"]/following-sibling::p'),
                ("Último_Año_Renovado", '//p[text()="Último año renovado"]/following-sibling::p'),
                ("Fecha_Actualización", '//p[text()="Fecha de Actualización"]/following-sibling::p'),
                ("Categoría_Matricula", '//p[text()="Categoria de la Matrícula"]/following-sibling::p'),
                ("Tipo_Sociedad", '//p[text()="Tipo de Sociedad"]/following-sibling::p'),
                ("Tipo_Organización", '//p[text()="Tipo Organización"]/following-sibling::p'),
                ("Número_Matricula", '//p[text()="Número de Matrícula"]/following-sibling::p'),
                ("Motivo_Cancelación", '//p[text()="Motivo Cancelación"]/following-sibling::p'),
                ("Fecha_Cancelación", '//p[text()="Fecha de Cancelación"]/following-sibling::p'),
            ]

            for key, xpath in campos:
                try:
                    datos[key] = driver.find_element(By.XPATH, xpath).text
                except NoSuchElementException:
                    datos[key] = ""

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//span[text()="Actividad económica"]'))
            ).click()

            time.sleep(1)

            try:
                AE = driver.find_element(By.XPATH, '//div[@id="detail-tabs-tabpane-pestana_economica"]').text
                rr = re.findall(r"(\d+)\s(.+)", AE)
                datos["Actividad_Económica"] = "| ".join([f"{codigo} {descripcion}" for codigo, descripcion in rr])
            except NoSuchElementException:
                datos["Actividad_Económica"] = ""

            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//a[@class="link-primary"]'))
            ).click()

            return datos

        except TimeoutException:
            return {"error": f"No se encontró información para el NIT {nit}"}

    except TimeoutException:
        return {"error": f"No se encontró información para el NIT {nit}"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consulta', methods=['POST'])
def consulta_nit():
    request_data = request.get_json()
    nit = request_data.get('nit')

    options = Options()
    options.headless = True
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get("https://ruesfront.rues.org.co/busqueda-avanzada")
    driver.maximize_window()
    time.sleep(1)

    datos = obtener_datos_nit(driver, nit)
    driver.quit()

    # Guarda los datos en un archivo JSON
    file_path = 'resultado.json'
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

    # Envía el archivo JSON como respuesta
    return send_file(file_path, as_attachment=True, mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
