"""
Logique de la machine Enigma — pur Python, aucune dépendance externe.

Supporte les rotors Wehrmacht I-V, Kriegsmarine VI-VIII,
les réflecteurs UKW-B et UKW-C, et le plugboard (Steckerbrett).
"""

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# ---------------------------------------------------------------------------
# Données historiques des rotors
# ---------------------------------------------------------------------------

ROTOR_WIRINGS: dict[str, str] = {
    "I":    "EKMFLGDQVZNTOWYHXUSPAIBRCJ",
    "II":   "AJDKSIRUXBLHWTMCQGZNPYFVOE",
    "III":  "BDFHJLCPRTXVZNYEIWGAKMUSQO",
    "IV":   "ESOVPZJAYQUIRHXLNFTGKDCMWB",
    "V":    "VZBRGITYUPSDNHLXAWMJQOFECK",
    "VI":   "JPGVOUMFYQBENHZRDKASXLICTW",
    "VII":  "NZJHGRCXMYSWBOUFAIVLPEKQDT",
    "VIII": "FKQHTLXOCBJSPDZRAMEWNIUYGV",
}

ROTOR_NOTCHES: dict[str, str] = {
    "I":    "Q",
    "II":   "E",
    "III":  "V",
    "IV":   "J",
    "V":    "Z",
    "VI":   "ZM",
    "VII":  "ZM",
    "VIII": "ZM",
}

REFLECTOR_WIRINGS: dict[str, str] = {
    "UKW-B": "YRUHQSLDPXNGOKMIEBFZCWVJAT",
    "UKW-C": "FVPJIAOYEDRZXWGCTKUQSBNMHL",
}


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

class Rotor:
    def __init__(self, name: str, ring_setting: int = 0, position: int = 0):
        self.name = name
        self.ring_setting = ring_setting
        self.position = position

        wiring_str = ROTOR_WIRINGS[name]
        self.wiring_forward = [ord(c) - ord("A") for c in wiring_str]
        self.wiring_backward = [0] * 26
        for i, w in enumerate(self.wiring_forward):
            self.wiring_backward[w] = i

        self.notches = ROTOR_NOTCHES[name]

    def forward(self, signal: int) -> int:
        shifted = (signal + self.position - self.ring_setting) % 26
        out = self.wiring_forward[shifted]
        return (out - self.position + self.ring_setting) % 26

    def backward(self, signal: int) -> int:
        shifted = (signal + self.position - self.ring_setting) % 26
        out = self.wiring_backward[shifted]
        return (out - self.position + self.ring_setting) % 26

    def step(self) -> None:
        self.position = (self.position + 1) % 26

    def at_notch(self) -> bool:
        return ALPHABET[self.position] in self.notches


class Plugboard:
    def __init__(self, pairs: list[tuple[str, str]] | None = None):
        self.mapping = list(range(26))
        if pairs:
            for a, b in pairs:
                ia = ord(a.upper()) - ord("A")
                ib = ord(b.upper()) - ord("A")
                self.mapping[ia] = ib
                self.mapping[ib] = ia

    def swap(self, signal: int) -> int:
        return self.mapping[signal]


class Reflector:
    def __init__(self, name: str):
        self.name = name
        wiring_str = REFLECTOR_WIRINGS[name]
        self.wiring = [ord(c) - ord("A") for c in wiring_str]

    def reflect(self, signal: int) -> int:
        return self.wiring[signal]


class EnigmaMachine:
    def __init__(
        self,
        rotors: list[Rotor],
        reflector: Reflector,
        plugboard: Plugboard | None = None,
    ):
        self.rotors = rotors  # [left, middle, right]
        self.reflector = reflector
        self.plugboard = plugboard or Plugboard()

    def step_rotors(self) -> None:
        """Mécanisme de pas incluant le double-stepping du rotor central."""
        # Double-step : si le rotor central est sur son notch, il avance
        # ET déclenche le rotor gauche
        if self.rotors[1].at_notch():
            self.rotors[1].step()
            self.rotors[0].step()
        elif self.rotors[2].at_notch():
            self.rotors[1].step()
        # Le rotor droit avance toujours
        self.rotors[2].step()

    def encrypt_letter(self, letter: str) -> tuple[str, list[dict]]:
        """
        Chiffre une seule lettre et retourne (lettre_chiffrée, signal_path).
        signal_path décrit chaque étape de transformation pour la visualisation.
        """
        letter = letter.upper()
        if letter not in ALPHABET:
            return letter, []

        self.step_rotors()

        signal = ord(letter) - ord("A")
        path: list[dict] = []

        # Plugboard entrée
        prev = signal
        signal = self.plugboard.swap(signal)
        path.append({"stage": "plugboard_in", "from": ALPHABET[prev], "to": ALPHABET[signal]})

        # Rotors aller (droite → milieu → gauche)
        stage_names_fwd = ["rotor_right_fwd", "rotor_middle_fwd", "rotor_left_fwd"]
        for i, name in zip([2, 1, 0], stage_names_fwd):
            prev = signal
            signal = self.rotors[i].forward(signal)
            path.append({"stage": name, "from": ALPHABET[prev], "to": ALPHABET[signal]})

        # Réflecteur
        prev = signal
        signal = self.reflector.reflect(signal)
        path.append({"stage": "reflector", "from": ALPHABET[prev], "to": ALPHABET[signal]})

        # Rotors retour (gauche → milieu → droite)
        stage_names_bwd = ["rotor_left_bwd", "rotor_middle_bwd", "rotor_right_bwd"]
        for i, name in zip([0, 1, 2], stage_names_bwd):
            prev = signal
            signal = self.rotors[i].backward(signal)
            path.append({"stage": name, "from": ALPHABET[prev], "to": ALPHABET[signal]})

        # Plugboard sortie
        prev = signal
        signal = self.plugboard.swap(signal)
        path.append({"stage": "plugboard_out", "from": ALPHABET[prev], "to": ALPHABET[signal]})

        return ALPHABET[signal], path

    def encrypt_text(self, text: str) -> str:
        """Chiffre un texte complet, ignorant les caractères non-alphabétiques."""
        result = []
        for char in text.upper():
            if char in ALPHABET:
                encrypted, _ = self.encrypt_letter(char)
                result.append(encrypted)
            else:
                result.append(char)
        return "".join(result)

    def get_rotor_positions(self) -> list[str]:
        """Retourne les positions courantes des rotors [gauche, milieu, droite]."""
        return [ALPHABET[r.position] for r in self.rotors]


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_machine(
    rotor_names: list[str],
    reflector_name: str = "UKW-B",
    ring_settings: list[int] | None = None,
    positions: list[int] | None = None,
    plugboard_pairs: list[list[str]] | None = None,
) -> EnigmaMachine:
    """Crée une machine Enigma à partir de paramètres de configuration."""
    ring_settings = ring_settings or [0, 0, 0]
    positions = positions or [0, 0, 0]

    rotors = [
        Rotor(rotor_names[i], ring_settings[i], positions[i])
        for i in range(3)
    ]
    reflector = Reflector(reflector_name)

    pairs = None
    if plugboard_pairs:
        pairs = [(p[0], p[1]) for p in plugboard_pairs]
    plugboard = Plugboard(pairs)

    return EnigmaMachine(rotors, reflector, plugboard)
