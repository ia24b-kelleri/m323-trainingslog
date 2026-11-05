# Design-Blatt: Statistik-Seite (/statistik)

## Ziel
Der Benutzer sieht, wie sich sein Trainingsvolumen über die Wochen entwickelt,
um Fortschritt oder Stillstand zu erkennen.

## Deklarative Anforderungen (WAS, nicht WIE)
- Für jede Kalenderwoche mit Training wird das Gesamtvolumen angezeigt.
- Volumen eines Satzes = Gewicht × Wiederholungen.
- Pro Woche werden zusätzlich Anzahl Trainings und Ø-Volumen pro Training angezeigt.
- Die Wochen sind absteigend sortiert (neueste zuerst), weil die aktuelle Woche am meisten interessiert.
- Wochen ohne Training werden weggelassen (kein Eintrag mit 0).
- Optional kann nach einer Übung gefiltert werden. Dann zählen nur die Sätze dieser Übung.
- Leere Datenbank: Hinweis "Noch keine Trainings erfasst" statt leerer Tabelle.

## Input / Output
- Input:  tuple[Training, ...]  (aus lade_trainings), optional Übungsname
- Output: tuple[WochenStatistik, ...]
  WochenStatistik (frozen dataclass): jahr, kw, volumen, anzahl_trainings, durchschnitt

## Datenfluss
Trainings
  → [map]     Training → Training mit nur den Sätzen der gewählten Übung (falls Filter aktiv)
  → [filter]  nur Trainings, die danach noch Sätze haben
  → [gruppieren] nach (jahr, kw)
  → [reduce]  Volumen pro Woche summieren
  → [map]     → WochenStatistik (inkl. Durchschnitt)
  → [sort]    nach (jahr, kw), neueste zuerst
  → Template (Tabelle + CSS-Balken relativ zur stärksten Woche)

## Geplante Operatoren / Funktionen
- satz_volumen(satz: Satz) -> float
- training_volumen(training: Training) -> float          # map + sum
- kalenderwoche(training: Training) -> tuple[int, int]   # (jahr, kw) via isocalendar
- nur_uebung(training: Training, uebung: str) -> Training  # neues Objekt, keine Mutation
- wochen_statistik(trainings, uebung=None) -> tuple[WochenStatistik, ...]  # Komposition

## Edge Cases
- Jahreswechsel: ISO-Kalenderwoche verwenden (z.B. 30.12.2024 = KW 1/2025),
  darum (jahr, kw) als Schlüssel, nicht nur kw.
- Training ohne Sätze → Volumen 0.
- Filter auf Übung, die nie trainiert wurde → leeres Resultat, Hinweis anzeigen.
- Gross-/Kleinschreibung beim Übungsfilter ignorieren.
