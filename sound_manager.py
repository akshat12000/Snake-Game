import pygame
import os
import numpy as np

class SoundManager:
    def __init__(self):
        """Initialize the sound system"""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.sounds_enabled = True
            self.sounds = {}
            self.load_sounds()
        except pygame.error:
            print("Sound system not available - running without audio")
            self.sounds_enabled = False
    
    def load_sounds(self):
        """Load all game sound effects"""
        if not self.sounds_enabled:
            return
        
        # Define sound files (we'll create simple beep sounds if files don't exist)
        sound_files = {
            'eat': 'eat.wav',
            'game_over': 'game_over.wav',
            'new_record': 'new_record.wav'
        }
        
        for sound_name, filename in sound_files.items():
            try:
                if os.path.exists(filename):
                    self.sounds[sound_name] = pygame.mixer.Sound(filename)
                else:
                    # Create simple beep sounds programmatically
                    self.sounds[sound_name] = self.create_beep_sound(sound_name)
            except pygame.error:
                print(f"Could not load sound: {filename}")
                self.sounds[sound_name] = None
    
    def create_beep_sound(self, sound_type):
        """Create simple beep sounds programmatically"""
        if not self.sounds_enabled:
            return None
        
        # Different frequencies for different sounds
        frequencies = {
            'eat': 800,      # Higher pitch for eating
            'game_over': 200, # Lower pitch for game over
            'new_record': 1000 # High pitch for celebration
        }
        
        frequency = frequencies.get(sound_type, 400)
        duration = 0.1 if sound_type == 'eat' else 0.3
        
        # Create a simple sine wave beep
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        # Create stereo array (2 channels)
        arr = np.zeros((frames, 2), dtype=np.float32)  # ✅ Make it 2D for stereo
        
        for i in range(frames):
            sample = np.sin(2 * np.pi * frequency * i / sample_rate)
            
            # Fade out to avoid clicks
            fade_frames = int(0.01 * sample_rate)
            if i >= frames - fade_frames:
                fade_factor = (frames - i) / fade_frames
                sample *= fade_factor
            
            # Apply same sample to both left and right channels
            arr[i, 0] = sample  # Left channel
            arr[i, 1] = sample  # Right channel
        
        # Convert to pygame sound
        arr = (arr * 32767).astype(np.int16)
        sound = pygame.sndarray.make_sound(arr)
        return sound
    
    def play_eat_sound(self):
        """Play sound when snake eats food"""
        self.play_sound('eat')
    
    def play_game_over_sound(self):
        """Play sound when game ends"""
        self.play_sound('game_over')
    
    def play_new_record_sound(self):
        """Play sound for new high score"""
        self.play_sound('new_record')
    
    def play_sound(self, sound_name):
        """Play a specific sound effect"""
        if self.sounds_enabled and sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except pygame.error:
                pass  # Ignore sound errors gracefully
    
    def set_volume(self, volume):
        """Set volume for all sounds (0.0 to 1.0)"""
        if self.sounds_enabled:
            for sound in self.sounds.values():
                if sound:
                    sound.set_volume(volume)
    
    def cleanup(self):
        """Clean up sound resources"""
        if self.sounds_enabled:
            pygame.mixer.quit()