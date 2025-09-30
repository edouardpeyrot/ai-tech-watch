
# 🤖 AI Tech Watch

> ⚠️ **Version Beta** - Ce projet est en développement actif et peut contenir des bugs. Utilisez-le à vos risques et périls.

Système automatisé de veille technologique utilisant l'API OpenAI pour générer des rapports hebdomadaires ou quotidiens envoyés par email avec images inline.

## ✨ Fonctionnalités

- 🤖 Génération automatique de contenu via OpenAI (GPT-4, GPT-4o-mini, etc.) - à venir : Azure AI, Claude
- 📧 Envoi d'emails HTML stylisés avec images embarquées (inline CID)
- 🎨 Templates Jinja2 personnalisables
- ⚙️ Configuration YAML simple
- 🔄 Compatible avec Cron pour automatisation
- 📦 Versions compilées disponibles (Windows, Linux, macOS)
- 🔐 Support SMTP/SMTP SSL/TLS et Amazon SES

## 📥 Installation

### Option 1 : Télécharger l'exécutable précompilé (Recommandé)

1. Rendez-vous sur la page [Releases](https://github.com/VOTRE_USERNAME/ai-tech-watch/releases)
2. Téléchargez la version correspondant à votre système :
   - `ai-tech-watch-linux-amd64` pour Linux
   - `ai-tech-watch-macos-amd64` pour macOS
   - `ai-tech-watch-windows-amd64.exe` pour Windows

3. Rendez l'exécutable... exécutable (Linux/macOS) :
   ```bash
   chmod +x ai-tech-watch-linux-amd64
   # ou
   chmod +x ai-tech-watch-macos-amd64
   ```

4. Placez-le dans un dossier de votre choix :
   ```bash
   mkdir -p ~/ai-tech-watch
   mv ai-tech-watch-* ~/ai-tech-watch/
   cd ~/ai-tech-watch
   ```

### Option 2 : Installer depuis les sources avec Python

#### Prérequis
- Python 3.13+ (testé avec 3.13.5)
- pip
- virtualenv (recommandé)

#### Installation

Créer et activer un environnement virtuel
python3 -m venv .venv source .venv/bin/activate # Linux/macOS
ou
.venv\Scripts\activate # Windows
Installer les dépendances
pip install -r requirements.txt``` 

## ⚙️ Configuration

### 1. Créer le fichier `.env`

Créez un fichier `.env` à la racine du projet :
```

bash
OpenAI Configuration
OPENAI_API_KEY=sk-proj-VOTRE_CLE_API_OPENAI OPENAI_BASE_URL=https://api.openai.com/v1
Email Configuration
MAIL_FROM=votre-email@example.com MAIL_TO=destinataire@example.com
Plusieurs destinataires séparés par des virgules :
MAIL_TO=user1@example.com,user2@example.com
SMTP Configuration (Gmail example)
SMTP_HOST=smtp.gmail.com SMTP_PORT=587 SMTP_USER=votre-email@example.com SMTP_PASSWORD=votre_mot_de_passe_application
Optional: Amazon SES SMTP (si utilisé, prioritaire sur SMTP_*)
SES_SMTP_HOST=email-smtp.eu-west-1.amazonaws.com
SES_SMTP_PORT=587
SES_SMTP_USER=VOTRE_SES_USER
SES_SMTP_PASSWORD=VOTRE_SES_PASSWORD
Optional: SMTP Options
SMTP_STARTTLS=true # Utiliser STARTTLS (défaut: true)
``` 

### 2. Configurer `config.yaml`

Le fichier `config.yaml` contient la configuration de la veille :
```

yaml model: "gpt-4o-mini" # ou "gpt-4", "gpt-3.5-turbo" 
temperature: 0.7 
max_tokens: 10000 
stack: DevOps / MLOps / AI / Cloud / Cybersecurity 
topics: Terraform / Kubernetes / AWS / Azure / GCP 
frequency: week # "week" ou "day" 
system_prompt: | You are an assistant specialized in {frequency} monitoring...
Voir config.yaml pour le prompt complet
``` 

### 3. Personnaliser les templates (optionnel)

- `email.j2` : Template HTML pour l'email
- `error.j2` : Template d'erreur en cas de problème

## 🚀 Utilisation

### Exécution manuelle

#### Avec l'exécutable
```

bash
Mode dry-run (test sans envoi d'email)
./ai-tech-watch-linux-amd64 --dry-run
Exécution normale (envoi d'email)
./ai-tech-watch-linux-amd64
``` 

#### Avec Python
```

bash
Activer le venv
source .venv/bin/activate
Mode dry-run
python main.py --dry-run
Exécution normale
python main.py
``` 

### Automatisation avec Cron

#### 1. Avec l'exécutable
```

bash
Editer la crontab
crontab -e
Ajouter une ligne pour exécution hebdomadaire (tous les lundis à 8h)
0 8 * * 1 cd /chemin/vers/ai-tech-watch && ./ai-tech-watch-linux-amd64 >> /tmp/ai-tech-watch.log 2>&1
Ou quotidienne (tous les jours à 8h)
0 8 * * * cd /chemin/vers/ai-tech-watch && ./ai-tech-watch-linux-amd64 >> /tmp/ai-tech-watch.log 2>&1``` 

#### 2. Avec Python et venv
```

bash crontab -e
Hebdomadaire (lundis à 8h)
0 8 * * 1 cd /chemin/vers/ai-tech-watch && /chemin/vers/ai-tech-watch/.venv/bin/python main.py >> /tmp/ai-tech-watch.log 2>&1
Quotidienne (tous les jours à 8h)
0 8 * * * cd /chemin/vers/ai-tech-watch && /chemin/vers/ai-tech-watch/.venv/bin/python main.py >> /tmp/ai-tech-watch.log 2>&1``` 

#### Exemples de planification Cron
```

bash
Tous les lundis à 8h00 (UTC)
0 8 * * 1 cd /home/user/ai-tech-watch && ./ai-tech-watch-linux-amd64
Tous les jours à 8h00
0 8 * * * cd /home/user/ai-tech-watch && ./ai-tech-watch-linux-amd64
Tous les premiers du mois à 9h00
0 9 1 * * cd /home/user/ai-tech-watch && ./ai-tech-watch-linux-amd64
Tous les vendredis à 17h00
0 17 * * 5 cd /home/user/ai-tech-watch && ./ai-tech-watch-linux-amd64
``` 

#### Vérifier les logs
```

bash tail -f /tmp/ai-tech-watch.log``` 

### Systemd Timer (Alternative à Cron sous Linux)

Créez `/etc/systemd/system/ai-tech-watch.service` :
```

ini [Unit] Description=AI Tech Watch Service After=network.target
[Service] Type=oneshot User=votre_user WorkingDirectory=/chemin/vers/ai-tech-watch ExecStart=/chemin/vers/ai-tech-watch/ai-tech-watch-linux-amd64 StandardOutput=journal StandardError=journal
[Install] WantedBy=multi-user.target
``` 

Créez `/etc/systemd/system/ai-tech-watch.timer` :
```

ini [Unit] Description=AI Tech Watch Timer (Weekly) Requires=ai-tech-watch.service
[Timer] OnCalendar=Mon --* 08:00:00 Persistent=true
[Install] WantedBy=timers.target``` 

Activez le timer :
```

bash sudo systemctl daemon-reload sudo systemctl enable ai-tech-watch.timer sudo systemctl start ai-tech-watch.timer
Vérifier le statut
sudo systemctl status ai-tech-watch.timer sudo systemctl list-timers``` 

## 📧 Configuration SMTP

### Gmail

1. Activez l'authentification à 2 facteurs
2. Générez un mot de passe d'application : https://myaccount.google.com/apppasswords
3. Utilisez ce mot de passe dans `.env`
```

env SMTP_HOST=smtp.gmail.com SMTP_PORT=587 SMTP_USER=votre-email@gmail.com SMTP_PASSWORD=votre_mot_de_passe_application``` 

### Amazon SES

```env
SES_SMTP_HOST=email-smtp.eu-west-1.amazonaws.com
SES_SMTP_PORT=587
SES_SMTP_USER=VOTRE_ACCESS_KEY
SES_SMTP_PASSWORD=VOTRE_SECRET_KEY
```
```

Autres fournisseurs SMTP
Outlook/Office365 : smtp.office365.com:587
Yahoo : smtp.mail.yahoo.com:587 

OVH : ssl0.ovh.net:587
SMTP SSL (port 465) : Le script détecte automatiquement
```
🛠️ Développement
Build depuis les sources
``` bash
# Installer PyInstaller
pip install pyinstaller

# Build
pyinstaller --onefile \
  --name ai-tech-watch \
  --add-data "email.j2:." \
  --add-data "error.j2:." \
  --add-data "config.yaml:." \
  --hidden-import=yaml \
  --hidden-import=jinja2 \
  --hidden-import=dotenv \
  main.py

# L'exécutable sera dans dist/
```

Structure du projet
``` 
ai-tech-watch/
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions pour build automatique
├── .env                    # Configuration (non versionné)
├── .gitignore
├── config.yaml             # Configuration de la veille
├── email.j2                # Template email HTML
├── error.j2                # Template email d'erreur
├── main.py                 # Script principal
├── requirements.txt        # Dépendances Python
└── README.md
```

🐛 Dépannage
```
L'exécutable ne trouve pas les templates
Assurez-vous d'exécuter le binaire depuis le dossier contenant email.j2, error.j2 et config.yaml.``` bash
cd /chemin/vers/ai-tech-watch
./ai-tech-watch-linux-amd64


#Erreur SMTP
Vérifiez vos identifiants SMTP
Pour Gmail : utilisez un mot de passe d'application
Vérifiez que le port est correct (587 pour TLS, 465 pour SSL)
#Erreur OpenAI API
Vérifiez que votre clé API est valide
Vérifiez votre crédit OpenAI : https://platform.openai.com/usage
Vérifiez le nom du modèle dans config.yaml

📝 Licence
Voir LICENSE
🤝 Contribuer
Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.
⚠️ Avertissement
Ce projet est en version beta et n'est pas stable. Il peut contenir des bugs, des problèmes de sécurité ou des comportements inattendus. Utilisez-le en connaissance de cause et à vos propres risques.
❌ Ne pas utiliser en production 
❌ Ne pas commiter le fichier .env (contient des secrets)
⚠️ Les coûts d'API OpenAI sont à votre charge
⚠️ Vérifiez les limites de votre fournisseur SMTP
📞 Support
Pour toute question ou problème :
Ouvrez une issue GitHub
Consultez les discussions
 
Note : Pensez à créer un tag pour déclencher un build de release :

git tag -a v0.1.0-beta -m "First beta release"
git push origin v0.1.0-beta
```

Cela déclenchera automatiquement le workflow GitHub Actions qui compilera les exécutables pour toutes les plateformes.

