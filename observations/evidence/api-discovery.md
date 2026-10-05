# Direct backend request provenance

Observed 30 September 2026 through Playwright Chromium's actual browser request/response events while navigating the public home page and then the known assessment project `/workflow/0` in an unauthenticated context. This is the same network traffic available in DevTools Network, not a guessed URL. Private full captures, if made, remain ignored under `artifacts/`.

| Method | Observed endpoint | Status | Response content |
|---|---|---|---|
| GET | `https://api.rhombusai.com/api/accounts/users/profile` | 401 | `{"detail":"Unauthorized"}` |
| GET | `https://api.rhombusai.com/api/accounts/users/project-limit` | 401 | `{"detail":"Unauthorized"}` |

Both responses were `application/json; charset=utf-8`. The direct API suite replays those read-only requests, asserts exact status and response contents, and adds an invalid-token variant. These test authentication boundaries, not pipeline execution. Add authenticated pipeline-run API coverage after observing the real run endpoints during the live journey.

Reproduce discovery: `node scripts/discover-public.mjs`. This opens an isolated signed-out browser, reads the pages, saves a redacted network summary and screenshot under `artifacts/`, and closes it.

## Output download request — 5 October

The inbuilt browser's supported page-asset inventory reported this actual
`xmlhttprequest` resource after CSV download attempts from the output preview:

```text
GET https://api.rhombusai.com/api/dataset/analyzer/v2/projects/0/nodes/output-download
node_name=output_40ec5f2cb904bb2f4fa10c284d282375
format=csv
custom_filename=orders-clean
```

CSV without the custom filename and XLSX variants were also observed. This
inventory identifies the request URL but does **not** expose the authenticated
response status/body. The asset-bundling capability does not support this type
of resource. The candidate reported “download stopped”; the download cause is
unresolved. A direct unauthenticated test was added for this observed endpoint;
its result tests data-access protection, not authenticated export correctness.

Direct replay result: **401**, `application/json`, exact body `{"detail":"Unauthorized"}`. The new test passed on 5 October.
