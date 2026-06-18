# Security model

## Protected assets

- Files outside the target repository.
- User-modified managed content.
- Existing project instructions outside PSP blocks.
- Credentials and private operational data.
- Production systems, data, access controls, billing, and shared history.
- The truthfulness of execution and verification claims.

## Controls

- Relative-path normalization and target-root confinement.
- Rejection of symlink path components.
- Full-plan conflict detection before mutation.
- Operation lock, staging, backup, atomic replacement, and rollback.
- Embedded lifecycle archive hash verification, bounded extraction, duplicate/path traversal rejection, and symlink rejection.
- Hash-based drift detection and conservative uninstall.
- Scope-bound safety approvals before high-impact actions.
- Trace redaction, claim-specific evidence semantics, upstream verification checks, scoped/expiring approvals, ordering checks, and stale-verification detection.

## Non-goals

PSP cannot force every host model to obey instructions when the host exposes no enforcement API. It cannot replace repository permissions, branch protection, sandboxing, code review, production change management, or secrets management. Behavioral reliability must be measured with host traces and evals.
