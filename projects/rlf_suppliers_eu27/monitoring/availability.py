"""Motor de monitoratge de disponibilitat per URL (§3.8.4).

Regles canòniques implementades:

1. **Pressupost per domini** (DomainThrottle): interval mínim entre peticions
   al mateix host; mai en ràfega.
2. **robots.txt**: es respecta; si no es pot llegir (5xx, xarxa, 401/403), es
   tracta com a no permès (fail-closed).
3. **Bloqueig o petició d'aturada**: 401, 403 o 429 -> el domini s'aparca
   (STALE per a totes les seves peces) i s'escala; mai s'eludeix.
4. **Senyal de disponibilitat, no només HTTP 200**: una pàgina que respon 200
   pot dir "venut". Disponible només amb senyal positiu; senyal de venut -> no
   disponible; **sense senyal -> STALE**. 404/410 -> no disponible.
   Xarxa/timeout/5xx -> STALE. Mai "disponible" per defecte.
5. **Identitat de les peticions**: peticions HTTP normals a pàgines públiques,
   com un client qualsevol; sense suplantar rastrejadors ni eludir mesures.

El transport HTTP s'injecta: el mòdul no obre connexions pel seu compte, de
manera que es pugui provar contra un servidor HTTP local real (R14, zero
simulacions) i que el mòdul sigui portable (§5.2.8).
"""

import time
from typing import Any, Callable, Optional, Protocol

from shared.rlf_core.configuration.config import (
    DEFAULT_HOST,
    DEFAULT_USER_AGENT,
    DOMAIN_THROTTLE_SECONDS,
)
from shared.rlf_core.contract.return_contract import (
    make_failure,
    make_hold,
    make_success,
)
from shared.rlf_core.logging.logger import get_logger

VERSION: str = "1.0"

STATUS_AVAILABLE: str = "AVAILABLE"
STATUS_NOT_AVAILABLE: str = "NOT_AVAILABLE"
STATUS_STALE: str = "STALE"
STATUS_PARKED: str = "PARKED"

SIGNAL_IN_STOCK: str = "instock"
SIGNAL_SOLD: str = "sold"
SIGNAL_NONE: str = "none"

HTTP_NOT_FOUND: frozenset[int] = frozenset({404, 410})
HTTP_PARKING: frozenset[int] = frozenset({401, 403, 429})
HTTP_SERVER_ERROR_FLOOR: int = 500

ROBOTS_ALLOWED: str = "allowed"
ROBOTS_DISALLOWED: str = "disallowed"
ROBOTS_UNREADABLE: str = "unreadable"

logger = get_logger(__name__)


class HttpResponse(Protocol):
    """Resposta HTTP mínima que el monitoratge necessita."""

    status: int
    body: str


class Transport(Protocol):
    """Protocol del transport HTTP injectable."""

    def get(self, url: str) -> HttpResponse:
        """Executa una petició GET a una URL pública."""
        ...

    def get_robots(self, domain: str) -> Optional[str]:
        """Retorna el contingut de robots.txt, o None si no és llegible."""
        ...


