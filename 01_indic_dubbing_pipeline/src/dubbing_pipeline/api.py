"""FastAPI service for synchronous prototype jobs."""

from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse

from .config import ASR_BACKENDS, TRANSLATION_BACKENDS, TTS_BACKENDS, offline_mode_enabled
from .eval import evaluate_transcript
from .pipeline import DubbingPipeline
from .schemas import DubbingJobResult, DubbingRunRequest, EvaluationResult, TranscriptEvaluationRequest
from .utils import executable_available, package_available

app = FastAPI(title="Indic Dubbing Pipeline", version="0.1.0")
LIVE_OUTPUT_ROOT = Path("outputs/live").resolve()


def backend_status() -> dict[str, list[dict[str, object]]]:
    return {
        "asr": [
            {"name": name, "available": name == "stub" or package_available("faster_whisper" if name == "faster-whisper" else name)}
            for name in ASR_BACKENDS
        ],
        "translation": [{"name": name, "available": name == "stub" or package_available("transformers")} for name in TRANSLATION_BACKENDS],
        "tts": [{"name": name, "available": name == "stub" or executable_available("espeak-ng" if name == "espeak" else name)} for name in TTS_BACKENDS],
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "offline": str(offline_mode_enabled()).lower()}


@app.get("/backends")
def backends() -> dict[str, list[dict[str, object]]]:
    return backend_status()


@app.post("/evaluate/transcript", response_model=EvaluationResult)
def evaluate(request: TranscriptEvaluationRequest) -> EvaluationResult:
    return evaluate_transcript(request.reference, request.hypothesis)


