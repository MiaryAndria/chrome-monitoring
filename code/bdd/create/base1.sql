table t_user
id
nom
mdp

table t_customer 
id 
email
nom

table t_filiale
id 
nom

table t_reseau 
id
valeur

table t_device 
id
cpu 
ram 
stockage
batterie 
et autres informations périphériques obtenu depuis telemetry_device et telemetry_events et telemetry_apli etc lié (on peut faire table si veut)

table t_imprimante
id 
imprimante

table t_statut
id
statut

table t_configuration
id
type
valeur

table t_evenements
id
type

table t_reseau
id 
valeur 

table t_customer_device
id
id_customer
id_device

table t_device_statut
id 
id_device
id_statut
date

table t_imprimante_statut
id
id_imprimante
id_statut
date 

table t_evenements_device
id
id_device
id_evenements
date

table t_filiale_device
id
id_filiale
id_device

table t_filiale imprimante
id 
id_filiale
id_imprimante

table t_comparaison
id
id_deviceA
id_deviceB
date
commentaires

table t_reseau_filiale
id
id_reseau
id_filiale

table t_filiale_user
id
id_filiale
id_user

nb:Filiale peut contenir reseau c'est pour ça genre pour bien savoir l'user dans quel filiale de quel reseaux 