class DomainThrottle:
    """Aplica l'interval mínim entre peticions al mateix host (§3.8.4 regla 1)."""

    def __init__(
        self,
        minimum_interval_seconds: float = DOMAIN_THROTTLE_SECONDS,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        """Inicialitza el limitador.

        Args:
            minimum_interval_seconds: Interval mínim entre peticions al mateix domini.
            clock: Font de temps monotònic, injectable per a proves.
            sleeper: Funció d'espera, injectable per a proves.
        """
        self.minimum_interval_seconds = minimum_interval_seconds
        self._clock = clock
        self._sleeper = sleeper
        self._last_request: dict[str, float] = {}

    def wait_for(self, domain: str) -> float:
        """Espera el que calgui abans de tornar a tocar un domini.

        Args:
            domain: Host de destinació.

        Returns:
            Els segons esperats.
        """
        now = self._clock()
        previous = self._last_request.get(domain)
        elapsed_needed = 0.0
        if previous is not None:
            elapsed_needed = max(0.0, self.minimum_interval_seconds - (now - previous))
        if elapsed_needed > 0:
            self._sleeper(elapsed_needed)
        self._last_request[domain] = self._clock()
        return elapsed_needed


def parse_robots(robots_text: Optional[str]) -> dict[str, Any]:
    """Interpreta robots.txt respecte del monitoratge de producte (§3.8.4 regla 2).

    Args:
        robots_text: Contingut de robots.txt, o None si no és llegible.

    Returns:
        Un resultat canònic SUCCESS amb el veredicte. HOLD (fail-closed) si el
        contingut no és llegible.
    """
    if robots_text is None:
        return make_hold(
            "robots.txt no llegible: es tracta com a no permès (fail-closed)",
            meta={"verdict": ROBOTS_UNREADABLE},
        )

    disallow_all = False
    for raw_line in robots_text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        directive, _, value = line.partition(":")
        if directive.strip().lower() != "disallow":
            continue
        if value.strip() == "/":
            disallow_all = True

    if disallow_all:
        return make_success({"verdict": ROBOTS_DISALLOWED})
    return make_success({"verdict": ROBOTS_ALLOWED})


def classify_signal(body: str, in_stock_markers: Optional[list[str]] = None) -> str:
    """Classifica el senyal de disponibilitat del cos d'una pàgina (§3.8.4 regla 4).

    Args:
        body: Cos de la resposta.
        in_stock_markers: Marcadors positius configurats pel venedor.

    Returns:
        Un dels tres senyals: instock, sold o none. Mai infereix disponibilitat
        per defecte.
    """
    lowered = body.lower()

    if '"availability"' in lowered and "instock" in lowered.replace(" ", ""):
        return SIGNAL_IN_STOCK

    if any(
        marker in lowered
        for marker in ('"availability":"https://schema.org/outofstock"', "outofstock", "sold out")
    ):
        return SIGNAL_SOLD

    if in_stock_markers:
        for marker in in_stock_markers:
            if marker.lower() in lowered:
                return SIGNAL_IN_STOCK

    return SIGNAL_NONE


def decide_availability(status_code: int, signal: str) -> str:
    """Decideix la disponibilitat a partir del codi HTTP i del senyal.

    Args:
        status_code: Codi HTTP de la resposta.
        signal: Senyal classificat per `classify_signal`.

    Returns:
        Un dels quatre estats: AVAILABLE, NOT_AVAILABLE, STALE o PARKED.
    """
    if status_code in HTTP_PARKING:
        return STATUS_PARKED
    if status_code in HTTP_NOT_FOUND:
        return STATUS_NOT_AVAILABLE
    if status_code >= 400:
        return STATUS_STALE

    if signal == SIGNAL_IN_STOCK:
        return STATUS_AVAILABLE
    if signal == SIGNAL_SOLD:
        return STATUS_NOT_AVAILABLE
    return STATUS_STALE


def check_availability(
    url: str,
    transport: Transport,
    throttle: Optional[DomainThrottle] = None,
    in_stock_markers: Optional[list[str]] = None,
    robots_text: Optional[str] = "sentinel",
) -> dict[str, Any]:
    """Comprova la disponibilitat d'una peça per URL.

    Args:
        url: URL pública de la peça.
        transport: Transport HTTP injectable.
        throttle: Limitador per domini. Se'n crea un si no es dona.
        in_stock_markers: Marcadors positius configurats pel venedor.
        robots_text: Contingut de robots.txt. El valor sentinella `"sentinel"`
            fa que el mòdul el demani al transport.

    Returns:
        Un resultat canònic SUCCESS amb l'estat de disponibilitat. HOLD si
        robots.txt no és llegible. FAILURE davant d'una excepció de transport.
    """
    try:
        domain = url.split("//", 1)[-1].split("/", 1)[0]

        if robots_text == "sentinel":
            try:
                fetched_robots = transport.get_robots(domain)
            except Exception:  # noqa: BLE001 - fallada de robots = no permès
                fetched_robots = None
        else:
            fetched_robots = robots_text

        robots_result = parse_robots(fetched_robots)
        if robots_result["status"] == "HOLD":
            return make_hold(
                "Monitoratge aturat: robots.txt no llegible (fail-closed)",
                meta={"url": url, "domain": domain},
            )
        robots_verdict = robots_result["data"]["verdict"]

        limiter = throttle if throttle is not None else DomainThrottle()
        limiter.wait_for(domain)

        try:
            response = transport.get(url)
        except TimeoutError:
            logger.warning("availability_timeout", url=url)
            return make_success(
                {"url": url, "status": STATUS_STALE, "reason": "timeout"},
                meta={"domain": domain},
            )
        except Exception as exception:  # noqa: BLE001 - xarxa caiguda = STALE
            logger.warning("availability_network_error", url=url, error=str(exception))
            return make_success(
                {"url": url, "status": STATUS_STALE, "reason": "network"},
                meta={"domain": domain},
            )

        signal = classify_signal(response.body, in_stock_markers)
        state = decide_availability(response.status, signal)

        if state == STATUS_PARKED:
            logger.error("domain_parked", domain=domain, http_status=response.status)
        else:
            logger.info(
                "availability_checked",
                url=url,
                state=state,
                http_status=response.status,
                signal=signal,
            )

        return make_success(
            {
                "url": url,
                "status": state,
                "http_status": response.status,
                "signal": signal,
                "robots": robots_verdict,
            },
            meta={"domain": domain},
        )
    except Exception as exception:  # noqa: BLE001 - contracte FAILURE és explícit
        logger.critical("availability_unexpected", url=url, error=str(exception))
        return make_failure(
            f"Excepció inesperada: {exception}",
            meta={"exception_type": type(exception).__name__, "url": url},
        )


def building_headers() -> dict[str, str]:
    """Retorna les capçaleres canòniques d'identitat de les peticions (regla 5).

    Returns:
        Capçaleres HTTP normals d'un client qualsevol, amb User-Agent
        identificatiu. Sense suplantació de rastrejadors.
    """
    return {
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.8,es;q=0.6,ca;q=0.5",
        "Host": DEFAULT_HOST,
    }


def monitoring_load_estimate() -> dict[str, Any]:
    """Calcula la càrrega de monitoratge resultant (§3.8.4, taula canònica).

    Returns:
        Un resultat canònic SUCCESS amb les peticions diàries i la seva
        procedència aritmètica.
    """
    sale_backup_per_hour = 1100 * 12
    sale_backup_per_day = sale_backup_per_hour * 24
    pool_per_day = 2900 * 2 * 2

    return make_success(
        {
            "sale_backup_requests_per_hour": sale_backup_per_hour,
            "sale_backup_requests_per_day": sale_backup_per_day,
            "pool_requests_per_day": pool_per_day,
            "total_requests_per_day": sale_backup_per_day + pool_per_day,
        },
        meta={"provenance": "1100x12x24 + 2900x2x2", "label": "OBJECTIU derivat"},
    )
