# Phirst-functions
🥁 Source code of Phirst's backend functions deployed in Google Cloud Functions.

## 💿 First things first: What's Phirst? 
Es un app de nicho que **mejora el flow de descubrimiento y consumo de música** para melómanos y fans. A partir de la biblioteca del usuario en Spotify, se le da seguimiento a:
- Los nuevos lanzamientos de los artistas que sigue.
- Los nuevos artículos de crítica musical de revistas y fuentes curadas por el staff de Phirst.  

### ✨ Alpha release features
- Autenticación con correo y contraseña
- Autenticación con Spotify
- Importación de artistas
- *Hot takes* de Pitchfork
- Actualizaciones de *hot releases* en tiempo real
- Actualizaciones de *hot takes* en tiempo real

### 📅 Coming soon
- iOS Accessibility features 
- Sistema de punteos del público
- *Hot takes* de Resident Advisor
- Sistema de punteos de los críticos
- Perfil de artistas
- Push notifications
- Feedback & tip jar functionalities

### 🚀 In the long run
- Social networking features
- Personal stats
- Personalized widget
- Personalized themes & app icons

## Technologies & design
Phirst utiliza una infraestructura serverless y se sirve de una base de datos NoSQL (Firestore) y del cache automanejado por los Cocoapods de Firebase y de URLImage. A continuación se describe la arquitectura del app. 

### Autenticación
![Infra de auth](https://i.imgur.com/INdZNUY.png)

La autenticación se realiza mediante Firebase Auth, con correo y password. 
Luego se le solicita al usuario darle permisos a Phirst para accesar a su biblioteca de Spotify (usando el enlace devuelto por `user-auth`).

Spotify devuelve un redirect URL que es capturado mediante deep links por el app. Este URL contiene un código. Este código y el user ID de Firebase son enviados a ``auth_import_user`` para que coordine `auth-token`, `set_user_artists` y `enqueue_albums`. 

`auth-token` refresca los tokens para mantener el acceso a Spotify, `set_user_artists` guarda en Firestore los artistas que el usuario sigue y `enqueue_albums` deja en queue la importación de los lanzamientos de los artistas.

El queue autoescala, llegando hasta 3mil instancias durante la importación de 1.5mil artistas nuevos.  

### Albums
![Infra de albumes](https://i.imgur.com/fmxtKX7.png)

El app tiene un snapshot de la colección de álbumes, lo cual le permite leer nuevos documentos en tiempo real.

Esta colección es actualizada cuando el usuario importa sus artistas y cuando un cronjob implementado con Google Scheduler escribe en un canal de pubsub llamado `update-albums`.

### Pitchfork
![Infra de pitchfork](https://i.imgur.com/qRtRpiu.png)

El app tiene un snapshot de la colección de hot takes, lo cual le permite leer nuevos documentos en tiempo real.

Esta colección es actualizada cuando se guardan nuevos hot takes. Para el source de Pitchfork se implementó un webhook con Superfeedr para guardar los nuevos artículos en cuanto son publicados por la revista. 

Para tener un respaldo en caso Superfeedr falle, hay también un cronjob que publica al canal `pitchfork-takes` y triggerea la actualización.  
