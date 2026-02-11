# Finetuning GPT Models

## What This Project Is About
As someone who's always been fascinated by how machines understand language... I decided to dive deep into Hugging Face Transformers and learn how to use and fine-tune pre-trained models. This notebook follows the Hugging Face LLM Course, and I got to explore so many cool things... from simple sentiment analysis to actually fine-tuning a BERT model on real data.

## Exploring Hugging Face Pipelines
The first thing I did was explore the `pipeline` API from Hugging Face... and honestly it felt like magic. With just a few lines of code, I could do things that would normally take hundreds of lines to build from scratch.

**Sentiment Analysis** — I started with sentiment analysis using DistilBERT... I passed in sentences like "I love reading" and "I hate self help books" and the model correctly classified them as POSITIVE and NEGATIVE with really high confidence scores (99%+). As a book lover this was fun to test.

**Zero-Shot Classification** — This one blew my mind... I gave the model a sentence like "I love playing pool" and candidate labels like sports, politics, and business... and without ever being trained on those specific categories, it correctly classified it as sports with 98.9% confidence.

**Text Generation** — I tested text generation with both GPT-2 and SmolLM2 (a smaller model from Hugging Face). I gave them the prompt "I love reading because" and they generated full paragraphs of text... some of it was surprisingly coherent and relatable.

**Mask Filling** — Using DistilRoBERTa, I gave the model a sentence with a missing word: "I love reading because it makes me \<mask\> alive." The model predicted "feel" with 94.8% confidence... which is exactly what I would have said.

**Named Entity Recognition (NER)** — I tested NER with my own sentence: "My name is Bernice and I work at Really Great Tech in Ghana." The model correctly identified Bernice as a person, Really Great Tech as an organization, and Ghana as a location... all with 99%+ confidence.

**Question Answering** — I gave the model a context about myself and asked "Where does I work?"... and it correctly answered "Really Great Tech in Ghana."

**Translation** — I tried translating French to English using the Helsinki-NLP/opus-mt-fr-en model... this one had some version compatibility issues but I worked through it using AutoTokenizer and AutoModelForSeq2SeqLM directly.

**Image Classification** — Using Google's ViT model, I classified an image of a cat... and the model predicted "lynx, catamount" with 43.3% confidence, followed by other cat-like animals.

**Automatic Speech Recognition** — I used OpenAI's Whisper large-v3 model to transcribe an audio clip of Martin Luther King Jr.'s famous "I Have a Dream" speech... and it correctly transcribed: "I have a dream that one day this nation will rise up and live out the true meaning of its creed."

## Bias and Limitations of Transformer Models
This part was really eye-opening... I used BERT's fill-mask pipeline with two sentences:
- "This man works as a [MASK]." → carpenter, lawyer, farmer, businessman, doctor
- "This woman works as a [MASK]." → nurse, maid, teacher, waitress, prostitute

The gender bias in the results was shocking... especially since BERT was trained on supposedly neutral data (Wikipedia and BookCorpus). It really shows that even "neutral" data carries societal biases and we need to be aware of this when using these models.

## Understanding Transformer Models Under the Hood
I didn't just use the pipelines... I also went deeper to understand how they work internally.

**Tokenization** — I learned how tokenizers break text into tokens, convert them to IDs, and decode them back. Using BERT's tokenizer, "Reading a nonfiction book is not fun" gets split into tokens like ['Reading', 'a', 'non', '##fiction', 'book', 'is', 'not', 'fun']... the ## prefix means that token is part of the previous word.

**Encoding and Decoding** — I explored how tokenizers add special tokens like [CLS] and [SEP], handle padding for batched inputs, and truncation for very long sentences.

**Attention Masks** — I learned how attention masks tell the model which tokens are real and which are just padding... this is important when you batch sentences of different lengths together.

**Going Through the Model** — I loaded DistilBERT manually and saw how raw inputs flow through the model... the output has a shape of [batch_size, sequence_length, hidden_size] (like [2, 18, 768]). Then I used the sequence classification version of the model and saw how it outputs logits, which get converted to probabilities using softmax.

## Fine-Tuning a Model
This was the big one... I actually fine-tuned a BERT model for paraphrase detection.

**Dataset** — I used the MRPC (Microsoft Research Paraphrase Corpus) dataset from the GLUE benchmark. It has 3,668 training examples, 408 validation examples, and 1,725 test examples. Each example has two sentences and a label indicating whether they're paraphrases of each other (equivalent or not_equivalent).

**Preprocessing** — I tokenized both sentences together using BERT's tokenizer with truncation enabled, and used dynamic padding with `DataCollatorWithPadding` to efficiently batch the data.

**Training** — I used the Hugging Face `Trainer` API with `TrainingArguments` to fine-tune `bert-base-uncased` for sequence classification with 2 labels. The training ran for 3 epochs on the MRPC training set.

**Evaluation** — After training, I used the model to make predictions on the validation set and evaluated performance using the GLUE MRPC metric (accuracy and F1 score).

## Tools and Libraries Used
- **Hugging Face Transformers** — for pipelines, models, tokenizers, and the Trainer API
- **Hugging Face Datasets** — for loading the MRPC dataset
- **PyTorch** — as the deep learning backend
- **Evaluate** — for computing evaluation metrics
- **Google Colab** — as the development environment

## What I Learned
This project taught me so much... I went from just knowing that AI models exist to actually understanding how they work under the hood. I learned that transformers are not just one thing... they can do sentiment analysis, translation, question answering, image classification, and speech recognition all with the same basic architecture. I also learned that fine-tuning a pre-trained model on your own data is not as scary as it sounds... Hugging Face makes it really accessible. But the biggest lesson was about bias... these models learn from human data, and that means they learn our biases too. That's something we always need to keep in mind.
