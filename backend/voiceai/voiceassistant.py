from ollama import chat 
import subprocess

while True:
    prompt = input("You: ")

    response = chat(
        model = 'qwen2.5:3B-instruct',
      
        messages=[
            {'role': 'user', 'content': prompt}
        ]
    )
    reply = response['message']['content']
    print("Assistant: ",reply)

    safe_reply = reply.replace("'", "''").replace("\n", " ").replace("\r", "")
    subprocess.run([
                "powershell", "-Command",
                f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{safe_reply}');"
                #   f'echo"{text}"| piper --model en-US-lessac-medium.onnx --output_raw | aplay -r 22050 -f S16_LE pt raw''
                #   shell = True
             ], creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000))