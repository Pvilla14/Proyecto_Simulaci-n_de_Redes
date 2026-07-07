import hmac
import hashlib
import os

# Clave secreta compartida entre sensores y salmuera. En un entorno real se
# inyecta por variable de entorno (FIRMA_KEY); aqui hay un valor por defecto
# para que la demo funcione sin configuracion extra.
_CLAVE = os.environ.get("FIRMA_KEY", "clave-demo-salmuera-2024").encode()


def _mensaje(valores):
    # Forma canonica estable: los mismos valores producen la misma cadena en el
    # emisor y en el receptor (repr conserva los floats de forma exacta).
    return "|".join(repr(v) for v in valores).encode()


def firmar(valores):
    """Devuelve la firma HMAC-SHA256 (hex) de una lista de valores."""
    return hmac.new(_CLAVE, _mensaje(valores), hashlib.sha256).hexdigest()


def verificar(firma, valores):
    """True si la firma corresponde a los valores (comparacion en tiempo constante)."""
    esperada = firmar(valores)
    return hmac.compare_digest(esperada, firma or "")
