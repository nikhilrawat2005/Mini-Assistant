# utils/vad.py
import audioop
import logging

class EnergyVAD:
    """Energy-based Voice Activity Detector"""
    def __init__(self, aggressiveness=2, threshold=500):
        self.threshold = threshold * (aggressiveness + 1)  # Scale with aggressiveness
    
    def is_speech(self, frame_bytes: bytes, sample_rate: int) -> bool:
        """Detect speech based on audio energy"""
        try:
            if not frame_bytes:
                return False
            rms = audioop.rms(frame_bytes, 2)  # 16-bit samples
            return rms > self.threshold
        except Exception as e:
            logging.error(f"VAD error: {e}")
            return False

def get_vad(aggressiveness: int = 2):
    """Return EnergyVAD instance (no external dependencies)"""
    return EnergyVAD(aggressiveness)