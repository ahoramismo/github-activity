"""GitHub Activity CLI Tool
This script fetches and displays recent GitHub events for a specified user.
Usage: github-activity <username>
"""
import sys
from datetime import datetime
import requests


def format_time(iso_time: str) -> str:
    """Convert ISO time string to a human-readable format."""
    try:
        dt = datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%Y/%m/%d %I:%M %p")
    except (TypeError, ValueError):
        return "Unknown Time"


def describe_event(event: dict) -> str | None:
    """Generate a description for a GitHub event."""
    event_type = event.get("type")
    payload = event.get("payload", {})
    repo = event.get("repo", {})
    repo_name = repo.get("name")
    created_at = format_time(event.get("created_at"))

    match event_type:
        case "PushEvent":
            commit_count = len(payload.get("commits", []))
            action = f"Pushed {commit_count} commit{'s' if commit_count != 1 else ''}"
        case "IssuesEvent" if payload.get("action") == "opened":
            action = "Opened a new issue"
        case "WatchEvent" if payload.get("action") == "started":
            action = "Starred"
        case "CreateEvent":
            ref_type = payload.get("ref_type")
            action = f"Created a new {ref_type}" if ref_type else None
        case _:
            return None

    return f"- [{action}] {repo_name} at {created_at}" if action and repo_name else None


def fetch_github_events(username):
    """Fetch and display recent GitHub events for a user."""
    if not username:
        print("Username cannot be empty.")
        return
    url = f"https://api.github.com/users/{username}/events"
    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException:
        print(f"Request failed: {e}")
        return

    if not response.ok:
        print(f"Error: Unable to fetch events(HTTP {response.status_code})")
        return

    events = response.json()

    if not events:
        print(f"No recent events found for user '{username}'.")
        return

    for event in events:
        description = describe_event(event)
        if description:
            print(description)


def main():
    """Main function to handle command-line arguments and fetch GitHub events."""

    if len(sys.argv) < 2:
        print("Usage: github-activity <username>")
        sys.exit(1)

    fetch_github_events(sys.argv[1])


if __name__ == "__main__":
    main()
