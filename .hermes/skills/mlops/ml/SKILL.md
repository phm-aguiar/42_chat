---
name: ml
description: "Toolkit MLOps consolidado: 8 modos — hf-hub, llama-cpp, vllm, eval, wandb, audiocraft, sam, jupyter."
version: 1.0.0
author: 42_chat
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [mlops, ml, toolkit, huggingface, llama.cpp, vllm, evaluation, wandb, audiocraft, sam, jupyter]
    category: mlops
---

# ML Toolkit — MLOps Consolidado

Toolkit unificado para operações de machine learning. 8 modos cobrindo descoberta de modelos, inferência local, serving produção, avaliação, tracking, geração de áudio, segmentação de imagem e exploração interativa.

| Modo | Função | Instalação |
|------|--------|------------|
| [hf-hub](#modo-hf-hub) | Hub HF: busca, download, upload | `curl -LsSf https://hf.co/cli/install.sh \| bash -s` |
| [llama-cpp](#modo-llama-cpp) | Inferência local GGUF | `brew install llama.cpp` |
| [vllm](#modo-vllm) | Serving produção OpenAI API | `pip install vllm` |
| [eval](#modo-eval) | Benchmarking LLMs | `pip install lm-eval` |
| [wandb](#modo-wandb) | Tracking experimentos | `pip install wandb && wandb login` |
| [audiocraft](#modo-audiocraft) | Geração música/áudio | `pip install audiocraft` |
| [sam](#modo-sam) | Segmentação zero-shot | `pip install git+https://github.com/facebookresearch/segment-anything.git` |
| [jupyter](#modo-jupyter) | REPL Python stateful | `uv tool install jupyterlab` + hamelnb |

---

## Modo: hf-hub

**Gatilho:** Buscar modelos/datasets no HuggingFace Hub, baixar/upload arquivos, gerenciar repositórios, executar SQL em datasets.

### Fluxo

```bash
# Autenticação
hf auth login                          # ou export HF_TOKEN=...
hf auth whoami

# Download/Upload
hf download REPO_ID                    # baixar modelo
hf upload REPO_ID ./pasta              # upload single-commit
hf upload-large-folder REPO_ID ./pasta # uploads grandes com resume

# Busca
hf models list --search "llama 7b" --sort downloads
hf datasets list --search "imagenet"

# SQL em datasets (DuckDB)
hf datasets sql "SELECT COUNT(*) FROM parquet_url" --dataset REPO_ID

# Repositórios e cache
hf repos create --type model NOME
hf repos duplicate REPO_ID NEW_ID
hf cache prune                         # limpar revisões detached
```

### Pitfalls

- `huggingface-cli` está **deprecated** — usar sempre `hf`.
- Token: criar em [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
- `--format json` para output parseável. Uploads >5GB: `upload-large-folder`.

---

## Modo: llama-cpp

**Gatilho:** Rodar LLMs localmente em CPU, Apple Silicon, CUDA, ROCm. Escolher GGUF. Servidor OpenAI-compatible local.

### Fluxo

```bash
# Instalação
brew install llama.cpp               # macOS/Linux
# ou: git clone + cmake -B build && cmake --build build

# Rodar direto do Hub
llama-server -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0
llama-server --hf-repo REPO --hf-file modelo-q4_k_m.gguf -c 4096

# Descoberta de modelos (URL-first)
# 1. https://huggingface.co/models?apps=llama.cpp&sort=trending
# 2. https://huggingface.co/<repo>?local-app=llama.cpp
# 3. https://huggingface.co/api/models/<repo>/tree/main?recursive=true
```

**Python (llama-cpp-python):**
```python
# pip install llama-cpp-python
# CUDA: CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

from llama_cpp import Llama

llm = Llama.from_pretrained(
    repo_id="bartowski/Llama-3.2-3B-Instruct-GGUF",
    filename="*Q4_K_M.gguf", n_gpu_layers=35, n_ctx=4096
)

resp = llm.create_chat_completion(
    messages=[{"role": "user", "content": "O que é Python?"}], max_tokens=256
)
print(resp["choices"][0]["message"]["content"])
```

### Pitfalls

- Quant: `Q4_K_M` (chat), `Q5_K_M` (código), `Q6_K` (qualidade máxima).
- **Nunca normalizar labels**: Hub mostra `UD-Q4_K_M` → reportar `UD-Q4_K_M`.
- Tree API é fonte da verdade para `.gguf` existentes. Separar `mmproj-*.gguf` do modelo principal.
- Fallback: se local-app não visível no fetch → tree API + heurísticas.

---

## Modo: vllm

**Gatilho:** Deploy produção de APIs LLM (100+ req/s), endpoint OpenAI-compatible, quantização (AWQ/GPTQ/FP8).

### Fluxo

```bash
pip install vllm

# Servidor OpenAI-compatible
vllm serve meta-llama/Llama-3-8B-Instruct

# Query via OpenAI SDK
python -c "
from openai import OpenAI
client = OpenAI(base_url='http://localhost:8000/v1', api_key='EMPTY')
print(client.chat.completions.create(
    model='meta-llama/Llama-3-8B-Instruct',
    messages=[{'role': 'user', 'content': 'Olá!'}]
).choices[0].message.content)
"

# 7B-13B GPU única
vllm serve MODELO --gpu-memory-utilization 0.9 --max-model-len 8192

# 30B-70B com tensor parallelism + quantização
vllm serve MODELO --tensor-parallel-size 4 --gpu-memory-utilization 0.9 --quantization awq

# Produção com cache + métricas
vllm serve MODELO --enable-prefix-caching --enable-metrics --port 8000 --host 0.0.0.0
```

**Offline batch:**
```python
from vllm import LLM, SamplingParams
llm = LLM(model="meta-llama/Llama-3-8B-Instruct", tensor_parallel_size=2)
sampling = SamplingParams(temperature=0.7, max_tokens=512)
outputs = llm.generate(["prompt 1", "prompt 2"], sampling)
for out in outputs: print(out.outputs[0].text)
```

### Pitfalls

- **OOM**: `--gpu-memory-utilization 0.7` ou `--quantization awq`.
- **TTFT > 1s**: `--enable-prefix-caching --enable-chunked-prefill`.
- **Modelo customizado**: `--trust-remote-code`.
- **Baixa vazão**: `--max-num-seqs 512`. Tensor parallelism = GPUs potência de 2.
- **Hardware**: 7B → 1× A10 (24GB), 70B → 4× A100 (40GB) ou 2× A100 (80GB) com AWQ.

---

## Modo: eval

**Gatilho:** Benchmarking padronizado de LLMs (MMLU, GSM8K, HumanEval, HellaSwag, TruthfulQA), comparação entre modelos, tracking de treino.

### Fluxo

```bash
pip install lm-eval

# Avaliação padrão (HF)
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu,gsm8k,hellaswag,truthfulqa,arc_challenge \
  --num_fewshot 5 --batch_size auto --output_path resultados.json

# Com vLLM (5-10× mais rápido)
lm_eval --model vllm \
  --model_args pretrained=modelo,tensor_parallel_size=2,gpu_memory_utilization=0.8 \
  --tasks mmlu --batch_size auto

# Listar tarefas / subconjunto rápido
lm_eval --tasks list
lm_eval --model hf --model_args pretrained=modelo --tasks mmlu_stem
```

**Script de comparação** (carregar JSONs, extrair `acc`/`exact_match`, gerar tabela com pandas). Output típico:

```
| Modelo        | MMLU  | GSM8K | HELLASWAG |
|---------------|-------|-------|-----------|
| llama-2-7b    | 0.459 | 0.142 | 0.765     |
| mistral-7b    | 0.626 | 0.395 | 0.812     |
```

### Pitfalls

- `--num_fewshot 5` (padrão papers). Nome exato: `mmlu`, não `mmlu_direct`.
- **HumanEval**: requer `--allow_code_execution` + `pip install human-eval`.
- **OOM**: `--batch_size 1` ou `load_in_8bit=True`.
- **Lento**: backend vllm, `--num_fewshot 0`, ou subconjunto (`mmlu_stem`).
- MMLU completo ~2h (A100, 7B). HellaSwag ~10min. GSM8K ~5min.

---

## Modo: wandb

**Gatilho:** Tracking de experimentos ML, hyperparameter sweeps, versionamento de artefatos, colaboração em equipe.

### Fluxo

```bash
pip install wandb && wandb login     # ou export WANDB_API_KEY=...
```

**Tracking + Sweeps + Artefatos:**
```python
import wandb

# Tracking básico
run = wandb.init(project="meu-projeto", config={"lr": 0.001, "epochs": 10})
for epoch in range(wandb.config.epochs):
    wandb.log({"epoch": epoch, "loss": treinar()})
wandb.finish()

# Sweeps (bayes recomendado)
sweep_config = {
    "method": "bayes", "metric": {"name": "val/accuracy", "goal": "maximize"},
    "parameters": {
        "lr": {"distribution": "log_uniform", "min": 1e-5, "max": 1e-1},
        "batch_size": {"values": [16, 32, 64]}
    }
}
sweep_id = wandb.sweep(sweep_config, project="meu-projeto")
wandb.agent(sweep_id, function=treinar, count=50)

# Artefatos e Model Registry
artifact = wandb.Artifact("dataset", type="dataset")
artifact.add_file("data/train.csv")
wandb.log_artifact(artifact)

model_art = wandb.Artifact("modelo", type="model")
model_art.add_file("model.pth")
wandb.log_artifact(model_art, aliases=["best", "production"])
run.link_artifact(model_art, "model-registry/production-models")
```

**Integração HuggingFace:** `TrainingArguments(output_dir="./results", report_to="wandb")` → Trainer loga automaticamente.

### Pitfalls

- `wandb.init()` uma vez por run. Usar `tags=["baseline"]`, `group="resnet-exp"`.
- Offline: `export WANDB_MODE=offline` + `wandb sync <dir>` depois.
- Logar GPU util, memória, git commit. Nomes descritivos: `"bert-lr0.001-bs32-epoch10"`.

---

## Modo: audiocraft

**Gatilho:** Gerar música (MusicGen), efeitos sonoros (AudioGen), condicionamento por melodia/estilo.

### Fluxo

```bash
pip install audiocraft
```

**MusicGen (texto → música):**
```python
from audiocraft.models import MusicGen
import torchaudio

model = MusicGen.get_pretrained("facebook/musicgen-medium")
model.set_generation_params(duration=30, top_k=250, temperature=1.0, cfg_coef=3.0)
wav = model.generate(["epic orchestral soundtrack with strings and brass"])
torchaudio.save("musica.wav", wav[0].cpu(), sample_rate=32000)
```

**AudioGen (texto → som):**
```python
from audiocraft.models import AudioGen
model = AudioGen.get_pretrained("facebook/audiogen-medium")
model.set_generation_params(duration=5)
wav = model.generate(["thunderstorm with heavy rain and lightning"])
torchaudio.save("som.wav", wav[0].cpu(), sample_rate=16000)
```

**Variantes:** `musicgen-small` (300M, rápido), `musicgen-medium` (1.5B), `musicgen-large` (3.3B, melhor), `musicgen-melody` (texto+melodia), `musicgen-stereo-medium`, `musicgen-style` (transferência de estilo), `audiogen-medium`.

### Pitfalls

- **CUDA OOM**: usar `small`, reduzir `duration`, `model.half()`.
- **Qualidade**: aumentar `cfg_coef` (3.0-7.0), prompts descritivos.
- **Estéreo**: usar modelo `-stereo`. FP32 VRAM: small ~4GB, medium ~8GB, large ~16GB.
- Batch (1 chamada `generate` com múltiplos prompts) > loop.

---

## Modo: sam

**Gatilho:** Segmentar objetos em imagens sem treinamento (zero-shot), anotação com pontos/boxes, geração automática de máscaras.

### Fluxo

```bash
pip install git+https://github.com/facebookresearch/segment-anything.git
pip install opencv-python matplotlib

# Checkpoints: vit_b (375MB), vit_l (1.2GB), vit_h (2.4GB)
wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
```

**Segmentação interativa:**
```python
from segment_anything import sam_model_registry, SamPredictor
import cv2, numpy as np

sam = sam_model_registry["vit_h"](checkpoint="sam_vit_h_4b8939.pth").to("cuda")
predictor = SamPredictor(sam)
predictor.set_image(cv2.cvtColor(cv2.imread("foto.jpg"), cv2.COLOR_BGR2RGB))

# Ponto: [x,y], label 1=foreground 0=background
masks, scores, _ = predictor.predict(
    point_coords=np.array([[500, 375]]), point_labels=np.array([1]),
    multimask_output=True
)
best = masks[np.argmax(scores)]

# Box: [x1,y1,x2,y2]
masks, _, _ = predictor.predict(box=np.array([100, 100, 500, 400]))

# Combinado (ponto + box + máscara anterior para refinar)
masks, _, _ = predictor.predict(
    point_coords=np.array([[300, 200]]), point_labels=np.array([1]),
    box=np.array([100, 100, 500, 400]),
    mask_input=logits  # refinar predição anterior
)
```

**Geração automática:**
```python
from segment_anything import SamAutomaticMaskGenerator
gen = SamAutomaticMaskGenerator(model=sam, points_per_side=32,
    pred_iou_thresh=0.88, stability_score_thresh=0.95, min_mask_region_area=100)
masks = gen.generate(image)
# masks[i] = {"segmentation", "bbox", "area", "predicted_iou", "stability_score"}
```

### Pitfalls

- **OOM**: `vit_b` (375MB), `sam.half()`, reduzir resolução.
- **Lento**: `vit_b` 6× mais rápido que `vit_h`, `points_per_side=16`.
- **Máscaras ruins**: box + pontos combinados, adicionar pontos background (label=0).
- **Objetos pequenos**: aumentar `points_per_side`, reduzir `min_mask_region_area`.
- Apenas 1 `set_image()` necessário — embeddings reutilizados.

---

## Modo: jupyter

**Gatilho:** Exploração iterativa com estado persistente, inspeção de DataFrames, prototipagem rápida de ML.

### Fluxo

```bash
# Setup único
uv tool install jupyterlab
git clone https://github.com/hamelsmu/hamelnb.git ~/.agent-skills/hamelnb

SCRIPT="$HOME/.agent-skills/hamelnb/skills/jupyter-live-kernel/scripts/jupyter_live_kernel.py"

# Iniciar JupyterLab (se não estiver rodando)
uv run "$SCRIPT" servers --compact
jupyter-lab --no-browser --port=8888 --notebook-dir=$HOME/notebooks \
  --IdentityProvider.token='' --ServerApp.password='' > /tmp/jupyter.log 2>&1 &
sleep 3

# Criar sessão
mkdir -p ~/notebooks
curl -s -X POST http://127.0.0.1:8888/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"path":"scratch.ipynb","type":"notebook","name":"scratch.ipynb","kernel":{"name":"python3"}}'
```

**Execução (estado persiste entre chamadas):**
```bash
uv run "$SCRIPT" execute --path scratch.ipynb --code 'import pandas as pd' --compact
uv run "$SCRIPT" execute --path scratch.ipynb --code 'df = pd.DataFrame({"a":[1,2,3]})' --compact
uv run "$SCRIPT" execute --path scratch.ipynb --code 'print(df.describe())' --compact

# Multilinha
uv run "$SCRIPT" execute --path scratch.ipynb --code $'import numpy as np\nprint(np.random.randn(100).mean())' --compact

# Inspecionar variáveis
uv run "$SCRIPT" variables --path scratch.ipynb list --compact
uv run "$SCRIPT" variables --path scratch.ipynb preview --name df --compact

# Editar células
uv run "$SCRIPT" contents --path scratch.ipynb --compact
uv run "$SCRIPT" edit --path scratch.ipynb insert --at-index 2 --cell-type code --source 'print("nova")' --compact

# Verificação limpa (restart + run all)
uv run "$SCRIPT" restart-run-all --path scratch.ipynb --save-outputs --compact
```

### Pitfalls

- **Primeira execução pode timeout**: kernel inicializando. Retentar.
- **Pacotes**: instalar no ambiente do JupyterLab (`uv tool install jupyterlab`).
- **Sempre usar `--compact`**. Ordem: `--path` antes do subcomando.
- **Sem sessão**: criar via REST API. **Timeout**: `--timeout 120`.

---

## Recursos

- HF Hub: https://huggingface.co/docs/hub
- llama.cpp: https://github.com/ggml-org/llama.cpp
- vLLM: https://docs.vllm.ai
- lm-eval: https://github.com/EleutherAI/lm-evaluation-harness
- W&B: https://docs.wandb.ai
- AudioCraft: https://github.com/facebookresearch/audiocraft
- SAM: https://github.com/facebookresearch/segment-anything
- hamelnb: https://github.com/hamelsmu/hamelnb
