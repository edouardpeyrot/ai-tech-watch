import yaml
from huggingface_hub import snapshot_download
from pathlib import Path

config = yaml.safe_load(open("configs/model.yaml"))
model_cfg = config["model"]

local_dir = Path(model_cfg["local_dir"])
local_dir.mkdir(parents=True, exist_ok=True)

print(f"Downloading {model_cfg['repo_id']} to {local_dir} ...")

snapshot_download(
    repo_id=model_cfg["repo_id"],
    local_dir=model_cfg["local_dir"],
    allow_patterns=model_cfg["allow_patterns"],
    local_dir_use_symlinks=False
)

