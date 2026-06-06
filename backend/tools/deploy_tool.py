import logging
import os
import subprocess

from core.runtime_config import PROJECT_DIR

logger = logging.getLogger("helios-deploy")

def deploy_project() -> dict:
    """Execute the project deployment script."""
    deploy_script = os.path.join(PROJECT_DIR, "ops", "deploy.sh")
    
    if not os.path.exists(deploy_script):
        return {
            "status": "failed",
            "error": f"Deployment script not found at {deploy_script}"
        }
    
    try:
        # Run the script and capture output
        result = subprocess.run(
            [deploy_script],
            capture_output=True,
            text=True,
            check=False,
            cwd=str(
                PROJECT_DIR
            ),
            timeout=900
        )
        
        status = "success" if result.returncode == 0 else "failed"
        
        return {
            "status": status,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "failed",
            "error": "Deployment timed out after 15 minutes."
        }
    except Exception as error:
        logger.exception(
            "Deployment failed."
        )
        return {
            "status": "failed",
            "error": str(
                error
            )
        }
