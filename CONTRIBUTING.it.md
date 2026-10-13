# Contribuire

Usa soltanto dati di rete sintetici o completamente sanitizzati. Non aprire pull request con
credenziali, configurazioni produttive, indirizzi interni, nomi di clienti o dati riservati.

1. Crea un branch mirato e descrivi il comportamento modificato.
2. Aggiungi o aggiorna i test prima di cambiare l'esito di una policy.
3. Esegui `ruff check src tests`, `ruff format --check src tests`, `mypy src`, `pytest` e `pip-audit`.
4. Per modifiche all'analizzatore, esegui la demo Batfish completa e controlla warning e report.
5. Mantieni semanticamente allineati `README.md`, `README.it.md` e i documenti in coppia.

Segnala i problemi di sicurezza privatamente come indicato in `SECURITY.it.md`, non con issue pubbliche.
