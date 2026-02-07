"""
Person Tracker Module
=====================

Handles tracking people across video frames following Single Responsibility Principle.

Author: AI-102 Study Implementation
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field

try:
    from .geometry_utils import calculate_distance_between_boxes, calculate_movement_speed
    from .config import TrackingConfig
except ImportError:
    from geometry_utils import calculate_distance_between_boxes, calculate_movement_speed
    from config import TrackingConfig


@dataclass
class PersonTrackingData:
    """Data structure for tracking a single person across frames."""
    
    person_id: str
    first_frame: int
    last_frame: int
    position_history: List[Dict] = field(default_factory=list)
    
    def add_position(self, position: Dict, frame_number: int) -> None:
        """
        Add a new position to tracking history.
        
        Args:
            position: Bounding box dictionary
            frame_number: Current frame number
        """
        self.position_history.append(position)
        self.last_frame = frame_number
        
        # Keep only recent positions to limit memory usage
        if len(self.position_history) > TrackingConfig.POSITION_HISTORY_SIZE:
            self.position_history = self.position_history[-TrackingConfig.POSITION_HISTORY_SIZE:]
    
    def calculate_dwell_time(self, current_frame: int, fps: int = TrackingConfig.DEFAULT_FPS) -> float:
        """
        Calculate how long this person has been present.
        
        Args:
            current_frame: Current frame number
            fps: Frames per second of the video
            
        Returns:
            Dwell time in seconds
        """
        frames_present = current_frame - self.first_frame
        return frames_present / fps
    
    def get_recent_positions(self, count: int = None) -> List[Dict]:
        """
        Get the most recent positions.
        
        Args:
            count: Number of recent positions to return (None for all)
            
        Returns:
            List of recent position dictionaries
        """
        if count is None:
            return self.position_history.copy()
        return self.position_history[-count:]


class PersonTracker:
    """
    Tracks people across video frames using simple spatial proximity matching.
    
    For production systems, consider using:
    - SORT (Simple Online Realtime Tracking)
    - DeepSORT (with appearance features)
    - ByteTrack
    - FairMOT
    """
    
    def __init__(self):
        """Initialize the person tracker."""
        self._tracked_people: Dict[str, PersonTrackingData] = {}
        self._next_person_id = 0
    
    def track_person(self, bounding_box: Dict, frame_number: int) -> str:
        """
        Track a person across frames or create new track.
        
        Args:
            bounding_box: Bounding box dictionary with x, y, width, height
            frame_number: Current frame number
            
        Returns:
            Person ID string
        """
        person_id = self._find_matching_track(bounding_box, frame_number)
        
        if person_id is None:
            person_id = self._create_new_track(bounding_box, frame_number)
        else:
            self._update_track(person_id, bounding_box, frame_number)
        
        return person_id
    
    def get_tracking_data(self, person_id: str) -> Optional[PersonTrackingData]:
        """
        Get tracking data for a specific person.
        
        Args:
            person_id: Person identifier
            
        Returns:
            PersonTrackingData or None if not found
        """
        return self._tracked_people.get(person_id)
    
    def get_all_tracked_people(self) -> Dict[str, PersonTrackingData]:
        """
        Get all currently tracked people.
        
        Returns:
            Dictionary of person_id -> PersonTrackingData
        """
        return self._tracked_people.copy()
    
    def cleanup_old_tracks(self, current_frame: int, max_age_frames: int = 300) -> None:
        """
        Remove tracks that haven't been updated recently.
        
        Args:
            current_frame: Current frame number
            max_age_frames: Maximum age in frames before removing track
        """
        to_remove = [
            person_id
            for person_id, data in self._tracked_people.items()
            if current_frame - data.last_frame > max_age_frames
        ]
        
        for person_id in to_remove:
            del self._tracked_people[person_id]
    
    def _find_matching_track(self, bounding_box: Dict, frame_number: int) -> Optional[str]:
        """
        Find existing track that matches this detection.
        
        Args:
            bounding_box: Current bounding box
            frame_number: Current frame number
            
        Returns:
            Person ID if match found, None otherwise
        """
        for person_id, data in self._tracked_people.items():
            # Only match with recent tracks (previous frame)
            if data.last_frame != frame_number - 1:
                continue
            
            # Get last known position
            if not data.position_history:
                continue
            
            last_position = data.position_history[-1]
            distance = calculate_distance_between_boxes(bounding_box, last_position)
            
            # If close enough, consider it the same person
            if distance < TrackingConfig.MAX_TRACKING_DISTANCE_PIXELS:
                return person_id
        
        return None
    
    def _create_new_track(self, bounding_box: Dict, frame_number: int) -> str:
        """
        Create a new person track.
        
        Args:
            bounding_box: Initial bounding box
            frame_number: Current frame number
            
        Returns:
            New person ID
        """
        person_id = f"person_{self._next_person_id}"
        self._next_person_id += 1
        
        tracking_data = PersonTrackingData(
            person_id=person_id,
            first_frame=frame_number,
            last_frame=frame_number,
            position_history=[bounding_box]
        )
        
        self._tracked_people[person_id] = tracking_data
        
        return person_id
    
    def _update_track(self, person_id: str, bounding_box: Dict, frame_number: int) -> None:
        """
        Update existing person track with new position.
        
        Args:
            person_id: Person identifier
            bounding_box: New bounding box
            frame_number: Current frame number
        """
        if person_id in self._tracked_people:
            self._tracked_people[person_id].add_position(bounding_box, frame_number)
