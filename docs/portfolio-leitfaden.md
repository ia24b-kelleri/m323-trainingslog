# Portfolio-Leitfaden M323 – wo finde ich was im Trainingslog?

Pro Kompetenzfeld: welches Feature, wo der Code liegt, was als Pflicht-Artefakt
reinkommt, welche Tests du als Testfälle zitieren kannst und welche Fragen dein
Text beantworten sollte. Die Texte selbst schreibst du (Erfahrungen, Entscheide,
Schwierigkeiten sind deine, und genau dafür gibt's die Punkte).

Zeichen: B ≥ 600, I ≥ 1000, A ≥ 1400 (ohne Leerzeichen, ohne Code).
Niveau A = immer **zwei Varianten vergleichen und begründet entscheiden**.

---

## A1 – Paradigmen

### A1B – Prozedur und pure function nebeneinander
- **Prozedur:** `app/db.py → speichere_training` (schreibt in die DB, Rückgabewert hängt vom DB-Zustand ab)
- **Pure function:** `app/services/volumen.py → training_volumen`
- **Testfälle:** `tests/test_filter.py::test_map_und_reduce` (gleicher Input → immer gleicher Output),
  `tests/test_db.py::test_roundtrip_mit_zwei_saetzen` (Prozedur nur mit temporärer DB testbar)
- **Text:** Woran erkennst du eine pure function? Warum lässt sich `speichere_training` nicht pure machen? Warum ist die Trennung Routes / services / db sinnvoll?

### A1I – Mutation und immutable Variante
- **Mutation:** `lade_trainings` im Stand *vorher* (`setdefault(...).append(...)`, `trainings.sort(...)`)
- **Immutable:** `app/services/statistik.py → nur_uebung` (`dataclasses.replace` erzeugt ein neues Training)
- Zusatzbeleg: Versuch `training.saetze = ()` wirft `FrozenInstanceError` (selbst ausprobieren, Fehlermeldung als Screenshot)
- **Testfälle:** `test_statistik.py::test_original_bleibt_unveraendert`, `test_filter.py::test_eingabe_bleibt_unveraendert`
- **Text:** Welche Fehler verhindert Immutability konkret in deiner App? Was kostet sie (Kopien)?

### A1A – Dieselbe Aufgabe in OO, prozedural, funktional
- **Code:** `app/services/vergleich.py` (alle drei Varianten), funktionale Variante wird in `/bestenliste` verwendet
- **Testfall:** `tests/test_vergleich.py::test_alle_drei_paradigmen_liefern_dasselbe` + Edge Case leer
- **Bewerten:** Lesbarkeit, Testbarkeit, Zustand, Performance (die funktionale Variante kopiert pro Satz das Dict!). Begründe, warum du in der App die funktionale nimmst bzw. wann du die prozedurale wählen würdest.

---

## B1 – Deklarative Anforderungen und Design

### B1B – Elemente des Functional Design mit Fundort
- **Immutable data types:** `app/models.py` (frozen dataclasses), `tuple` als Rückgabetyp überall in `services/`
- **Constructors:** `normalisiere_zeile` (baut `Satz` aus Rohtext), `baue_woche` (baut `WochenStatistik`), `Training(...)` in `erfassen.parse_formular`
- **Composable operators:** `filter.py → nach_uebung`, `ab_datum`, `bis_datum`, `alle(...)` (kombiniert Filter), `suche` als Komposition
- **Testfall:** `test_filter.py::test_alle_kombiniert_filter`

### B1I – Design-Blatt (deklarative Anforderungen, Datenfluss, Operatoren)
- **Artefakt:** `docs/design-statistik.md`, Commit **vor** dem Code (Commit-Hash + Datum nennen!)
- **Umsetzung:** `app/services/statistik.py`
- **Text:** Vergleiche Design und Umsetzung. Wo wurde abgewichen? (z. B. "Filter" wurde zu map → filter, weil nur die Sätze der Übung zählen sollen.)
- **Testfälle:** `test_statistik.py::test_wochen_neueste_zuerst`, `test_jahreswechsel_iso_woche`

### B1A – Imperative Route deklarativ umgesetzt
- **Vorher:** `/export` in `app/routes.py` (Schleifen, append, String-Verkettung)
- **Nachher:** `app/services/csv_export.py → exportiere_csv`, Route nur noch 3 Zeilen (Refactoring Schritt 4)
- **Testfälle:** `test_routes.py::test_export_inhalt_exakt` (vorher und nachher grün), `test_csv_export.py::test_komma_im_uebungsnamen_wird_korrekt_gequotet` (Bug der alten Variante!)
- **Vor-/Nachteile:** Testbarkeit ohne Flask, csv-Modul kennt Quoting / aber Abhängigkeit zu `io.StringIO`, für Anfänger evtl. weniger direkt lesbar.

---

## C1 – Algorithmen (CSV-Import)

### C1B – Algorithmus mit Beispieldurchlauf
- **Code:** `app/services/csv_import.py → importiere_csv`
- **Beispieldurchlauf:** `beispieldaten/import_test.csv` → 2 Trainings, 4 Sätze, 5 Fehler (Zeilen 6–10). Zeig, was mit Zeile 3 (`82,5`) passiert.

### C1I – In Teilfunktionen zerlegt, mit Signaturen
- `parse_zeile(zeile: str, trennzeichen: str) -> tuple[str, ...]`
- `validiere_zeile(felder) -> str | None`
- `normalisiere_zeile(felder) -> tuple[date, Satz]`
- `gruppiere_zu_trainings(eintraege) -> tuple[Training, ...]`
- **Testfälle:** die fünf Teilfunktions-Tests oben in `tests/test_csv_import.py`
- **Text:** Warum gibt `validiere_zeile` einen String statt eine Exception zu werfen?

### C1A – Komposition zu einem Ablauf mit Edge Cases
- **Code:** `importiere_csv` als Komposition
- **Edge Cases:** `test_leere_datei`, `test_nur_kopfzeile`, `test_falsche_kopfzeile`, `test_ungueltiges_datum_und_negatives_gewicht_brechen_nicht_ab`, `test_dezimalkomma_und_semikolon`, `test_bom_und_leerzeilen_werden_toleriert`
- **Vergleich:** "Abbrechen beim ersten Fehler" vs. "Fehler sammeln" – warum letzteres?

---

## C2 – Funktionen als Objekte, Lambda, map / filter / reduce (3 verschiedene Features!)

### C2B – Feature Suche/Filter (`app/services/filter.py`)
- **Funktion in Variable:** `SORTIERUNGEN["volumen"].schluessel` = `training_volumen`; `ist_kreuzheben = nach_uebung("kreuzheben")`
- **map:** `volumina` · **filter:** `filtere` · **reduce:** `gesamtvolumen`
- **Testfälle:** `test_filter_fabrik_liefert_funktion`, `test_map_und_reduce`

### C2I – Feature Wochenstatistik (`app/services/statistik.py`)
- **Lambda:** in `auswahl`, `baue_woche`, `max_volumen`
- **Verkettet:** `filter(lambda…, map(lambda…, trainings))` in `auswahl`, danach `reduce` in `baue_woche`
- **Testfälle:** `test_filter_auf_uebung_zaehlt_nur_deren_saetze`, `test_unbekannte_uebung_und_leere_liste`
- **Text:** Wo wäre eine benannte Funktion lesbarer als das Lambda?

### C2A – Feature Bestenliste (`app/services/bestenliste.py`)
- **Aggregation:** bestes 1RM pro Übung
- **Benutzerdefinierte Sortierung:** `rang_schluessel` als `key=` (1RM absteigend, dann Name)
- **Testfälle:** `test_rangliste`, `test_gleichstand_alphabetisch_und_erster_satz_gewinnt`
- **Vergleich:** benannte Funktion vs. Lambda `key=lambda b: (-b.geschaetztes_1rm, b.uebung.lower())` – Entscheid begründen.

---

## D1 – Refactoring und Optimierung

### D1B – 3 Refactoring-Techniken + 2 Performance-Massnahmen
- **Refactoring:** *Extract Function* (Export aus Route → `exportiere_csv`), *Substitute Algorithm* (Bestenliste), *Replace Loop with Pipeline* (`lade_trainings` mit groupby/Comprehension)
- **Performance:** Dict statt Listensuche (O(1) statt O(n)), ein Durchlauf statt verschachtelter Schleifen, Index `idx_satz_training`, `executemany` in einer Transaktion beim Import/Seed

### D1I – Vorher/Nachher aus der Commit-Historie
- Commits aus den Refactoring-Schritten 2–4 (Hashes notieren: `git log --oneline`)
- **Gleiches Verhalten:** Test aus Schritt 1 (`test_bestenliste_viele_uebungen.py`) wurde VOR der Änderung committet und ist vorher und nachher grün; `test_export_inhalt_exakt` ebenso

### D1A – Messung + Begründung Datenstruktur
- `docs/messung_vorher.txt` vs. `docs/messung_nachher.txt` (aus `scripts/messung.py`)
- **Erwartung:** Bestenliste deutlich schneller (bei 5000 Trainings etwa Faktor 3), `lade_trainings` etwa gleich schnell → ehrlich festhalten: dort ging es um Lesbarkeit, nicht Speed
- **Begründung:** Warum `dict` (Schlüssel = Übung, Lookup O(1)) und nicht `list` oder `set`? Warum ist der Gewinn "nur" Faktor 3? (nur 12 Übungen → O(Ü × S) ist bei kleinem Ü noch harmlos)
