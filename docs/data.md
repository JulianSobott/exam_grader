# List
	Header
		- Name der Prüfung
		- x Personen / x Personen durchgekommen

	Body
		- Name der Person
		- ZK1 Punkte, ZK2 Punkte, boolean bestanden
		- x Punkte / maxPunkten
		- if bookmarked
		- Status (unstarted, active, done)

# Correction
	Header
		- Name
		- Matrikel oder ID
		- Teilaufgaben korrekt / maxTeilaufgaben
		- Punkte / maxPunkten
		- enum: step_failed (optional)

	Body
		Aufgabe
			- Name
			- Punkte / maxPunkte
			- if bookarked

		Teilaufgabe
			- Aufgabenname
			- Aufgabenbeschreibung
			- Punkte / maxPunkte
			- if bookmarked

			Snippet
				- Klassenname, Snnipped-name
				- Code
			Testcase
				- Name
				- bestanden
				- Assertions