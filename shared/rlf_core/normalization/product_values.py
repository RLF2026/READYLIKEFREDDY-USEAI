"""Motor de normalització de valors canònics de producte Fred Perry.

Implementa §3.5.8, §3.5.8.2, §3.5.8.4, §3.5.8.5 i §3.5.8.8–§3.5.8.13 del
document mestre canònic (OP-032 i OP-033, ambdós TANCATS).

Regla d'or ratificada pel propietari: **el prefix alfabètic del codi de model
no és per si sol un discriminador de categoria fiable.** El mateix prefix
apareix en categories diferents (J1331 és un polo; J2660 és una jaqueta).
Per tant, `category`/`subcategory` són els camps que determinen la categoria;
el prefix es conserva només com a component literal del codi.

Cap valor "típic de família" s'extrapola d'un altre colorway: extrapolar-lo
violaria R14 i R17 (§3.5.8.10).
"""

from typing import Any, Optional

from shared.rlf_core.contract.return_contract import (
    make_failure,
    make_hold,
    make_reject,
    make_success,
)
from shared.rlf_core.logging.logger import get_logger

VERSION: str = "1.0"

NOT_APPLICABLE: str = "NOT_APPLICABLE"

CATEGORIES: tuple[str, ...] = (
    "Polo Shirts",
    "Coats & Jackets",
    "Overshirts",
    "Shirts",
    "Sweatshirts",
    "Knitwear",
    "T-Shirts",
    "Track Jackets",
    "Tracksuits",
    "Trousers",
    "Shorts",
    "Accessories",
    "Bags",
    "Shoes",
)

TOP_SIZE_LETTERS: tuple[str, ...] = ("XS", "S", "M", "L", "XL", "XXL", "XXXL")
TOP_SIZE_CHEST_INCHES: tuple[str, ...] = (
    "32-34", "35-37", "38-40", "41-43", "44-46", "47-49", "50-52"
)
TROUSER_WAIST_INCHES: tuple[str, ...] = ("30", "32", "34", "36", "38", "40")
TROUSER_WAIST_CENTIMETRES: tuple[str, ...] = ("76", "81", "86", "91", "96", "101")

PLAUSIBILITY_RANGES: dict[str, tuple[str, ...]] = {
    "Coats & Jackets": ("100% Polyamide", "53% Cotton / 47% Lyocell"),
    "Overshirts": ("100% Cotton", "60% Polyester / 40% Recycled Polyamide"),
    "Shirts": ("100% Cotton",),
    "Sweatshirts": ("100% Cotton", "79% Cotton / 21% Polyester"),
    "Knitwear": ("52% Wool / 48% Cotton", "54% Wool / 46% Cotton"),
    "T-Shirts": ("100% Cotton",),
    "Track Jackets": (
        "54% Recycled Polyester / 46% Cotton",
        "56-59% Recycled Polyester / 41-44% Cotton",
    ),
    "Trousers": (
        "54% Recycled Polyester / 46% Cotton",
        "53% Cotton / 44% Recycled Polyester / 3% Elastane",
    ),
    "Shorts": ("100% Cotton", "54% Recycled Polyester / 46% Cotton"),
    "Accessories": ("100% Cotton",),
    "Bags": ("100% Recycled Polyester",),
}

logger = get_logger(__name__)


def normalise_model_code(raw_value: str) -> dict[str, Any]:
    """Normalitza un codi de model o d'estil.

    Conserva el codi literal en majúscules, sense extreure'n cap inferència de
    categoria (§3.5.8.9).

    Args:
        raw_value: Valor cru del codi.

    Returns:
        Un resultat canònic SUCCESS amb el codi normalitzat i el prefix, o
        REJECT si el valor és buit.
    """
    if not raw_value or not raw_value.strip():
        return make_reject("El codi de model no pot ser buit")

    cleaned = raw_value.strip().upper().replace(" ", "")
    prefix = "".join(character for character in cleaned if character.isalpha())
    return make_success(
        {
            "raw_value": raw_value,
            "normalized_value": cleaned,
            "prefix": prefix,
            "prefix_is_category_discriminator": False,
        }
    )


def normalise_colour(raw_value: str) -> dict[str, Any]:
    """Normalitza una cadena de color conservant-la sencera.

    Args:
        raw_value: Cadena de color tal com apareix a la font.

    Returns:
        Un resultat canònic SUCCESS amb el valor normalitzat, o REJECT si és buit.
    """
    if not raw_value or not raw_value.strip():
        return make_reject("La cadena de color no pot ser buida")

    collapsed = " ".join(raw_value.strip().split())
    return make_success({"raw_value": raw_value, "normalized_value": collapsed.title()})


