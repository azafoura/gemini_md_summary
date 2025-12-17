This workflow processes a Markdown document through the Gemini API to produce a structured summary.

It runs autonomously with no human intervention once started.
The workflow reads a Markdown file, calls Gemini, and validates the response deterministically.
API failures are retried up to three times with exponential backoff.
Schema validation failures trigger a single retry.
All execution steps are logged as flat JSON events.
On terminal failure, an alert is emitted.

Configuration is handled via environment variables.

To run:
1. Set GEMINI_API_KEY
2. Install dependencies
3. Run: python main.py -i input.md
