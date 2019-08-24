# IBZ Notenprüfer
## Voraussetzungen
#### Folgende Software muss beim Server installiert sein
- [Docker](https://www.digitalocean.com/community/tutorials/so-installieren-und-verwenden-sie-docker-auf-ubuntu-18-04-de "Docker")
- [Splash](https://splash.readthedocs.io/en/stable/install.html#linux-docker)

## Skript bei eurem Computer installieren
1.  Den ordner `IBZ` beim folgenden Pfad mit sudo installieren `/`:  
**Kommand**: `sudo mkdir /IBZ`  

2. Den Ordner REchte für euren Benutzer geben:  
**Kommand**: `sudo chown -R ${USER}:sudo /IBZ`  

3. Den Ordner beitreten:  
**Kommand**: `cd /IBZ`  
  
4.  Dieses Projekt anhand mit git clone kopieren:  
**Kommand**: `git clone git@github.com:IBZTI2018/notenpruefer.git .`  
  
5. Eine neue Datei namens `.env` mit nano erstellen:  
**Kommand**: `nano .env`  
  
6. Eure E-Mail Adresse, Password und Benachrichtungskanal definieren ohne die spitzigen klammern. Im Moment sind folgende Benachrichtungskanäle möglich (E-Mail, Slack). Falls ihr Slack auswählt, wird es beim #bot channel Meldungen schreiben:  
```
EMAIL=<eure_ibz_email_adresse>
PASSWORD=<eure_ibz_passwort>
ALERT_CHANNEL=email
```  

7. Die Daten speichern mit `CTRL + X`, dann `Y` und dann mit Taste `ENTER`.  
  
8. Den Cronjob installieren, damit der Skript jede 5 Minute die Prüfungsnoten überprüfen kann:  
`echo '*/5 * * * *	root	cd /IBZ && bash notify_notes.sh > /IBZ/log' >> /etc/crontab`  
  
9. Installation abgeschlossen. In 5 Minuten solltest du die 1. Meldung erhalten.
