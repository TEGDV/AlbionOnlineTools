# Obsidian — Albion Online Tools

Obsidian is a high-performance web application designed for Albion Online players to build, manage, and export custom party compositions. Built on a modern tech stack, Obsidian utilizes FastAPI, Alpine.js, Tailwind CSS v4, and Bun to deliver a pixel-perfect, lightning-fast user experience with an aesthetic inspired by the Obsidian theme.

## Features

- **Party Composition Builder**: Drag-and-drop Albion Online equipment slots to design tactical group compositions.
- **Vault (Inventory) search**: Quick filtering of weapons, armors, accessories, and consumables.
- **Role swap manager**: Configure multiple build setups ("Main", "Swap 1", "Swap 2", etc.) per player role.
- **Image exporter**: Export pixel-perfect representations of compositions as PNG files using Playwright.
- **In-memory caching**: Fast loading and image encoding with database safety and isolation.

## Tech Stack

- **Backend**: Python 3, FastAPI, Jinja2 Templates, Playwright (for PNG rendering), Pydantic
- **Frontend**: Alpine.js, Vanilla CSS / Tailwind CSS v4
- **Runtime & Tooling**: Bun, Tailwind CLI

## Project Structure

```
├── data/
│   └── db_group_builds.json      # Isolated local database file (git-ignored)
├── models/
│   ├── database.py               # Albion items definitions database
│   ├── db_group_builds.py        # Group compositions database loader and model schema
│   └── item_model.py             # Item schema definition
├── static/
│   ├── css/
│   │   ├── input.css             # Tailwind source stylesheet (custom component utilities)
│   │   └── output.css            # Compiled production stylesheet
│   ├── html/                     # Jinja2 layout and views templates
│   ├── items/                    # Local item icons assets repository
│   └── js/                       # Client-side Alpine.js page controllers
├── utils/
│   ├── helpers.py                # Base64 image encoding and disk caching helpers
│   └── processors.py             # Dehydration / Hydration database processors
├── dev.py                        # Python development server runner
├── main.py                       # FastAPI application entry point
├── package.json                  # Bun package setup
└── README.md                     # Documentation
```

## Getting Started

### Prerequisites

- Python 3.10+
- [Bun](https://bun.sh) (v1.2+)

### Installation

1. Clone the repository and navigate into the project directory:
   ```bash
   git clone <repository-url>
   cd PersonalAlbionProject
   ```

2. Create a Python virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install fastapi uvicorn fastapi-cache2 playwright jinja2
   python -m playwright install
   ```

3. Install Bun dev tools and Tailwind compilation CLI:
   ```bash
   bun install
   ```

### Development

To start the Tailwind CSS watcher compiler and Python FastAPI application concurrently:

```bash
bun run dev
```

The application will be running locally at `http://127.0.0.1:8000`.

### Production Build

To compile and minify the Tailwind CSS stylesheet:

```bash
bun run build:css
```
