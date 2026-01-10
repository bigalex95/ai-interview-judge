# 🔧 Utility Scripts

This directory contains utility scripts for managing the AI Interview Judge system.

## 🚀 Quick Start

### System Management

- **[start.sh](start.sh)** - Start all services (Docker Compose)

  ```bash
  ./scripts/start.sh        # CPU version
  ./scripts/start.sh gpu    # GPU version
  ```

- **[status.sh](status.sh)** - Check system status and health
  ```bash
  ./scripts/status.sh
  ```

## 🌍 Public Sharing

### Share Your Project

- **[share.sh](share.sh)** - Share via ngrok (requires registration)

  ```bash
  ./scripts/share.sh
  ```

- **[share-cloudflare.sh](share-cloudflare.sh)** - Share via Cloudflare Tunnel (no registration)
  ```bash
  ./scripts/share-cloudflare.sh
  ```

### Documentation

See [../docs/SHARING_GUIDE.md](../docs/SHARING_GUIDE.md) for detailed sharing instructions.

## 🏗️ Build Scripts

- **[build.sh](build.sh)** - Build C++ core module

## 💡 Usage Tips

All scripts should be run from the project root:

```bash
# From project root
./scripts/start.sh
./scripts/status.sh
./scripts/share.sh

# Or with explicit path
cd /path/to/ai-interview-judge
./scripts/script-name.sh
```

## 🔙 Back to Main

See [../README.md](../README.md) for the main project documentation.
