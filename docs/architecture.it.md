# Architettura

## Requisiti e decisioni

NetChange Guard deve analizzare snapshot sanitizzati senza credenziali degli apparati, esprimere
l'intento in un formato revisionabile, produrre evidenze ripetibili e fallire in modo chiuso su input
non valido. L'implementazione è volutamente un piccolo livello di orchestrazione intorno a Batfish,
non un nuovo simulatore: la semantica dei protocolli resta affidata al motore di analisi maturo.

Lo schema YAML è intenzionalmente ristretto. Ogni policy descrive una posizione sorgente, spazi IPv4
sorgente/destinazione, protocollo, porte di destinazione e stato atteso. Un input limitato riduce
l'ambiguità e facilita la revisione. Le espressioni Batfish arbitrarie sono escluse perché esporrebbero
un linguaggio molto più ampio e difficile da validare.

## Componenti e flusso

1. `policy_loader` interpreta YAML con `safe_load`, controlla la versione e rifiuta campi sconosciuti,
   ID duplicati, prefissi malformati e porte non valide.
2. `BatfishBackend` inizializza una rete, carica uno snapshot offline e traduce ogni policy in
   `HeaderConstraints` e `PathConstraints`.
3. `engine` valuta separatamente ogni policy, mantenendo la corrispondenza con un requisito aziendale.
4. `reporting` produce viste equivalenti JSON e Markdown.
5. `cli` espone validazione, controllo singolo, confronto rigoroso e demo auto-verificante.

## Contratto degli exit code

| Codice | Significato |
|---:|---|
| 0 | Verifica richiesta superata |
| 1 | Errore di input, connessione, filesystem o operativo |
| 2 | Analisi completata con almeno una policy non soddisfatta |

## Alternative considerate

- **Replay diretto di pacchetti:** utile per esempi scelti, ma non copre l'intero spazio degli header.
- **Parser routing/ACL personalizzato:** scartato perché duplicare la semantica vendor genererebbe
  fiducia ingiustificata e un elevato costo di manutenzione.
- **Raccolta da apparati live:** scartata per mantenere il progetto gratuito, sicuro e senza credenziali.

## Punti di estensione

Il protocollo del backend permette di sostituire l'analizzatore senza cambiare la valutazione. Il
versionamento consente di aggiungere IPv6, nodi di transito o scenari di guasto senza modificare in
silenzio la versione 1.
