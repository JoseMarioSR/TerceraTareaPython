import requests
import threading
import os
import requests
import threading
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
from PIL import Image, ImageFilter, ImageOps
import unittest
from unittest.mock import patch, mock_open, MagicMock

# Configuración del log de errores
logging.basicConfig(filename='error.log', level=logging.ERROR)

# Constantes
AUTH_URL = 'https://python-course.lat/image-app/api-token-auth/'
IMAGE_URL = 'https://python-course.lat/image-app/images/'
TEMP_DIR = 'imag_descargadas/'
REQUIREMENTS_PATH = 'requirements.txt'  # Ruta al archivo requirements.txt

def obtener_token():
    """
    Obtiene el token de autenticación desde el servidor.

    Returns:
    str: Token de autenticación.
    """
    try:
        response = requests.post(AUTH_URL, json= {
            'user': 'user',
            'password': 'python22024!'
        })
        response.raise_for_status()
        
        # Manejar la respuesta como cadena
        token = response.text
        token = token[1: -1]
        if token:
            return token
        else:
            logging.error("No se encontró el token en la respuesta.")
            return None
            
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return None
    except Exception as err:
        logging.error(f"An error occurred: {err}")
        return None


def descargar_imagen(token, index):
    """
    Descarga una imagen desde el servidor usando el token de autenticación.

    Args:
    token (str): Token de autenticación.
    index (int): Índice de la imagen a descargar.
    """
    headers = {'Authorization': f'Bearer {token}'}
    try:
        response = requests.post(IMAGE_URL, headers=headers, json={'cantidad': 1})
        response.raise_for_status()
        with open(f"{TEMP_DIR}imagen_{index}.jpg", 'wb') as file:
            file.write(response.content)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error de red al descargar la imagen {index}: {e}")
    except IOError as e:
        logging.error(f"Error de E/S al guardar la imagen {index}: {e}")
    except Exception as e:
        logging.error(f"Error inesperado al descargar la imagen {index}: {e}")

def aplicar_transformaciones(imagen_path, transformaciones):
    """
    Aplica las transformaciones solicitadas a una imagen.

    Args:
    imagen_path (str): Ruta de la imagen a transformar.
    transformaciones (list): Lista de transformaciones a aplicar.
    """
    try:
        if not os.path.exists(imagen_path):
            raise FileNotFoundError(f"La imagen {imagen_path} no existe.")
        imagen = Image.open(imagen_path)
        for transformacion in transformaciones:
            if transformacion == 'blanco_y_negro':
                imagen = ImageOps.grayscale(imagen)
            elif transformacion == 'transponer':
                imagen = imagen.transpose(Image.FLIP_LEFT_RIGHT)
            elif transformacion == 'difuminar':
                imagen = imagen.filter(ImageFilter.GaussianBlur(5))
            elif transformacion == 'rotar':
                imagen = imagen.rotate(-90, expand=True)
        imagen.save(imagen_path)
    except Exception as e:
        logging.error(f"Error aplicando transformaciones a la imagen {imagen_path}: {e}")

def enviar_correo(destinatario, asunto, mensaje, adjuntos):
    """
    Envía un correo electrónico con los adjuntos especificados.

    Args:
    destinatario (str): Dirección de correo del destinatario.
    asunto (str): Asunto del correo.
    mensaje (str): Mensaje del correo.
    adjuntos (list): Lista de rutas de archivos a adjuntar.
    """
    try:
        remitente = "jmario.sanchezramirez@gmail.com"
        password = "hcilfythbxzwfpht"  # Contraseña de aplicación

        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = asunto
        msg.attach(MIMEText(mensaje, 'plain'))

        for adjunto in adjuntos:
            if os.path.exists(adjunto):
                part = MIMEBase('application', 'octet-stream')
                with open(adjunto, 'rb') as file:
                    part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(adjunto)}')
                msg.attach(part)
            else:
                logging.error(f"No se encontró el archivo adjunto: {adjunto}")

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        text = msg.as_string()
        server.sendmail(remitente, destinatario, text)
        server.quit()
    except Exception as e:
        logging.error(f"Error enviando correo a {destinatario}: {e}")

def main():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    try:
        cantidad_imagenes = int(input("Ingrese el número de imágenes a descargar (1-10): "))
    except ValueError:
        print("Entrada no válida. Debe ingresar un número entre 1 y 10.")
        return

    if cantidad_imagenes < 1 o cantidad_imagenes > 10:
        print("Número de imágenes no válido. Debe ser entre 1 y 10.")
        return

    token = obtener_token()
    if not token:
        print("Error obteniendo el token de autenticación.")
        return

    hilos_descarga = []
    for i in range(cantidad_imagenes):
        hilo = threading.Thread(target=descargar_imagen, args=(token, i + 1))
        hilos_descarga.append(hilo)
        hilo.start()

    for hilo in hilos_descarga:
        hilo.join()

    transformaciones_posibles = ['blanco_y_negro', 'transponer', 'difuminar', 'rotar']
    transformaciones_aplicadas = []

    for i in range(cantidad_imagenes):
        imagen_path = f"{TEMP_DIR}imagen_{i + 1}.jpg"
        transformaciones = []
        print(f"\nTransformaciones para imagen_{i + 1}.jpg:")
        for transformacion in transformaciones_posibles:
            aplicar = input(f"¿Desea aplicar {transformacion.replace('_', ' ')}? (s/n): ").strip().lower()
            if aplicar == 's':
                transformaciones.append(transformacion)
        aplicar_transformaciones(imagen_path, transformaciones)
        transformaciones_aplicadas.append(transformaciones)

    destinatario = input("Ingrese el correo electrónico del destinatario: ").strip()
    asunto = "Imágenes modificadas"
    mensaje = f"Hola,\n\nAdjunto encontrarás {cantidad_imagenes} imágenes modificadas.\n\nTransformaciones aplicadas:\n"

    for i, transformaciones in enumerate(transformaciones_aplicadas):
        mensaje += f"Imagen {i + 1}: {', '.join(transformaciones) if transformaciones else 'Ninguna'}\n"

    mensaje += "\nSaludos."

    # Agregar el archivo requirements.txt a la lista de adjuntos
    adjuntos = [f"{TEMP_DIR}imagen_{i + 1}.jpg" for i in range(cantidad_imagenes)]
    adjuntos.append(REQUIREMENTS_PATH)

    hilos_envio = threading.Thread(target=enviar_correo, args=(destinatario, asunto, mensaje, adjuntos))
    hilos_envio.start()
    hilos_envio.join()

