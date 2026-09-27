# ImmoTrack

Mini-projet pour suivre des biens immobiliers (prix, surface, ville, statut, prix au m²).

| Couche | Techno |
|---|---|
| Frontend | Vue.js 3 (Vite, Composition API) |
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Base de données | PostgreSQL 16 |
| Conteneurs | Podman (pods) |
| CI/CD | GitHub Actions, GitHub Container Registry |

## Avancement

- [x] Étape 1 : Podman + PostgreSQL
- [x] Étape 2 : Backend FastAPI + tests
- [ ] Étape 3 : Conteneuriser le backend (`Containerfile`)
- [ ] Étape 4 : Frontend Vue 3 + tests Vitest
- [ ] Étape 5 : Orchestration (compose / Kubernetes YAML)
- [ ] Étape 6 : CI/CD GitHub Actions
- [ ] Bonus : Alembic, Pinia, Vue Router

## Structure

```
immotrack/
├── backend/
│   ├── app/
│   │   ├── config.py      # réglages (lus depuis les variables d'env)
│   │   ├── database.py    # engine, session, get_db
│   │   ├── models.py      # tables SQLAlchemy
│   │   ├── schemas.py     # entrées / sorties de l'API (Pydantic)
│   │   ├── main.py        # application FastAPI
│   │   └── routers/
│   │       └── biens.py   # routes CRUD
│   ├── tests/
│   ├── pyproject.toml     # config pytest + ruff
│   └── requirements.txt
├── frontend/
├── deploy/
└── .github/workflows/
```

---

## Démarrage rapide (routine quotidienne)

```powershell
# 1. Démarrer la VM Podman et la base
podman machine start
podman pod start immo

# 2. Lancer l'API (depuis backend/)
cd backend
.venv\Scripts\Activate.ps1
fastapi dev app/main.py
```

- API : http://127.0.0.1:8000
- Documentation Swagger : http://127.0.0.1:8000/docs
- Santé : http://127.0.0.1:8000/health

## Installation depuis zéro

```powershell
# Base de données
podman volume create immo-data
podman pod create --name immo -p 5432:5432
podman run -d --pod immo --name immo-db -e POSTGRES_USER=immo -e POSTGRES_PASSWORD=immo -e POSTGRES_DB=immo -v immo-data:/var/lib/postgresql/data docker.io/library/postgres:16
podman exec -it immo-db psql -U immo -d immo -c "CREATE DATABASE immo_test;"

# Backend
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Aide-mémoire Podman

### Concepts clés

- **Sans démon** : pas de service en arrière-plan, les conteneurs sont des processus normaux.
- **Rootless** : les conteneurs tournent avec mon utilisateur, pas en root.
- **Pod** : groupe de conteneurs qui partagent le même réseau (comme Kubernetes).
  Dans un pod, les conteneurs se parlent via `localhost`.
- **Les ports se publient sur le pod**, pas sur les conteneurs (`podman pod create -p ...`).
  Impossible de les modifier ensuite : il faut recréer le pod.
- **Noms d'images complets** : `docker.io/library/postgres:16` plutôt que `postgres:16`.
- **Sous Windows/macOS**, Podman tourne dans une VM (`podman machine`).
  Quand la VM s'arrête, les conteneurs s'arrêtent et **ne redémarrent pas seuls**.

### La VM (Windows / macOS)

```powershell
podman machine init            # créer la VM (une seule fois)
podman machine start           # démarrer
podman machine stop            # arrêter
podman machine ls              # état, date de création
podman system connection list  # connexions (rootless / root), laquelle est par défaut
```

### Pods

```powershell
podman pod create --name immo -p 5432:5432   # créer (avec les ports)
podman pod ps                                # lister
podman pod start immo                        # démarrer tous ses conteneurs
podman pod stop immo                         # arrêter
podman pod restart immo                      # redémarrer
podman pod rm -f immo                        # supprimer le pod ET ses conteneurs
podman pod inspect immo                      # détails (ports, conteneurs...)
```

### Conteneurs

```powershell
podman run -d --pod immo --name NOM IMAGE    # lancer dans un pod
podman ps                                    # conteneurs actifs
podman ps -a --pod                           # tous, avec leur pod
podman logs NOM                              # logs
podman logs -f --tail 20 NOM                 # suivre les 20 dernières lignes
podman exec -it NOM COMMANDE                 # exécuter une commande dedans
podman exec -it NOM bash                     # ouvrir un shell dedans
podman stop NOM / podman start NOM
podman rm -f NOM                             # supprimer
podman inspect NOM                           # tous les détails
```

### Volumes et images

```powershell
podman volume create NOM
podman volume ls
podman volume inspect NOM
podman volume rm NOM             # ⚠️ supprime les données

