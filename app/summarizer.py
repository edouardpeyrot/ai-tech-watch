from transformers import pipeline

def build_summarizer(tokenizer, model):
    return pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=256,
        temperature=0.7,
        do_sample=True,
    )

def summarize(text: str, summarizer):
    prompt = f"Résume ce texte de manière claire et concise :\n\n{text}\n\nRésumé :"
    result = summarizer(prompt)
    return result[0]["generated_text"].split("Résumé :")[-1].strip()
