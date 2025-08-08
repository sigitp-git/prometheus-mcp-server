"""
Authentication utilities for Amazon Managed Prometheus queries.

This module provides utilities for AWS SigV4 signing of requests to
Amazon Managed Prometheus endpoints.
"""

import urllib.parse

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest


class PrometheusAuth:
    """Handle authentication for Amazon Managed Prometheus queries"""

    def __init__(self, region: str = "us-east-1"):
        """Initialize the authentication handler"""
        self.region = region
        self.session = boto3.Session()
        self.credentials = self.session.get_credentials()

    def sign_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        data: str | None = None,
    ) -> dict[str, str]:
        """
        Sign a request using AWS SigV4 for Amazon Managed Prometheus.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL to sign
            headers: Optional headers to include
            data: Optional request body data

        Returns:
            Dictionary of headers including Authorization header
        """
        if not self.credentials:
            raise ValueError("AWS credentials not found")

        # Create AWS request object
        request = AWSRequest(method=method, url=url, data=data, headers=headers or {})

        # Sign the request
        signer = SigV4Auth(self.credentials, "aps", self.region)
        signer.add_auth(request)

        return dict(request.headers)

    def get_signed_headers(
        self, method: str, url: str, params: dict[str, str] | None = None
    ) -> dict[str, str]:
        """
        Get signed headers for a Prometheus query request.

        Args:
            method: HTTP method
            url: Base URL
            params: Query parameters

        Returns:
            Dictionary of signed headers
        """
        # Build full URL with parameters
        if params:
            query_string = urllib.parse.urlencode(params)
            full_url = f"{url}?{query_string}"
        else:
            full_url = url

        return self.sign_request(method, full_url)


def create_auth_headers(
    region: str, method: str, url: str, params: dict[str, str] | None = None
) -> dict[str, str]:
    """
    Convenience function to create authenticated headers.

    Args:
        region: AWS region
        method: HTTP method
        url: Request URL
        params: Query parameters

    Returns:
        Dictionary of authenticated headers
    """
    auth = PrometheusAuth(region)
    return auth.get_signed_headers(method, url, params)