podman images                    # images téléchargées
podman pull docker.io/library/postgres:16
podman rmi IMAGE
podman system prune              # nettoyer ce qui ne sert plus
```

### Podman vs Docker

| | Docker | Podman |
|---|---|---|
| Démon | oui (`dockerd`) | non |
| Root par défaut | oui | non (rootless) |
| Pods | non | oui |
| Fichier de build | `Dockerfile` | `Containerfile` (Dockerfile accepté) |
| Compatibilité CLI | | `alias docker=podman` marche dans la plupart des cas |
| Kubernetes | | `podman kube generate` / `podman kube play` |

---

## Aide-mémoire PostgreSQL

```powershell
podman exec -it immo-db psql -U immo -d immo   # console SQL
```

Commandes `psql` :

```
\l            lister les bases
\c immo_test  changer de base
\dt           lister les tables
\d biens      structure d'une table
\dT+          lister les types (ex : l'enum statut)
\x            affichage vertical (pratique pour les longues lignes)
\q            quitter
```

SQL utile :

```sql
SELECT * FROM biens;
SELECT ville, COUNT(*), AVG(prix / surface) AS prix_m2_moyen FROM biens GROUP BY ville;
SELECT * FROM biens WHERE statut = 'visite' ORDER BY prix;
```

---

## Aide-mémoire Python / FastAPI

```powershell
python -m venv .venv                  # créer l'environnement virtuel
.venv\Scripts\Activate.ps1            # l'activer (PowerShell)
deactivate                            # le désactiver
pip install -r requirements.txt
pip freeze                            # versions installées

fastapi dev app/main.py               # serveur de dev (rechargement auto)
fastapi dev app/main.py --port 8001   # sur un autre port
fastapi run app/main.py               # mode production
```

### Concepts FastAPI à retenir

- **Modèle SQLAlchemy** (`models.py`) = la table en base.
- **Schéma Pydantic** (`schemas.py`) = ce que l'API accepte / renvoie. Valide les données (erreur 422 sinon).
- **Dépendance** (`Depends(get_db)`) = FastAPI fournit une ressource à la route (ici une session DB).
- **`dependency_overrides`** = remplacer une dépendance dans les tests.
- **`model_dump(exclude_unset=True)`** = ne garder que les champs envoyés (indispensable pour un PATCH).
- **`lifespan`** = code exécuté au démarrage / à l'arrêt de l'application.

### Tests et qualité

```powershell
pytest -v                     # lancer les tests
pytest -v -k statut           # seulement les tests dont le nom contient "statut"
pytest -x                     # s'arrêter à la première erreur
ruff check .                  # linter
ruff check . --fix            # corriger automatiquement
ruff format .                 # formater le code
```

---

## Aide-mémoire Git

```powershell
git switch -c feat/ma-branche     # créer une branche et y aller
git switch main                   # revenir sur main
git status
git add .
git commit -m "feat(backend): description"
git push -u origin feat/ma-branche
git pull                          # récupérer les changements
git log --oneline --graph         # historique
```

### Conventional Commits

| Préfixe | Usage |
|---|---|
| `feat:` | nouvelle fonctionnalité |
| `fix:` | correction de bug |
| `test:` | ajout / modification de tests |
| `docs:` | documentation |
| `refactor:` | réécriture sans changer le comportement |
| `chore:` | maintenance (config, dépendances...) |
| `ci:` | pipeline CI/CD |

---

## Pièges rencontrés (et solutions)

**`podman machine init` échoue avec `unexpected EOF`**
Téléchargement de l'image de la VM interrompu. Réessayer, désactiver VPN/antivirus, ou passer en partage de connexion.

**Erreur d'authentification en français avec accents cassés**
L'image Postgres officielle répond en anglais : un message en français veut dire qu'un **PostgreSQL installé sur Windows** occupe le port 5432. Vérifier avec `Get-Service *postgres*`.

**L'API reste bloquée sur `Waiting for application startup.`**
Elle n'arrive pas à joindre la base. Vérifier `podman ps --pod` (le conteneur tourne-t-il ?) et `Test-NetConnection 127.0.0.1 -Port 5432`. Ajouter `connect_args={"connect_timeout": 5}` à `create_engine` pour avoir une vraie erreur au lieu d'une attente infinie.

**`ERR_CONNECTION_REFUSED` sur le port 8000**
Uvicorn n'ouvre le port qu'une fois le démarrage terminé : le problème est en amont (souvent la base).

**`ERR_EMPTY_RESPONSE` sur le port 8000**
Le pod publie déjà le port 8000 et intercepte les requêtes. Ne publier sur le pod que les ports des conteneurs qui existent vraiment.

**Le pod a disparu**
La VM a été recréée (vérifier la colonne CREATED de `podman machine ls`). Tout ce qui était dedans est perdu : d'où l'intérêt de commandes reproductibles.

**`localhost` vs `127.0.0.1`**
`localhost` peut être résolu en IPv6 (`::1`) et bloquer. Utiliser `127.0.0.1` dans les URLs de connexion.

**PowerShell refuse d'activer le venv**
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

**Commandes multi-lignes**
Linux utilise `\` en fin de ligne, PowerShell utilise le backtick `` ` ``.

**Projet dans OneDrive**
À éviter : OneDrive synchronise `.venv` et `node_modules`, ce qui ralentit et verrouille des fichiers. Préférer `C:\dev\`.