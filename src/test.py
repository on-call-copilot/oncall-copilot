import subprocess
import comet

prompt = "What is the meaning of life?"
model_name = "olla-m3-8b"
output_file = "output.txt"

subprocess.run([
    "comet",
    "--input", prompt,
    "--model-name", model_name,
    "--output-file", output_file,
], check=True)