Réponse à ta question métier :

1) OUI — un même réseau PEUT légitimement appartenir à 2 filiales
   (sous-réseau partagé). Donc :
   - PAS de script DELETE pour les 3 réseaux partagés.
   - PAS de script DELETE pour les 5 liaisons 172.22.64.* hors SODIREX.
   - PAS de contrainte UNIQUE à ajouter.
   - On garde les données telles quelles.

2) Dans t_device, la colonne IP s'appelle `ip_adress` (attention
   à l'orthographe : un seul "d"). Utilise cette colonne pour le
   fallback de résolution du id_reseau (au lieu de `adresse_ip`).

3) Concernant t_reseau_filiale : la question que je te posais n'était
   pas "y a-t-il des doublons globaux" mais "pour CHAQUE filiale
   individuellement, y a-t-il des doublons INTERNES ?" C'est-à-dire :
   - Pour id_filiale=1 : y a-t-il des id_reseau en double ?
   - Pour id_filiale=2 : y a-t-il des id_reseau en double ?
   - Pour id_filiale=3 : ...
   - etc. pour toutes les filiales.
   Le cas échéant, fournis un script de nettoyage CIBLÉ PAR FILIALE
   (à exécuter manuellement par moi, pas par toi).

