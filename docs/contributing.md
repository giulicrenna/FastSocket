# Contribuir

¡Las contribuciones son bienvenidas! Seguí estos pasos para colaborar.

## Setup de desarrollo

```bash
git clone https://github.com/giulicrenna/FastSocket.git
cd FastSocket
pip install -e ".[dev]"
```

## Ejecutar tests

```bash
pytest tests/
```

## Estilo de código

- Seguir PEP 8.
- Tipado con `typing` en firmas públicas.
- Docstrings en clases y métodos públicos.

## Pull Requests

1. Crear un branch desde `main`.
2. Hacer los cambios con commits descriptivos.
3. Abrir un PR explicando el motivo del cambio.
4. Esperar revisión antes de mergear.

## Reportar bugs

Usar [GitHub Issues](https://github.com/giulicrenna/FastSocket/issues) con:

- Versión de Python y FastSocket.
- Reproducción mínima del problema.
- Traceback completo si aplica.
