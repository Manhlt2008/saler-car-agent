import shutil
import sounddevice as sd
import torch
from scipy.io.wavfile import write
import numpy as np
import os
from transformers import VitsModel, AutoTokenizer
audio_folder = "audio"
folder = f"backend/{audio_folder}"
os.makedirs(folder, exist_ok=True)

model = VitsModel.from_pretrained("facebook/mms-tts-vie")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")

def empty_audio():
  for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.remove(file_path)  # remove file or symlink
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)  # remove folder and its contents
    except Exception as e:
        print(f'Failed to delete {file_path}. Reason: {e}')

def get_audio(text):
  inputs = tokenizer(text, return_tensors="pt")
  with torch.no_grad():
      output = model(**inputs).waveform

  # Convert waveform to numpy array
  waveform = output.squeeze().cpu().numpy()
  # sd.wait()  # Wait until playback is finished
  return waveform


def save_audio(waveform, id):
  file_name = get_file_name_by_id(id)
  path = os.path.join(folder, file_name)
  write(path, model.config.sampling_rate| 16000, waveform)


def request_audio(text, id):
  audio =  get_audio(text)
  save_audio(audio,id)

def get_file_name_by_id(id):
  return f"{id}.wav"
