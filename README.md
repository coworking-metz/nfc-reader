# NFC UID Auto Typer for ACR122U Readers

This Python script listens for NFC cards using an ACR122U USB reader and **automatically types the UID** into the currently focused text field on Windows.

It also **disables the default beep** of the reader to provide a silent, background-friendly experience.

---

## 🧩 Features

* ✅ Reads the UID from NFC/RFID cards (MIFARE / ISO 14443-A/B).
* 🎹 Simulates keyboard input to type the UID wherever your text cursor is.
* 🔇 Disables the reader's default beep via low-level command.
* 🔁 Loops indefinitely to support multiple cards.
* 💻 Fully compatible with **Windows and French AZERTY keyboards**.
* 🔐 UID output is formatted as lowercased hex, colon-separated (e.g. `b6:8d:d3:8c`).

---

## 🖥️ Compatible NFC Readers

This script is built specifically for the **[ACS ACR122U-A9 USB NFC reader](https://www.acs.com.hk/en/products/150/acr122u-usb-nfc-reader/)**.

Other PC/SC-compatible readers *may* work but are **not guaranteed**, especially for beep deactivation.

---

## ⚙️ Requirements

* Python 3.10+ (tested on Windows)
* An ACR122U reader connected via USB
* One or more NFC/RFID cards or tags (ISO 14443-A/B)

---

## 📦 Dependencies

Install the following Python libraries before running:

```bash
pip install pyscard pyautogui pyperclip
```
