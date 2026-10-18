"""Build the faculty presentation guide (HTML -> PDF via headless Microsoft Edge / Chrome).

    python docs/presentation/build_guide.py            # writes RAMEI-Presentation-Guide.pdf here

Numbers are read from docs/reports/data/*.json (M2) or quoted from the M0/M1 reports, so the
guide never drifts from the measured results. Screenshots live in docs/presentation/img/.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import figures as F

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DATA = REPO / "docs" / "reports" / "data"
OUT_HTML = HERE / "guide.html"
OUT_PDF = HERE / "RAMEI-Presentation-Guide.pdf"

cv = json.loads((DATA / "m2_cv_summary.json").read_text(encoding="utf-8"))
an = json.loads((DATA / "m2_analysis_e8.json").read_text(encoding="utf-8"))


def m(exp, scenario, key="macro_f1"):
    return cv[exp]["summary"][scenario][key]["mean"]


def sd(exp, scenario, key="macro_f1"):
    return cv[exp]["summary"][scenario][key]["std"]


E8 = "e8_rgcmt"
CLEAN = m(E8, "clean")
AUDIO_ONLY = m(E8, "clean", "branch_audio")
VISUAL_ONLY = m(E8, "clean", "branch_visual")
TEXT_ONLY = m(E8, "clean", "branch_text")
ECE = m(E8, "clean", "ece")
SEL = an["scenarios"]["clean"]

SCEN = [("clean", "Clean input"), ("audio_noise_10db", "Audio noise 10 dB"),
        ("noisy_room_0db", "Noisy room 0 dB"), ("visual_blur", "Face blurred"),
        ("visual_dark", "Face dark"), ("visual_occluded", "Face half hidden"),
        ("text_word_drop", "Half the words lost"), ("camera_off", "Camera off"),
        ("audio_missing", "Microphone off"), ("noisy_room_camera_off", "Noise + camera off")]


# ============================================================================ figures
def figs():
    f = {}
    f["concept"] = F.concept()
    f["arch"] = F.architecture()
    f["upload"] = F.upload_workflow()
    f["live"] = F.live_sequence()
    f["model"] = F.model_diagram()
    f["cv"] = F.cv_diagram()
    f["corrupt"] = F.corruption_diagram()
    f["milestones"] = F.milestones()
    f["leak"] = F.grouped(
        [("E0 thesis MLP", 0.550, 0.696), ("E1 repo 1D-CNN", 0.538, 0.750)],
        "Same models, same data — only the evaluation split differs (macro-F1)",
        ("New speakers (honest)", "Same speakers in train and test (leaky)"),
        colors=(F.BLUE, F.ORANGE), fmt="{:.2f}", note="RAVDESS, single split. The original ~70% "
        "claim only appears when the test speakers were also in training.")
    f["ravdess"] = F.hbars(
        [("Thesis baseline (MFCC + MLP)", 0.512, F.GRAY, 0.076),
         ("Repository 1D-CNN", 0.549, F.GRAY, 0.050),
         ("RAMEI voice branch (WavLM + LoRA)", 0.686, F.BLUE, 0.028)],
        "Voice only, unseen speakers — macro-F1 (RAVDESS, 6-fold cross-validation)",
        note="Bars show the mean; the thin line shows ± one standard deviation across folds.")
    f["fusion"] = F.hbars(
        [("Words only", TEXT_ONLY, F.GRAY, None), ("Voice only", AUDIO_ONLY, F.GRAY, None),
         ("Face only", VISUAL_ONLY, F.GRAY, None), ("Simple average of the three", m(E8, "clean", "e5_static"), F.GRAY, None),
         ("RAMEI fusion", CLEAN, F.BLUE, sd(E8, "clean"))],
        "All three signals, unseen speakers — macro-F1 (CREMA-D, 5-fold cross-validation)",
        note="Words score low here because every CREMA-D actor reads the same 12 neutral sentences.")
    f["robust"] = F.dumbbell(
        [(lab, m(E8, k), m("e10_clean_train", k)) for k, lab in SCEN],
        "Robustness: macro-F1 under damaged or missing signals",
        ("RAMEI (trained with damaged inputs)", "Same model trained on clean data only"),
        ref=(CLEAN * 0.9, "10% drop limit"), xmin=0.0, xmax=0.8,
        note="Values shown are RAMEI's scores. Every corruption stays within the 10% limit; "
        "a missing camera or microphone does not.")
    f["abstain"] = F.grouped(
        [(lab, an["scenarios"][k]["selective_accuracy"], an["scenarios"][k]["abstained_accuracy"])
         for k, lab in [("clean", "Clean input"), ("noisy_room_0db", "Noisy room"), ("visual_dark", "Face dark"),
                        ("camera_off", "Camera off"), ("noisy_room_camera_off", "Noise + camera off")]],
        "When RAMEI says “uncertain”, it is usually right to: accuracy of each group",
        ("Segments it labelled", "Segments it marked “uncertain”"), fmt="{:.0%}")
    f["fair"] = F.dumbbell(
        [(lab, an["scenarios"][k]["macro_f1_by_gender"]["female"], an["scenarios"][k]["macro_f1_by_gender"]["male"])
         for k, lab in [("clean", "Clean input"), ("noisy_room_0db", "Noisy room"), ("visual_dark", "Face dark"),
                        ("camera_off", "Camera off")]],
        "Fairness check: macro-F1 for female and male speakers",
        ("Female speakers", "Male speakers"), xmin=0.5, xmax=0.85,
        note="The gap is 5.1 points on clean input (target ≤ 5) and shrinks to 0.2 without the face.")
    return f


# ============================================================================ helpers
def tile(value, label, sub=""):
    return (f'<div class="tile"><div class="tv">{value}</div><div class="tl">{label}</div>'
            f'<div class="ts">{sub}</div></div>')


def shot(name, caption, cls=""):
    return (f'<figure class="shot {cls}"><img src="img/{name}.jpg" alt="{caption}"/>'
            f'<figcaption>{caption}</figcaption></figure>')


def fig(svg, caption=""):
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return f'<figure class="diagram">{svg}{cap}</figure>'


def say(text):
    return f'<div class="say"><span>Say</span>{text}</div>'


def table(head, rows, cls=""):
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


# ============================================================================ content
def pages(f):
    P = []

    # ---------------------------------------------------------------- cover
    P.append(f"""
