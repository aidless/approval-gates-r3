# Provenance correction

The first R2 writing-log record accidentally used an invalid placeholder evidence digest. It is preserved as an invalid record in the append-only audit log; the immediately following correction supersedes it and contains the actual SHA256 of evidence_manifest.json. Do not treat the first digest as authentic evidence. No raw experiment record or published artifact was altered.

Actual digest: 259666d73184614a9d5e594365d00bf2e99f863d068dbc9276afe60a5284956c