def build_canonical_name(
    product_name: str,
    model_code: str,
    colour_chain: str,
    category: Optional[str] = None,
) -> dict[str, Any]:
    """Construeix el nom canònic d'un producte (§3.5.8.2, §3.5.8.12).

    A diferència del cas polo, a la resta de categories **no s'elimina cap
    redundància**: el nom de producte de cada categoria és el que la font
    declara, sense reconstruir-lo.

    Args:
        product_name: Nom oficial de producte a la font.
        model_code: Codi de model o d'estil.
        colour_chain: Cadena de color completa.
        category: Categoria pare, si es coneix.

    Returns:
        Un resultat canònic SUCCESS amb el nom canònic. REJECT si falta algun
        component obligatori. HOLD si la categoria és desconeguda.
    """
    if not product_name or not product_name.strip():
        return make_reject("El nom de producte no pot ser buit")
    if not model_code or not model_code.strip():
        return make_reject("El codi de model no pot ser buit")
    if not colour_chain or not colour_chain.strip():
        return make_reject("La cadena de color no pot ser buida")

    if category is not None and category not in CATEGORIES:
        return make_hold("Categoria no reconeguda a la taxonomia oficial", meta={"category": category})

    parts = [
        product_name.strip(),
        model_code.strip().upper(),
        " ".join(colour_chain.strip().split()),
    ]
    return make_success(
        {
            "canonical_name": " — ".join(parts),
            "redundancy_removed": False,
            "category": category,
        }
    )


def resolve_sizing_system(category: str) -> dict[str, Any]:
    """Determina el sistema de talla aplicable a una categoria (§3.5.8.11).

    Args:
        category: Categoria pare.

    Returns:
        Un resultat canònic SUCCESS amb el sistema de talla. HOLD si la
        categoria és desconeguda.
    """
    if category not in CATEGORIES:
        return make_hold("Categoria no reconeguda", meta={"category": category})

    if category == "Shoes":
        return make_success(
            {
                "sizing_system": "footwear",
                "reference_systems": ("UK", "EU", "US"),
                "fit_field_value": "not_applicable_until_declared_by_sku",
            }
        )

    if category == "Bags":
        return make_success(
            {
                "sizing_system": "none",
                "fit_field_value": NOT_APPLICABLE,
                "persistent_justification": "categoria sense talla de cos",
            }
        )

    if category == "Accessories":
        return make_success(
            {
                "sizing_system": "one_size_adjustable",
                "fit_field_value": "as_declared_by_sku",
            }
        )

    return make_success(
        {
            "sizing_system": "top_letters",
            "size_letters": TOP_SIZE_LETTERS,
            "chest_inches": TOP_SIZE_CHEST_INCHES,
        }
    )


def resolve_trouser_sizing() -> dict[str, Any]:
    """Retorna el sistema numèric de talla de pantalons (§3.5.8.11).

    Returns:
        Un resultat canònic SUCCESS amb les talles en polzades i centímetres.
    """
    return make_success(
        {
            "sizing_system": "trouser_numeric",
            "waist_inches": TROUSER_WAIST_INCHES,
            "waist_centimetres": TROUSER_WAIST_CENTIMETRES,
            "letters_not_used_for_general_trouser_line": True,
        }
    )


def normalise_material(
    raw_value: str,
    category: str,
    is_shoes: bool = False,
) -> dict[str, Any]:
    """Normalitza la composició material d'un SKU (§3.5.8.10, §3.5.8.13).

    Sempre amb el valor declarat a la fitxa concreta de l'SKU (colorway
    inclòs), mai amb un valor típic de família extrapolat.

    Args:
        raw_value: Composició declarada a la fitxa.
        category: Categoria pare.
        is_shoes: True si és calçat, que requereix format de dues parts.

    Returns:
        Un resultat canònic SUCCESS amb el valor normalitzat. REJECT si el
        valor és buit. HOLD si el calçat no porta composició de dues parts.
    """
    if not raw_value or not raw_value.strip():
        return make_reject("La composició no pot ser buida")

    collapsed = " ".join(raw_value.strip().split())

    if is_shoes or category == "Shoes":
        has_two_parts = "Upper:" in collapsed and "Sole:" in collapsed
        if not has_two_parts:
            return make_hold(
                "El calçat requereix composició en dues parts: Upper: ... — Sole: ...",
                meta={"category": category, "declared": collapsed},
            )
        return make_success(
            {"normalized_value": collapsed, "two_part": True, "value_from_sku_declaration": True}
        )

    ranges = PLAUSIBILITY_RANGES.get(category)
    plausible = True
    if ranges:
        plausible = any(fragment.split("%")[0].rstrip("-") in collapsed for fragment in ranges)

    return make_success(
        {
            "normalized_value": collapsed,
            "two_part": False,
            "value_from_sku_declaration": True,
            "within_plausibility_range": plausible,
        }
    )