<section class="page cover">
  <div class="brand"><div class="logo">∿</div><div><b>RAMEI</b><br/><span>Emotion Intelligence</span></div></div>
  <h1>Reliability-Aware Adaptive<br/>Multimodal Emotion Intelligence</h1>
  <p class="lead">Recognising how people feel from <b>voice</b>, <b>words</b> and <b>face</b> together —
  and knowing when not to trust a signal.</p>
  <div class="cover-fig">{f['concept']}</div>
  <div class="cover-meta">
    <div><span>Document</span>Project presentation guide for the faculty review</div>
    <div><span>Project</span>AD-INFOCOMM internship</div>
    <div><span>Presented by</span>[Student name] · [Roll number]</div>
    <div><span>Guide</span>[Guide name]</div>
  </div>
</section>""")

    # ---------------------------------------------------------------- contents
    toc = [("1", "The project at a glance", "One-page summary to open with"),
           ("2", "The problem we started from", "The baseline and why its 70% was misleading"),
           ("3", "Our idea", "Three signals, a reliability check, and honest output"),
           ("4", "System architecture", "How the pieces fit together"),
           ("5", "How an analysis works", "Upload workflow and live mode"),
           ("6", "The AI model inside", "Fusion model and how it was trained"),
           ("7", "How we evaluated it", "Datasets and speaker-independent testing"),
           ("8", "Results", "Accuracy, robustness, calibration, fairness"),
           ("9", "What we learned — honestly", "Findings and limitations"),
           ("10", "The application", "Screens you will show in the demo"),
           ("11", "Engineering quality", "Tests, security, Docker, milestones"),
           ("12", "Presentation script", "A 12-minute talk, slide by slide"),
           ("13", "Live demo runbook", "Exact steps and a backup plan"),
           ("14", "Questions faculty may ask", "With short, accurate answers"),
           ("15", "Glossary", "Technical terms in plain words")]
    rows = "".join(f'<div class="toc-row"><span class="n">{n}</span><span class="tt">{t}</span>'
                   f'<span class="td">{d}</span></div>' for n, t, d in toc)
    P.append(f"""
<section class="page">
  <h2 class="plain">Contents</h2>
  <div class="toc">{rows}</div>
  <div class="note"><b>How to use this guide.</b> Sections 1–11 explain the project; read them once so you can
  answer any question. Sections 12–14 are your preparation: the talk you will give, the demo you will run,
  and the questions you should expect. Every number in this guide comes from the project's measured results.</div>
</section>""")

    # ---------------------------------------------------------------- 1 at a glance
    P.append(f"""
<section class="page">
  <h2><span>1</span>The project at a glance</h2>
  <p class="lead">RAMEI is an emotion-recognition system and web platform. It listens to the voice, reads the
  words and watches the face, checks how trustworthy each signal is at every moment, and combines them into one
  emotion with an honest confidence — or says “uncertain” instead of guessing.</p>
  <div class="tiles">
    {tile(f"{CLEAN:.3f}", "Macro-F1, all three signals", "unseen speakers (CREMA-D)")}
    {tile(f"+{(CLEAN - AUDIO_ONLY) * 100:.1f}", "points over voice alone", "same speakers, same test")}
    {tile(f"{ECE:.3f}", "Calibration error (ECE)", "target ≤ 0.05 — met")}
    {tile("≤ 10%", "Drop under every corruption", "noise · blur · dark · occlusion")}
  </div>
  <div class="cols">
    <div>
      <h3>The problem</h3>
      <p>The starting point was a voice-only emotion recogniser that claimed about 70% accuracy. Tested fairly —
      on speakers it had never heard — it scored only <b>0.51</b>. It also failed whenever the voice was noisy and
      gave no sign of when it was wrong.</p>
      <h3>What we built</h3>
      <ul>
        <li>Three AI branches: <b>voice</b> (WavLM), <b>words</b> (Whisper + DeBERTa), <b>face</b> (ViT).</li>
        <li>A <b>reliability score</b> for each signal, from measurable quality cues.</li>
        <li>A <b>fusion model</b> trained to keep working with damaged or missing signals.</li>
        <li><b>Calibrated confidence</b>, an “uncertain” option, and plain-language reasons.</li>
        <li>A full <b>web platform</b>: upload, live camera + microphone, reports, alerts, export.</li>
      </ul>
    </div>
    <div>
      <h3>Technology</h3>
      {table(["Layer", "Tools"], [
        ["AI models", "PyTorch · WavLM · Whisper · DeBERTa-v3 · ViT · MediaPipe"],
        ["Backend", "Python · FastAPI · WebSocket · SQLAlchemy"],
        ["Frontend", "React · TypeScript · Vite · Tailwind"],
        ["Data", "RAVDESS · CREMA-D (91 actors) · MELD"],
        ["Delivery", "Docker · nginx · GitHub Actions CI"],
      ], "compact")}
      <h3>Status</h3>
      <p>All six milestones (M0–M5) are complete. The application runs end to end, in development and in Docker,
      with 64 automated tests passing on every change.</p>
    </div>
  </div>
