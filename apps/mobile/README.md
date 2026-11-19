# Jefamora mobile

Application Flutter pour les clients et les ouvriers. Elle parle à l’API Django sur `/api/v1`.

## Lancer

Depuis `apps/mobile`, avec l’API sur le port 8000 :

```bash
flutter run
```

Sur l’émulateur Android, l’adresse par défaut est `http://10.0.2.2:8000`. Sur un téléphone réel, passez l’adresse de la machine :

```bash
flutter run --dart-define=API_BASE=http://192.168.1.20:8000
```

Le parcours client envoie une demande à des ouvriers vérifiés, compare les devis et confirme la fin de mission. Le parcours ouvrier reçoit les demandes, envoie un devis, démarre la mission et en déclare la fin.
