# V42 execution incidents

## Pre-formal configuration abort

The first formal launch was interrupted before any case result was written after
discovering that Mem0 classified `deepseek-flash` as a regular model and therefore
did not transmit the intended low reasoning effort. V42 was patched prospectively
to send low reasoning explicitly, re-tested, and restarted in a new directory.

## Local-proxy outage and fail-closed recovery

The main V42 run completed cases 1–9. During case 10 the local proxy at
`127.0.0.1:7891` stopped listening. Case 10 ended with a connection failure; cases
11 and 12 then failed immediately. The runner marked the cohort incomplete.

Direct access to the official DeepSeek API was tested successfully. The same
results directory was resumed with `--resume`, which verified and skipped cases
1–9 and reran only cases 10–12. All three completed. The final manifest reports
12 entries and zero failures, and all final result files pass SHA-256 verification.

The network failures are infrastructure events, not scientific nulls, and were
not included in the final analysis.
