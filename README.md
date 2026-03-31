# SAE401 - Plateforme de gestion des déploiements


# Service Users

## Description

Le service **Users** fait partie de la plateforme de gestion des déploiements d’applications.
Il gère la création, la lecture et la vérification des utilisateurs.

> Pour l’instant, l’authentification utilise un **token statique**. Les futures versions intégreront un système complet de login et génération dynamique de tokens.

Parfait, je vais te refaire un README pour ton service **Users** en listant **tous les endpoints disponibles**, avec les détails sur l’auth (token statique pour l’instant) et un exemple simple. Voici une version complète :

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

* Tous les endpoints nécessitant une authentification utilisent le **token statique** pour l’instant.
* Le service est conçu pour être intégré à la plateforme complète en utilisant le docker-compose sur le dépot principal.
* Mot de passe utilisateur stocké via la bibliothèque Argon2, recommandé par l’OWASP (Open Web Application Security Project) pour les mots de passe car contient un salt. Cela permet d’éviter de deviner le hash via des comparaisons de hash. 
