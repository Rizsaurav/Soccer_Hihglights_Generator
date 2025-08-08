import os
import cv2
import json
import pandas as pd
from tqdm import tqdm
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BowlingCropExtractor:
    def __init__(self, root_dir: Optional[str] = None, allowed_roles: Optional[List[str]] = None):
        if root_dir is None:
            root_dir = Path(__file__).parent.parent.parent.parent.absolute()
        else:
            root_dir = Path(root_dir)

        self.root_dir = root_dir
        self.data_dir = root_dir / 'cricket' / 'datasets' / 'sportradar'
        self.split_csv_path = self.data_dir / 'data_split.csv'
        self.annotation_dir = self.data_dir / 'data'
        self.video_dir = self.data_dir / 'videos'
        self.output_dir = root_dir / 'cricket' / 'crops'

        self.allowed_roles = allowed_roles or ["bowler", "batsman"]
        logger.info(f"Extracting crops for roles: {self.allowed_roles}")

        self._validate_paths()
        self.metadata_buffer = {}
        self.stats = {
            'total_json_files': 0,
            'matched_pairs': 0,
            'missing_videos': 0,
            'processed_files': 0,
            'failed_frames': 0,
            'extracted_crops': 0,
            'invalid_bboxes': 0,
            'filtered_roles': 0
        }

    def _validate_paths(self) -> None:
        required_paths = [
            self.split_csv_path,
            self.annotation_dir,
            self.video_dir
        ]
        for path in required_paths:
            if not path.exists():
                raise FileNotFoundError(f"Required path not found: {path}")
        logger.info(f"Validated paths. Root directory: {self.root_dir}")

    def _load_split_mapping(self) -> Dict[str, str]:
        split_df = pd.read_csv(self.split_csv_path)
        split_map = dict(zip(split_df['video_name'], split_df['set_name']))
        logger.info(f"Loaded split mapping for {len(split_map)} videos")
        return split_map

    def _find_matching_files(self) -> List[Tuple[Path, Path, str]]:
        """Find JSON files that have matching video files"""
        annotation_files = list(self.annotation_dir.glob("*.json"))
        self.stats['total_json_files'] = len(annotation_files)
        
        # Common video extensions to check
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        
        matched_pairs = []
        
        for annotation_path in annotation_files:
            video_id = annotation_path.stem
            video_path = None
            
            # Try to find matching video file with any common extension
            for ext in video_extensions:
                potential_video_path = self.video_dir / f"{video_id}{ext}"
                if potential_video_path.exists():
                    video_path = potential_video_path
                    break
            
            if video_path:
                matched_pairs.append((annotation_path, video_path, video_id))
                self.stats['matched_pairs'] += 1
            else:
                self.stats['missing_videos'] += 1
                logger.debug(f"No matching video found for {video_id}")
        
        logger.info(f"Found {len(matched_pairs)} matching annotation-video pairs out of {len(annotation_files)} JSON files")
        return matched_pairs

    def _validate_bbox(self, bbox: List, frame_shape: Tuple[int, int]) -> bool:
        if not bbox or len(bbox) != 4:
            return False
        x, y, w, h = bbox
        frame_height, frame_width = frame_shape[:2]
        if x < 0 or y < 0 or w <= 0 or h <= 0:
            return False
        if x + w > frame_width or y + h > frame_height:
            return False
        if w < 10 or h < 10:
            return False
        return True

    def _extract_and_save_crop(self, frame: np.ndarray, bbox: List[float], save_path: Path, role: str, video_id: str, frame_idx: int, set_name: str) -> bool:
        try:
            x, y, w, h = [int(round(val)) for val in bbox]
            frame_height, frame_width = frame.shape[:2]
            x = max(0, x)
            y = max(0, y)
            w = min(w, frame_width - x)
            h = min(h, frame_height - y)

            if not self._validate_bbox([x, y, w, h], frame.shape):
                logger.warning(f"Invalid bbox {bbox} for frame shape {frame.shape}")
                self.stats['invalid_bboxes'] += 1
                return False

            crop = frame[y:y+h, x:x+w]
            if crop.size == 0:
                logger.warning(f"Empty crop extracted for {role}")
                return False

            save_path.parent.mkdir(parents=True, exist_ok=True)
            if not cv2.imwrite(str(save_path), crop):
                logger.error(f"Failed to save crop to {save_path}")
                return False

            relative_path = save_path.relative_to(self.root_dir)
            metadata_row = {
                'video_id': video_id,
                'frame_idx': frame_idx,
                'role': role,
                'image_path': str(relative_path),
                'set_name': set_name
            }
            self.metadata_buffer.setdefault(set_name, []).append(metadata_row)
            self.stats['extracted_crops'] += 1
            return True

        except Exception as e:
            logger.error(f"Error extracting crop for {role}: {e}")
            return False

    def _process_video(self, video_path: Path, annotation_path: Path, video_id: str, set_name: str) -> None:
        try:
            if annotation_path.stat().st_size == 0:
                logger.warning(f"Empty annotation file: {annotation_path}")
                return
            with open(annotation_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load annotation {annotation_path}: {e}")
            return

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            logger.error(f"Failed to open video: {video_path}")
            return

        try:
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            # Get events dictionary where keys are frame numbers
            events_dict = data.get("event", {})

            if not events_dict:
                logger.warning(f"No events found in {annotation_path.name}")
                return

            # Process each frame that has events
            for frame_str, frame_events in events_dict.items():
                try:
                    frame_idx = int(frame_str)
                except ValueError:
                    logger.warning(f"Invalid frame number: {frame_str}")
                    continue
                    
                if frame_idx < 0 or frame_idx >= total_frames:
                    continue
                    
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                success, frame = cap.read()
                if not success:
                    self.stats['failed_frames'] += 1
                    continue

                # Process each event in this frame
                for event in frame_events:
                    if not isinstance(event, dict):
                        continue
                        
                    event_type = event.get("event", "")
                    bbox = event.get("box", [])
                    
                    # Skip if not a bowl release event or no bbox
                    if event_type.strip().lower() != "bowl release" or not bbox:
                        continue
                    
                    # Convert box format [x1, y1, x2, y2, score] to [x, y, w, h]
                    if len(bbox) >= 4:
                        x1, y1, x2, y2 = bbox[:4]
                        w = x2 - x1
                        h = y2 - y1
                        bbox_xywh = [x1, y1, w, h]
                        
                        # For now, assume role is "bowler" since we don't have role info in this format
                        role = "bowler"
                        if role in self.allowed_roles:
                            save_dir = self.output_dir / set_name / video_id / str(frame_idx)
                            save_path = save_dir / f"{role}.jpg"
                            self._extract_and_save_crop(frame, bbox_xywh, save_path, role, video_id, frame_idx, set_name)

        finally:
            cap.release()

    def extract_bowling_frames(self) -> None:
        logger.info("Starting bowling crop extraction...")
        split_map = self._load_split_mapping()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find matching annotation-video pairs
        matched_pairs = self._find_matching_files()
        
        if not matched_pairs:
            logger.error("No matching annotation-video pairs found!")
            return

        for annotation_path, video_path, video_id in tqdm(matched_pairs, desc="Extracting crops"):
            set_name = split_map.get(video_id, "unspecified")
            try:
                self._process_video(video_path, annotation_path, video_id, set_name)
                self.stats['processed_files'] += 1
            except Exception as e:
                logger.error(f"Error processing video {video_id}: {e}")

        self._print_statistics()
        self._save_metadata_csvs()

    def _save_metadata_csvs(self) -> None:
        logger.info("Saving metadata CSVs for CNN+SVM training...")
        for set_name, rows in self.metadata_buffer.items():
            if not rows:
                continue
            df = pd.DataFrame(rows)
            csv_path = self.output_dir / f"{set_name}_labels.csv"
            df.to_csv(csv_path, index=False)
        if self.metadata_buffer:
            all_rows = [row for rows in self.metadata_buffer.values() for row in rows]
            pd.DataFrame(all_rows).to_csv(self.output_dir / "all_labels.csv", index=False)

    def _print_statistics(self) -> None:
        logger.info("Extraction completed!")
        for k, v in self.stats.items():
            logger.info(f"  {k.replace('_', ' ').capitalize()}: {v}")
        total_metadata = sum(len(rows) for rows in self.metadata_buffer.values())
        logger.info(f"  Metadata rows: {total_metadata}")


def main():
    extractor = BowlingCropExtractor(allowed_roles=["bowler", "batsman"])
    extractor.extract_bowling_frames()


if __name__ == "__main__":
    main()