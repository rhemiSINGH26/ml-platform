"""
Approval manager - manages human-in-loop approval queue.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.settings import settings
from agent.core.decision_engine import Action


class ApprovalRequest:
    """Represents an approval request."""
    
    def __init__(self, action: Action):
        """
        Initialize approval request.
        
        Args:
            action: Action requiring approval
        """
        self.action = action
        self.request_id = f"APR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.created_at = datetime.now()
        self.status = "pending"  # pending, approved, rejected, expired
        self.reviewed_by = None
        self.reviewed_at = None
        self.review_comment = None
        self.expires_at = self.created_at + timedelta(hours=24)
    
    def approve(self, reviewer: str, comment: str = None):
        """Approve the request."""
        self.status = "approved"
        self.reviewed_by = reviewer
        self.reviewed_at = datetime.now()
        self.review_comment = comment
        logger.info(f"Request {self.request_id} approved by {reviewer}")
    
    def reject(self, reviewer: str, comment: str = None):
        """Reject the request."""
        self.status = "rejected"
        self.reviewed_by = reviewer
        self.reviewed_at = datetime.now()
        self.review_comment = comment
        logger.info(f"Request {self.request_id} rejected by {reviewer}")
    
    def is_expired(self) -> bool:
        """Check if request has expired."""
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "action": self.action.to_dict(),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "review_comment": self.review_comment
        }


class ApprovalManager:
    """Manage approval queue for actions requiring human review."""
    
    def __init__(self, queue_file: Path = None):
        """
        Initialize approval manager.
        
        Args:
            queue_file: Path to approval queue file
        """
        self.queue_file = queue_file or (settings.base_dir / "data" / "approval_queue.jsonl")
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.queue_file.exists():
            self.queue_file.touch()
        
        self.pending_requests = []
        self._load_queue()
    
    def _load_queue(self):
        """Load approval queue from file."""
        if not self.queue_file.exists() or self.queue_file.stat().st_size == 0:
            return
        
        try:
            with open(self.queue_file, "r") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if data.get("status") == "pending":
                            # Reconstruct ApprovalRequest
                            # Note: This is simplified - in production, properly deserialize Action
                            logger.info(f"Loaded pending request: {data.get('request_id')}")
        except Exception as e:
            logger.error(f"Error loading approval queue: {e}")
    
    def _save_request(self, request: ApprovalRequest):
        """Save approval request to file."""
        try:
            with open(self.queue_file, "a") as f:
                f.write(json.dumps(request.to_dict()) + "\n")
        except Exception as e:
            logger.error(f"Error saving approval request: {e}")
    
    def submit_for_approval(self, action: Action) -> ApprovalRequest:
        """
        Submit an action for approval.
        
        Args:
            action: Action requiring approval
            
        Returns:
            Approval request
        """
        request = ApprovalRequest(action)
        self.pending_requests.append(request)
        self._save_request(request)
        
        logger.info(
            f"Submitted for approval: {request.request_id} "
            f"({action.action_type}, risk: {action.risk_level})"
        )
        
        return request
    
    def get_pending_requests(self, include_expired: bool = False) -> List[ApprovalRequest]:
        """
        Get all pending approval requests.
        
        Args:
            include_expired: Whether to include expired requests
            
        Returns:
            List of pending approval requests
        """
        # Clean expired requests
        if not include_expired:
            self.pending_requests = [
                req for req in self.pending_requests
                if not req.is_expired() and req.status == "pending"
            ]
        
        return [req for req in self.pending_requests if req.status == "pending"]
    
    def approve_request(
        self,
        request_id: str,
        reviewer: str,
        comment: str = None
    ) -> bool:
        """
        Approve a request.
        
        Args:
            request_id: ID of the request
            reviewer: Name/email of reviewer
            comment: Optional comment
            
        Returns:
            True if approved, False if not found
        """
        for request in self.pending_requests:
            if request.request_id == request_id:
                if request.is_expired():
                    logger.warning(f"Request {request_id} has expired")
                    request.status = "expired"
                    return False
                
                request.approve(reviewer, comment)
                self._save_request(request)
                return True
        
        logger.warning(f"Request {request_id} not found")
        return False
    
    def reject_request(
        self,
        request_id: str,
        reviewer: str,
        comment: str = None
    ) -> bool:
        """
        Reject a request.
        
        Args:
            request_id: ID of the request
            reviewer: Name/email of reviewer
            comment: Optional comment
            
        Returns:
            True if rejected, False if not found
        """
        for request in self.pending_requests:
            if request.request_id == request_id:
                request.reject(reviewer, comment)
                self._save_request(request)
                return True
        
        logger.warning(f"Request {request_id} not found")
        return False
    
    def get_approved_actions(self) -> List[Action]:
        """
        Get all approved actions ready for execution.
        
        Returns:
            List of approved actions
        """
        approved = []
        for request in self.pending_requests:
            if request.status == "approved":
                approved.append(request.action)
        
        # Remove from pending
        self.pending_requests = [
            req for req in self.pending_requests
            if req.status not in ["approved", "rejected"]
        ]
        
        return approved
    
    def get_request_by_id(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get a specific approval request."""
        for request in self.pending_requests:
            if request.request_id == request_id:
                return request
        return None
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get approval queue statistics.
        
        Returns:
            Dictionary with statistics
        """
        total = len(self.pending_requests)
        pending = sum(1 for r in self.pending_requests if r.status == "pending")
        approved = sum(1 for r in self.pending_requests if r.status == "approved")
        rejected = sum(1 for r in self.pending_requests if r.status == "rejected")
        expired = sum(1 for r in self.pending_requests if r.is_expired())
        
        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "expired": expired
        }
    
    def cleanup_old_requests(self, days: int = 30):
        """
        Remove old completed/rejected requests.
        
        Args:
            days: Remove requests older than this many days
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        initial_count = len(self.pending_requests)
        
        self.pending_requests = [
            req for req in self.pending_requests
            if req.status == "pending" or req.created_at > cutoff
        ]
        
        removed = initial_count - len(self.pending_requests)
        
        if removed > 0:
            logger.info(f"Cleaned up {removed} old approval requests")
        
        return removed
