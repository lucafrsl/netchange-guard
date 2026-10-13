# Rapporto di verifica

Data: **2026-10-13**
Ambiente: host Windows, Python 3.11.9, Docker Engine 29.8.2
Analizzatore: Batfish 2026.08.27.3685, PyBatfish 2026.9.17.3748

Questo rapporto distingue i controlli eseguiti dalle sole definizioni dei workflow. Ogni risultato
seguente è stato osservato localmente sui file della versione 0.1.0; non sono state coinvolte reti
produttive o risorse cloud.

| Controllo | Comando/strumento | Risultato osservato |
|---|---|---|
| Schema policy | `netchange-guard validate --policies policies/security.yml` | 4 policy valide |
| Lint | `ruff check src tests` | Superato |
| Formattazione | `ruff format --check src tests` | 12 file già formattati |
| Type checking | `mypy src` | Nessun problema in 7 file sorgente |
| Test unitari | `pytest` | 31 superati |
| Soglia coverage | pytest-cov | 93,41%; minimo richiesto 90% |
| Audit dipendenze | `pip-audit --progress-spinner off` | Nessuna vulnerabilità nota; il pacchetto locale non pubblicato non è su PyPI ed è stato saltato |
| Scansione segreti | Gitleaks 8.30.0, scansione directory | 47 file consegnabili / 74,79 KB analizzati; nessun segreto rilevato |
| Demo Batfish | `netchange-guard demo ...` | Baseline 4/4; candidate 3/4; rilevata esattamente 1 regressione |
| Integrità parsing | Batfish `fileParseStatus` e `parseWarning` | Tutti i 6 file `PASSED`; 0 warning |
| Validazione Compose | `docker compose config --quiet` | Superata |

## Risultati osservati delle policy

| Policy | Baseline | Candidate |
|---|---:|---:|
| `users_no_ssh_to_management` | PASS (negato) | FAIL (consentito) |
| `users_can_reach_internal_https` | PASS (consentito) | PASS (consentito) |
| `dmz_cannot_reach_management` | PASS (negato) | PASS (negato) |
| `dmz_can_reach_internal_api` | PASS (consentito) | PASS (consentito) |

Le evidenze JSON e Markdown generate sono conservate in `reports/`.

## Non ancora eseguito

Non è possibile dichiarare superati i workflow ospitati da GitHub prima della pubblicazione e della
loro esecuzione. Le definizioni sono presenti in `.github/workflows/`; questo rapporto non attribuisce
esiti alla CI esterna.
