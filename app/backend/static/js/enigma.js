/**
 * Enigma Machine — Alpine.js component
 */
function enigmaApp() {
    return {
        // Configuration
        rotorChoices: ['III', 'II', 'I'],
        reflector: 'UKW-B',
        rotorPositions: [0, 0, 0],
        ringSettings: [0, 0, 0],
        plugboardPairs: [],

        // Available options
        availableRotors: [],
        availableReflectors: [],

        // State
        inputText: '',
        outputText: '',
        litLetter: null,
        pressedKey: null,
        signalPath: [],
        configOpen: false,
        processing: false,

        // Plugboard UI state
        plugboardFirstSocket: null,

        // Lamp timeout
        _lampTimeout: null,

        async init() {
            // Load available rotors/reflectors
            try {
                const resp = await fetch('/api/rotors');
                const data = await resp.json();
                this.availableRotors = data.rotors;
                this.availableReflectors = data.reflectors;
            } catch (e) {
                this.availableRotors = ['I', 'II', 'III', 'IV', 'V'];
                this.availableReflectors = ['UKW-B', 'UKW-C'];
            }

            // Physical keyboard listener
            document.addEventListener('keydown', (e) => {
                if (this.configOpen) return;
                if (e.ctrlKey || e.metaKey || e.altKey) return;

                const letter = e.key.toUpperCase();
                if (/^[A-Z]$/.test(letter)) {
                    e.preventDefault();
                    this.pressKey(letter);
                }
                // Backspace: remove last character
                if (e.key === 'Backspace' && this.inputText.length > 0) {
                    e.preventDefault();
                    this.inputText = this.inputText.slice(0, -1);
                    this.outputText = this.outputText.slice(0, -1);
                }
            });

            document.addEventListener('keyup', () => {
                this.pressedKey = null;
            });
        },

        async pressKey(letter) {
            if (this.processing) return;
            this.processing = true;
            this.pressedKey = letter;

            try {
                const resp = await fetch('/api/encrypt-letter', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        letter: letter,
                        config: this.buildConfig()
                    })
                });

                const data = await resp.json();

                // Update state
                this.inputText += letter;
                this.outputText += data.output;
                this.signalPath = data.signal_path;

                // Update rotor positions from server response
                this.rotorPositions = data.rotor_positions.map(
                    c => c.charCodeAt(0) - 65
                );

                // Light up lamp
                this.litLetter = data.output;
                if (this._lampTimeout) clearTimeout(this._lampTimeout);
                this._lampTimeout = setTimeout(() => {
                    this.litLetter = null;
                }, 600);

            } catch (e) {
                console.error('Erreur de chiffrement:', e);
            } finally {
                this.processing = false;
            }
        },

        buildConfig() {
            return {
                rotors: [...this.rotorChoices],
                reflector: this.reflector,
                positions: [...this.rotorPositions],
                ring_settings: [...this.ringSettings],
                plugboard: this.plugboardPairs.map(p => [...p]),
            };
        },

        resetMachine() {
            this.rotorPositions = [0, 0, 0];
            this.inputText = '';
            this.outputText = '';
            this.signalPath = [];
            this.litLetter = null;
        },

        applyConfig() {
            // Reset text when config changes (different machine = different output)
            this.inputText = '';
            this.outputText = '';
            this.signalPath = [];
            this.litLetter = null;
        },

        // --- Plugboard ---
        togglePlugboardSocket(letter) {
            // If already connected, ignore (must remove pair first)
            const connected = this.plugboardPairs.flat();
            if (connected.includes(letter)) return;

            if (this.plugboardFirstSocket === null) {
                this.plugboardFirstSocket = letter;
            } else if (this.plugboardFirstSocket === letter) {
                this.plugboardFirstSocket = null;
            } else {
                if (this.plugboardPairs.length < 13) {
                    this.plugboardPairs.push([this.plugboardFirstSocket, letter]);
                }
                this.plugboardFirstSocket = null;
            }
        },

        removePlugboardPair(idx) {
            this.plugboardPairs.splice(idx, 1);
        },

        getPlugboardSocketClass(letter) {
            const connected = this.plugboardPairs.flat();
            if (connected.includes(letter)) {
                return 'bg-primary text-white border-2 border-primary-light';
            }
            if (this.plugboardFirstSocket === letter) {
                return 'bg-amber-400 text-amber-900 border-2 border-amber-500 scale-110';
            }
            return 'bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-500 hover:bg-gray-300 dark:hover:bg-gray-500';
        },

        // --- Signal path labels ---
        getStageLabel(stage) {
            const labels = {
                'plugboard_in': 'Plugboard',
                'rotor_right_fwd': 'Rotor D \u2192',
                'rotor_middle_fwd': 'Rotor M \u2192',
                'rotor_left_fwd': 'Rotor G \u2192',
                'reflector': 'Reflecteur',
                'rotor_left_bwd': '\u2190 Rotor G',
                'rotor_middle_bwd': '\u2190 Rotor M',
                'rotor_right_bwd': '\u2190 Rotor D',
                'plugboard_out': 'Plugboard',
            };
            return labels[stage] || stage;
        },
    };
}
