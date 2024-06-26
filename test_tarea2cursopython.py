import unittest
import os
from io import BytesIO
from unittest.mock import patch, MagicMock
from PIL import Image, ImageFilter
from tarea2cursopython import obtener_token, descargar_imagen, aplicar_transformaciones, enviar_correo, TEMP_DIR, REQUIREMENTS_PATH

class TestObtenerToken(unittest.TestCase):
    """
    Pruebas unitarias para la función obtener_token.

    Métodos de prueba:
    - test_obtener_token_exitoso: Verifica el caso de éxito al obtener el token.
    - test_obtener_token_fallo: Verifica el manejo de errores al no poder obtener el token.
    """

    @patch('requests.post')
    def test_obtener_token_exitoso(self, mock_post):
        """
        Caso de prueba: Obtener token exitosamente.
        """
        mock_response = MagicMock()
        mock_response.text = '"abcdef1234567890"'
        mock_post.return_value = mock_response

        token = obtener_token()

        self.assertEqual(token, 'abcdef1234567890')

    @patch('requests.post')
    def test_obtener_token_fallo(self, mock_post):
        """
        Caso de prueba: Fallo al obtener el token.
        """
        mock_post.side_effect = Exception("Error de prueba")

        token = obtener_token()

        self.assertIsNone(token)

class TestDescargarImagen(unittest.TestCase):
    """
    Pruebas unitarias para la función descargar_imagen.

    Métodos de prueba:
    - test_descargar_imagen_exitoso: Verifica la descarga exitosa de una imagen.
    - test_descargar_imagen_fallo_red: Verifica el manejo de errores de red durante la descarga.
    """

    @patch('requests.post')
    def test_descargar_imagen_exitoso(self, mock_post):
        """
        Caso de prueba: Descargar imagen exitosamente.
        """
        mock_response = MagicMock()
        mock_response.content = b'imagen_binaria_simulada'
        mock_post.return_value = mock_response

        token = 'abcdef1234567890'
        index = 1

        descargar_imagen(token, index)

        filename = f"{TEMP_DIR}imagen_{index}.jpg"
        self.assertTrue(os.path.exists(filename))

    @patch('requests.post')
    def test_descargar_imagen_fallo_red(self, mock_post):
        """
        Caso de prueba: Fallo de red durante la descarga de imagen.
        """
        mock_post.side_effect = requests.exceptions.RequestException("Error de red")

        token = 'abcdef1234567890'
        index = 2

        descargar_imagen(token, index)

        filename = f"{TEMP_DIR}imagen_{index}.jpg"
        self.assertFalse(os.path.exists(filename))

class TestAplicarTransformaciones(unittest.TestCase):
    """
    Pruebas unitarias para la función aplicar_transformaciones.

    Métodos de prueba:
    - test_aplicar_transformaciones_normales: Verifica la aplicación de transformaciones normales a una imagen.
    - test_aplicar_transformaciones_sin_archivo: Verifica el manejo de error al intentar aplicar transformaciones a una imagen inexistente.
    """

    def setUp(self):
        # Crear una imagen de prueba
        self.imagen_path = f"{TEMP_DIR}imagen_prueba.jpg"
        imagen = Image.new('RGB', (100, 100), color='red')
        imagen.save(self.imagen_path)

    def tearDown(self):
        # Eliminar la imagen de prueba
        if os.path.exists(self.imagen_path):
            os.remove(self.imagen_path)

    def test_aplicar_transformaciones_normales(self):
        """
        Caso de prueba: Aplicar transformaciones normales a una imagen.
        """
        transformaciones = ['blanco_y_negro', 'rotar']
        aplicar_transformaciones(self.imagen_path, transformaciones)

        self.assertTrue(os.path.exists(self.imagen_path))

    def test_aplicar_transformaciones_sin_archivo(self):
        """
        Caso de prueba: Manejo de error al aplicar transformaciones a una imagen inexistente.
        """
        with self.assertRaises(FileNotFoundError):
            aplicar_transformaciones("imagen_inexistente.jpg", ['blanco_y_negro'])

class TestEnviarCorreo(unittest.TestCase):
    """
    Pruebas unitarias para la función enviar_correo.

    Métodos de prueba:
    - test_enviar_correo_exitoso: Verifica el envío exitoso de correo electrónico.
    - test_enviar_correo_fallo: Verifica el manejo de errores al intentar enviar correo electrónico.
    """

    @patch('smtplib.SMTP')
    def test_enviar_correo_exitoso(self, mock_smtp):
        """
        Caso de prueba: Envío exitoso de correo electrónico.
        """
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        destinatario = 'destinatario@example.com'
        asunto = 'Prueba de correo'
        mensaje = 'Este es un mensaje de prueba'
        adjuntos = []

        enviar_correo(destinatario, asunto, mensaje, adjuntos)

        mock_server.sendmail.assert_called_once()

    @patch('smtplib.SMTP')
    def test_enviar_correo_fallo(self, mock_smtp):
        """
        Caso de prueba: Fallo al enviar correo electrónico.
        """
        mock_smtp.side_effect = Exception("Error de prueba")

        destinatario = 'destinatario@example.com'
        asunto = 'Prueba de correo'
        mensaje = 'Este es un mensaje de prueba'
        adjuntos = []

        enviar_correo(destinatario, asunto, mensaje, adjuntos)

        mock_smtp.assert_called_once()

if __name__ == '__main__':
    unittest.main()
