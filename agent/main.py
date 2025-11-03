"""
Autonomous agent main orchestrator.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import time
from datetime import datetime
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import settings
from config.logging_config import setup_logging
from agent.core import (
    DiagnosisEngine,
    DecisionEngine,
    ActionExecutor,
    ApprovalManager,
    Issue,
    Action
)


class AutonomousAgent:
    """Main autonomous agent orchestrator."""
    
    def __init__(
        self,
        check_interval: int = 300,  # 5 minutes
        dry_run: bool = False
    ):
        """
        Initialize autonomous agent.
        
        Args:
            check_interval: Time between health checks (seconds)
            dry_run: If True, simulate actions without executing
        """
        self.check_interval = check_interval
        self.dry_run = dry_run
        
        # Initialize components
        self.diagnosis_engine = DiagnosisEngine()
        self.decision_engine = DecisionEngine(auto_approve_low_risk=True)
        self.executor = ActionExecutor(dry_run=dry_run)
        self.approval_manager = ApprovalManager()
        
        self.running = False
        self.last_check = None
        self.cycle_count = 0
        
        logger.info("Autonomous Agent initialized")
        logger.info(f"Check interval: {check_interval}s")
        logger.info(f"Dry run mode: {dry_run}")
    
    def run_diagnosis_cycle(
        self,
        current_data=None,
        predictions=None,
        probabilities=None
    ) -> List[Issue]:
        """
        Run a complete diagnosis cycle.
        
        Args:
            current_data: Current dataset for drift detection
            predictions: Recent predictions for anomaly detection
            probabilities: Prediction probabilities
            
        Returns:
            List of detected issues
        """
        logger.info("=" * 80)
        logger.info(f"Starting diagnosis cycle #{self.cycle_count + 1}")
        logger.info("=" * 80)
        
        # Run diagnosis
        issues = self.diagnosis_engine.run_full_diagnosis(
            current_data=current_data,
            predictions=predictions,
            probabilities=probabilities
        )
        
        self.cycle_count += 1
        self.last_check = datetime.now()
        
        return issues
    
    def run_decision_cycle(self, issues: List[Issue]) -> List[Action]:
        """
        Run decision cycle to recommend actions.
        
        Args:
            issues: List of detected issues
            
        Returns:
            List of recommended actions
        """
        logger.info("Running decision cycle...")
        
        actions = self.decision_engine.recommend_actions(issues)
        
        return actions
    
    def run_execution_cycle(self, actions: List[Action]) -> Dict[str, Any]:
        """
        Run execution cycle for approved actions.
        
        Args:
            actions: List of actions to execute
            
        Returns:
            Execution summary
        """
        logger.info("Running execution cycle...")
        
        # Separate actions by approval requirement
        auto_execute = [a for a in actions if not a.requires_approval]
        needs_approval = [a for a in actions if a.requires_approval]
        
        logger.info(f"Auto-execute: {len(auto_execute)} actions")
        logger.info(f"Needs approval: {len(needs_approval)} actions")
        
        # Submit actions requiring approval
        for action in needs_approval:
            self.approval_manager.submit_for_approval(action)
        
        # Execute auto-approved actions
        auto_results = []
        for action in auto_execute:
            result = self.executor.execute(action)
            auto_results.append({
                "action_id": action.action_id,
                "action_type": action.action_type,
                "success": result.success,
                "message": result.message
            })
        
        # Check for any newly approved actions
        approved_actions = self.approval_manager.get_approved_actions()
        
        approved_results = []
        for action in approved_actions:
            logger.info(f"Executing approved action: {action.action_id}")
            result = self.executor.execute(action)
            approved_results.append({
                "action_id": action.action_id,
                "action_type": action.action_type,
                "success": result.success,
                "message": result.message
            })
        
        summary = {
            "auto_executed": len(auto_results),
            "auto_results": auto_results,
            "submitted_for_approval": len(needs_approval),
            "approved_executed": len(approved_results),
            "approved_results": approved_results,
            "total_executed": len(auto_results) + len(approved_results)
        }
        
        logger.info(f"Execution summary: {summary['total_executed']} actions executed")
        
        return summary
    
    def run_single_cycle(
        self,
        current_data=None,
        predictions=None,
        probabilities=None
    ) -> Dict[str, Any]:
        """
        Run a complete cycle: diagnose -> decide -> execute.
        
        Args:
            current_data: Current dataset
            predictions: Recent predictions
            probabilities: Prediction probabilities
            
        Returns:
            Cycle summary
        """
        cycle_start = time.time()
        
        # 1. Diagnose
        issues = self.run_diagnosis_cycle(current_data, predictions, probabilities)
        
        # 2. Decide
        actions = self.run_decision_cycle(issues)
        
        # 3. Execute
        execution_summary = self.run_execution_cycle(actions)
        
        cycle_duration = time.time() - cycle_start
        
        summary = {
            "cycle_number": self.cycle_count,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(cycle_duration, 2),
            "issues_detected": len(issues),
            "actions_recommended": len(actions),
            "execution": execution_summary,
            "issues": [issue.to_dict() for issue in issues],
            "actions": [action.to_dict() for action in actions]
        }
        
        logger.info("=" * 80)
        logger.info(f"Cycle #{self.cycle_count} completed in {cycle_duration:.2f}s")
        logger.info(f"Issues: {len(issues)}, Actions: {len(actions)}, "
                   f"Executed: {execution_summary['total_executed']}")
        logger.info("=" * 80)
        
        return summary
    
    def start(self):
        """Start the autonomous agent in continuous mode."""
        logger.info("Starting autonomous agent in continuous mode...")
        self.running = True
        
        try:
            while self.running:
                # Run cycle
                self.run_single_cycle()
                
                # Wait for next cycle
                logger.info(f"Waiting {self.check_interval}s until next cycle...")
                time.sleep(self.check_interval)
        
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            self.stop()
        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            self.stop()
    
    def stop(self):
        """Stop the autonomous agent."""
        logger.info("Stopping autonomous agent...")
        self.running = False
        
        # Print statistics
        stats = self.approval_manager.get_statistics()
        logger.info(f"Approval queue stats: {stats}")
        logger.info(f"Total cycles run: {self.cycle_count}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get agent status.
        
        Returns:
            Status dictionary
        """
        approval_stats = self.approval_manager.get_statistics()
        
        return {
            "running": self.running,
            "cycle_count": self.cycle_count,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "check_interval": self.check_interval,
            "dry_run": self.dry_run,
            "approval_queue": approval_stats,
            "detected_issues": len(self.diagnosis_engine.detected_issues),
            "recommended_actions": len(self.decision_engine.recommended_actions)
        }


def main():
    """Main entry point for autonomous agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run autonomous agent")
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Check interval in seconds (default: 300)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode - simulate actions without executing"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (don't loop)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    # Create agent
    agent = AutonomousAgent(
        check_interval=args.interval,
        dry_run=args.dry_run
    )
    
    if args.once:
        # Run single cycle
        logger.info("Running single cycle...")
        summary = agent.run_single_cycle()
        
        import json
        print("\n" + "=" * 80)
        print("CYCLE SUMMARY")
        print("=" * 80)
        print(json.dumps(summary, indent=2))
    else:
        # Run continuously
        agent.start()


if __name__ == "__main__":
    main()