# Pruebas unitarias
class TestImageProcessing(unittest.TestCase):

    @patch('requests.post')
    def test_obtener_token_exito(self, mock_post):
        """
        Prueba obtener_token con una respuesta exitosa.

        Args:
        mock_post (Mock): Objeto de prueba para requests.post.
        """
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = '"mocked_token"'
        token = obtener_token()
        self.assertEqual(token, 'mocked_token')

    @patch('requests.post')
    def test_obtener_token_error_http(self, mock_post):
        """
        Prueba obtener_token con un error HTTP.

        Args:
        mock_post (Mock): Objeto de prueba para requests.post.
        """
        mock_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("HTTP Error")
        token = obtener_token()
        self.assertIsNone(token)

    @patch('requests.post')
    @patch('builtins.open', new_callable=mock_open)
    def test_descargar_imagen_exito(self, mock_open, mock_post):
        """
        Prueba descargar_imagen con una descarga exitosa.

        Args:
        mock_open (Mock): Objeto de prueba para la función open.
        mock_post (Mock): Objeto de prueba para requests.post.
        """
        mock_post.return_value.status_code = 200
        mock_post.return_value.content = b'fake_image_content'
        token = 'mocked_token'
        index = 1
        descargar_imagen(token, index)
        mock_open.assert_called_with('imag_descargadas/imagen_1.jpg', 'wb')

    @patch('requests.post')
    def test_descargar_imagen_error_red(self, mock_post):
        """
        Prueba descargar_imagen con un error de red.

        Args:
        mock_post (Mock): Objeto de prueba para requests.post.
        """
        mock_post.side_effect = requests.exceptions.RequestException("Network Error")
        token = 'mocked_token'
        index = 1
        with self.assertLogs(level='ERROR') as log:
            descargar_imagen(token, index)
            self.assertIn("Error de red al descargar la imagen 1: Network Error", log.output[0])

    def test_aplicar_transformaciones_exito(self):
        """
        Prueba aplicar_transformaciones con una imagen y transformaciones válidas.

        """
        image = Image.new('RGB', (100, 100))
        image_path = 'imag_descargadas/imagen_test.jpg'
        image.save(image_path)
        transformaciones = ['blanco_y_negro', 'transponer', 'difuminar', 'rotar']
        aplicar_transformaciones(image_path, transformaciones)
        result_image = Image.open(image_path)
        self.assertIsNotNone(result_image)
        os.remove(image_path)

    def test_aplicar_transformaciones_imagen_no_existe(self):
        """
        Prueba aplicar_transformaciones con una imagen inexistente.

        """
        image_path = 'imag_descargadas/imagen_inexistente.jpg'
        transformaciones = ['blanco_y_negro']
        with self.assertLogs(level='ERROR') as log:
            aplicar_transformaciones(image_path, transformaciones)
            self.assertIn(f"La imagen {image_path} no existe.", log.output[0])

    @patch('smtplib.SMTP')
    @patch('os.path.exists', return_value=True)
    def test_enviar_correo_exito(self, mock_exists, mock_smtp):
        """
        Prueba enviar_correo con un envío exitoso.

        Args:
        mock_exists (Mock): Objeto de prueba para os.path.exists.
        mock_smtp (Mock): Objeto de prueba para smtplib.SMTP.
        """
        destinatario = 'test@example.com'
        asunto = 'Test Email'
        mensaje = 'This is a test email.'
        adjuntos = ['imag_descargadas/imagen_1.jpg']
        enviar_correo(destinatario, asunto, mensaje, adjuntos)
        mock_smtp.return_value.sendmail.assert_called()

    @patch('smtplib.SMTP')
    @patch('os.path.exists', return_value=False)
    def test_enviar_correo_archivo_no_existe(self, mock_exists, mock_smtp):
        """
        Prueba enviar_correo con un archivo adjunto inexistente.

        Args:
        mock_exists (Mock): Objeto de prueba para os.path.exists.
        mock_smtp (Mock): Objeto de prueba para smtplib.SMTP.
        """
        destinatario = 'test@example.com'
        asunto = 'Test Email'
        mensaje = 'This is a test email.'
        adjuntos = ['imag_descargadas/imagen_inexistente.jpg']
        with self.assertLogs(level='ERROR') as log:
            enviar_correo(destinatario, asunto, mensaje, adjuntos)
            self.assertIn("No se encontró el archivo adjunto: imag_descargadas/imagen_inexistente.jpg", log.output[0])

if __name__ == '__main__':
    unittest.main(exit=False)  # Ejecutar pruebas unitarias
    main()
