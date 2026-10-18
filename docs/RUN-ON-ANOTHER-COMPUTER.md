# Run RAMEI on another computer

Use this to run RAMEI on a friend's laptop or a lab PC **without retraining** (training takes
about 6 hours and needs the datasets). You need two things:

1. **The code** — this GitHub repository.
2. **The trained model** — a 9 MB zip. Model weights are not stored on GitHub, so it is shared
   separately.

The large public AI models (WavLM, ViT, DeBERTa, Whisper, face detector — about 2 GB) download
automatically the first time a recording is analysed.

## Requirements

| | Minimum | Recommended |
|---|---|---|
| OS | Windows 10/11, macOS or Linux | — |
| Memory | 8 GB RAM | 16 GB RAM |
| Disk | 15 GB free | 20 GB free |
| Internet | Needed for the first analysis (~2 GB of models) | — |
| GPU | Not needed (CPU works) | NVIDIA GPU — about 3× faster |

On CPU, a 17-second video is analysed in about 14 s; on an RTX 3050 GPU, about 4 s.

## Step 0 — on the computer that has the trained model

```bash
python scripts/package_bundle.py
```

This writes `ramei-model-bundle.zip` (about 9 MB). Send it by USB, Drive or email.

## Step 1 — on the new computer: get the code and the model

```bash
git clone https://github.com/Pawanp-23/Emotion_Intelligence.git
cd Emotion_Intelligence
```

Extract `ramei-model-bundle.zip` into `ml/artifacts/bundles/`. This file must exist afterwards:

```
ml/artifacts/bundles/ramei-rgcmt-1.0.0/manifest.json
```

Then choose **Option A** (simplest) or **Option B** (faster with an NVIDIA GPU).

## Option A — Docker (simplest)

Install [Docker Desktop](https://www.docker.com/products/docker-desktop/), open it and wait for
"Engine running". Then, in the `Emotion_Intelligence` folder:

```bash
cp .env.example .env            # Windows Command Prompt: copy .env.example .env
```

Open `.env` and set `JWT_SECRET` to any random text of **32 or more characters**. Then:

```bash
docker compose up -d --build    # first build takes 15–20 minutes
docker compose exec api python -m app.cli create-user --email admin@ramei.local --role admin --password "ChooseAPassword1"
```

Open **http://localhost:8080** and sign in. Runs on CPU.

Stop with `docker compose down` (your data is kept); start again with `docker compose up -d`.

## Option B — without Docker

Needs **Python 3.11 or 3.12** and **Node.js 20+**.

```bash
cd ml
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate

# NVIDIA GPU:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu124
# No NVIDIA GPU (or macOS): use this instead
# pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

pip install -e ".[audio,multimodal]" -e "../backend[inference]"

cd ../backend
python -m app.cli create-user --email admin@ramei.local --role admin --password "ChooseAPassword1"
uvicorn app.main:app --port 8000          # keep this terminal open
```

In a second terminal:

```bash
cd Emotion_Intelligence/frontend
npm install
npm run dev
```

Open **http://localhost:5173** and sign in.

## Check that it works

Open http://localhost:8080/api/v1/health (Docker) or http://127.0.0.1:8000/api/v1/health
(Option B). You should see `"model_bundle_found": true`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `"model_bundle_found": false` / "Model bundle not found" | The zip was extracted one folder too deep or too shallow — check the `manifest.json` path above. |
| The first analysis takes several minutes | One-time download of the public models. Keep the internet on; later runs are fast. |
| Docker: "Set JWT_SECRET to a random value of 32+ characters" | Edit `JWT_SECRET` in `.env`, then `docker compose up -d` again. |
| Live mode: camera or microphone not working | Allow camera and microphone for `localhost` in the browser. |
| `pip` cannot find `torch` | Use Python 3.11 or 3.12 (64-bit) and the install line above. |
| Port already in use | Close the other program, or change `WEB_PORT` in `.env` (Docker). |

The new computer starts with an empty database — sessions and logins are not copied over.
