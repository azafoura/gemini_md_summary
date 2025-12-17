This workflow processes a Markdown document through the Gemini API to produce a structured summary.

It runs autonomously with no human intervention once started.
The workflow reads a Markdown file, calls Gemini, and validates the response deterministically.
API failures are retried up to three times with exponential backoff.
Schema validation failures trigger a single retry.
All execution steps are logged as flat JSON events.
On terminal failure, an alert is emitted.

Configuration is handled via environment variables.
To run: set GEMINI_API_KEY, pip install requests and execute `python main.py -i input.md`.
