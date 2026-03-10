from transformers import GPT2ForSequenceClassification, AutoTokenizer
import os

print("Loading model...")
model = GPT2ForSequenceClassification.from_pretrained("./emotion_detector_vellichor")
tokenizer = AutoTokenizer.from_pretrained("./emotion_detector_vellichor")

os.makedirs("./upload_model", exist_ok=True)
model.save_pretrained("./upload_model")
tokenizer.save_pretrained("./upload_model")

print("Files to upload:")
for f in sorted(os.listdir("./upload_model")):
    size = os.path.getsize(f"./upload_model/{f}")
    print(f"  {f}: {size/1024/1024:.1f}MB" if size > 1024*1024 else f"  {f}: {size/1024:.1f}KB")
print("Done!")