def normalise_dimensions_for_bags(raw_value: str) -> dict[str, Any]:
    """Normalitza les dimensions d'una bossa (§3.5.8.13).

    Format literal de la font: `L[llarg] X H[alt] X W[ample] CM — [capacitat] Litres`.
    Cap conversió d'unitats ni capacitat inferida.

    Args:
        raw_value: Dimensions tal com apareixen a la font.

    Returns:
        Un resultat canònic SUCCESS amb el valor literal. REJECT si no compleix
        el format esperat.
    """
    if not raw_value or not raw_value.strip():
        return make_reject("Les dimensions no poden ser buides")

    collapsed = " ".join(raw_value.strip().split())
    if "CM" not in collapsed.upper():
        return make_reject(
            "Les dimensions han de portar la unitat CM en el format de la font",
            meta={"declared": collapsed},
        )

    return make_success(
        {"normalized_value": collapsed, "units_converted": False, "capacity_inferred": False}
    )


def normalise_product_category(
    raw_category: str,
    raw_subcategory: Optional[str] = None,
) -> dict[str, Any]:
    """Normalitza categoria i subcategoria (§3.5.8.8).

    Args:
        raw_category: Categoria pare declarada.
        raw_subcategory: Família comercial, si n'hi ha.

    Returns:
        Un resultat canònic SUCCESS amb els valors normalitzats. HOLD si la
        categoria no és a la taxonomia oficial.
    """
    if not raw_category or not raw_category.strip():
        return make_reject("La categoria no pot ser buida")

    candidate = " ".join(raw_category.strip().split())
    match = next((name for name in CATEGORIES if name.lower() == candidate.lower()), None)
    if match is None:
        return make_hold(
            "Categoria fora de la taxonomia oficial de dos nivells",
            meta={"declared": candidate, "taxonomy": CATEGORIES},
        )

    subcategory = " ".join(raw_subcategory.strip().split()) if raw_subcategory else NOT_APPLICABLE
    justification = None
    if subcategory == NOT_APPLICABLE:
        justification = "categoria pare sense família comercial pròpia a la font"

    return make_success(
        {
            "category": match,
            "subcategory": subcategory,
            "not_applicable_justification": justification,
        }
    )


def normalise_record(record: dict[str, Any]) -> dict[str, Any]:
    """Normalitza un registre de producte complet.

    Args:
        record: Diccionari amb els camps crus del registre.

    Returns:
        Un resultat canònic SUCCESS amb el registre normalitzat i cada camp amb
        el seu `raw_value` i `normalized_value` (§3.6.5). HOLD si algun camp
        obligatori no es pot resoldre. FAILURE davant d'una excepció.
    """
    try:
        if not isinstance(record, dict) or not record:
            return make_reject("El registre no és un diccionari amb contingut")

        fields: dict[str, Any] = {}

        category_result = normalise_product_category(
            record.get("category", ""), record.get("subcategory")
        )
        if category_result["status"] != "SUCCESS":
            return make_hold(
                "No s'ha pogut normalitzar la categoria",
                meta={"detail": category_result.get("reason")},
            )
        fields["category"] = category_result["data"]

        code_result = normalise_model_code(record.get("model_code", ""))
        if code_result["status"] != "SUCCESS":
            return make_hold("No s'ha pogut normalitzar el codi de model")
        fields["model_code"] = code_result["data"]

        colour_result = normalise_colour(record.get("colour", ""))
        if colour_result["status"] != "SUCCESS":
            return make_hold("No s'ha pogut normalitzar el color")
        fields["colour"] = colour_result["data"]

        name_result = build_canonical_name(
            record.get("product_name", ""),
            code_result["data"]["normalized_value"],
            colour_result["data"]["normalized_value"],
            category_result["data"]["category"],
        )
        if name_result["status"] != "SUCCESS":
            return make_hold(
                "No s'ha pogut construir el nom canònic",
                meta={"detail": name_result.get("reason")},
            )
        fields["canonical_name"] = name_result["data"]

        sizing_result = resolve_sizing_system(category_result["data"]["category"])
        if sizing_result["status"] == "SUCCESS":
            fields["sizing"] = sizing_result["data"]

        if record.get("material"):
            material_result = normalise_material(
                record["material"],
                category_result["data"]["category"],
                bool(record.get("is_shoes")),
            )
            fields["material"] = (
                material_result["data"]
                if material_result["status"] == "SUCCESS"
                else {
                    "raw_value": record["material"],
                    "unresolved_reason": material_result.get("reason"),
                }
            )

        if record.get("dimensions"):
            dimensions_result = normalise_dimensions_for_bags(record["dimensions"])
            fields["dimensions"] = (
                dimensions_result["data"]
                if dimensions_result["status"] == "SUCCESS"
                else {
                    "raw_value": record["dimensions"],
                    "unresolved_reason": dimensions_result.get("reason"),
                }
            )

        logger.info("record_normalised", fields=len(fields))
        return make_success(fields, meta={"fields_normalised": sorted(fields.keys())})
    except Exception as exception:  # noqa: BLE001 - contracte FAILURE és explícit
        logger.critical("normalise_unexpected", error=str(exception))
        return make_failure(
            f"Excepció inesperada: {exception}",
            meta={"exception_type": type(exception).__name__},
        )
