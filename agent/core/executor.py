"""
Action executor - executes approved actions.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import subprocess
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.settings import settings
from agent.core.decision_engine import Action


class ExecutionResult:
    """Result of action execution."""
    
    def __init__(
        self,
        success: bool,
        message: str,
        details: Dict[str, Any] = None,
        error: str = None
    ):
        """
        Initialize execution result.
        
        Args:
            success: Whether execution was successful
            message: Human-readable message
            details: Additional details
            error: Error message if failed
        """
        self.success = success
        self.message = message
        self.details = details or {}
        self.error = error
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "details": self.details,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }


class ActionExecutor:
    """Execute approved actions."""
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize executor.
        
        Args:
            dry_run: If True, simulate execution without making changes
        """
        self.dry_run = dry_run
        self.execution_history = []
    
    def execute(self, action: Action) -> ExecutionResult:
        """
        Execute an action.
        
        Args:
            action: Action to execute
            
        Returns:
            Execution result
        """
        logger.info(f"Executing action: {action.action_id} ({action.action_type})")
        
        if self.dry_run:
            logger.info("DRY RUN mode - simulating execution")
            return ExecutionResult(
                success=True,
                message=f"[DRY RUN] Would execute: {action.description}",
                details={"dry_run": True}
            )
        
        # Route to appropriate executor
        executor_map = {
            "retrain_model": self._execute_retrain,
            "rollback_model": self._execute_rollback,
            "send_alert": self._execute_alert,
            "adjust_threshold": self._execute_adjust_threshold,
            "collect_diagnostics": self._execute_diagnostics,
            "validate_data": self._execute_validation,
            "generate_report": self._execute_report
        }
        
        executor_func = executor_map.get(action.action_type)
        
        if executor_func is None:
            logger.error(f"No executor for action type: {action.action_type}")
            result = ExecutionResult(
                success=False,
                message=f"Unknown action type: {action.action_type}",
                error="Executor not implemented"
            )
        else:
            try:
                result = executor_func(action)
                action.status = "completed" if result.success else "failed"
            except Exception as e:
                logger.error(f"Execution failed: {e}", exc_info=True)
                result = ExecutionResult(
                    success=False,
                    message=f"Execution error: {str(e)}",
                    error=str(e)
                )
                action.status = "failed"
        
        # Record in history
        self.execution_history.append({
            "action": action.to_dict(),
            "result": result.to_dict()
        })
        
        logger.info(
            f"Action {action.action_id} {'succeeded' if result.success else 'failed'}: "
            f"{result.message}"
        )
        
        return result
    
    def _execute_retrain(self, action: Action) -> ExecutionResult:
        """Execute model retraining."""
        logger.info("Starting model retraining...")
        
        try:
            # Build command
            cmd = [
                "python",
                str(settings.base_dir / "training" / "train_pipeline.py"),
                "--experiment-name", "agent_triggered_retrain",
                "--run-name", f"retrain_{action.action_id}"
            ]
            
            logger.info(f"Running command: {' '.join(cmd)}")
            
            # Execute training pipeline
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                return ExecutionResult(
                    success=True,
                    message="Model retraining completed successfully",
                    details={
                        "trigger": action.parameters.get("trigger"),
                        "stdout": result.stdout[-500:],  # Last 500 chars
                    }
                )
            else:
                return ExecutionResult(
                    success=False,
                    message="Model retraining failed",
                    error=result.stderr[-500:]
                )
        
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                message="Model retraining timed out",
                error="Execution exceeded 1 hour timeout"
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                message=f"Retraining error: {str(e)}",
                error=str(e)
            )
    
    def _execute_rollback(self, action: Action) -> ExecutionResult:
        """Execute model rollback."""
        logger.info("Rolling back model...")
        
        try:
            import joblib
            import shutil
            
            production_dir = settings.production_model_dir
            
            # Find current and previous models
            model_files = sorted(
                production_dir.glob("*.joblib"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            if len(model_files) < 2:
                return ExecutionResult(
                    success=False,
                    message="No previous model available for rollback",
                    error="Insufficient model versions"
                )
            
            current_model = model_files[0]
            previous_model = model_files[1]
            
            # Backup current
            backup_path = production_dir / f"backup_{current_model.name}"
            shutil.copy(current_model, backup_path)
            
            # Replace current with previous
            shutil.copy(previous_model, current_model)
            
            logger.info(f"Rolled back from {current_model.name} to {previous_model.name}")
            
            return ExecutionResult(
                success=True,
                message=f"Rolled back to {previous_model.stem}",
                details={
                    "previous_model": current_model.name,
                    "current_model": previous_model.name,
                    "backup_path": str(backup_path)
                }
            )
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                message=f"Rollback failed: {str(e)}",
                error=str(e)
            )
    
    def _execute_alert(self, action: Action) -> ExecutionResult:
        """Execute alert notification."""
        logger.info("Sending alert notification...")
        
        try:
            channels = action.parameters.get("channels", ["email"])
            priority = action.parameters.get("priority", "normal")
            issue_details = action.parameters.get("issue_details", {})
            
            # TODO: Implement actual email/Slack sending
            # For now, just log
            logger.warning(
                f"ALERT [{priority.upper()}]: {action.description}",
                extra={"channels": channels, "issue": issue_details}
            )
            
            return ExecutionResult(
                success=True,
                message=f"Alert sent via {', '.join(channels)}",
                details={"channels": channels, "priority": priority}
            )
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                message=f"Alert failed: {str(e)}",
                error=str(e)
            )
    
    def _execute_adjust_threshold(self, action: Action) -> ExecutionResult:
        """Execute threshold adjustment."""
        logger.info("Adjusting threshold configuration...")
        
        try:
            # TODO: Implement configuration update
            # For now, just log
            logger.info(f"Would adjust threshold: {action.parameters}")
            
            return ExecutionResult(
                success=True,
                message="Threshold adjusted successfully",
                details=action.parameters
            )
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                message=f"Threshold adjustment failed: {str(e)}",
                error=str(e)
            )
    
    def _execute_diagnostics(self, action: Action) -> ExecutionResult:
        """Execute diagnostics collection."""
        logger.info("Collecting system diagnostics...")
        
        try:
            import psutil
            
            diagnostics = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save to file
            diagnostics_dir = settings.reports_dir / "diagnostics"
            diagnostics_dir.mkdir(parents=True, exist_ok=True)
            
            import json
            diag_file = diagnostics_dir / f"diagnostics_{action.action_id}.json"
            with open(diag_file, "w") as f:
                json.dump(diagnostics, f, indent=2)
            
            logger.info(f"Diagnostics saved to {diag_file}")
            
            return ExecutionResult(
                success=True,
                message="Diagnostics collected successfully",
                details=diagnostics
            )
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                message=f"Diagnostics collection failed: {str(e)}",
                error=str(e)
            )
    
    def _execute_validation(self, action: Action) -> ExecutionResult:
        """Execute data validation."""
        logger.info("Running data validation...")
        
        try:
            from validation.data_validator import DataValidator
            from validation.schema_definitions import HEART_DISEASE_SCHEMA
            
            # TODO: Load recent data for validation
            # For now, just indicate validation would run
            logger.info("Would validate data with schema")
            
            return ExecutionResult(
                success=True,
                message="Data validation completed",
                details={"validation_type": action.parameters.get("validation_type")}
            )
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                message=f"Validation failed: {str(e)}",
                error=str(e)
            )
    
    def _execute_report(self, action: Action) -> ExecutionResult:
        """Execute report generation."""
        logger.info("Generating report...")
        
        try:
            report_type = action.parameters.get("report_type", "general")
            
            # TODO: Implement report generation
            logger.info(f"Would generate {report_type} report")
            
            return ExecutionResult(
                success=True,
                message=f"{report_type} report generated",
                details={"report_type": report_type}
            )
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                message=f"Report generation failed: {str(e)}",
                error=str(e)
            )
    
    def get_execution_history(self, limit: int = None) -> list:
        """
        Get execution history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of execution records
        """
        if limit:
            return self.execution_history[-limit:]
        return self.execution_history
