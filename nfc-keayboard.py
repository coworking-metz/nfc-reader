import time
import pyautogui
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException
from smartcard.scard import *
import pyperclip
import os
import sys

if os.name == "nt":
    import msvcrt
    lock_file = open("script.lock", "w")

    try:
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        print("Une autre instance du script est déjà en cours.")
        sys.exit(1)

else:
    import fcntl
    lock_file = open("script.lock", "w")

    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("Une autre instance du script est déjà en cours.")
        sys.exit(1)

# Liste les lecteurs NFC disponibles
r = readers()
if not r:
    print("Aucun lecteur détecté.")
    exit()

# Récupère le nom du premier lecteur trouvé (ex: ACR122U)
reader_name = str(r[0])

# Établit un contexte PC/SC pour la communication avec les périphériques smartcard
hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
if hresult != SCARD_S_SUCCESS:
    print("Erreur SCardEstablishContext")
    exit()

# Connexion au lecteur en mode DIRECT pour envoyer une commande ESCAPE (sans carte nécessaire)
hresult, hcard, dwActiveProtocol = SCardConnect(
    hcontext,
    reader_name,
    SCARD_SHARE_DIRECT,  # Mode spécial pour envoyer des commandes au périphérique lui-même
    0                    # Pas de protocole (car on ne parle pas à une carte)
)

if hresult == SCARD_S_SUCCESS:
    # Commande spécifique au lecteur ACR122U pour désactiver le bip sonore
    disable_beep_command = [0xFF, 0x00, 0x52, 0x00, 0x00]

    # Code de contrôle IOCTL utilisé pour envoyer une Escape Command via SCardControl
    IOCTL = SCARD_CTL_CODE(3500)

    # Envoie la commande au lecteur pour désactiver le bip
    hresult, response = SCardControl(hcard, IOCTL, disable_beep_command)

    # Vérifie si la réponse est un succès (statut APDU 0x9000)
    if hresult == SCARD_S_SUCCESS and response[-2:] == [0x90, 0x00]:
        print("✅ Bip désactivé.")
    else:
        print("❌ Échec désactivation bip :", response)

    # Ferme proprement la connexion directe au lecteur
    SCardDisconnect(hcard, SCARD_LEAVE_CARD)

# Libère le contexte PC/SC
SCardReleaseContext(hcontext)

# Prépare une connexion standard pour la lecture des cartes NFC
reader = readers()[0]
connection = reader.createConnection()

# 🔁 Boucle infinie pour détecter les cartes et lire les UID
last_uid = None
while True:
    try:
        # Tente de se connecter à une carte présente sur le lecteur
        connection.connect()
    except NoCardException:
        # Si aucune carte n’est présente, attend un peu et réessaie
        time.sleep(0.5)
        continue

    # Commande APDU pour lire l’UID de la carte NFC (standard ISO 14443)
    get_uid_command = [0xFF, 0xCA, 0x00, 0x00, 0x00]

    # Envoie la commande à la carte
    data, sw1, sw2 = connection.transmit(get_uid_command)

    # Vérifie que la réponse est correcte (0x9000)
    if sw1 == 0x90 and sw2 == 0x00:
        # Formate l'UID en hexadécimal minuscule séparé par des ":"
        uid = ":".join(f"{b:02x}" for b in data)
        print(f"UID détecté : {uid}")

        # Copie l’UID dans le presse-papiers
        pyperclip.copy(uid)

        # Colle l’UID via Ctrl+V (plus fiable que pyautogui.write pour les claviers AZERTY)
        pyautogui.hotkey("ctrl", "v")

    else:
        print("Erreur de lecture UID.")

    # Attend que la carte soit retirée avant de continuer (évite doublons)
    while True:
        try:
            connection.connect()
            time.sleep(0.2)
        except NoCardException:
            # La carte a été retirée, retourne au début de la boucle
            break
