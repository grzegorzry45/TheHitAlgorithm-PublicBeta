"""
Playlist Gatekeeper - Production-ready MIR system
Checks if a User Upload fits a Playlist Profile using Golden 8 parameters
with sklearn-based analysis and LLM prompt generation
"""

import librosa
import numpy as np
from typing import Dict, List, Optional, Tuple
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import warnings
warnings.filterwarnings('ignore')


class PlaylistGatekeeper:
    """
    Production-ready Playlist Compatibility Checker

    Golden 8 Parameters:
    1. BPM (Tempo)
    2. Beat Strength
    3. Onset Rate
    4. Energy (RMS)
    5. Danceability (Pulse Clarity via Tempogram)
    6. Spectral Rolloff
    7. Spectral Flatness
    8. Dynamic Range

    Uses sklearn for robust statistical comparison.
    """

    # Feature weights for weighted Z-score calculation
    FEATURE_WEIGHTS = {
        'beat_strength': 3.0,    # CRITICAL for genre vibe
        'onset_rate': 2.0,       # Important for density
        'bpm': 1.5,              # Important but allow half-time matches
        'energy': 1.5,           # Important
        'danceability': 2.0,     # Important for groove
        'spectral_rolloff': 1.0, # Moderate importance
        'spectral_flatness': 1.0,# Moderate importance
        'dynamic_range': 0.5     # Least important (mastering)
    }

    # Critical threshold for rhythm features
    CRITICAL_THRESHOLD = 2.0

    def __init__(self):
        """Initialize the Gatekeeper"""
        self.scaler = None
        self.playlist_features = None
        self.nn_model = None

    def extract_golden_8(self, file_path: str) -> Optional[Dict]:
        """
        Extract Golden 8 features from audio file
        Uses NATIVE sampling rate (sr=None)

        Args:
            file_path: Path to audio file

        Returns:
            Dictionary with Golden 8 features or None if error
        """
        try:
            # Load audio with NATIVE sampling rate
            y, sr = librosa.load(file_path, sr=None, mono=True)

            features = {}

            # 1. BPM (Tempo)
            features['bpm'] = self._extract_bpm(y, sr)

            # 2. Beat Strength (mean onset strength)
            features['beat_strength'] = self._extract_beat_strength(y, sr)

            # 3. Onset Rate (events per second)
            features['onset_rate'] = self._extract_onset_rate(y, sr)

            # 4. Energy (RMS mean)
            features['energy'] = self._extract_energy(y)

            # 5. Danceability (Pulse Clarity via Tempogram)
            features['danceability'] = self._extract_pulse_clarity(y, sr)

            # 6. Spectral Rolloff (mean)
            features['spectral_rolloff'] = self._extract_spectral_rolloff(y, sr)

            # 7. Spectral Flatness (mean)
            features['spectral_flatness'] = self._extract_spectral_flatness(y, sr)

            # 8. Dynamic Range (Peak - RMS in dB)
            features['dynamic_range'] = self._extract_dynamic_range(y)

            # Validate all values
            for key, value in features.items():
                if np.isnan(value) or np.isinf(value):
                    print(f"Warning: {key} returned invalid value ({value}), using 0.0")
                    features[key] = 0.0

            return features

        except Exception as e:
            print(f"Error extracting features from {file_path}: {e}")
            return None

    def _extract_bpm(self, y: np.ndarray, sr: int) -> float:
        """Extract BPM (Tempo)"""
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        return float(tempo)

    def _extract_beat_strength(self, y: np.ndarray, sr: int) -> float:
        """Extract Beat Strength (mean onset strength)"""
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        return float(np.mean(onset_env))

    def _extract_onset_rate(self, y: np.ndarray, sr: int) -> float:
        """
        Extract Onset Rate (events per second)
        Uses Rhythmic Density formula
        """
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        duration = librosa.get_duration(y=y, sr=sr)

        if duration > 0:
            return float(len(onset_frames) / duration)
        return 0.0

    def _extract_energy(self, y: np.ndarray) -> float:
        """Extract Energy (RMS mean)"""
        rms = librosa.feature.rms(y=y)
        return float(np.mean(rms))

    def _extract_pulse_clarity(self, y: np.ndarray, sr: int) -> float:
        """
        Extract Pulse Clarity (Danceability via Tempogram)

        Measures rhythmic regularity/stability without correlation to Beat Strength:
        1. Compute Tempogram
        2. Calculate ratio of highest peak to mean energy
        3. High ratio = Strong, clear, regular pulse (High Danceability)
        4. Low ratio = Chaotic or weak pulse (Low Danceability)
        """
        try:
            # Compute onset strength envelope
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)

            # Compute tempogram
            tempogram = librosa.feature.tempogram(onset_envelope=onset_env, sr=sr)

            # Calculate mean energy across all tempo bins and time frames
            mean_energy = np.mean(tempogram)

            # Find the highest peak in the tempogram
            max_peak = np.max(tempogram)

            # Calculate ratio (pulse clarity)
            if mean_energy > 0:
                pulse_clarity = max_peak / mean_energy
                # Normalize to 0-1 range (empirically, good values are 2-10)
                pulse_clarity_normalized = np.clip(pulse_clarity / 10.0, 0, 1)
                return float(pulse_clarity_normalized)

            return 0.0
        except:
            return 0.0

    def _extract_spectral_rolloff(self, y: np.ndarray, sr: int) -> float:
        """Extract Spectral Rolloff (mean)"""
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.85)
        return float(np.mean(rolloff))

    def _extract_spectral_flatness(self, y: np.ndarray, sr: int) -> float:
        """Extract Spectral Flatness (mean)"""
        flatness = librosa.feature.spectral_flatness(y=y)
        return float(np.mean(flatness))

    def _extract_dynamic_range(self, y: np.ndarray) -> float:
        """Extract Dynamic Range (Peak - RMS in dB)"""
        peak = np.max(np.abs(y))
        rms = np.sqrt(np.mean(y**2))

        if rms > 0 and peak > 0:
            dr = 20 * np.log10(peak / rms)
            return float(dr)
        return 0.0

    def fit_playlist(self, playlist_features: List[Dict]) -> bool:
        """
        Fit the model on playlist features

        Args:
            playlist_features: List of feature dicts from playlist tracks

        Returns:
            True if successful, False otherwise
        """
        if not playlist_features or len(playlist_features) < 2:
            print("Error: Need at least 2 tracks to fit playlist")
            return False

        try:
            # Store playlist features
            self.playlist_features = playlist_features

            # Convert to numpy array
            feature_matrix = self._features_to_matrix(playlist_features)

            # Fit StandardScaler on playlist
            self.scaler = StandardScaler()
            scaled_features = self.scaler.fit_transform(feature_matrix)

            # Fit NearestNeighbors (k=1 to find closest reference track)
            self.nn_model = NearestNeighbors(n_neighbors=1, metric='euclidean')
            self.nn_model.fit(scaled_features)

            return True

        except Exception as e:
            print(f"Error fitting playlist: {e}")
            return False

    def check_track(self, user_features: Dict) -> Dict:
        """
        Check if user track fits the playlist

        Args:
            user_features: Features dict from user track

        Returns:
            Complete analysis dict with LLM prompt
        """
        if self.scaler is None or self.nn_model is None:
            return {
                "error": "Playlist not fitted. Call fit_playlist() first."
            }

        try:
            # Convert user features to array
            user_array = self._feature_dict_to_array(user_features)
            user_scaled = self.scaler.transform(user_array.reshape(1, -1))

            # Find nearest reference track
            distances, indices = self.nn_model.kneighbors(user_scaled)
            nearest_idx = indices[0][0]
            nearest_ref = self.playlist_features[nearest_idx]

            # Calculate weighted Z-scores
            weighted_z_scores = self._calculate_weighted_z_scores(
                user_features, nearest_ref
            )

            # Identify critical alerts
            critical_alerts = self._identify_critical_alerts(weighted_z_scores)

            # Generate LLM prompt
            llm_prompt = self._generate_llm_prompt(
                user_features,
                nearest_ref,
                weighted_z_scores,
                critical_alerts
            )

            return {
                "user_features": user_features,
                "nearest_reference": nearest_ref,
                "weighted_z_scores": weighted_z_scores,
                "critical_alerts": critical_alerts,
                "llm_prompt": llm_prompt
            }

        except Exception as e:
            print(f"Error checking track: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": f"Failed to analyze track: {str(e)}"
            }

    def _features_to_matrix(self, features_list: List[Dict]) -> np.ndarray:
        """Convert list of feature dicts to numpy matrix"""
        matrix = []
        for features in features_list:
            row = self._feature_dict_to_array(features)
            matrix.append(row)
        return np.array(matrix)

    def _feature_dict_to_array(self, features: Dict) -> np.ndarray:
        """Convert feature dict to ordered numpy array (Golden 8 order)"""
        golden_8_order = [
            'bpm', 'beat_strength', 'onset_rate', 'energy',
            'danceability', 'spectral_rolloff', 'spectral_flatness', 'dynamic_range'
        ]
        return np.array([features[key] for key in golden_8_order])

    def _calculate_weighted_z_scores(
        self, user_features: Dict, ref_features: Dict
    ) -> Dict:
        """
        Calculate weighted Z-scores comparing user vs reference

        Z-Score = (user_value - ref_value) / std_dev * weight
        """
        # Calculate playlist std dev for each feature
        feature_matrix = self._features_to_matrix(self.playlist_features)
        stds = np.std(feature_matrix, axis=0)

        golden_8_order = [
            'bpm', 'beat_strength', 'onset_rate', 'energy',
            'danceability', 'spectral_rolloff', 'spectral_flatness', 'dynamic_range'
        ]

        weighted_z_scores = {}

        for i, feature_name in enumerate(golden_8_order):
            user_val = user_features[feature_name]
            ref_val = ref_features[feature_name]
            std_val = stds[i]
            weight = self.FEATURE_WEIGHTS[feature_name]

            # Calculate z-score
            if std_val > 0:
                z_score = (user_val - ref_val) / std_val
                weighted_z = z_score * weight
            else:
                z_score = 0.0
                weighted_z = 0.0

            weighted_z_scores[feature_name] = {
                'user_value': user_val,
                'ref_value': ref_val,
                'z_score': z_score,
                'weighted_z': weighted_z,
                'weight': weight
            }

        return weighted_z_scores

    def _identify_critical_alerts(self, weighted_z_scores: Dict) -> List[str]:
        """
        Identify CRITICAL ALERTS for rhythm features

        Critical if Weighted Z-Score > 2.0 for Beat Strength or Onset Rate
        """
        alerts = []

        # Check Beat Strength
        beat_z = abs(weighted_z_scores['beat_strength']['weighted_z'])
        if beat_z > self.CRITICAL_THRESHOLD:
            direction = "below" if weighted_z_scores['beat_strength']['weighted_z'] < 0 else "above"
            alerts.append(f"Beat Strength: {beat_z:.1f}σ {direction} reference (CRITICAL)")

        # Check Onset Rate
        onset_z = abs(weighted_z_scores['onset_rate']['weighted_z'])
        if onset_z > self.CRITICAL_THRESHOLD:
            direction = "below" if weighted_z_scores['onset_rate']['weighted_z'] < 0 else "above"
            alerts.append(f"Onset Rate: {onset_z:.1f}σ {direction} reference (CRITICAL)")

        # Add warnings for other high deviations
        for feature, data in weighted_z_scores.items():
            if feature not in ['beat_strength', 'onset_rate']:
                wz = abs(data['weighted_z'])
                if wz > 1.5:
                    direction = "below" if data['weighted_z'] < 0 else "above"
                    alerts.append(f"{feature.replace('_', ' ').title()}: {wz:.1f}σ {direction} reference (WARNING)")

        return alerts

    def _generate_llm_prompt(
        self,
        user_features: Dict,
        ref_features: Dict,
        weighted_z_scores: Dict,
        critical_alerts: List[str]
    ) -> str:
        """
        Generate LLM prompt for decision making

        Returns a complete prompt ready to copy-paste into ChatGPT/Claude
        """
        prompt = """You are an expert music industry A&R assistant specializing in playlist curation.

Your task: Analyze whether a submitted track fits a specific playlist profile.

CONTEXT:
The track has been analyzed against a playlist's sonic signature using the "Golden 8" audio parameters. Each parameter has been compared to the CLOSEST REFERENCE TRACK from the playlist (not the average, to handle multi-modal distributions like mixed tempos).

---

GOLDEN 8 COMPARISON (User Track vs Closest Reference):
"""

        # Add each parameter comparison
        golden_8_order = [
            'bpm', 'beat_strength', 'onset_rate', 'energy',
            'danceability', 'spectral_rolloff', 'spectral_flatness', 'dynamic_range'
        ]

        for feature in golden_8_order:
            data = weighted_z_scores[feature]
            user_val = data['user_value']
            ref_val = data['ref_value']
            weighted_z = data['weighted_z']
            weight = data['weight']

            feature_display = feature.replace('_', ' ').title()

            prompt += f"\n{feature_display}:\n"
            prompt += f"  User: {user_val:.2f}\n"
            prompt += f"  Reference: {ref_val:.2f}\n"
            prompt += f"  Weighted Z-Score: {weighted_z:.2f} (weight: {weight}x)\n"

        # Add critical alerts section
        if critical_alerts:
            prompt += "\n---\n\n⚠️ CRITICAL ALERTS:\n"
            for alert in critical_alerts:
                prompt += f"  • {alert}\n"
        else:
            prompt += "\n---\n\n✓ No critical alerts detected.\n"

        # Add instructions for LLM
        prompt += """
---

INSTRUCTIONS:
1. Evaluate the track based on:
   - Overall similarity to the reference track
   - Critical rhythm features (Beat Strength, Onset Rate) - these are MOST important
   - Genre/playlist context (consider if differences are acceptable or disqualifying)

2. Provide a verdict: [PASS / REJECT / CONDITIONAL]
   - PASS: Track fits the playlist well (minor differences acceptable)
   - REJECT: Track does not fit (major incompatibilities)
   - CONDITIONAL: Could work with specific adjustments (list them)

3. Explain your reasoning in 2-3 sentences focusing on:
   - Why the track does/doesn't fit
   - Which parameters are most concerning (if any)
   - What adjustments would improve fit (if CONDITIONAL)

FORMAT YOUR RESPONSE:

VERDICT: [PASS / REJECT / CONDITIONAL]

REASONING:
[Your analysis here]

KEY ISSUES (if any):
[List specific problems]

RECOMMENDED ACTIONS (if CONDITIONAL):
[Specific mixing/production suggestions]
"""

        return prompt


def generate_decision_prompt(user_stats: Dict, ref_stats: Dict, z_scores: Dict) -> str:
    """
    Standalone function to generate LLM decision prompt
    (Alternative API for direct use without class instantiation)
    """
    gatekeeper = PlaylistGatekeeper()

    # Simulate the internal prompt generation
    critical_alerts = []

    # Check for critical alerts
    if abs(z_scores.get('beat_strength', {}).get('weighted_z', 0)) > 2.0:
        critical_alerts.append("Beat Strength deviation exceeds threshold")
    if abs(z_scores.get('onset_rate', {}).get('weighted_z', 0)) > 2.0:
        critical_alerts.append("Onset Rate deviation exceeds threshold")

    return gatekeeper._generate_llm_prompt(
        user_stats, ref_stats, z_scores, critical_alerts
    )
