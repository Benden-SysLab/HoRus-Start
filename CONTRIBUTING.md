# Contributing

HoRus-Start covers SSH bootstrap, Debian/Proxmox base preparation and four-node cluster formation. Keep changes within that scope unless the project's scope is explicitly revised. Disk management, GPU passthrough, VM templates and applications are separate tasks.

Do not commit passwords, private keys or generated `runtime/` reports. Before proposing a change, run Ansible syntax checks for the three playbooks and `python3 scripts/validate_schemas.py`. Describe which nodes or services a change can affect and whether a rerun is safe.
