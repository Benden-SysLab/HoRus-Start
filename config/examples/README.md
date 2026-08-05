# Configuration Examples

This directory contains template and example configuration files for HoRus-Start v2.

To customize your cluster configuration, copy any of these examples to the parent `config/` directory:

```bash
cp config/examples/cluster.example.yml config/cluster.yml
cp config/examples/network.example.yml config/network.yml
cp config/examples/storage.example.yml config/storage.yml
```

## Files Overview

- **`cluster.example.yml`**: Defines cluster name, node hostnames, and node roles.
- **`network.example.yml`**: Maps target node hostnames to management IP addresses.
- **`storage.example.yml`**: Configures physical disk storage allocations, mount points, and PVE storage definitions by persistent disk ID (`/dev/disk/by-id/`).
