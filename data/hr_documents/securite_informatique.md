# Politique de Securite Informatique - TechCorp France

## Introduction

La securite informatique est l'affaire de tous chez TechCorp France. Ce document presente les regles et bonnes pratiques que chaque collaborateur doit respecter pour proteger les donnees de l'entreprise, de nos clients et de nos partenaires.

Le non-respect de ces regles peut entrainer des sanctions disciplinaires et, dans les cas les plus graves, des poursuites judiciaires.

## Acces et authentification

### Identifiants
- Chaque salarie recoit un identifiant unique lors de son arrivee (format : prenom.nom).
- Le mot de passe initial est fourni par le service IT lors de la journee d'integration.
- Le mot de passe doit etre change obligatoirement lors de la premiere connexion.

### Politique de mots de passe
- Longueur minimale : 12 caracteres.
- Doit contenir au moins : 1 majuscule, 1 minuscule, 1 chiffre et 1 caractere special.
- Le mot de passe expire tous les 90 jours (notification 7 jours avant l'expiration).
- Les 10 derniers mots de passe ne peuvent pas etre reutilises.
- Ne jamais partager son mot de passe, meme avec le service IT (le service IT ne vous le demandera jamais).
- Utiliser un gestionnaire de mots de passe : l'entreprise fournit une licence Bitwarden a chaque salarie.

### Authentification a deux facteurs (2FA)
- Le 2FA est obligatoire pour :
  - L'acces VPN (teletravail)
  - Les applications critiques (GitLab, AWS, base de donnees clients)
  - L'acces email depuis un appareil personnel
- Application 2FA recommandee : Microsoft Authenticator (fourni par l'entreprise).
- En cas de perte du telephone : contacter immediatement le service IT pour reinitialiser le 2FA.

## Materiel informatique

### Equipement fourni
- Ordinateur portable professionnel (Dell ou MacBook selon le poste et les preferences).
- Un ecran 24 pouces au bureau.
- Peripheriques : clavier, souris, casque audio.
- Telephone professionnel (pour les postes eligibles : managers, commerciaux, astreinte).

### Regles d'utilisation
- Le materiel professionnel est destine a un usage principalement professionnel.
- Une utilisation personnelle raisonnable est toleree (navigation web, emails personnels) a condition de ne pas impacter la productivite ni la securite.
- Il est interdit d'installer des logiciels non autorises sur le materiel professionnel. La liste des logiciels autorises est disponible sur l'intranet IT.
- Les mises a jour de securite sont obligatoires et deployees automatiquement. Ne pas reporter les mises a jour de plus de 48 heures.
- En cas de perte ou de vol du materiel, prevenir immediatement le service IT (it@techcorp.fr) et votre manager. Un signalement a la police est requis en cas de vol.

### BYOD (Bring Your Own Device)
- L'utilisation d'appareils personnels pour acceder aux ressources de l'entreprise est autorisee sous conditions :
  - Inscription de l'appareil aupres du service IT.
  - Installation de l'application MDM (Mobile Device Management) de l'entreprise.
  - Systeme d'exploitation a jour (derniere version majeure).
  - Antivirus actif et a jour.

## Messagerie et communication

### Email professionnel
- L'adresse email professionnelle (prenom.nom@techcorp.fr) est strictement reservee aux communications professionnelles.
- Ne jamais ouvrir de pieces jointes provenant d'expediteurs inconnus.
- Signaler tout email suspect (phishing) en le transferant a securite@techcorp.fr.
- Les emails contenant des donnees sensibles doivent etre chiffres (utiliser la fonction de chiffrement d'Outlook ou GPG).
- Taille maximale des pieces jointes : 25 Mo. Pour les fichiers volumineux, utiliser le partage via SharePoint ou le drive d'equipe.

### Messagerie instantanee (Slack)
- Slack est l'outil de communication instantanee officiel de TechCorp.
- Ne jamais partager d'informations confidentielles (mots de passe, tokens, cles API) via Slack.
- Les canaux publics sont accessibles a tous les salaries. Les informations sensibles doivent etre partagees uniquement en messages prives ou dans des canaux restreints.
- Canaux importants pour les nouveaux arrivants :
  - #general : annonces et informations generales
  - #random : discussions informelles
  - #onboarding : questions et ressources pour les nouveaux
  - #it-support : demandes d'assistance technique
  - #rh-questions : questions RH generales

### Visioconference
- Outil officiel : Google Meet (acces via Google Workspace).
- Pour les reunions avec des participants externes : toujours activer la salle d'attente.
- Les reunions confidentielles ne doivent pas etre tenues dans des lieux publics (cafe, train).

## Protection des donnees

### Classification des donnees
TechCorp classe ses donnees en 4 niveaux :

1. **Public** : informations pouvant etre partagees sans restriction (site web, blog, communiques de presse).
2. **Interne** : informations reservees aux salaries (intranet, procedures internes, organigramme).
3. **Confidentiel** : informations sensibles a acces restreint (donnees clients, contrats, informations financieres).
4. **Strictement confidentiel** : informations critiques (donnees personnelles au sens RGPD, secrets commerciaux, strategies).

### Regles de manipulation
- Les donnees confidentielles et strictement confidentielles ne doivent jamais etre :
  - Copiees sur des supports personnels (cle USB, cloud personnel, email personnel).
  - Imprimees sans necessite (les impressions doivent etre recuperees immediatement).
  - Envoyees par email non chiffre.
  - Partagees avec des personnes non habilitees.
- Le stockage se fait obligatoirement sur les serveurs de l'entreprise ou le cloud d'entreprise (Google Drive / SharePoint).
- L'utilisation de services cloud tiers (Dropbox, WeTransfer, etc.) est interdite pour les donnees internes et superieures.

### RGPD
- TechCorp est soumis au Reglement General sur la Protection des Donnees (RGPD).
- Le Delegue a la Protection des Donnees (DPO) est Marc Levy (dpo@techcorp.fr).
- Tout traitement de donnees personnelles doit etre declare au DPO.
- En cas de fuite de donnees, prevenir immediatement le DPO et le service IT.

## Incidents de securite

### Que faire en cas d'incident ?
1. Ne pas paniquer et ne pas tenter de resoudre le probleme seul.
2. Deconnecter l'appareil du reseau si possible (debrancher le cable Ethernet ou desactiver le Wi-Fi).
3. Contacter immediatement le service IT : it@techcorp.fr ou 01 40 50 60 80 (ligne d'urgence 24h/24 : 01 40 50 60 81).
4. Ne pas eteindre l'ordinateur (les preuves forensiques pourraient etre perdues).
5. Noter le maximum de details : heure, ce que vous faisiez, messages affiches, etc.

### Exemples d'incidents a signaler
- Vous avez clique sur un lien suspect dans un email.
- Un programme inconnu s'execute sur votre ordinateur.
- Vous avez perdu ou vous etes fait voler votre materiel professionnel.
- Vous avez accidentellement envoye des donnees confidentielles au mauvais destinataire.
- Votre compte semble avoir ete compromis (connexion inhabituelle, mot de passe change sans votre action).

## Formation securite

- Une formation de sensibilisation a la securite informatique est obligatoire pour tous les nouveaux arrivants (planifiee lors de la premiere semaine d'onboarding).
- Un rappel annuel est organise chaque annee en octobre (mois de la cybersecurite).
- Des campagnes de phishing simulees sont menees regulierement pour tester la vigilance des salaries. Les resultats sont anonymes et servent a ameliorer les formations.

## Contact securite informatique

- Service IT (support general) : it@techcorp.fr ou 01 40 50 60 80
- Urgence securite (24h/24) : 01 40 50 60 81
- Signalement phishing : securite@techcorp.fr
- DPO (donnees personnelles) : Marc Levy (dpo@techcorp.fr)
- Responsable IT : Thomas Girard (thomas.girard@techcorp.fr)
