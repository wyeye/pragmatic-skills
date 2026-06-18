# Primary mode matrix

| Signal | Fast Patch | Exploration | Standard Change | Strict Change |
|---|---:|---:|---:|---:|
| User requests implementation | Yes | No | Yes | Yes |
| Tiny and fully specified | Required | Not relevant | No | No |
| Read-only intent | No | Required | No | No |
| Material requirements/design work | No | May discover facts | Often | Often |
| Production/data/auth/billing/destructive impact | No | Analysis only | Re-triage | Required |
| Explicit safety approval | No | No execution | Only if re-triaged | At execution boundary |
| Final verification | Targeted | Evidence validation | Risk-based | Strong plus rollback/containment |

Only one primary mode is active at a time. Re-triage changes the active mode rather than stacking multiple modes indefinitely.
