# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

## [1.0] - 31/03/2026
### Added
- Création du service **Users & Auth** en Flask.
- Authentification avec **login** et **vérification de token** (`/auth/login`, `/auth/verify`).
- Gestion des utilisateurs : création, lecture, modification, suppression (`/users`, `/users/<user_id>`).
- Gestion des rôles : `ADMIN`, `USER`.
- Gestion des tokens avec stockage JSON simple.
- Hashing des mots de passe avec **argon2**.
- Endpoint **health** pour le service Users (`/users/health`).
- Création automatique d’un utilisateur admin par défaut (`admin` / `admin123`) pour les tests.
- Gestion des erreurs : champs manquants, utilisateur non trouvé, utilisateur désactivé, rôle invalide.
- CORS activé pour Swagger / test local.
- Stockage persistant simple dans des fichiers JSON : `users.json`, `pwd.json`, `tokens.json`.

### Changed
- N/A (première version)

### Fixed
- N/A (première version)

## [2.0] - 02/04/2026
### Added
- JWT dynamique

### Changed
- Ajout de MongoDB à la place de JSON
- Image alpine python

### Fixed
- N/A
