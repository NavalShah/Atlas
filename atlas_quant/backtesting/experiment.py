"""Experiment
=============

Tracks and manages backtesting experiments.
"""
import json
import yaml
from typing import Dict, Any, Optional
from datetime import datetime
import os
import hashlib

class Experiment:
    """
    Represents a single backtesting experiment.
    """
    
    def __init__(self, 
                 name: str,
                 config: Dict[str, Any],
                 results: Dict[str, Any] = None):
        """
        Initialize an experiment.
        """
        self.name = name
        self.config = config
        self.results = results or {}
        self.timestamp = datetime.now()
        self.experiment_id = self._generate_id()
    
    def _generate_id(self) -> str:
        """
        Generate a unique ID for the experiment.
        """
        # Create a hash based on name, config, and timestamp
        data = f"{self.name}{json.dumps(self.config, sort_keys=True)}{self.timestamp.isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()[:8]
    
    def save(self, directory: str = "experiments/results") -> str:
        """
        Save the experiment to disk.
        """
        # Create directory if it does not exist
        os.makedirs(directory, exist_ok=True)
        
        # Prepare data for saving
        data = {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "timestamp": self.timestamp.isoformat(),
            "config": self.config,
            "results": self.results
        }
        
        # Save as JSON file
        filepath = os.path.join(directory, f"experiment_{self.experiment_id}.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
        
        return filepath
    
    @classmethod
    def load(cls, filepath: str) -> "Experiment":
        """
        Load an experiment from disk.
        """
        with open(filepath, "r") as f:
            data = json.load(f)
        
        experiment = cls(
            name=data["name"],
            config=data["config"],
            results=data.get("results", {})
        )
        experiment.timestamp = datetime.fromisoformat(data["timestamp"])
        experiment.experiment_id = data["experiment_id"]
        
        return experiment

