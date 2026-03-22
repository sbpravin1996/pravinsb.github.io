#!/usr/bin/env python3
"""CLI entry point: ingest PDFs or query the RAG pipeline."""

import argparse
import sys

from src.ingest import ingest
from src.rag import query


def main():
    parser = argparse.ArgumentParser(description="Local RAG pipeline for PDFs")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("ingest", help="Load PDFs from data/, chunk, embed, and store")

    query_parser = subparsers.add_parser("query", help="Ask a question")
    query_parser.add_argument(
        "question",
        nargs="?",
        default=None,
        help="Question to ask (or omit for interactive mode)",
    )

    args = parser.parse_args()

    if args.command == "ingest":
        ingest()
    elif args.command == "query":
        q = args.question
        if q is None:
            print("Enter your question (Ctrl+C to quit):")
            try:
                q = input("> ").strip()
            except KeyboardInterrupt:
                sys.exit(0)
        if not q:
            print("No question provided.")
            sys.exit(1)
        answer = query(q)
        print(answer)


if __name__ == "__main__":
    main()
