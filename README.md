# J.A.R.V.I.S 🤖

### Just A Rather Very Intelligent System — A personal AI Assistant for avenger level threats, calendar, emails and more

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 👇 Watch This First

[![Watch the tutorial](https://img.youtube.com/vi/Qav7NJIsKL4/maxresdefault.jpg)](https://www.youtube.com/watch?v=Qav7NJIsKL4&t=30s)

> ⚠️ **Please watch the video above before continuing.**

---

## 🎬 Project Demo

[![Watch the J.A.R.V.I.S Demo](https://img.shields.io/badge/Watch%20Demo-red?style=for-the-badge&logo=youtube)](YOUR_DEMO_LINK_HERE)

---

## 🧠 Overview

J.A.R.V.I.S is a personal, voice-enabled AI assistant, inspired by J.A.R.V.I.S from Iron Man. It combines a **React** frontend with a **Python/FastAPI** backend powered by **Pipecat** framework. You can spin it up locally with a single terminal alias, speak to it in real time, and have it manage your calendar, inbox, and (soon) send messages on your behalf via Twilio — all through natural conversation.

This is a living project. More tools and integrations are being added continuously.

---

## ✨ Features
- **ignition** - cool start up sequence mirroring iron man II
- **Voice conversation** — Real-time speech-to-text and text-to-speech that actually sounds like JARVIS
- **Gmail** — Read your inbox and send emails
- **Google Calendar** — Check availability and create calendar events
- **System shut-down** - cool shut down sequence when given command
- **contact book** store contacts and information messages and emails can be sent easily
- **SMS via Twilio** — *(coming soon, pending campaign approval)* Send text messages by voice command


---

## 🗂️ Repository Layout

| Path | Role |
|------|------|
| [`backend/`](backend/) | FastAPI app and Pipecat framework |
| [`frontend/`](frontend/) | React + Vite UI, WebRTC and audio hooks |
| [`ignition/`](ignition/) | Launch scripts and ElevenLabs audio downloader |

---

## ⚙️ Prerequisites

- **Python** — version pinned in [`backend/.python-version`](backend/.python-version)
- **Node.js** — current LTS
- **Google Cloud project** with Calendar and Gmail APIs enabled
- **OpenAI API key**
- **Deepgrame API key**
- **ElevenLabs API key**
- **Twilio account**

---
## 🚀 Getting Started

1. **Clone the repo**
```bash
   git clone https://github.com/javiermfriedman/J.A.R.V.I.S.git
   cd J.A.R.V.I.S
```

2. **Configure backend**
   See [backend/README](./backend/README.md)

3. **Install frontend dependencies**
```bash
   cd frontend
   npm install
```

4. **Set up your startup alias**

   From the root of the cloned repo, run:
```bash
   echo "alias jj=\"$(pwd)/backend/venv/bin/python $(pwd)/ignition/tony_stark.py\"" >> ~/.zshrc
   source ~/.zshrc
```

   Then open `ignition/tony_stark.py` and on **line 153** change `"Arc"` to your default browser:
```python
   # "safari" or "chrome"
   browser = "Arc"
```

5. **Launch J.A.R.V.I.S**
```bash
   jj
```
---

## 🐛 Known Issues

- **Google OAuth setup is finicky** — credentials must be configured precisely or the auth flow will fail silently. Follow the backend README carefully.
- **Windows is not supported** — developed and tested on macOS only. Path issues likely exist in the `ignition/` scripts.
- **Twilio SMS is not yet live** — pending campaign approval. The integration exists in code but is not active.

---

## 🤝 Contributing

This is a personal project but PRs are welcome. Please **open an issue before submitting a pull request** so we can align on the approach first. Keep changes focused and match the existing code style in each subproject.

---

## 📄 License

MIT © [Javier Friedman](https://github.com/javiermfriedman)