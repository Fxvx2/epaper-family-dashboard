"""Scientist of the day + theorem/concept via Gemini (cached per day)."""

import os
import json
import hashlib
from datetime import date

from data.gemini import call_gemini

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
CACHE_FILE = os.path.join(CACHE_DIR, 'scientist_of_day.json')

# Rotate through famous scientists with their signature theorems (110+).
# Formulas use Unicode math symbols -- rendered with DejaVuSans math font.
SCIENTISTS = [
    ('Albert Einstein', 'Relativitaetstheorie', 'E = m·c²'),
    ('Isaac Newton', 'Gravitationsgesetz', 'F = G·m₁·m₂/r²'),
    ('Marie Curie', 'Radioaktiver Zerfall', 'N(t) = N₀·e^(-λt)'),
    ('Pythagoras', 'Pythagoras-Satz', 'a² + b² = c²'),
    ('Euklid', 'Geometrie', 'α + β + γ = 180°'),
    ('Archimedes', 'Auftriebsgesetz', 'F = ρ·V·g'),
    ('Galileo Galilei', 'Fallgesetz', 's = ½·g·t²'),
    ('Johannes Kepler', 'Kepler 3. Gesetz', 'T² = a³'),
    ('Max Planck', 'Quantentheorie', 'E = h·f'),
    ('Charles Darwin', 'Evolutionstheorie', 'Natuerliche Auslese'),
    ('Nikola Tesla', 'Wechselstrom', 'P = U·I'),
    ('Ada Lovelace', 'Algorithmus', 'Erstes Computerprogramm'),
    ('Carl Friedrich Gauss', 'Gausssche Summe', '∑₁ⁿ k = n·(n+1)/2'),
    ('Leonhard Euler', 'Eulersche Identitaet', 'e^(iπ) + 1 = 0'),
    ('Niels Bohr', 'Atommodell', 'Eₙ = -13.6/n² eV'),
    ('Erwin Schrodinger', 'Quantenmechanik', 'iℏ·∂ψ/∂t = Ĥψ'),
    ('Werner Heisenberg', 'Unschaerferelation', 'Δx·Δp ≥ ℏ/2'),
    ('Stephen Hawking', 'Hawking-Strahlung', 'T = ℏ·c³/(8π·G·M·k)'),
    ('Rosalind Franklin', 'DNA-Doppelhelix', 'Photo 51 Roentgenbild'),
    ('Emmy Noether', 'Noether-Theorem', 'Symmetrie ⇔ Erhaltungssatz'),
    ('Alan Turing', 'Turing-Maschine', 'Halteproblem unentscheidbar'),
    ('Louis Pasteur', 'Keimtheorie', 'Pasteurisierung toetet Keime'),
    ('Gregor Mendel', 'Vererbungsgesetze', 'Dominant : rezessiv = 3 : 1'),
    ('Alexander Fleming', 'Penicillin', 'Antibiotikum (1928)'),
    ('James Clerk Maxwell', 'Elektromagnetismus', '∇·E = ρ/ε₀   ∇×B = μ₀J'),
    ('Michael Faraday', 'Induktion', 'U = -dΦ/dt'),
    ('Richard Feynman', 'Quantenelektrodynamik', 'Pfadintegral-Formulierung'),
    ('Lise Meitner', 'Kernspaltung', '²³⁵U + n → Ba + Kr + 3n'),
    ('Fibonacci', 'Fibonacci-Folge', 'Fₙ = Fₙ₋₁ + Fₙ₋₂'),
    ('Grigori Perelman', 'Poincare-Vermutung', 'Geometrisierung 3-Mannigfaltigkeiten'),
    ('Hypatia von Alexandria', 'Mathematik/Astronomie', 'Diophantos Kommentare'),
    ('Aristoteles', 'Logik', 'Syllogismus (Schlussfolgerung)'),
    ('Dmitri Mendelejew', 'Periodensystem', 'Ordnung nach Atommasse'),
    ('Antoine Lavoisier', 'Erhaltung der Masse', 'm(Reaktanten) = m(Produkte)'),
    ('Charles Babbage', 'Analytical Engine', 'Erste mechanische Rechenmaschine'),
    ('Claude Shannon', 'Informationstheorie', 'H = -∑ pᵢ·log₂(pᵢ)'),
    ('John von Neumann', 'Von-Neumann-Architektur', 'Programm + Daten im gleichen Speicher'),
    ('Grace Hopper', 'COBOL/Compiler', 'Erster Compiler (A-0)'),
    ('Dennis Ritchie', 'C-Sprache + UNIX', 'printf("hello, world")'),
    ('Tim Berners-Lee', 'World Wide Web', 'HTTP + HTML + URL'),
    ('Rachel Carson', 'Silent Spring 1962', 'DDT toetet Voegel'),
    ('Jane Goodall', 'Schimpansen-Werkzeuge', '60 Jahre Gombe-Feldforschung'),
    ('Katherine Johnson', 'Raumfahrt-Mathematik', 'Apollo 11 Flugbahnen'),
    ('Dorothy Hodgkin', 'Roentgenkristallographie', 'Struktur von Insulin'),
    ('Barbara McClintock', 'Springende Gene', 'Transposons im Mais'),
    ('Vera Rubin', 'Dunkle Materie', 'Galaxien-Rotationskurven'),
    ('Chien-Shiung Wu', 'Paritaet-Verletzung', 'Beta-Zerfall Experiment'),
    ('Caroline Herschel', 'Kometen-Entdeckerin', '8 Kometen entdeckt'),
    ('Maria Mitchell', 'Astronomin', 'Komet 1847 VI'),
    ('Shakuntala Devi', 'Kopfrechnen-Genie', '13-stellige Multiplikation'),
    ('Srinivasa Ramanujan', 'Zahlentheorie', 'Ramanujan-Summe'),
    ('Henri Poincare', 'Chaostheorie', 'Dreikoerperproblem'),
    ('Karl Weierstrass', 'Analysis', 'Weierstrass-Funktion (stetig, nirgends differenzierbar)'),
    ('Bernhard Riemann', 'Riemann-Hypothese', 'Re(s) = ½ fuer Nullstellen'),
    ('Georg Cantor', 'Mengenlehre', 'Unendlichkeiten: ℵ₀ vs 2^ℵ₀'),
    ('David Hilbert', '23 Probleme (1900)', 'Hilbertsche Probleme'),
    ('Kurt Goedel', 'Unvollstaendigkeitssatz', 'Kein System ist vollstaendig + konsistent'),
    ('Paul Dirac', 'Dirac-Gleichung', '(iγ^μ·∂_μ - m)ψ = 0'),
    ('Wolfgang Pauli', 'Pauli-Prinzip', 'Keine 2 Elektronen mit gleichen QZ'),
    ('Enrico Fermi', 'Kernreaktor (1942)', 'Chicago Pile-1'),
    ('Robert Oppenheimer', 'Manhattan-Projekt', 'Erste Atombombe 1945'),
    ('Kip Thorne', 'Gravitationswellen', 'LIGO-Entdeckung 2015'),
    ('Peter Higgs', 'Higgs-Boson', 'Massenmechanismus (2012 gefunden)'),
    ('Murray Gell-Mann', 'Quarks', '8-Way = Hadronen-Klassifikation'),
    ('Francis Crick', 'DNA-Struktur', 'Zentrales Dogma: DNA → RNA → Protein'),
    ('James Watson', 'DNA-Doppelhelix', 'Mit Crick 1953'),
    ('Linus Pauling', 'Chemische Bindung', 'Elektronegativitaet-Skala'),
    ('Jonas Salk', 'Polio-Impfstoff', '1955 inaktivierter Virusimpfstoff'),
    ('Edward Jenner', 'Pocken-Impfstoff', 'Kuhpocken → Immunitaet'),
    ('Robert Koch', 'Bakteriologie', 'Kochs Postulate (4 Regeln)'),
    ('Sigmund Freud', 'Psychoanalyse', 'Es, Ich, Ueber-Ich'),
    ('Iwan Pawlow', 'Klassische Konditionierung', 'Hundespeichel-Experiment'),
    ('Nikolaus Kopernikus', 'Heliozentrik', 'Erde kreist um Sonne'),
    ('Tycho Brahe', 'Astronomische Messungen', 'Praezisionsdaten ohne Teleskop'),
    ('Edwin Hubble', 'Hubble-Konstante', 'v = H₀·d (Rotverschiebung)'),
    ('Carl Sagan', 'Kosmologie', 'Wir sind Sternenstaub'),
    ('Frank Drake', 'Drake-Gleichung', 'N = R*·fₚ·nₑ·fₗ·fᵢ·f꜀·L'),
    ('Jocelyn Bell Burnell', 'Pulsare', 'CP 1919 (1967)'),
    ('Henrietta Leavitt', 'Perioden-Leuchtkraft', 'Cepheiden: L = f(Periode)'),
    ('Cecilia Payne', 'Sterne bestehen aus H', 'Dissertation 1925'),
    ('Annie Jump Cannon', 'Stern-Klassifikation', 'OBAFGKM System'),
    ('Mileva Maric', 'Mathematische Physik', 'Mitarbeit Relativitaet'),
    ('Marie-Sophie Germain', 'Zahlentheorie', 'Germains Theorem'),
    ('Emilie du Chatelet', 'Kinetische Energie', 'E ∝ m·v² (nicht m·v)'),
    ('Archimedes von Syrakus', 'π-Annaeherung', '3.1408 < π < 3.1429'),
    ('Apollonius von Perge', 'Kegelschnitte', 'Ellipse, Parabel, Hyperbel'),
    ('Ptolemaeus', 'Almagest', 'Geozentrisches Weltbild (ueber 1400 Jahre gueltig)'),
    ('Al-Khwarizmi', 'Algebra', 'Wort "Algorithmus" stammt von ihm'),
    ('Ibn al-Haytham', 'Optik', 'Licht faellt von Objekt ins Auge (nicht umgekehrt)'),
    ('Avicenna', 'Medizin', 'Kanon der Medizin (5 Baende)'),
    ('Al-Biruni', 'Erdradius-Messung', 'Methode mit Hoehenmessung'),
    ('Leonardo da Vinci', 'Renaissance-Genie', 'Anatomie, Mechanik, Kunst'),
    ('Galileo Galilei', 'Teleskop-Beobachtung', 'Jupiter-Monde 1610'),
    ('Antony van Leeuwenhoek', 'Mikroskop', 'Entdeckte Bakterien (1676)'),
    ('Robert Hooke', 'Hookesches Gesetz', 'F = -k·x'),
    ('Blaise Pascal', 'Pascal-Dreieck', 'Binomialkoeffizienten'),
    ('Pierre de Fermat', 'Fermats letzter Satz', 'aⁿ + bⁿ ≠ cⁿ fuer n > 2'),
    ('Alessandro Volta', 'Voltaische Saeule', 'Erste Batterie (1800)'),
    ('Andre-Marie Ampere', 'Amperesches Gesetz', '∮ B·dl = μ₀·I'),
    ('Georg Simon Ohm', 'Ohmsches Gesetz', 'U = R·I'),
    ('Heinrich Hertz', 'Elektromagnetische Wellen', 'Nachweis von Maxwells Theorie'),
    ('Guglielmo Marconi', 'Radio-Telegrafie', 'Transatlantische Uebertragung 1901'),
    ('Wilhelm Roentgen', 'Roentgenstrahlen', '1. Nobelpreis Physik 1901'),
    ('Henri Becquerel', 'Radioaktivitaet', 'Uran-Salze (1896)'),
    ('Ernest Rutherford', 'Atomkern', 'α-Streuversuch 1909'),
    ('Satyendra Nath Bose', 'Bose-Einstein-Statistik', 'Bose-Einstein-Kondensat'),
    ('Subrahmanyan Chandrasekhar', 'Chandrasekhar-Grenze', 'M_max = 1.4 M☉ (Weisser Zwerg)'),
    ('Fred Hoyle', 'Nukleosynthese', 'Sterne erzeugen schwere Elemente'),
    ('Arno Penzias', 'Kosmische Hintergrundstrahlung', '2.7 K Mikrowellen (1964)'),
    ('Roger Penrose', 'Singularitaetentheoreme', 'Schwarze Loecher in GR'),
    ('Benoit Mandelbrot', 'Fraktale', 'zₙ₊₁ = zₙ² + c'),
    ('John Nash', 'Nash-Gleichgewicht', 'Spieltheorie'),
    ('Paul Erdos', 'Kombinatorik', 'Erdos-Zahl'),
]