</section>""")

    # ---------------------------------------------------------------- 2 problem
    P.append(f"""
<section class="page">
  <h2><span>2</span>The problem we started from</h2>
  <p>The internship began from two audio-only projects: a 2021 thesis (MFCC features + MLP) and an open-source
  1D-CNN that reported ~70% accuracy. Before improving anything, we measured them honestly.</p>
  {fig(f['leak'])}
  <div class="callout"><b>Why the 70% was misleading.</b> Emotion datasets contain many clips from each actor.
  If the same actor appears in training and test data, the model can partly recognise the <i>person</i> instead
  of the <i>emotion</i>. This “speaker leakage” added 15–21 points. Every result in this project uses
  <b>speaker-independent</b> testing: the model is always tested on people it has never heard or seen.</div>
  <h3>Gaps in the baseline</h3>
  {table(["#", "Gap", "Consequence"], [
    ["G1", "Voice is the only signal", "Fails when the voice is unclear, flat or missing"],
    ["G2", "No idea of signal quality", "Confidently wrong on noisy or silent input"],
    ["G3", "Uncalibrated confidence", "A score of 90% does not mean 90% likely"],
    ["G4", "Breaks without inputs", "Nothing works if the mic or camera is off"],
    ["G5", "One label per file", "No timeline, no alerts, no insight"],
    ["G6", "Unclear evaluation", "Results do not transfer to new people"],
    ["G7", "Notebook code only", "Not usable by anyone"],
  ], "compact")}
</section>""")

    # ---------------------------------------------------------------- 3 idea
    P.append(f"""
<section class="page">
  <h2><span>3</span>Our idea</h2>
  <p class="lead">People show emotion through several channels at once. When one channel is unreliable — a noisy
  room, a dark camera, mumbled words — a person naturally relies on the others. RAMEI is built to do the same.</p>
  {fig(f['concept'], "Each signal is analysed separately, checked for quality, and combined into one decision.")}
  <div class="cols three">
    <div class="pill"><h4>1 · Measure quality</h4><p>Signal-to-noise ratio for the voice; speech-recognition
    confidence for the words; face visibility, blur and lighting for the face.</p></div>
    <div class="pill"><h4>2 · Combine robustly</h4><p>A fusion model trained on deliberately damaged and missing
    inputs, so a weak signal does not drag the decision down.</p></div>
    <div class="pill"><h4>3 · Be honest</h4><p>Confidence is calibrated; low-confidence segments are marked
    “uncertain”; every result comes with the reasons behind it.</p></div>
  </div>
  <h3>Before and after</h3>
  {table(["", "Original baseline", "RAMEI"], [
    ["Signals", "Voice only", "Voice + words + face"],
    ["Fair accuracy (unseen people)", "0.51 macro-F1 (RAVDESS)", f"{CLEAN:.3f} macro-F1 (CREMA-D)"],
    ["Noisy room", "Not handled", f"{m(E8, 'noisy_room_0db'):.3f} — only a 7% drop"],
    ["Confidence", "Uncalibrated (ECE 0.28)", f"Calibrated (ECE {ECE:.3f})"],
    ["When unsure", "Guesses anyway", "Says “uncertain”"],
    ["Explanations", "None", "Per-segment reasons"],
    ["Product", "Notebook", "Web platform with live analysis"],
  ], "compact")}
</section>""")

    # ---------------------------------------------------------------- 4 architecture
    P.append(f"""
<section class="page">
  <h2><span>4</span>System architecture</h2>
  <p>RAMEI has two halves that meet at one contract. An <b>offline ML pipeline</b> trains and evaluates the models and
  exports a versioned <b>model bundle</b>. The <b>online platform</b> loads that bundle and serves users.</p>
  {fig(f['arch'], "The browser talks to one address; nginx routes pages and the API, including the live WebSocket.")}
  <div class="cols">
    <div>
      <h3>Main components</h3>
      {table(["Component", "Responsibility"], [
        ["Dashboard (React)", "Upload, live analysis, session reports, system page"],
        ["API (FastAPI)", "Login, roles, sessions, uploads, export, alerts"],
        ["Live stream", "Receives audio and frames, returns results every 3 s"],
        ["Inference engine", "Runs the models, fusion, calibration, explanations"],
        ["Model bundle", "Weights + calibration + measured results, versioned"],
        ["Database", "Sessions, segments, alerts (no raw media by default)"],
      ], "compact")}
    </div>
    <div>
      <h3>Design decisions</h3>
      <ul>
        <li><b>One versioned bundle</b> — the platform never loads loose training files, so every result records
        exactly which model produced it.</li>
        <li><b>Same interfaces, simpler parts</b> — SQLite instead of PostgreSQL and in-process workers instead
        of a queue for the internship build (ADR-0008); both can be swapped without changing the API.</li>
        <li><b>Privacy by default</b> — consent before any capture; recordings deleted after analysis.</li>
        <li><b>Decisions are written down</b> — architecture decision records (ADRs) explain every major choice.</li>
      </ul>
    </div>
  </div>
</section>""")

    # ---------------------------------------------------------------- 5 workflows
    P.append(f"""
<section class="page">
  <h2><span>5</span>How an analysis works</h2>
  <h3>Upload mode — a recorded call or video</h3>
  {fig(f['upload'])}
  <h3>Live mode — camera and microphone in the browser</h3>
  {fig(f['live'])}
</section>""")

    # ---------------------------------------------------------------- 6 model
    P.append(f"""
