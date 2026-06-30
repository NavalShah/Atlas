"""Scheduler
============

Handles scheduling of rebalancing events.
"""
from typing import List
from datetime import datetime, timedelta
import pandas as pd

class RebalanceScheduler:
    """
    Determines when rebalancing should occur based on frequency.
    """
    
    def __init__(self, frequency: str = "weekly"):
        """
        Initialize the scheduler.
        
        Args:
            frequency: Rebalancing frequency ("daily", "weekly", "monthly")
        """
        self.frequency = frequency.lower()
        self.last_rebalance_date = None
    
    def is_rebalance_date(self, current_date: datetime) -> bool:
        """
        Check if the current date is a rebalancing date.
        """
        if self.last_rebalance_date is None:
            # First call - always rebalance on first date
            self.last_rebalance_date = current_date
            return True
        
        if self.frequency == "daily":
            return True
        elif self.frequency == "weekly":
            # Rebalance if it has been at least 7 days
            return (current_date - self.last_rebalance_date).days >= 7
        elif self.frequency == "monthly":
            # Rebalance if it has been at least 30 days
            # Simplified - real implementation would consider calendar months
            return (current_date - self.last_rebalance_date).days >= 30
        else:
            # Default to weekly
            return (current_date - self.last_rebalance_date).days >= 7
    
    def update_last_rebalance(self, date: datetime) -> None:
        """
        Update the last rebalance date.
        """
        self.last_rebalance_date = date

