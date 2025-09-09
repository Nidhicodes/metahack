# SourceSense

SourceSense is a data source application built using the Atlan Apps Framework. It connects to the GitHub API to extract and display metadata about a repository.

## Features

- **Metadata Extraction:** Extracts repository details, README content, and file tree from any public GitHub repository.
- **Web Interface:** A simple, clean web interface to input a GitHub repository URL and view the extracted metadata.
- **Temporal Workflows:** Uses Temporal for robust and reliable workflow management.
- **Atlan Apps Framework:** Built on the Atlan Apps Framework, demonstrating its capabilities for building data applications.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- [Dapr CLI](https://docs.dapr.io/getting-started/install-dapr-cli/)
- [Temporal CLI](https://docs.temporal.io/cli)
- A GitHub Personal Access Token (PAT) with `repo` scope. You can create one [here](https://github.com/settings/tokens).

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Set up the environment:**
   - Create a `.env` file from the `.env.example`:
     ```bash
     cp .env.example .env
     ```
   - Add your GitHub PAT to the `.env` file:
     ```
     GITHUB_TOKEN="your_github_pat"
     ```

3. **Install dependencies and start the application:**
   - The sample applications from Atlan use a `poe` task to download and start dependencies. This project does not have `poethepoet` configured yet. You will need to start dapr and temporal manually in separate terminals.

   - **Start Temporal:**
     ```bash
     temporal server start-dev --db-filename ./temporal.db
     ```

   - **Start Dapr:**
     ```bash
     dapr run --enable-api-logging --log-level debug --app-id app --app-port 3000 --dapr-http-port 3500 --dapr-grpc-port 50001 --dapr-http-max-request-size 1024
     ```

   - **Run the application:**
     ```bash
     uv run main.py
     ```

4. **Access the application:**
   - **Web Interface:** http://localhost:8000
   - **Temporal UI:** http://localhost:8233


├── tests/              # Test files
├── main.py             # Application entry point
├── pyproject.toml      # Dependencies and config
└── README.md           # This file
```