<section class="page">
  <h2><span>6</span>The AI model inside</h2>
  <p>Large pretrained models turn each signal into numbers (“features”). RAMEI's own fusion model then learns how
  to combine them. Training the fusion model on stored features is what made a 4 GB laptop GPU sufficient.</p>
  {fig(f['model'], "Each branch makes its own guess; reliability scores and a transformer combine them; the result is calibrated.")}
  {fig(f['corrupt'])}
  <div class="cols">
    <div class="pill"><h4>Why “frozen” encoders?</h4><p>On 24 RAVDESS speakers, fine-tuning the voice encoder (LoRA)
    and keeping it frozen scored the same (0.686 vs 0.701, within noise). Frozen is cheaper and more stable, so the
    fusion model uses frozen features.</p></div>
    <div class="pill"><h4>How confidence is calibrated</h4><p>A single “temperature” is fitted on validation speakers
    so that, for example, 80% confidence really means about 80% correct. Below 0.45 the segment is “uncertain”.</p></div>
  </div>
</section>""")

    # ---------------------------------------------------------------- 7 evaluation
    P.append(f"""
<section class="page">
  <h2><span>7</span>How we evaluated it</h2>
  {table(["Dataset", "What it contains", "Used for"], [
    ["RAVDESS", "24 actors (12 F / 12 M), 1,440 acted speech clips", "Baselines and the voice branch"],
    ["CREMA-D", "91 actors, 7,442 clips with audio and video", "Face branch and the full fusion model"],
    ["MELD", "~13,000 lines of TV dialogue (Friends)", "The words branch (natural conversation)"],
  ], "compact")}
  {fig(f['cv'])}
  <h3>What we measure</h3>
  {table(["Metric", "In plain words"], [
    ["Macro-F1", "Accuracy that treats every emotion equally, so rare emotions count as much as common ones"],
    ["ECE (calibration error)", "How far stated confidence is from real accuracy — lower is better"],
    ["Relative drop", "How much the score falls when a signal is damaged or missing"],
    ["Selective accuracy", "Accuracy on the segments the model chose to label"],
    ["Per-gender F1", "Whether it works equally well for female and male speakers"],
  ], "compact")}
  <p class="small">CREMA-D has six emotions (no “surprise”), so its scores are over six classes. Comparisons within
  CREMA-D are like-for-like; comparisons with the seven-class RAVDESS numbers are indicative.</p>
</section>""")

    # ---------------------------------------------------------------- 8 results (1)
    P.append(f"""
<section class="page">
  <h2><span>8</span>Results</h2>
  <h3>Step 1 — a stronger voice model</h3>
  {fig(f['ravdess'])}
  <p>The WavLM voice branch alone improves the honest baseline by <b>+17 points</b>, which already meets the
  “baseline + 10 points” target.</p>
  <h3>Step 2 — combining voice, words and face</h3>
  {fig(f['fusion'])}
  <p>Fusion scores <b>{CLEAN:.3f}</b>: <b>+{(CLEAN - AUDIO_ONLY) * 100:.1f}</b> points above voice alone and
  <b>+{(CLEAN - VISUAL_ONLY) * 100:.1f}</b> above the best single signal (face), on the same unseen speakers.
  The learned fusion is also <b>+{(CLEAN - m(E8, 'clean', 'e5_static')) * 100:.1f}</b> points better than simply
  averaging the three.</p>
</section>""")

    # ---------------------------------------------------------------- 8 results (2)
    P.append(f"""
<section class="page">
  <h3>Step 3 — staying reliable when signals are damaged</h3>
  {fig(f['robust'])}
  <p>Every corruption — noise, blur, darkness, occlusion, lost words — keeps RAMEI within 10% of its clean score.
  The same model trained only on clean data collapses in a noisy room (0.38). With a whole signal missing, RAMEI
  falls back to roughly the level of the remaining signal: graceful, not catastrophic.</p>
  <h3>Step 4 — knowing when it does not know</h3>
  {fig(f['abstain'])}
  <p>On clean input RAMEI labels 96% of segments with <b>{SEL['selective_accuracy']:.0%}</b> accuracy; the 4% it
  marks “uncertain” are only {SEL['abstained_accuracy']:.0%} accurate — exactly the ones worth not trusting. As
  conditions worsen it abstains more (4% → 28% → 46%) instead of guessing.</p>
</section>""")

    # ---------------------------------------------------------------- 8 results (3)
    P.append(f"""
<section class="page">
  <h3>Step 5 — fairness</h3>
  {fig(f['fair'])}
  <h3>Requirement scorecard</h3>
  {table(["Target", "Requirement", "Result", ""], [
    ["NFR-03", "Fused score ≥ audio baseline + 10 points", f"+{(CLEAN - AUDIO_ONLY) * 100:.1f} points", '<b class="ok">Met</b>'],
    ["NFR-04", "≤ 10% drop with a degraded signal", "2–9% across all corruptions", '<b class="ok">Met</b>'],
    ["NFR-04", "≤ 10% drop with a missing signal", "20–23% (falls to one-signal level)", '<b class="no">Not met</b>'],
    ["NFR-05", "Calibration error ECE ≤ 0.05", f"{ECE:.3f} clean · 0.043–0.057 degraded", '<b class="ok">Met</b> (clean)'],
    ["NFR-09", "Gender gap ≤ 5 points", "5.1 clean · 0.2–3.9 degraded", '<b class="warn">Borderline</b>'],
    ["FR-14", "Abstain when uncertain", "37% vs 79% accuracy split", '<b class="ok">Met</b>'],
  ])}
  <h3>Speed</h3>
  {table(["Setting", "Measured"], [
    ["Analyse a 17-second three-signal video (laptop GPU, RTX 3050)", "4.2 s — about 4× faster than real time"],
    ["Same video inside Docker on CPU only", "14.3 s — still faster than real time"],
    ["Web API, 10 concurrent users", "105 requests/s, median 48 ms, 0 errors"],
  ], "compact")}
