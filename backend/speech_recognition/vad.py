import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    trust_repo=True
)
model = model.to(device)

(get_speech_timestamps,
 save_audio,
 read_audio,
 VADIterator,
 collect_chunks) = utils


def detect_speech(audio, sr=16000):

    audio_tensor = torch.tensor(audio).to(device)

    timestamps = get_speech_timestamps(
        audio_tensor,
        model,
        sampling_rate=sr
    )

    return timestamps