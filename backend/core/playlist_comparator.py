"""
PlaylistComparator - Wrapper for Comparator class
Creates playlist profile and compares tracks
"""

from typing import Dict, List
import numpy as np
from .comparator import Comparator


class PlaylistComparator:
    """Analyze playlist and compare tracks against it"""

    def __init__(self, playlist_tracks: List[Dict] = None, existing_profile: Dict = None):
        """
        Initialize with list of analyzed tracks OR existing profile

        Args:
            playlist_tracks: List of track features from playlist
            existing_profile: Pre-calculated profile (optional)
        """
        self.playlist_tracks = playlist_tracks or []
        
        if existing_profile:
            self.profile = existing_profile
        else:
            self.profile = self._create_profile()
            
        self.comparator = Comparator(self.profile)

    def _create_profile(self) -> Dict:
        """Create statistical profile from playlist tracks"""
        if not self.playlist_tracks:
            return {}

        profile = {}

        # Dynamically collect ALL numeric parameters from tracks
        all_params = set()
        for track in self.playlist_tracks:
            for key, value in track.items():
                # Skip non-numeric fields
                if key in ['filename', 'key']:
                    continue
                # Check if it's a numeric value
                if isinstance(value, (int, float)):
                    all_params.add(key)

        # Calculate mean and std for each parameter
        # Use nested dict structure: {param: {'mean': x, 'std': y, 'min': z, 'max': w}}
        for param in all_params:
            values = []
            for track in self.playlist_tracks:
                if param in track and track[param] is not None:
                    try:
                        values.append(float(track[param]))
                    except (ValueError, TypeError):
                        continue

            if values:
                profile[param] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values))
                }

        return profile

    def get_playlist_profile(self) -> Dict:
        """Return the playlist profile"""
        return self.profile

    def compare_track(self, track_features: Dict) -> List[Dict]:
        """
        Compare single track against playlist profile

        Args:
            track_features: Features of track to compare

        Returns:
            List of recommendations
        """
        return self.comparator.compare_track(track_features)

    def generate_recommendations(self, comparison: List[Dict]) -> List[Dict]:
        """
        Generate formatted recommendations

        Args:
            comparison: Comparison results from compare_track

        Returns:
            List of formatted recommendations
        """
        recommendations = []

        for item in comparison:
            rec = {
                'category': item.get('parameter', 'General'),
                'suggestion': item.get('message', ''),
                'status': item.get('status', 'info')
            }
            recommendations.append(rec)

        return recommendations