</section>""")

    # ---------------------------------------------------------------- 9 honest
    P.append(f"""
<section class="page">
  <h2><span>9</span>What we learned — honestly</h2>
  <p class="lead">Faculty value honesty over hype. These findings are reported exactly as measured.</p>
  <div class="cols">
    <div class="pill"><h4>Finding 1 · The reliability bias did not add accuracy</h4><p>We removed the reliability
    term from the fusion attention (experiment E9) and the score did not change (0.766 vs 0.769). The reliability
    <i>scores</i> still work — they fall when a signal is damaged — and they drive explanations, abstention and
    conflict detection.</p></div>
    <div class="pill"><h4>Finding 2 · Training on damaged data is what matters</h4><p>The same model trained only on
    clean data (E10) collapsed under noise: 0.38 vs 0.72 in a noisy room, 0.08 vs 0.46 with noise and no camera.
    Robustness came from <i>how</i> the model was trained.</p></div>
    <div class="pill"><h4>Finding 3 · The face dominates on acted data</h4><p>On CREMA-D the fusion gives the face about
    84% of the weight on average, because acted faces are frontal and well lit. On natural conversations the
    balance would differ — a reason to test on real recordings next.</p></div>
    <div class="pill"><h4>Finding 4 · Honest evaluation changes the story</h4><p>The baseline's 70% became 51% under a
    fair test. Every number in this project is speaker-independent and averaged over several rounds.</p></div>
  </div>
  <h3>Limitations</h3>
  <ul>
    <li><b>Acted datasets.</b> Actors read fixed sentences, so the words carry little emotion and real calls will
    differ. Licensed conversational data (IEMOCAP, MSP-Podcast) is the next step.</li>
    <li><b>A missing signal costs 20–23 points</b>, back to single-signal level; calibration also weakens then.</li>
    <li><b>Valence/arousal</b> (positive–negative, calm–excited) is estimated from class probabilities, not trained.</li>
    <li><b>Prototype deployment.</b> Runs on one machine (SQLite, CPU in Docker); production would add PostgreSQL,
    HTTPS and a GPU server.</li>
  </ul>
  <h3>Ethics</h3>
  <p>Emotion recognition is probabilistic and culturally variable. RAMEI must not be used for decisions about
  individuals (hiring, discipline, diagnosis) or for monitoring people without consent. The platform requires consent
  before every analysis, deletes recordings by default, abstains when unsure and explains every result.</p>
</section>""")

    # ---------------------------------------------------------------- 10 app
    P.append(f"""
<section class="page">
  <h2><span>10</span>The application</h2>
  {shot("02_overview", "Overview — sessions, emotion mix, signal reliability and recent alerts across the organisation.")}
  {shot("01_login", "Sign-in — accounts are created by an administrator; there is no public sign-up.", "half")}
</section>""")
    P.append(f"""
<section class="page">
  {shot("06_report_full", "Session report for a 48-second demo call: summary, emotion timeline (shaded = alert), signal reliability over time, colour-coded transcript, and the segment inspector with probabilities, per-signal reliability and weight, and the reasons. Alerts fired for sustained anger (33 s) and prolonged negative mood.", "tall")}
</section>""")
    P.append(f"""
<section class="page">
  <div class="shot-grid">
    {shot("04_upload", "Upload — any WAV, MP3, MP4 or WEBM up to 200 MB; consent is required.")}
    {shot("05_live", "Live analysis — microphone + camera or microphone only; results every 3 seconds.")}
    {shot("03_sessions", "Sessions — search and filter every analysis; export to CSV or JSON.")}
    {shot("07_system_full", "Model & system — the active model, its calibration and its measured robustness.")}
  </div>
</section>""")

    # ---------------------------------------------------------------- 11 engineering
    P.append(f"""
<section class="page">
  <h2><span>11</span>Engineering quality</h2>
  {fig(f['milestones'])}
  <div class="cols">
    <div>
      <h3>Quality and testing</h3>
      {table(["Area", "Evidence"], [
        ["Automated tests", "64 tests: 39 ML, 20 backend, 5 frontend"],
        ["Continuous integration", "GitHub Actions: lint, type-check, tests, build on every push"],
        ["End-to-end check", "Real video through API and dashboard, GPU and Docker"],
        ["Load test", "0 errors at 1, 10 and 50 concurrent users"],
        ["Documentation", "PRD, TRD, architecture, 2 ADRs, 3 milestone reports, final report"],
      ], "compact")}
    </div>
    <div>
      <h3>Security and privacy</h3>
      {table(["Control", "How"], [
        ["Login", "JWT tokens, Argon2 password hashing"],
        ["Access", "Agent / analyst / admin roles; organisations isolated"],
        ["Abuse", "Rate-limited login attempts"],
        ["Uploads", "Random file names, size cap, content validated"],
        ["Browser", "Strict content-security policy and security headers"],
        ["Privacy", "Consent per session; recordings deleted after analysis"],
      ], "compact")}
    </div>
  </div>
  <h3>Deployment</h3>
  <p>The whole platform runs with one command — <code>docker compose up</code> — as two containers (dashboard and
  API) behind nginx, with the database and model cache in persistent volumes. Building and running it in Docker
  found and fixed six deployment bugs that the developer setup had hidden.</p>
