# Migration integrity status after cleanup

The original migration ledger `SHA256SUMS.txt` describes the unmodified V40 ZIP
as extracted on 2026-09-20. It is retained as a historical ledger, not as the
current workspace checksum file.

After intentional cleanup:

- original ledger entries: 1297;
- present and matching: 856;
- intentionally absent: 441;
- present but hash-mismatched: 0.

Of the 441 absent entries, 411 belong to the historical
`sandbox_snapshot/mnt_data/c33_v38/venv` tree. The remainder are Python bytecode
and test caches. No research source, decision document or structured result was
reported as hash-mismatched.

The original ZIP remains available at:

`/Users/slumpyfufu/Downloads/AM_AUTO_20260918_R1_FINAL_SANDBOX_MIGRATION_20260919.zip`

ZIP SHA-256:

`a673b88582cb01a76f53d0c3139357c289bacc75b27adb6c098cea55c17bf66c`

Current V42–V44 assets are independently covered by their version-specific
SHA-256 manifests. See the root `README.md` for paths.
