import requests


def send_data_tor(url, data, timeout=30):
    """
    Envía datos a través de la red Tor usando un proxy SOCKS5 local.
    El usuario debe tener el servicio Tor corriendo en 127.0.0.1:9050.
    Devuelve el contenido de la respuesta o None si hay error.
    """
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    try:
        response = requests.post(url, data=data, proxies=proxies, timeout=timeout)
        response.raise_for_status()
        print(f"[Tor] Datos enviados correctamente a {url} (status {response.status_code})")
        return response.content
    except requests.RequestException as e:
        print(f"[Tor] Error enviando datos a {url}: {e}")
        return None

def receive_data_tor(url, timeout=30):
    """
    Recibe datos a través de la red Tor usando un proxy SOCKS5 local.
    Devuelve el contenido de la respuesta o None si hay error.
    """
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    try:
        response = requests.get(url, proxies=proxies, timeout=timeout)
        response.raise_for_status()
        print(f"[Tor] Datos recibidos correctamente de {url} (status {response.status_code})")
        return response.content
    except requests.RequestException as e:
        print(f"[Tor] Error recibiendo datos de {url}: {e}")
        return None 