</section>""")

    # ---------------------------------------------------------------- 12 script
    script = [
        ("0:00", "Title", "Introduce yourself, the internship and the one-line idea: emotion from voice, words and face — that knows when not to trust a signal."),
        ("0:45", "The problem", "Baseline: voice only, claimed ~70%. Show the leakage chart: on new speakers it is 51%. Explain speaker leakage in one sentence."),
        ("2:00", "Our idea", "Show the concept diagram. Three signals, a quality check for each, one combined, honest answer."),
        ("3:00", "Architecture", "Offline pipeline produces a versioned model bundle; the platform serves it. Point to the browser, API, engine."),
        ("4:00", "How it works", "Walk the nine-step upload flow; mention live mode returns a result every 3 seconds."),
        ("5:00", "The model", "Branch heads, reliability scores, transformer, calibration. Mention training on damaged inputs."),
        ("6:00", "Evaluation", "Three datasets; every actor tested on a model that never saw them (cross-validation diagram)."),
        ("7:00", "Results", "0.51 → 0.69 (voice) → 0.769 (fusion). Robustness chart: within 10% under every corruption."),
        ("8:15", "Honesty", "Abstention: 79% vs 37%. Then the honest finding: robustness came from training, not the reliability bias."),
        ("9:15", "Live demo", "Run the demo (Section 13): show a report, the inspector, an alert, then live mode."),
        ("11:15", "Close", "Scorecard, limitations, next steps (real conversational data). Thank the faculty and invite questions."),
    ]
    rows = "".join(f'<tr><td class="time">{t}</td><td><b>{s}</b></td><td>{d}</td></tr>' for t, s, d in script)
    P.append(f"""
<section class="page">
  <h2><span>12</span>Presentation script — about 12 minutes</h2>
  <p>Use one slide per row. Each slide can reuse a figure from this guide. Speak to the faculty, not the screen;
  the “say” boxes are suggested phrasings, not text to read aloud.</p>
  <table class="script"><thead><tr><th>Time</th><th>Slide</th><th>What to cover</th></tr></thead><tbody>{rows}</tbody></table>
  {say("“The original model claimed 70%. When we tested it fairly — on people it had never heard — it scored 51%. That honest number is what we set out to beat.”")}
  {say("“RAMEI looks at three signals, checks how trustworthy each one is, and when it cannot be confident it says so instead of guessing.”")}
  {say(f"“On 91 actors it never saw during training, RAMEI scores {CLEAN:.2f}, almost 18 points above voice alone, and it stays within 10% when the audio is noisy or the face is dark.”")}
  {say("“We also report what did not work: removing the reliability term did not change accuracy. Robustness came from training on damaged inputs.”")}
</section>""")

    # ---------------------------------------------------------------- 13 demo
    P.append(f"""
<section class="page">
  <h2><span>13</span>Live demo runbook</h2>
  <div class="cols">
    <div>
      <h3>The day before</h3>
      <ol>
        <li>Record your own 20–40 second clip: face well lit, a clear emotion (for example annoyed, then calm).</li>
        <li>Create degraded copies: <code>python scripts/make_demo_clips.py my_clip.mp4</code></li>
        <li>Upload the clean, noisy and dark copies once, so the reports are ready.</li>
        <li>Charge and plug in the laptop; close other GPU apps; silence notifications.</li>
        <li>Rehearse the full talk once with a timer.</li>
      </ol>
      <h3>Thirty minutes before</h3>
      <ol>
        <li>Start the backend: <code>uvicorn app.main:app --port 8000</code> (in <code>backend/</code>).</li>
        <li>Start the dashboard: <code>npm run dev</code> (in <code>frontend/</code>) and open <code>localhost:5173</code>.</li>
        <li>Sign in, open one report so the models are loaded and warm.</li>
        <li>Allow camera and microphone for <code>localhost</code>; zoom the browser to 110–125%.</li>
      </ol>
    </div>
    <div>
      <h3>During the demo (about 2 minutes)</h3>
      <ol>
        <li><b>Overview</b> — point at the emotion mix, reliability and the alert list.</li>
        <li><b>Open the demo call report</b> — read the summary; show the timeline with the shaded anger alert.</li>
        <li><b>Click a segment</b> — show probabilities, each signal's reliability and weight, and the “why” lines.</li>
        <li><b>Compare clean vs noisy upload</b> — voice reliability falls, the reason says why, the emotion holds.</li>
        <li><b>Live analysis</b> — start with camera; speak for 15 seconds; cover the lens: the face becomes
        unavailable and voice + words carry the decision.</li>
        <li><b>Model &amp; system</b> — the measured robustness table, for anyone who asks “how do you know?”</li>
      </ol>
      <h3>Backup plan</h3>
      <ul>
        <li>If live capture fails, show the pre-computed reports — they prove the same points.</li>
        <li>If the laptop fails, use the screenshots in Section 10 of this guide.</li>
        <li>Docker alternative: <code>docker compose up -d</code>, then <code>localhost:8080</code> (CPU, slower).</li>
      </ul>
    </div>
  </div>
