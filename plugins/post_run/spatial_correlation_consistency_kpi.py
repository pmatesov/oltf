from core.models import PluginResult, TestContext
from core.post_run_plugin import PostRunPlugin
import json
from pathlib import Path
import math


class SpatialCorrelationConsistencyPlugin(PostRunPlugin):
    """
    This plugin computes the spatial correlation between the camera 3D bounding box and radar points per fused object.
    It calculates centroids of each and compares them via Euclidean distance.
    The score is normalized by the maximum diagonal distance of the camera bounding box.
    The final success is based on the average score vs a configurable threshold (default 0.85).
    """
    def execute(self, context: TestContext) -> PluginResult:
        threshold = self.config.get("spatial_correlation_threshold", 0.85)  # default threshold
        scenario_path = context.data_path  # TODO pass data_path by Scenario object not by contex
        correlation_scores = []

        try:
            with open(scenario_path, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    fused_objects = entry.get("fused_objects", [])

                    for obj in fused_objects:
                        camera_bbox = obj.get("camera_bbox_3d")
                        radar_points = obj.get("radar_points")

                        if not camera_bbox or not radar_points:
                            continue

                        camera_center = self._calculate_centroid(camera_bbox)
                        radar_center = self._calculate_centroid(radar_points)

                        distance = self._euclidean_distance(camera_center, radar_center)
                        max_distance = self._max_expected_distance(camera_bbox)
                        score = max(0.0, 1.0 - distance / max_distance) if max_distance else 0.0
                        correlation_scores.append(score)

            if not correlation_scores:
                return PluginResult(success=False, message="No valid correlation data found")

            avg_score = sum(correlation_scores) / len(correlation_scores)
            success = avg_score >= threshold

            message = (
                f"Avg spatial correlation score {avg_score:.2f} meets threshold {threshold:.2f}"
                if success else
                f"Avg spatial correlation score {avg_score:.2f} below threshold {threshold:.2f}"
            )

            return PluginResult(
                success=success,
                message=message,
                metrics={
                    "spatial_correlation_score": {
                        "avg": avg_score,
                        "threshold": threshold
                    }
                }
            )

        except Exception as e:
            return PluginResult(success=False, message=str(e))

    @staticmethod
    def _calculate_centroid(points):
        if not points:
            return (0, 0, 0)
        x = sum(p["x"] for p in points) / len(points)
        y = sum(p["y"] for p in points) / len(points)
        z = sum(p["z"] for p in points) / len(points)
        return (x, y, z)

    @staticmethod
    def _euclidean_distance(p1, p2):
        return math.sqrt(
            (p1[0] - p2[0]) ** 2 +
            (p1[1] - p2[1]) ** 2 +
            (p1[2] - p2[2]) ** 2
        )

    @staticmethod
    def _max_expected_distance(bbox):
        # Estimate maximum size of object as the diagonal of the bbox
        if len(bbox) < 2:
            return 1.0
        max_dist = 0
        for i in range(len(bbox)):
            for j in range(i + 1, len(bbox)):
                d = SpatialCorrelationConsistencyPlugin._euclidean_distance(
                    (bbox[i]["x"], bbox[i]["y"], bbox[i]["z"]),
                    (bbox[j]["x"], bbox[j]["y"], bbox[j]["z"])
                )
                if d > max_dist:
                    max_dist = d
        return max_dist or 1.0
