# Current S3 destination and permission scope

The candidate created an AWS key and explicitly authorized using that existing
credential in Rhombus. Destination **64** is now connected. The agent did not
generate or retrieve a secret from AWS. No key or secret is stored in the project.

The sole inline policy for `assessment-export-example` grants bucket location/list
and GetObject/PutObject only to `orders-clean.csv` in the dedicated assessment bucket,
expiring **5 October 18:30 Sydney / 07:30 UTC**. Console access is disabled;
other object reads, delete and other AWS services are not granted. The candidate
explicitly approved the exact-file read addition after the credit redemption.
[Applied policy](../config/aws-destination-policy.json).

Connection setup writes a 103-byte root object named
`rhombus-ai-write-permission-test-file-…tmp`. The candidate approved one temporary
root-write connection test excluding input/. It succeeded, and the temporary
grant was immediately removed. The marker remains because no delete was granted.
This marker is not cleaned-data output.

The filename UI rejects `output/orders-clean`. It accepts `orders-clean`, and the
candidate approved changing writes to the exact root CSV. A subsequent manual
pipeline run still failed at orders_output, while also logging completed
successfully. The detailed AWS exception, actual key and job ID were unavailable
through the diagnostic assistant. A prefix/operation mismatch is a hypothesis,
not an established cause. Subsequent jobs have IDs recorded in the diagnostic
file, but the provider exception and attempted key remain unavailable. Adding
the documented exact-file read action and rebuilding the output node did not
repair export. Do not broaden permissions on that hypothesis alone.

[Redacted observations](../observations/evidence/s3-destination-diagnostic-20261005.json).
Existing direct AWS location/list/tiny-marker writes returned HTTP 200; those
diagnostics are separate from the still-unverified pipeline export.

Permission expiry does not deactivate the key itself. Deactivate the credential
after testing with the candidate's authorization; do not delete the user or
versioned bucket as part of evidence preparation. Google Cloud stays unused.
S3 is a candidate-approved deviation from GCS; employer acceptance is unconfirmed.