def _daily_index(seed='scientist'):
    """Sequential daily rotation: every scientist shown once before any repeat."""
    n = len(SCIENTISTS)
    offset = int(hashlib.md5(seed.encode()).hexdigest(), 16) % n
    return (date.today().toordinal() + offset) % n


def get_scientist_of_day():
    """Return today's scientist + theorem with Gemini-enriched explanation + kid analogy."""
    idx = _daily_index()
    name, topic, formula = SCIENTISTS[idx]

    cached = _load_cache()
    today = date.today().isoformat()
    if (cached.get('date') == today and cached.get('name') == name
            and cached.get('kid_analogy_fr')):
        return cached

    try:
        prompt = (
            "Fuer diese Wissenschaftler/in und ihr/sein Theorem:\n"
            "Name: " + name + "\n"
            "Thema: " + topic + "\n"
            "Formel: " + formula + "\n\n"
            "Antworte NUR in JSON (ASCII, ae/oe/ue/ss, pas d'accents) mit:\n"
            "- 'description' (2 Saetze auf Deutsch: was ist das Thema)\n"
            "- 'importance' (1 Satz auf Deutsch: warum wichtig)\n"
            "- 'kid_analogy' (2 Saetze auf Deutsch, einfache Analogie aus dem Alltag fuer 8-11jaehrige)\n"
            "- 'kid_analogy_fr' (2 phrases en francais, analogie simple du quotidien pour enfants 8-11 ans, sans accents)"
        )
        result = call_gemini(prompt, max_tokens=2000)
        if not result:
            return _fallback(name, topic, formula)

        out = {
            'date': today,
            'name': name,
            'topic': topic,
            'formula': formula,
            'description': result.get('description', ''),
            'importance': result.get('importance', ''),
            'kid_analogy': result.get('kid_analogy', ''),
            'kid_analogy_fr': result.get('kid_analogy_fr', ''),
        }
        # Only cache if we got real data
        if out['description']:
            _save_cache(out)
        return out
    except Exception as e:
        print("Scientist enrich error:", e)
        return _fallback(name, topic, formula)


def _fallback(name, topic, formula):
    return {
        'date': date.today().isoformat(),
        'name': name,
        'topic': topic,
        'formula': formula,
        'description': '',
        'importance': '',
        'kid_analogy': '',
        'kid_analogy_fr': '',
    }


def _load_cache():
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_cache(data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass
