# SAE401 - Plateforme de gestion des déploiements


# Service Users

## Description

Le service **Users** fait partie de la plateforme de gestion des déploiements d’applications.
Il gère la création, la lecture et la vérification des utilisateurs.
L'authentification se fait via JWT dynamique.

---

## Endpoints

| Méthode | Endpoint        | Auth | Description                                                               |
| ------- | --------------- | ---- | ------------------------------------------------------------------------- |
| POST    | `/auth/login`   | Non  | Authentifie un utilisateur et retourne un token (statique pour l’instant) |
| POST    | `/auth/verify`  | Oui  | Vérifie la validité du token                                              |
| GET     | `/users`        | Oui  | Liste tous les utilisateurs                                               |
| POST    | `/users`        | Oui  | Crée un nouvel utilisateur                                                |
| GET     | `/users/{id}`   | Oui  | Récupère un utilisateur par son ID                                        |
| PUT     | `/users/{id}`   | Oui  | Met à jour les informations d’un utilisateur                              |
| DELETE  | `/users/{id}`   | Oui  | Supprime un utilisateur                                                   |
| GET     | `/users/health` | Non  | Vérifie l’état du service Users                                           |


## Notes

* Le service est conçu pour être intégré à la plateforme complète en utilisant le docker-compose sur le dépot principal.
* Mot de passe utilisateur stocké via la bibliothèque Argon2, recommandé par l’OWASP (Open Web Application Security Project) pour les mots de passe car contient un salt. Cela permet d’éviter de deviner le hash via des comparaisons de hash.
* Stockage en MongoDB.