</section>""")

    # ---------------------------------------------------------------- 14 Q&A
    qa = [
        ("Why is your accuracy lower than the original 70%?", "Because we test on people the model has never seen. The 70% came from the same actors appearing in training and test; under a fair test the original scores 51%. Our 0.769 is on unseen speakers."),
        ("What is new compared to existing work?", "The combination: three signals, a measured reliability for each, a fusion model trained on damaged and missing inputs, calibrated confidence with an abstain option, explanations, and a working platform with live analysis — all evaluated speaker-independently."),
        ("Does the reliability module actually help?", "The reliability scores track damage correctly and drive explanations, abstention and conflict detection. But the reliability term inside the fusion did not add accuracy (ablation E9 equals E8). The robustness came from training with damaged inputs — we report this openly."),
        ("How do you handle a missing camera or microphone?", "Missing signals are masked out of the fusion, so the model uses whatever is available. The score falls to about the level of the remaining signal (0.59–0.61), rather than failing."),
        ("What does “uncertain” mean?", "The calibrated confidence is below 0.45. Those segments are only about 37% accurate, so refusing to label them is the right behaviour."),
        ("Why not train everything end to end?", "Our GPU has 4 GB. Fine-tuning the voice encoder matched the frozen encoder on 24 speakers, so frozen features were cheaper and equally good."),
        ("Is it biased?", f"We measured it: female {SEL['macro_f1_by_gender']['female']:.3f} vs male {SEL['macro_f1_by_gender']['male']:.3f} on clean input — a 5.1-point gap, just above our 5-point target, and almost zero when the face is removed. The face model is the likely source."),
        ("Will it work on real phone calls?", "Not proven yet. The data is acted. The next step is licensed conversational data such as IEMOCAP or MSP-Podcast."),
        ("How fast is it?", "About 4× faster than real time on the laptop GPU, and still faster than real time on CPU inside Docker. Live mode returns a result every 3 seconds."),
        ("What about privacy?", "Consent is required before any capture; recordings are deleted after analysis by default; only results are stored; accounts are created by an administrator."),
        ("Why these three datasets?", "RAVDESS for a fair comparison with the baseline, CREMA-D because it has video and 91 actors for strong speaker-independent testing, and MELD because it is natural dialogue for the text model."),
        ("How do you know the numbers are right?", "Five-fold cross-validation over 91 speakers, results stored as data files, an analysis script that reproduces the pooled score exactly, and CI running 64 tests on every change."),
        ("What would you do with more time?", "Test on conversational data, train a real valence/arousal head, fine-tune encoders end to end with more GPU memory, and move to PostgreSQL and GPU serving for production."),
        ("Could this be misused?", "Yes, which is why we state it must not be used for decisions about individuals or monitoring without consent, and why the system defaults to consent, deletion, abstention and explanation."),
    ]
    items = "".join(f'<div class="qa"><div class="q">{q}</div><div class="a">{a}</div></div>' for q, a in qa)
    P.append(f"""
<section class="page">
  <h2><span>14</span>Questions faculty may ask</h2>
  <div class="qa-grid">{items}</div>
</section>""")

    # ---------------------------------------------------------------- 15 glossary
    gl = [
        ("Multimodal", "Using more than one kind of input — here voice, words and face."),
        ("Modality / signal", "One input channel (voice, words or face)."),
        ("Encoder", "A large pretrained model that turns raw audio, text or images into numbers (features)."),
        ("Frozen", "An encoder used as-is, without retraining its weights."),
        ("LoRA", "A cheap way to fine-tune a large model by training a small number of extra weights."),
        ("Fusion", "Combining the three signals into one decision."),
        ("Reliability score", "RAMEI's estimate (0–1) of how trustworthy a signal is for a given segment."),
        ("Transformer / attention", "A neural network that decides how much each input should influence the output."),
        ("Macro-F1", "An accuracy measure that treats every emotion equally (1.0 = perfect)."),
        ("Calibration / ECE", "Whether stated confidence matches real accuracy; ECE is the average gap (0 = perfect)."),
        ("Temperature scaling", "A single learned number that adjusts confidence so it becomes calibrated."),
        ("Abstention", "Deliberately answering “uncertain” instead of guessing."),
        ("Speaker leakage", "When test speakers also appear in training, inflating results."),
        ("Cross-validation", "Repeating training and testing on different groups of people, then averaging."),
        ("Ablation", "Removing one part of the system to measure what it contributes."),
        ("SNR (dB)", "Signal-to-noise ratio: how loud speech is compared to background noise; 0 dB means equally loud."),
        ("ASR", "Automatic speech recognition — turning speech into text (Whisper)."),
        ("WebSocket", "A connection that keeps data flowing both ways in real time, used for live mode."),
        ("Docker", "Packaging the application with everything it needs, so it runs the same on any machine."),
    ]
    rows = "".join(f'<div class="gl"><b>{t}</b><span>{d}</span></div>' for t, d in gl)
    P.append(f"""
<section class="page">
  <h2><span>15</span>Glossary</h2>
  <div class="glossary">{rows}</div>
  <div class="note"><b>Where to find more.</b> Full details are in the repository: <code>docs/reports/Final-Report.md</code>
  (and the Word version), the milestone reports <code>M0</code>, <code>M1</code> and <code>M2</code>, the
  architecture document, and the decision records in <code>docs/adr/</code>.</div>
