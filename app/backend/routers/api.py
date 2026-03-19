from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from enigma_core import (
    REFLECTOR_WIRINGS,
    ROTOR_WIRINGS,
    create_machine,
)
from database import get_configurations, save_configuration, delete_configuration

router = APIRouter(prefix="/api")


def _parse_config(body: dict) -> dict:
    """Extrait et valide la configuration Enigma depuis le body JSON."""
    config = body.get("config", body)
    return {
        "rotors": config.get("rotors", ["I", "II", "III"]),
        "reflector": config.get("reflector", "UKW-B"),
        "positions": config.get("positions", [0, 0, 0]),
        "ring_settings": config.get("ring_settings", [0, 0, 0]),
        "plugboard": config.get("plugboard", []),
    }


@router.post("/encrypt-letter")
async def encrypt_letter(request: Request):
    body = await request.json()
    letter = body.get("letter", "")
    cfg = _parse_config(body)

    machine = create_machine(
        rotor_names=cfg["rotors"],
        reflector_name=cfg["reflector"],
        ring_settings=cfg["ring_settings"],
        positions=cfg["positions"],
        plugboard_pairs=cfg["plugboard"],
    )

    output, signal_path = machine.encrypt_letter(letter)

    return {
        "output": output,
        "signal_path": signal_path,
        "rotor_positions": machine.get_rotor_positions(),
    }


@router.post("/encrypt-text")
async def encrypt_text(request: Request):
    body = await request.json()
    text = body.get("text", "")
    cfg = _parse_config(body)

    machine = create_machine(
        rotor_names=cfg["rotors"],
        reflector_name=cfg["reflector"],
        ring_settings=cfg["ring_settings"],
        positions=cfg["positions"],
        plugboard_pairs=cfg["plugboard"],
    )

    output = machine.encrypt_text(text)

    return {
        "output": output,
        "rotor_positions": machine.get_rotor_positions(),
    }


@router.get("/rotors")
async def list_rotors():
    return {
        "rotors": list(ROTOR_WIRINGS.keys()),
        "reflectors": list(REFLECTOR_WIRINGS.keys()),
    }


# ---------------------------------------------------------------------------
# Configurations sauvegardées
# ---------------------------------------------------------------------------

@router.get("/configurations")
async def list_configurations():
    return get_configurations()


@router.post("/configurations")
async def create_configuration(request: Request):
    body = await request.json()
    config_id = save_configuration(body)
    return {"id": config_id}


@router.delete("/configurations/{config_id}")
async def remove_configuration(config_id: int):
    deleted = delete_configuration(config_id)
    if not deleted:
        return JSONResponse({"error": "Configuration introuvable"}, status_code=404)
    return {"ok": True}
