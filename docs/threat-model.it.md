# Modello delle minacce

## Risorse e confini di fiducia

Le risorse sono l'integrità delle decisioni, la riservatezza delle configurazioni importate,
l'accuratezza dei report e la disponibilità della CI. Gli input non fidati sono policy YAML, snapshot,
immagini container e pacchetti. Batfish è considerato affidabile solo per analizzare i dati sintetici
forniti; nel laboratorio previsto non è esposto oltre l'host locale.

## Minacce e mitigazioni

| Minaccia | Impatto | Mitigazione |
|---|---|---|
| Policy malformata o ambigua | Approvazione errata | Schema rigoroso, loader YAML sicuro, rifiuto di chiavi sconosciute e duplicati |
| Symlink nello snapshot | Analisi involontaria di dati locali | Rifiuto di ogni symlink sotto lo snapshot |
| Semantica vendor mancante | Falsa fiducia | Revisione dei warning di parsing e limiti documentati |
| Segreti o configurazioni reali nel repository | Perdita di riservatezza | Fixture sintetiche, `.gitignore`, workflow anti-segreti e guida alla revisione |
| Dipendenza/immagine compromessa | Esecuzione di codice | Versioni Python esatte, audit, aggiornamenti revisionati e isolamento container |
| Report obsoleto o falsificato | Decisione errata | Rigenerazione in CI, timestamp, snapshot, conteggi e risultato machine-readable |
| Input enorme | Esaurimento risorse CI | Snapshot revisionati; limiti di risorse/dimensione previsti come hardening futuro |

## Rischi residui

Batfish potrebbe non implementare una funzione di configurazione o differire dalla release di un
apparato. I report dimostrano l'intento rispetto al modello fornito, non lo stato runtime. Le immagini
container sono contenuto eseguibile di terze parti. Compose pubblica Batfish soltanto su loopback, ma
la configurazione resta adatta a un laboratorio locale fidato, non a un server condiviso.
