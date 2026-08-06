# 13 — Template Recovery & The Rebuild Doctrine

In an enterprise Infrastructure-as-Code environment, virtual machine templates are treated as **ephemeral, reproducible artifacts**. This document details the **Rebuild Doctrine** and disaster recovery procedures.

---

## 🚫 The Golden Rule: Never Repair a Corrupted Template

> 🛑 **ARCHITECTURAL MANDATE**: If an existing Golden Template exhibits configuration drift, package corruption, missing keys, or unexpected runtime errors, **DO NOT ATTEMPT TO REPAIR IT**. 
>
> Un-templating a Proxmox VM, modifying it manually, and re-converting it introduces hidden state, un-audited history, and non-reproducible artifacts. **Destroy the corrupted template and rebuild it from source using the documented build sequence.**

```
[ Corrupted / Stale Template Detected ]
                 │
                 ▼
    DO NOT EDIT IN-PLACE!
                 │
                 ▼
1. Mark Stale Template as Deprecated (`qm set <vmid> --description "DEPRECATED"`)
                 │
                 ▼
2. Execute Fresh Assembly Sequence (Docs 01 -> 09)
                 │
                 ▼
3. Validate Candidate Template via 12-validation.md
                 │
                 ▼
4. Assign New Version Tag & Convert to Template
                 │
                 ▼
5. Destroy Old Template (`qm destroy <old_vmid>`)
```

---

## 🛠️ Step-by-Step Template Recovery Procedure

### Step 1: Identify and Deprecate the Faulty Template
Rename or tag the compromised template in Proxmox to prevent new clones from spawning off it:

```bash
# Append DEPRECATED flag to VM description
qm set 9000 --description "DEPRECATED - Corrupted GPG Keys - Do Not Clone"
```

### Step 2: Assemble Replacement Template from Clean Media
Follow [02-debian-9000-base.md](./02-debian-9000-base.md) to build a new candidate instance on a temporary VM ID (e.g., `90009`):

```bash
# Example: Create new candidate shell on ID 90009
qm create 90009 --name "debian-13-trixie-base-candidate" ...
```

### Step 3: Run Full Validation Suite
Execute the entire audit checklist in [12-validation.md](./12-validation.md) against candidate VM `90009`.

### Step 4: Destroy Old Template & Promote New Template
Once candidate `90009` passes 100% of validation checks:

```bash
# 1. Destroy old corrupted template 9000
qm destroy 9000 --purge 1

# 2. Clone candidate 90009 to official template ID 9000
qm clone 90009 9000 --name "debian-13-trixie-base" --full 1

# 3. Convert VM 9000 to official Template
qm template 9000

# 4. Clean up temporary candidate shell
qm destroy 90009 --purge 1
```
