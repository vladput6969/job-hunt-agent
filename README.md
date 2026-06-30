# Job Hunt Agent

An AI-powered, locally-run agent that discovers, scores, and ranks job opportunities against your profile — and in later phases, drafts applications and outreach for your approval before anything leaves the system.

---

## Quick Start

```bash
git clone https://github.com/vladput6969/job-hunt-agent.git
cd job-hunt-agent
./setup.sh
```

`setup.sh` installs and configures everything: Homebrew, Python 3.12, MongoDB, Ollama, the `llama3.1:8b` model, the Python virtualenv, and your `.env` file. Safe to re-run.

Once setup is done:

```bash
source .venv/bin/activate
python main.py
```

---

## Documentation

| Doc | Description |
|-----|-------------|
| [PREREQUISITES.md](docs/PREREQUISITES.md) | Manual walkthrough of what `setup.sh` installs — useful if you prefer to install things yourself |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture, design principles, agent roster |
| [HLD.md](docs/HLD.md) | High Level Design — components, tech stack, phased delivery |

---

## Phases

- **Phase 1 (current):** Profile parsing → job discovery → scoring → ranked report. No outbound.
- **Phase 2:** Draft generation → CLI approval queue → send executor.
- **Phase 3:** Learning loop → follow-up agent → outreach effectiveness tracking.
