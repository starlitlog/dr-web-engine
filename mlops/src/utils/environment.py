import os
from typing import Literal

EnvironmentType = Literal["development", "staging", "production"]


def detect_environment() -> EnvironmentType:
    """
    Detect the current environment based on various indicators.
    
    Returns:
        Environment type: development, staging, or production
    """
    # Check explicit environment variable
    env = os.getenv("ANYSECRET_ENV", "").lower()
    if env in ["development", "dev"]:
        return "development"
    elif env in ["staging", "stage"]:
        return "staging"
    elif env in ["production", "prod"]:
        return "production"
    
    # Check CI/CD environment indicators
    ci_indicators = [
        "CI", "CONTINUOUS_INTEGRATION", "GITHUB_ACTIONS", 
        "GITLAB_CI", "JENKINS_URL", "BUILDKITE"
    ]
    if any(os.getenv(var) for var in ci_indicators):
        return "production"
    
    # Check cloud environment indicators
    cloud_indicators = [
        "AWS_EXECUTION_ENV", "GOOGLE_CLOUD_PROJECT", "AZURE_CLIENT_ID",
        "KUBERNETES_SERVICE_HOST", "CONTAINER_NAME"
    ]
    if any(os.getenv(var) for var in cloud_indicators):
        return "production"
    
    # Check for LakeFS production indicators
    if os.getenv("LAKEFS_ENDPOINT") and "localhost" not in os.getenv("LAKEFS_ENDPOINT", ""):
        return "production"
    
    # Default to development for local machines
    return "development"


def get_default_data_source_type() -> Literal["local", "lakefs"]:
    """
    Get the default data source type based on environment.
    
    Returns:
        Data source type: local for development, lakefs for staging/production
    """
    env = detect_environment()
    
    if env == "development":
        return "local"
    else:
        return "lakefs"


def should_use_lakefs() -> bool:
    """
    Determine if LakeFS should be used based on environment detection.
    
    Returns:
        True if LakeFS should be used, False for local filesystem
    """
    return get_default_data_source_type() == "lakefs"