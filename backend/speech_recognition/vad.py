import torch

model, utils = torch.hub.load(
    repo = 'snaker4/silero-vad',
    model='silero-vad',
    trust_repo=True
)

(get_speech_timestamps,
_, _, _, _) = utils

def detect_speech(audio, sr=16000):

    audio_tensor = torch.tensor(audio)

    timestamps= get_speech_timestamps(
        audio_tensor,
        model,
        sampling_rate=sr
    )

    return timestamps
