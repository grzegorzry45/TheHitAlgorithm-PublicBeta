"""
Comparator - AI Assistant that generates actionable recommendations
Compares your tracks against target playlist profile
"""

from typing import Dict, List
import numpy as np


class Comparator:
    """Compare tracks and generate recommendations"""

    def __init__(self, target_profile: Dict):
        """
        Initialize comparator with target profile

        Args:
            target_profile: Statistical profile of target playlist
        """
        self.target_profile = target_profile

        # Tolerance levels (in standard deviations)
        self.tolerance = {
            'perfect': 0.5,   # Within 0.5 std
            'good': 1.0,      # Within 1 std
            'warning': 1.5,   # Within 1.5 std
            'critical': 2.0   # Beyond 1.5 std
        }

    def compare_track(self, track_features: Dict) -> List[Dict]:
        """
        Compare single track against target profile (DYNAMIC VERSION)
        Only compares parameters that exist in both track and profile

        Args:
            track_features: Features of your track

        Returns:
            List of recommendations with status and messages
        """
        recommendations = []

        # Calculate overall match score
        score = self.calculate_match_score(track_features)
        recommendations.append({
            'status': self.get_score_status(score),
            'message': f"Overall match: {score}% compatible with target playlist",
            'score': score,
            'parameter': 'Overall Score'
        })

        # Define parameter metadata (labels and units)
        param_metadata = {
            # Core features
            'bpm': {'name': 'BPM', 'unit': 'BPM'},
            'energy': {'name': 'Energy', 'unit': ''},
            'loudness': {'name': 'Loudness', 'unit': 'LUFS'},
            'spectral_centroid': {'name': 'Brightness', 'unit': 'Hz'},
            'rms': {'name': 'RMS Level', 'unit': ''},

            # Tier 1: Spectral
            'spectral_rolloff': {'name': 'High-Freq Content', 'unit': 'Hz'},
            'spectral_flatness': {'name': 'Spectral Flatness', 'unit': ''},
            'zero_crossing_rate': {'name': 'Zero Crossing Rate', 'unit': ''},
            'spectral_contrast': {'name': 'Spectral Contrast', 'unit': 'dB'},

            # Tier 1B: Energy Distribution
            'low_energy': {'name': 'Low Energy', 'unit': '%'},
            'mid_energy': {'name': 'Mid Energy', 'unit': '%'},
            'high_energy': {'name': 'High Energy', 'unit': '%'},
            'sub_bass_presence': {'name': 'Sub-Bass', 'unit': '%'},

            # Tier 2: Perceptual
            'danceability': {'name': 'Danceability', 'unit': ''},
            'beat_strength': {'name': 'Beat Strength', 'unit': ''},
            'valence': {'name': 'Valence (Mood)', 'unit': ''},
            'stereo_width': {'name': 'Stereo Width', 'unit': ''},
            'key_confidence': {'name': 'Key Confidence', 'unit': ''},

            # Tier 3: Production
            'dynamic_range': {'name': 'Dynamic Range', 'unit': 'dB'},
            'loudness_range': {'name': 'Loudness Range', 'unit': 'LU'},
            'true_peak': {'name': 'True Peak', 'unit': 'dBTP'},
            'crest_factor': {'name': 'Crest Factor', 'unit': 'dB'},
            'transient_energy': {'name': 'Transient Energy', 'unit': '%'},
            'harmonic_to_noise_ratio': {'name': 'Harmonic/Noise Ratio', 'unit': 'dB'},

            # Tier 4: Compositional
            'harmonic_complexity': {'name': 'Harmonic Complexity', 'unit': ''},
            'melodic_range': {'name': 'Melodic Range', 'unit': 'semitones'},
            'rhythmic_density': {'name': 'Rhythmic Density', 'unit': 'events/s'},
            'arrangement_density': {'name': 'Arrangement Density', 'unit': ''},
            'repetition_score': {'name': 'Repetition Score', 'unit': ''},
            'frequency_occupancy': {'name': 'Frequency Occupancy', 'unit': '%'},
            'timbral_diversity': {'name': 'Timbral Diversity', 'unit': ''},
            'vocal_instrumental_ratio': {'name': 'Vocal/Instrumental', 'unit': ''},
            'energy_curve': {'name': 'Energy Curve', 'unit': ''},
            'call_response_presence': {'name': 'Call-Response', 'unit': ''}
        }

        # Dynamically compare all parameters that exist in both track and profile
        for param_key, metadata in param_metadata.items():
            if param_key in track_features and param_key in self.target_profile:
                rec = self.compare_feature(
                    track_features,
                    param_key,
                    metadata['name'],
                    metadata['unit']
                )
                rec['parameter'] = metadata['name']
                recommendations.append(rec)

        # Handle special case for key (string value)
        if 'key' in track_features:
            recommendations.append({
                'status': 'good',
                'message': f"Key: {track_features.get('key', 'Unknown')}",
                'parameter': 'Key'
            })

        return recommendations

    def calculate_match_score(self, track_features: Dict) -> float:
        """
        Calculate overall match score (0-100)

        Args:
            track_features: Track features

        Returns:
            Match score percentage
        """
        scores = []

        for key, value in track_features.items():
            if key in self.target_profile and key != 'filename':
                # Skip non-numeric values
                if isinstance(value, str) or isinstance(value, type(None)):
                    continue

                profile = self.target_profile[key]
                target_mean = profile['mean']
                target_std = profile['std']

                # Skip if target_mean is not numeric
                if isinstance(target_mean, str) or isinstance(target_mean, type(None)):
                    continue

                # Calculate normalized distance
                if target_std > 0:
                    try:
                        distance = abs(value - target_mean) / target_std
                        # Convert to score (0-100)
                        score = max(0, 100 - (distance * 33.3))  # 3 std = 0 score
                        scores.append(score)
                    except (TypeError, ValueError):
                        # Skip problematic values
                        continue

        return float(round(np.mean(scores), 1)) if scores else 0.0

    def get_score_status(self, score: float) -> str:
        """Get status based on score"""
        if score >= 80:
            return 'perfect'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'warning'
        else:
            return 'critical'

    def compare_bpm(self, bpm: float) -> Dict:
        """Generate BPM recommendation"""
        try:
            profile = self.target_profile['bpm']
            target_mean = profile['mean']
            target_std = profile['std']
            target_range = (profile['min'], profile['max'])

            diff = abs(bpm - target_mean)
            std_distance = diff / target_std if target_std > 0 else 0
        except (KeyError, TypeError, ValueError):
            return {'status': 'good', 'message': f"Tempo: {bpm:.1f} BPM - nie można porównać"}

        if std_distance <= self.tolerance['perfect']:
            return {
                'status': 'perfect',
                'message': f"Tempo: {bpm:.1f} BPM - Idealne! (cel: {target_mean:.1f})"
            }
        elif std_distance <= self.tolerance['good']:
            return {
                'status': 'good',
                'message': f"Tempo: {bpm:.1f} BPM - Dobre dopasowanie (zakres: {target_range[0]:.1f}-{target_range[1]:.1f})"
            }
        elif std_distance <= self.tolerance['warning']:
            direction = "Przyspiesz" if bpm < target_mean else "Zwolnij"
            change = abs(bpm - target_mean)
            return {
                'status': 'warning',
                'message': f"Tempo: {bpm:.1f} BPM - {direction} o ~{change:.0f} BPM (cel: {target_mean:.1f})"
            }
        else:
            direction = "Za szybko" if bpm > target_mean else "Za wolno"
            change = abs(bpm - target_mean)
            return {
                'status': 'critical',
                'message': f"Tempo: {bpm:.1f} BPM - {direction}! Zmień o ~{change:.0f} BPM (cel: {target_mean:.1f})"
            }

    def compare_energy(self, energy: float) -> Dict:
        """Generate energy recommendation"""
        profile = self.target_profile['energy']
        target_mean = profile['mean']
        target_std = profile['std']

        diff = abs(energy - target_mean)
        std_distance = diff / target_std if target_std > 0 else 0

        if std_distance <= self.tolerance['perfect']:
            return {
                'status': 'perfect',
                'message': f"Energia: {energy:.3f} - Idealny poziom intensywności!"
            }
        elif std_distance <= self.tolerance['good']:
            return {
                'status': 'good',
                'message': f"Energia: {energy:.3f} - Dobre dopasowanie (cel: {target_mean:.3f})"
            }
        elif std_distance <= self.tolerance['warning']:
            direction = "Za wysoka" if energy > target_mean else "Za niska"
            return {
                'status': 'warning',
                'message': f"Energia: {energy:.3f} - {direction} (cel: {target_mean:.3f})"
            }
        else:
            suggestion = "Zmniejsz intensywność/kompresję" if energy > target_mean else "Zwiększ intensywność/dynamikę"
            return {
                'status': 'critical',
                'message': f"Energia: {energy:.3f} - {suggestion} (cel: {target_mean:.3f})"
            }

    def compare_loudness(self, loudness: float) -> Dict:
        """Generate loudness recommendation"""
        profile = self.target_profile['loudness']
        target_mean = profile['mean']
        target_std = profile['std']

        diff = abs(loudness - target_mean)
        std_distance = diff / target_std if target_std > 0 else 0

        if std_distance <= self.tolerance['perfect']:
            return {
                'status': 'perfect',
                'message': f"Głośność: {loudness:.1f} LUFS - Idealny mastering!"
            }
        elif std_distance <= self.tolerance['good']:
            return {
                'status': 'good',
                'message': f"Głośność: {loudness:.1f} LUFS - Dobry mastering (cel: {target_mean:.1f})"
            }
        elif std_distance <= self.tolerance['warning']:
            direction = "Za głośno" if loudness > target_mean else "Za cicho"
            change = abs(loudness - target_mean)
            return {
                'status': 'warning',
                'message': f"Głośność: {loudness:.1f} LUFS - {direction}. Dostosuj o ~{change:.1f} dB (cel: {target_mean:.1f})"
            }
        else:
            suggestion = "Zmniejsz głośność masteringu" if loudness > target_mean else "Zwiększ głośność masteringu"
            change = abs(loudness - target_mean)
            return {
                'status': 'critical',
                'message': f"Głośność: {loudness:.1f} LUFS - {suggestion} o ~{change:.1f} dB! (cel: {target_mean:.1f})"
            }

    def compare_brightness(self, spectral_centroid: float) -> Dict:
        """Generate brightness recommendation"""
        profile = self.target_profile['spectral_centroid']
        target_mean = profile['mean']
        target_std = profile['std']

        diff = abs(spectral_centroid - target_mean)
        std_distance = diff / target_std if target_std > 0 else 0

        if std_distance <= self.tolerance['perfect']:
            return {
                'status': 'perfect',
                'message': f"Jasność: {spectral_centroid:.0f} Hz - Idealny balans tonalny!"
            }
        elif std_distance <= self.tolerance['good']:
            return {
                'status': 'good',
                'message': f"Jasność: {spectral_centroid:.0f} Hz - Dobre dopasowanie (cel: {target_mean:.0f})"
            }
        elif std_distance <= self.tolerance['warning']:
            direction = "Za jasno" if spectral_centroid > target_mean else "Za ciemno"
            eq_suggestion = "Obniż wysokie (8kHz+)" if spectral_centroid > target_mean else "Podnieś wysokie (5-10kHz)"
            return {
                'status': 'warning',
                'message': f"Jasność: {spectral_centroid:.0f} Hz - {direction}. {eq_suggestion} (cel: {target_mean:.0f})"
            }
        else:
            eq_suggestion = "Mocno obniż high-shelf" if spectral_centroid > target_mean else "Mocno podnieś high-shelf"
            return {
                'status': 'critical',
                'message': f"Jasność: {spectral_centroid:.0f} Hz - {eq_suggestion}! (cel: {target_mean:.0f})"
            }

    def compare_rms(self, rms: float) -> Dict:
        """Generate RMS energy recommendation"""
        profile = self.target_profile['rms']
        target_mean = profile['mean']
        target_std = profile['std']

        diff = abs(rms - target_mean)
        std_distance = diff / target_std if target_std > 0 else 0

        if std_distance <= self.tolerance['perfect']:
            return {
                'status': 'perfect',
                'message': f"Poziom energii: {rms:.3f} - Idealna dynamika!"
            }
        elif std_distance <= self.tolerance['good']:
            return {
                'status': 'good',
                'message': f"Poziom energii: {rms:.3f} - Dobra dynamika (cel: {target_mean:.3f})"
            }
        elif std_distance <= self.tolerance['warning']:
            suggestion = "Zmniejsz kompresję" if rms > target_mean else "Zwiększ kompresję"
            return {
                'status': 'warning',
                'message': f"Poziom energii: {rms:.3f} - {suggestion} (cel: {target_mean:.3f})"
            }
        else:
            suggestion = "Przekompresowane! Zmniejsz limiting" if rms > target_mean else "Niedokompresowane! Zwiększ limiting"
            return {
                'status': 'critical',
                'message': f"Poziom energii: {rms:.3f} - {suggestion} (cel: {target_mean:.3f})"
            }

    def compare_key(self, key: str) -> Dict:
        """Generate key recommendation"""
        if 'key' not in self.target_profile:
            return {'status': 'good', 'message': f"Tonacja: {key} - brak danych playlisty do porównania"}

        profile = self.target_profile['key']
        target_key = profile.get('mean', 'Unknown')  # Most common key in playlist

        if key == target_key:
            return {
                'status': 'perfect',
                'message': f"Tonacja: {key} - Idealna! Pasuje do najczęstszej tonacji playlisty"
            }
        else:
            return {
                'status': 'good',
                'message': f"Tonacja: {key} - Inna niż najczęstsza ({target_key}), ale często to OK"
            }

    def compare_feature(self, track_features: Dict, feature_key: str, feature_name: str, unit: str) -> Dict:
        """
        Universal feature comparison method
        Works for any numeric feature using standard deviation logic
        """
        if feature_key not in track_features or feature_key not in self.target_profile:
            return {'status': 'good', 'message': f"{feature_name}: brak danych"}

        value = track_features[feature_key]
        profile = self.target_profile[feature_key]
        target_mean = profile['mean']
        target_std = profile['std']

        # Handle string values or None
        if isinstance(value, str) or isinstance(target_mean, str):
            return {'status': 'good', 'message': f"{feature_name}: {value}"}
        if value is None or target_mean is None:
            return {'status': 'good', 'message': f"{feature_name}: brak danych"}

        try:
            diff = abs(value - target_mean)
            std_distance = diff / target_std if target_std > 0 else 0
        except (TypeError, ValueError):
            return {'status': 'good', 'message': f"{feature_name}: błąd porównania"}

        # Format value with unit
        value_str = f"{value:.2f} {unit}".strip() if unit else f"{value:.2f}"
        target_str = f"{target_mean:.2f} {unit}".strip() if unit else f"{target_mean:.2f}"

        if std_distance <= self.tolerance['perfect']:
            return {
                'status': 'perfect',
                'message': f"{feature_name}: {value_str} - Idealne dopasowanie!"
            }
        elif std_distance <= self.tolerance['good']:
            return {
                'status': 'good',
                'message': f"{feature_name}: {value_str} - Dobre dopasowanie (cel: {target_str})"
            }
        elif std_distance <= self.tolerance['warning']:
            direction = "wyższa" if value > target_mean else "niższa"
            return {
                'status': 'warning',
                'message': f"{feature_name}: {value_str} - Nieco {direction} niż średnia playlisty (cel: {target_str})"
            }
        else:
            direction = "znacznie wyższa" if value > target_mean else "znacznie niższa"
            return {
                'status': 'critical',
                'message': f"{feature_name}: {value_str} - {direction} niż playlista! (cel: {target_str})"
            }
