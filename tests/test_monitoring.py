"""Proves del mòdul de monitoratge de disponibilitat (§3.8.4).

R14, zero simulacions: aquestes proves construeixen **servidors HTTP locals
reals** sobre `http.server`, no objectes simulats que substitueixin el sistema
provat. El transport injectat fa peticions HTTP de veritat a una adreça local.
"""

import sys
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from projects.rlf_suppliers_eu27.monitoring.availability import (  # noqa: E402
    ROBOTS_ALLOWED,
    ROBOTS_DISALLOWED,
    ROBOTS_UNREADABLE,
    SIGNAL_IN_STOCK,
    SIGNAL_NONE,
    SIGNAL_SOLD,
    STATUS_AVAILABLE,
    STATUS_NOT_AVAILABLE,
    STATUS_PARKED,
    STATUS_STALE,
    DomainThrottle,
    check_availability,
    classify_signal,
    decide_availability,
    monitoring_load_estimate,
    parse_robots,
)


class _Handler(BaseHTTPRequestHandler):
    """Gestor de proves que serveix un cos i un codi fixats per la prova."""

    status_code: int = 200
    body: str = ""
    robots_body: str = "User-agent: *\nAllow: /\n"
    robots_readable: bool = True

    def do_GET(self) -> None:  # noqa: N802 - nom imposat per BaseHTTPRequestHandler
        """Respon la petició amb el codi i el cos configurats."""
        if self.path == "/robots.txt":
            if not self.robots_readable:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"error")
                return
            payload = self.robots_body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        payload = self.body.encode("utf-8")
        self.send_response(self.status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        """Silencia el registre per defecte del servidor de proves."""
        return


class LocalTransport:
    """Transport real contra un servidor HTTP local (R14)."""

    def __init__(self, base_url: str) -> None:
        """Guarda l'adreça base del servidor local.

        Args:
            base_url: URL base, per exemple `http://127.0.0.1:PORT`.
        """
        self.base_url = base_url.rstrip("/")

    def get(self, url: str) -> Any:
        """Executa una petició GET real al servidor local.

        Args:
            url: URL completa.

        Returns:
            Un objecte amb `status` i `body`.
        """
        path = "/" + url.split("/", 3)[3] if url.count("/") >= 3 else "/"
        with urllib.request.urlopen(f"{self.base_url}{path}", timeout=5) as response:
            body = response.read().decode("utf-8", errors="replace")
            return type("Response", (), {"status": response.status, "body": body})()

    def get_robots(self, domain: str) -> Optional[str]:
        """Llegeix robots.txt real del servidor local.

        Args:
            domain: Host (no s'usa; el servidor és local).

        Returns:
            El contingut de robots.txt, o None si la resposta no és 200.
        """
        try:
            with urllib.request.urlopen(f"{self.base_url}/robots.txt", timeout=5) as response:
                if response.status != 200:
                    return None
                return response.read().decode("utf-8", errors="replace")
        except Exception:  # noqa: BLE001 - no llegible és el resultat esperat
            return None


def _start_server() -> tuple[HTTPServer, str]:
    """Arrenca un servidor HTTP local real i retorna la seva URL base.

    Returns:
        Una tupla amb el servidor i la URL base.
    """
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[0], server.server_address[1]
    return server, f"http://{host}:{port}"


def _no_wait_throttle() -> DomainThrottle:
    """Retorna un limitador sense espera real, per no alentir les proves."""
    return DomainThrottle(minimum_interval_seconds=0.0)


def test_parse_robots_detects_disallow_all() -> None:
    """Un Disallow: / es llegeix com a prohibició."""
    result = parse_robots("User-agent: *\nDisallow: /\n")
    assert result["data"]["verdict"] == ROBOTS_DISALLOWED


def test_parse_robots_allows_when_not_disallowed() -> None:
    """Sense prohibició global, el veredicte és permès."""
    result = parse_robots("User-agent: *\nDisallow: /private/\n")
    assert result["data"]["verdict"] == ROBOTS_ALLOWED


def test_parse_robots_is_fail_closed_when_unreadable() -> None:
    """robots.txt no llegible és HOLD amb veredicte unreadable."""
    result = parse_robots(None)
    assert result["status"] == "HOLD"
    assert result["meta"]["verdict"] == ROBOTS_UNREADABLE


def test_classify_signal_does_not_default_to_in_stock() -> None:
    """Sense senyal, no s'inventa disponibilitat."""
    assert classify_signal("<html><body>Product</body></html>") == SIGNAL_NONE
    assert classify_signal('{"availability":"https://schema.org/InStock"}') == SIGNAL_IN_STOCK
    assert classify_signal("This item is sold out") == SIGNAL_SOLD


def test_decide_availability_parks_on_rate_limit() -> None:
    """401/403/429 aparquen el domini."""
    assert decide_availability(429, SIGNAL_IN_STOCK) == STATUS_PARKED
    assert decide_availability(403, SIGNAL_IN_STOCK) == STATUS_PARKED


def test_decide_availability_never_available_without_signal() -> None:
    """HTTP 200 sense senyal positiu és STALE, mai AVAILABLE."""
    assert decide_availability(200, SIGNAL_NONE) == STATUS_STALE
    assert decide_availability(200, SIGNAL_IN_STOCK) == STATUS_AVAILABLE
    assert decide_availability(200, SIGNAL_SOLD) == STATUS_NOT_AVAILABLE


def test_decide_availability_maps_404_to_not_available() -> None:
    """404 i 410 signifiquen no disponible."""
    assert decide_availability(404, SIGNAL_NONE) == STATUS_NOT_AVAILABLE
    assert decide_availability(410, SIGNAL_NONE) == STATUS_NOT_AVAILABLE


def test_decide_availability_maps_server_error_to_stale() -> None:
    """Un 5xx és STALE, no no-disponible."""
    assert decide_availability(503, SIGNAL_NONE) == STATUS_STALE


def test_check_availability_against_a_real_local_server() -> None:
    """Prova real: servidor HTTP local que respon InStock."""
    _Handler.status_code = 200
    _Handler.body = '{"availability":"https://schema.org/InStock"}'
    _Handler.robots_body = "User-agent: *\nAllow: /\n"
    _Handler.robots_readable = True
    server, base_url = _start_server()
    try:
        transport = LocalTransport(base_url)
        result = check_availability(
            f"{base_url}/item/1", transport, throttle=_no_wait_throttle()
        )
        assert result["status"] == "SUCCESS"
        assert result["data"]["status"] == STATUS_AVAILABLE
        assert result["data"]["robots"] == ROBOTS_ALLOWED
    finally:
        server.shutdown()


def test_check_availability_reads_sold_page_as_not_available() -> None:
    """Prova real: pàgina 200 que diu venut -> no disponible."""
    _Handler.status_code = 200
    _Handler.body = "<html>Sold out</html>"
    server, base_url = _start_server()
    try:
        transport = LocalTransport(base_url)
        result = check_availability(
            f"{base_url}/item/2", transport, throttle=_no_wait_throttle()
        )
        assert result["data"]["status"] == STATUS_NOT_AVAILABLE
        assert result["data"]["signal"] == SIGNAL_SOLD
    finally:
        server.shutdown()


def test_check_availability_holds_when_robots_unreadable() -> None:
    """Prova real: robots.txt que respon 500 -> HOLD, fail-closed."""
    _Handler.robots_readable = False
    server, base_url = _start_server()
    try:
        transport = LocalTransport(base_url)
        result = check_availability(
            f"{base_url}/item/3", transport, throttle=_no_wait_throttle()
        )
        assert result["status"] == "HOLD"
    finally:
        _Handler.robots_readable = True
        server.shutdown()


def test_monitoring_load_matches_the_canonical_arithmetic() -> None:
    """La càrrega calculada coincideix amb §3.8.4: ≈328.400 peticions/dia."""
    result = monitoring_load_estimate()
    assert result["data"]["sale_backup_requests_per_hour"] == 13200
    assert result["data"]["sale_backup_requests_per_day"] == 316800
    assert result["data"]["pool_requests_per_day"] == 11600
    assert result["data"]["total_requests_per_day"] == 328400


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
    print(f"OK: {len(tests)} proves passades")
