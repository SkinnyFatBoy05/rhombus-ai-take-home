# Synthetic orders contract

All names and addresses are invented; emails use reserved example.com. Input header:
`order_id,customer_name,email,amount,order_date,country`.

Business meaning: positive USD amounts, US month/day dates. Valid amount range is 0 < amount <= 10000. The intended dates in this fixture are in September 2026. No FX conversion. These are explicit test-domain rules, not claimed Rhombus defaults.

1. Trim every field. Uppercase order IDs and country codes. Lowercase emails.
2. Missing name becomes `Unknown`; missing email becomes `unknown@example.com`.
3. Remove `$` and grouping commas from amount, parse using decimal arithmetic, require at most two decimal places and a finite value in range. Emit two decimal places.
4. Parse input dates strictly as `%m/%d/%Y`; emit ISO `YYYY-MM-DD`.
5. Reject a row with missing order ID, malformed nonblank email, invalid/out-of-range amount, impossible date or country outside AU/US/NZ.
6. Remove duplicates after normalization, retaining the first valid occurrence of each order ID. Preserve no rejected rows; no fabricated totals or rows.
7. Emit exactly the six named columns, in the declared order, sorted by order_id.

The baseline has 12 source rows: 6 accepted unique orders, 1 duplicate and 5 rejected rows. The hand-reviewed golden file is `datasets/expected/baseline-clean.csv`; it is **not a GCS export**. The Python oracle is independent of the platform and must never be uploaded as a manual transformation.

Schema mutations: remove `email`; rename `amount` to `total_amount`; replace numeric amounts with `USD <number>` strings; add `campaign`; combine all four. The validator reports input schema changes even if Rhombus continues. Missing/renamed required columns do not get silently repaired by the oracle. Numeric-to-text is a value/type-contract change in CSV (CSV itself has no physical typed columns).

Semantic mutations: multiply numeric amounts by 100 with the same header (dollars -> cents); swap valid date month/day components (MM/DD -> DD/MM). Dates deliberately remain parseable in both formats. Ground-truth canaries are the six known baseline orders, whose intended amounts/dates do not change. This catches silent errors that schema/type/range checks alone can miss. The expected values come from the controlled experiment, not general anomaly detection; an unknown production dataset would need an external business reference.

For drift runs, report detection separately from data correctness. A schema warning or failure to produce output is not a valid clean output. A safe pipeline stop can still be a useful platform result. For post-fix testing, give the AI the intended meaning and require the original six-order business result where recovery is possible. Keep initial and fixed runs separately, and freeze the configuration for each determinism group.