@app.post("/dubbing/jobs/run", response_model=DubbingJobResult)
def run_job(request: DubbingRunRequest) -> DubbingJobResult:
    try:
        return DubbingPipeline().run(**request.model_dump())
    except (ValueError, FileNotFoundError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/dubbing/jobs/upload")
def upload_audio_job(
    audio: UploadFile = File(...),
    source_language: str = Form("hi-IN"),
    target_language: str = Form("en-IN"),
    asr_backend: str = Form("stub"),
    translation_backend: str = Form("indictrans2"),
    tts_backend: str = Form("espeak"),
    model_size: str = Form("tiny"),
    device: str = Form("cpu"),
    compute_type: str = Form("int8"),
) -> dict[str, object]:
    """Accept a browser/multipart recording and return a playable dubbed artifact."""
    allowed_suffixes = {".wav", ".mp3", ".m4a", ".ogg", ".webm", ".flac"}
    suffix = Path(audio.filename or "recording.webm").suffix.lower()
    if suffix not in allowed_suffixes:
        raise HTTPException(status_code=415, detail=f"Unsupported audio type: {suffix or 'missing extension'}")
    job_id = str(uuid4())
    output_dir = LIVE_OUTPUT_ROOT / job_id
    output_dir.mkdir(parents=True, exist_ok=False)
    input_path = output_dir / f"input{suffix}"
    try:
        with input_path.open("wb") as destination:
            shutil.copyfileobj(audio.file, destination)
        if input_path.stat().st_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded audio is empty")
        result = DubbingPipeline().run(
            audio_path=str(input_path), source_language=source_language, target_language=target_language,
            output_dir=output_dir, asr_backend=asr_backend, translation_backend=translation_backend,
            tts_backend=tts_backend, model_size=model_size, device=device, compute_type=compute_type,
        )
        return {"result": result.model_dump(mode="json"), "audio_url": f"/dubbing/jobs/{job_id}/audio"}
    except HTTPException:
        raise
    except (ValueError, FileNotFoundError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        audio.file.close()


@app.post("/dubbing/jobs/text")
def text_dubbing_job(
    text: str = Form(...),
    source_language: str = Form("hi-IN"),
    target_language: str = Form("en-IN"),
    translation_backend: str = Form("indictrans2"),
    tts_backend: str = Form("espeak"),
) -> dict[str, object]:
    """Run text through translation and TTS and expose the generated artifact."""
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty")
    job_id = str(uuid4())
    output_dir = LIVE_OUTPUT_ROOT / job_id
    try:
        result = DubbingPipeline().run(
            source_text=text, source_language=source_language, target_language=target_language,
            output_dir=output_dir, asr_backend="stub", translation_backend=translation_backend,
            tts_backend=tts_backend, model_size="tiny", device="cpu", compute_type="int8",
        )
        return {"result": result.model_dump(mode="json"), "audio_url": f"/dubbing/jobs/{job_id}/audio"}
    except (ValueError, FileNotFoundError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/dubbing/jobs/{job_id}/audio")
def get_dubbed_audio(job_id: str) -> FileResponse:
    if not job_id or any(char not in "0123456789abcdef-" for char in job_id.lower()):
        raise HTTPException(status_code=404, detail="Audio artifact not found")
    job_dir = (LIVE_OUTPUT_ROOT / job_id).resolve()
    if job_dir.parent != LIVE_OUTPUT_ROOT:
        raise HTTPException(status_code=404, detail="Audio artifact not found")
    candidates = [job_dir / "dubbed_audio.wav", job_dir / "dubbed_audio.placeholder.txt"]
    artifact = next((path for path in candidates if path.is_file()), None)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Audio artifact not found")
    media_type = "audio/wav" if artifact.suffix == ".wav" else "text/plain"
    return FileResponse(artifact, media_type=media_type, filename=artifact.name)


@app.get("/live", response_class=HTMLResponse)
def live_test_page() -> str:
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Local Dubbing Studio</title><style>
*{box-sizing:border-box}body{font-family:system-ui;max-width:920px;margin:2rem auto;padding:0 1rem;background:#0f172a;color:#e5e7eb}
.card{background:#1e293b;padding:1.25rem;border:1px solid #334155;border-radius:12px;margin:1rem 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:.75rem}
button,select,input,textarea{font:inherit;padding:.7rem;border-radius:7px;border:1px solid #475569}select,input,textarea{background:#0f172a;color:#e5e7eb;width:100%}
textarea{min-height:110px;resize:vertical}button{cursor:pointer;background:#2563eb;color:white;border:0;margin:.35rem .35rem .35rem 0}button:disabled{opacity:.5}
pre{white-space:pre-wrap;overflow:auto;max-height:420px;background:#080d1a;padding:1rem;border-radius:8px}label{display:block;margin:.35rem 0}audio{width:100%;margin-top:1rem}.recording{background:#dc2626}.muted{color:#94a3b8}.status{padding:.7rem 0;font-weight:600}
</style></head><body><h1>Local Indic Dubbing Studio</h1>
<p class="muted">Typed text, audio-file, and microphone inputs. Default processing is fully offline and uses stub adapters unless you explicitly select local model backends.</p>
<div class="card"><h2>Pipeline settings</h2><div class="grid">
<label>Source language<select id="source"><option>hi-IN</option><option>en-IN</option></select></label>
<label>Target language<select id="target"><option>en-IN</option><option>hi-IN</option></select></label>
<label>Translation<select id="translation"><option value="indictrans2" selected>IndicTrans2 (local cache only)</option><option value="identity">Identity (same language)</option><option value="stub">Stub / glossary-safe</option></select></label>
<label>Speech output<select id="tts"><option value="espeak" selected>eSpeak WAV</option><option value="stub">Placeholder</option></select></label></div></div>
<div class="card"><h2>1. Text input</h2><textarea id="textInput" placeholder="For hi-IN → en-IN, enter Hindi in Devanagari script...">नमस्ते, आज हम स्थानीय भाषण डबिंग प्रणाली का परीक्षण कर रहे हैं।</textarea>
<button id="textDub">Dub text</button></div>
<div class="card"><h2>2. Audio-file input</h2><input id="audioFile" type="file" accept="audio/*,.wav,.mp3,.m4a,.ogg,.webm,.flac">
<button id="fileDub">Upload and dub audio</button><p class="muted">Uses the stub ASR transcript by default. Select real ASR through the API only after pre-caching models locally.</p></div>
<div class="card"><h2>3. Microphone input</h2><button id="start">Start recording</button><button id="stop" disabled>Stop and dub</button></div>
<div class="card"><h2>Dubbed output</h2><div id="status" class="status">Ready</div><audio id="player" controls></audio><pre id="artifact"></pre><pre id="result">No result yet.</pre></div>
<script>
let recorder,chunks=[];const q=s=>document.querySelector(s),start=q('#start'),stop=q('#stop'),status=q('#status');
function alignTranslation(){if(q('#source').value===q('#target').value)q('#translation').value='identity';else if(q('#translation').value==='identity')q('#translation').value='indictrans2'}
q('#source').onchange=alignTranslation;q('#target').onchange=alignTranslation;
const setting=(id)=>q(id).value;function baseForm(){const f=new FormData();f.append('source_language',setting('#source'));f.append('target_language',setting('#target'));f.append('translation_backend',setting('#translation'));f.append('tts_backend',setting('#tts'));return f}
async function submit(url,form){status.textContent='Processing locally...';q('#player').removeAttribute('src');q('#artifact').textContent='';try{const response=await fetch(url,{method:'POST',body:form});const data=await response.json();if(!response.ok)throw new Error(data.detail||JSON.stringify(data));q('#result').textContent=JSON.stringify(data.result,null,2);if(data.result.tts.backend==='stub'){const artifact=await fetch(data.audio_url+'?t='+Date.now());q('#artifact').textContent=await artifact.text();status.textContent='Completed — placeholder artifact shown below.';}else{q('#player').src=data.audio_url+'?t='+Date.now();q('#player').load();status.textContent='Completed — press play.';}}catch(e){status.textContent='Failed: '+e.message;}}
function audioForm(file){const f=baseForm();f.append('audio',file);f.append('asr_backend','stub');f.append('model_size','tiny');f.append('device','cpu');f.append('compute_type','int8');return f}
q('#textDub').onclick=()=>{const text=q('#textInput').value.trim();if(!text){status.textContent='Enter text first.';return}const f=baseForm();f.append('text',text);submit('/dubbing/jobs/text',f)};
q('#fileDub').onclick=()=>{const file=q('#audioFile').files[0];if(!file){status.textContent='Choose an audio file first.';return}submit('/dubbing/jobs/upload',audioForm(file))};
start.onclick=async()=>{try{const stream=await navigator.mediaDevices.getUserMedia({audio:true});chunks=[];recorder=new MediaRecorder(stream);recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};recorder.onstop=()=>{stream.getTracks().forEach(t=>t.stop());const type=recorder.mimeType;const ext=type.includes('ogg')?'ogg':'webm';submit('/dubbing/jobs/upload',audioForm(new File([new Blob(chunks,{type})],'microphone.'+ext,{type})));start.disabled=false;stop.disabled=true;start.classList.remove('recording')};recorder.start();start.disabled=true;stop.disabled=false;start.classList.add('recording');status.textContent='Recording...';}catch(e){status.textContent='Microphone error: '+e.message;}};
stop.onclick=()=>{if(recorder&&recorder.state==='recording'){status.textContent='Finishing recording...';recorder.stop()}};
</script></body></html>"""
