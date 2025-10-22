from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def load_model(model_name: str = "mistralai/Mistral-7B-Instruct-v0.3"):
    print(f"Loading model: {model_name}")

    if torch.cuda.is_available():
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        device_map = "auto"
    else:
        dtype = torch.float32
        device_map = "mps"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype=dtype,
        device_map=device_map
    )
    model.eval()
    return tokenizer, model

