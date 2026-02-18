# Hyperparameter Tuning for GPT-2 

## What This Is About

So for this experiment, I fine-tuned a **GPT-2** model on the **Wikitext-2** dataset and played around with different hyperparameters to see how they affect the model's performance. The whole point was to understand what happens when you change things like the learning rate, batch size, and number of epochs — and honestly, the results were very interesting (and a bit humbling ).

## Setup

- **Model:** GPT-2 (124M parameters) from Hugging Face
- **Dataset:** Wikitext-2 (raw) — Wikipedia articles used as a standard benchmark for language models
- **Framework:** PyTorch + Hugging Face Transformers
- **Hardware:** Google Colab (GPU — CUDA enabled)
- **Metric:** Perplexity (lower = better) and Eval Loss

### What is Perplexity?
Perplexity measures how "surprised" the model is when it sees new text. Think of it like this — if the model has a perplexity of 28, it's basically as confused as if it had to randomly pick from 28 equally likely next words. So **lower perplexity = the model is better at predicting what comes next**.

## Methodology

I used a scientific approach — **change only one variable at a time** so I can clearly see its effect. I started with a baseline (control) and then ran 6 experiments, each changing just one hyperparameter.

### The Baseline (Control)
My starting settings:
- Learning Rate: `5e-5`
- Batch Size: `8`
- Epochs: `3`
- Weight Decay: `0.01` (kept constant in all experiments)

### The Experiments

| Experiment | Learning Rate | Batch Size | Epochs | What Changed |
|---|---|---|---|---|
| **Baseline** | 5e-5 | 8 | 3 | Control (nothing changed) |
| **Exp A1** | 1e-5 | 8 | 3 | Low learning rate |
| **Exp A2** | 5e-4 | 8 | 3 | High learning rate |
| **Exp B1** | 5e-5 | 4 | 3 | Small batch size |
| **Exp B2** | 5e-5 | 16 | 3 | Large batch size |
| **Exp C1** | 5e-5 | 8 | 1 | Few epochs |
| **Exp C2** | 5e-5 | 8 | 5 | Many epochs |

## Results

### Summary Table

| Experiment | Eval Loss | Perplexity | Compared to Baseline |
|---|---|---|---|
| **Baseline** | 3.3522 | 28.56 | — |
| **Exp A1 (Low LR)** | 3.3543 | 28.63 | Barely different (+0.2%) |
| **Exp A2 (High LR)** | 3.9799 | 53.51 | Much worse (+87.4%) |
| **Exp B1 (Small Batch)** | 3.3697 | 29.07 | Slightly worse (+1.8%) |
| **Exp B2 (Large Batch)** | 3.3354 | 28.09 | Best result (-1.6%) |
| **Exp C1 (Few Epochs)** | 3.3431 | 28.31 | Slightly better (-0.9%) |
| **Exp C2 (Many Epochs)** | 3.4056 | 30.13 | Worse (+5.5%) |

### What I Learned From Each Experiment

#### Experiment A: Learning Rate
- **Low LR (1e-5):** Barely changed anything from the baseline. The model was learning too slowly to make a meaningful difference in just 3 epochs. It needed more time.
- **High LR (5e-4):** This was the worst result by far — perplexity shot up to 53.51! The training loss kept going down (2.21 by epoch 3) but the validation loss went UP (3.98). Classic **overfitting**. The model was learning the training data too aggressively and couldn't generalize.

**Takeaway:** Learning rate is the most sensitive hyperparameter. Too high and it destroys your model. Too low and it barely does anything.

#### Experiment B: Batch Size
- **Small Batch (4):** Slightly worse than baseline. More frequent but noisier updates.
- **Large Batch (16):** Actually gave the best result! Perplexity of 28.09 — slightly better than baseline. The smoother gradient updates helped.

**Takeaway:** Batch size had a moderate effect. Larger batches gave more stable training in this case.

#### Experiment C: Number of Epochs
- **1 Epoch:** Surprisingly close to the baseline (28.31 vs 28.56). The model learned most of what it needed in just one pass!
- **5 Epochs:** Worse than baseline (30.13). Training loss kept dropping (down to 2.72) but validation loss kept rising (up to 3.41). This is textbook **overfitting** — the model memorized the training data instead of learning general patterns.

**Takeaway:** More epochs ≠ better model. For fine-tuning GPT-2 on this dataset, 1-3 epochs seems to be the sweet spot. Beyond that, the model starts to overfit.

## Honest Thoughts

These results are honestly not great . The perplexity numbers are all quite high (28-53 range), and the differences between most experiments are pretty small. Here's what I think is going on:

1. **The dataset is small** — Wikitext-2 only has ~23,000 training examples after tokenization. GPT-2 has 124M parameters. That's a LOT of model for not much data.
2. **The tokenization approach** — Using fixed 128-token chunks with max_length padding means a lot of shorter sequences are padded with empty tokens, which wastes training signal.
3. **The base model is already pretty good** — GPT-2 was pretrained on a massive dataset, so fine-tuning it on a small subset of Wikipedia doesn't add much new knowledge.

## What's Next

I want to explore ways to improve these results:
- Try a better tokenization strategy (concatenate text and chunk properly instead of padding)
- Use a learning rate scheduler (warmup + decay)
- Try gradient accumulation to simulate larger batch sizes
- Maybe use a smaller model variant or a different/larger dataset

## Tools & Libraries Used

- Python 3.12
- PyTorch (with CUDA)
- Hugging Face Transformers
- Hugging Face Datasets
- Matplotlib & Pandas (for visualization)
