from llama_cpp import Llama
import os
class LlamaModel:
  def __init__(self, model_path, n_ctx=512):
    """
    Initializes the Llama model.
    Args:
    model_path (str): The path to the LLaMA model file.
    n_ctx (int): The context size.
    """
    if not os.path.exists(model_path):
      raise FileNotFoundError(f"Model file not found at: {model_path}")
    try:
      self.llm = Llama(model_path=model_path, n_ctx=n_ctx)
      print(f"LLaMA model loaded successfully from {model_path}")
    except Exception as e:
      raise RuntimeError(f"Failed to load LLaMA model: {e}")
  def generate_text(self, prompt, max_tokens=100, temperature=0.7):
    """
    Generates text using the loaded Llama model.
    Args:
    prompt (str): The input prompt for text generation.
    max_tokens (int): The maximum number of tokens to generate.
    temperature (float): The sampling temperature.
    Returns:
    str: The generated text.
    """
    try:
      #output = self.llm(prompt, max_tokens=max_tokens,temperature=temperature)
      prompt_text="Rewrite the following text to be more engaging and informative: xin chào bạn, mình tên  là Mạnh"
      output = self.llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "You are a helpful assistant that rewrites text."},
            {"role": "user", "content": prompt_text}
        ],
		    # Specify output format to JSON
        response_format={
            "type": "json_object",
        })
      print(f"Raw output from LLaMA model: {output}")
      return output['choices'][0]["message"]['content']
    except Exception as e:
      raise RuntimeError(f"Failed to generate text: {e}")
# Example usage:
# Replace 'path/to/your/llama.gguf' with the actual path to your LLaMA model file.
# You would typically download this file from a source like Hugging Face.
# You might need to download a model first.
# For example, using a shell command to download from Hugging Face:
# Make sure to choose a compatible model file (e.g., .gguf format)
#!wget https://huggingface.co/TheBloke/Llama-2-7B-ChatGGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf -O llama-2-7b-chat.Q4_K_M.gguf
model_file_path = 'llama-2-7b-chat.Q4_K_M.gguf' # Replace with your downloaded model path
try:
  # Initialize the model
  llama_model = LlamaModel(model_file_path)
  # Generate text
  prompt_text = "Tuyệt vời! Xe 7 chỗ rất phù hợp cho gia đình hoặc nhóm bạn. Bạn có thể cho tôi biết thêm về ngân sách cũng như các yêu cầu cụ thể khác (ví dụ: loại xe muốn, thương hiệu, mục đích sử dụng) để tôi có thể tư vấn tốt hơn cho bạn?"
  generated_text = llama_model.generate_text(prompt_text, max_tokens=50)
  print("\nGenerated Text:")
  print(generated_text)
except FileNotFoundError as e:
  print(f"Error: {e}")
  print("Please ensure the model file exists at the specified path.")
except RuntimeError as e:
  print(f"Error during model operation: {e}")
except Exception as e:
  print(f"An unexpected error occurred: {e}")