</section>""")
    return "\n".join(P)


CSS = """
@page { size: A4; margin: 16mm 15mm 16mm 15mm;
  @bottom-right { content: counter(page); font: 9pt 'Segoe UI', sans-serif; color: #94a3b8; }
  @bottom-left { content: 'RAMEI — Project presentation guide'; font: 9pt 'Segoe UI', sans-serif; color: #94a3b8; } }
@page :first { @bottom-right { content: none; } @bottom-left { content: none; } }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font-family: 'Segoe UI', Inter, Arial, sans-serif; color: #0f172a; font-size: 10.4pt; line-height: 1.5; background: #fff; }
.page { page-break-after: always; break-after: page; }
.page:last-child { page-break-after: auto; }
h1 { font-size: 27pt; line-height: 1.15; margin: 18mm 0 6mm; letter-spacing: -0.5px; }
h2 { font-size: 17pt; margin: 0 0 4mm; display: flex; align-items: center; gap: 10px; letter-spacing: -0.2px; }
h2 span { background: #0f766e; color: #fff; border-radius: 8px; font-size: 12pt; min-width: 30px; height: 30px; display: inline-flex; align-items: center; justify-content: center; }
h2.plain { margin-top: 2mm; }
h3 { font-size: 12pt; margin: 5mm 0 2mm; color: #134e4a; }
h4 { margin: 0 0 1.5mm; font-size: 10.5pt; color: #134e4a; }
p { margin: 0 0 2.5mm; }
.lead { font-size: 11.5pt; color: #334155; }
.small { font-size: 9pt; color: #64748b; }
ul, ol { margin: 0 0 3mm; padding-left: 5mm; } li { margin-bottom: 1mm; }
code { font-family: Consolas, monospace; font-size: 9pt; background: #f1f5f9; padding: 0.5px 4px; border-radius: 4px; }
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 7mm; }
.cols.three { grid-template-columns: 1fr 1fr 1fr; gap: 4mm; margin: 2mm 0 3mm; }
.cols .pill, .pill { background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #0f766e; border-radius: 8px; padding: 3mm 4mm; margin-bottom: 3mm; }
.pill p { margin: 0; font-size: 9.6pt; color: #334155; }
table { width: 100%; border-collapse: collapse; margin: 1mm 0 3mm; font-size: 9.5pt; }
th { text-align: left; background: #f1f5f9; color: #334155; font-weight: 600; padding: 2mm 2.5mm; border-bottom: 1px solid #cbd5e1; }
td { padding: 1.8mm 2.5mm; border-bottom: 1px solid #e2e8f0; vertical-align: top; }
table.compact td, table.compact th { padding: 1.4mm 2.2mm; }
.ok { color: #0f766e; } .no { color: #b91c1c; } .warn { color: #b45309; }
figure { margin: 2mm 0 4mm; break-inside: avoid; }
figure.diagram { border: 1px solid #e2e8f0; border-radius: 10px; padding: 4mm; background: #fff; }
figcaption { font-size: 9pt; color: #64748b; margin-top: 2mm; }
.shot img { width: 100%; border: 1px solid #cbd5e1; border-radius: 8px; display: block; }
.shot.half img { width: 70%; } .shot.half { text-align: left; }
.shot.tall img { width: 100%; max-height: 236mm; object-fit: contain; object-position: top; }
.shot-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 5mm; }
.shot-grid figure { margin: 0; }
.tiles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4mm; margin: 4mm 0 2mm; }
.tile { background: #0f766e; color: #fff; border-radius: 10px; padding: 4mm; }
.tile .tv { font-size: 20pt; font-weight: 700; line-height: 1.1; }
.tile .tl { font-size: 9.5pt; font-weight: 600; margin-top: 1.5mm; }
.tile .ts { font-size: 8.5pt; opacity: 0.85; }
.callout { background: #fff7ed; border: 1px solid #fed7aa; border-radius: 8px; padding: 3mm 4mm; margin: 2mm 0 3mm; }
.note { background: #f0fdfa; border: 1px solid #99d5cc; border-radius: 8px; padding: 3mm 4mm; margin-top: 6mm; color: #134e4a; }
.say { border-left: 4px solid #2a78d6; background: #eff6ff; border-radius: 6px; padding: 2.5mm 4mm; margin: 2.5mm 0; font-style: italic; color: #1e3a5f; }
.say span { font-style: normal; font-weight: 700; font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.6px; color: #2a78d6; margin-right: 3mm; }
table.script td.time { font-family: Consolas, monospace; color: #0f766e; white-space: nowrap; }
.qa-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 3mm 5mm; }
.qa { break-inside: avoid; border: 1px solid #e2e8f0; border-radius: 8px; padding: 2.5mm 3.5mm; }
.qa .q { font-weight: 600; color: #134e4a; margin-bottom: 1mm; font-size: 9.8pt; }
.qa .a { font-size: 9.2pt; color: #334155; }
.glossary { display: grid; grid-template-columns: 1fr 1fr; gap: 0 6mm; }
.gl { padding: 2mm 0; border-bottom: 1px solid #e2e8f0; break-inside: avoid; }
.gl b { display: block; color: #134e4a; } .gl span { font-size: 9.4pt; color: #334155; }
.toc { margin-top: 4mm; }
.toc-row { display: grid; grid-template-columns: 12mm 70mm 1fr; padding: 2.4mm 0; border-bottom: 1px solid #e2e8f0; align-items: baseline; }
.toc-row .n { color: #0f766e; font-weight: 700; } .toc-row .tt { font-weight: 600; } .toc-row .td { color: #64748b; font-size: 9.5pt; }
.cover .brand { display: flex; gap: 10px; align-items: center; margin-top: 4mm; }
.cover .logo { width: 40px; height: 40px; border-radius: 10px; background: #0f766e; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 700; }
.cover .brand span { color: #64748b; font-size: 9.5pt; }
.cover .lead { font-size: 13pt; max-width: 160mm; }
.cover-fig { margin: 10mm 0 8mm; border: 1px solid #e2e8f0; border-radius: 12px; padding: 5mm; }
.cover-meta { display: grid; grid-template-columns: 1fr 1fr; gap: 3mm 8mm; border-top: 2px solid #0f766e; padding-top: 5mm; }
.cover-meta div { font-size: 10.5pt; } .cover-meta span { display: block; font-size: 8.5pt; color: #64748b; text-transform: uppercase; letter-spacing: 0.6px; }
"""


def find_browser() -> str:
    for c in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              shutil.which("chromium") or "", shutil.which("google-chrome") or ""):
        if c and Path(c).exists():
            return c
    sys.exit("Need Microsoft Edge or Chrome to print the PDF.")


def main() -> None:
    html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"/><title>RAMEI — Presentation guide</title>'
            f"<style>{CSS}</style></head><body>{pages(figs())}</body></html>")
    OUT_HTML.write_text(html, encoding="utf-8")
    browser = find_browser()
    subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={OUT_PDF}", "--allow-file-access-from-files",
                    OUT_HTML.as_uri()], check=True, timeout=180)
    print(f"wrote {OUT_PDF} ({OUT_PDF.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
