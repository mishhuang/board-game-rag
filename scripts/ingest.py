#!/usr/bin/env python3
import argparse
import os
import sys
import uuid
from pathlib import Path

import requests


LIBRECHAT_URL = "http://localhost:3080"  # used for auth only
RAG_API_URL = "http://localhost:8000"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Ingest a rulebook PDF into the LibreChat RAG pipeline"
    )
    parser.add_argument("--file", required=True, help="Path to the rulebook PDF")
    parser.add_argument("--game", required=True, help="Game name (used as entity scope and file identifier)")
    return parser.parse_args()


def get_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"Error: environment variable {name} is not set", file=sys.stderr)
        sys.exit(1)
    return value


def authenticate(email: str, password: str) -> str:
    resp = requests.post(
        f"{LIBRECHAT_URL}/api/auth/login",
        json={"email": email, "password": password},
        timeout=10,
    )
    if resp.status_code != 200:
        print(f"Error: LibreChat login failed ({resp.status_code}): {resp.text}", file=sys.stderr)
        sys.exit(1)
    data = resp.json()
    token = data.get("token")
    if not token:
        print(f"Error: login response missing 'token': {data}", file=sys.stderr)
        sys.exit(1)
    return token


def trigger_embedding(token: str, file_id: str, pdf_path: Path, game: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    entity_id = game.lower().replace(" ", "-")
    with open(pdf_path, "rb") as f:
        resp = requests.post(
            f"{RAG_API_URL}/embed",
            headers=headers,
            data={"file_id": file_id, "entity_id": entity_id},
            files={"file": (pdf_path.name, f, "application/pdf")},
            timeout=300,
        )
    if resp.status_code != 200:
        print(f"Error: RAG embedding failed ({resp.status_code}): {resp.text}", file=sys.stderr)
        sys.exit(1)
    data = resp.json()
    if not data.get("status"):
        print(f"Error: RAG API returned failure: {data.get('message')}", file=sys.stderr)
        sys.exit(1)
    print(f"Embedding complete: {data.get('message')}")


def main():
    args = parse_args()
    pdf_path = Path(args.file)
    if not pdf_path.exists():
        print(f"Error: file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    if not pdf_path.suffix.lower() == ".pdf":
        print(f"Error: expected a .pdf file, got: {pdf_path.suffix}", file=sys.stderr)
        sys.exit(1)

    email = get_env("LIBRECHAT_EMAIL")
    password = get_env("LIBRECHAT_PASSWORD")

    print(f"Ingesting {pdf_path.name} for game: {args.game}")
    print("Authenticating with LibreChat...")
    token = authenticate(email, password)
    print("Authentication successful.")

    file_id = str(uuid.uuid4())
    print("Triggering RAG embedding (this may take a few minutes)...")
    trigger_embedding(token, file_id, pdf_path, args.game)

    print(f"\nDone! File ID: {file_id}")
    print(f"Attach this file_id to your '{args.game}' agent in LibreChat.")


if __name__ == "__main__":
    main()
