# Observed UI controls — 30 September 2026

These are live browser observations, not proof of an executed CLI suite.

## Source

1. AI Builder tab → unnamed attachment menu. Observed selector:
   `button.workflow-composer-control[aria-haspopup="menu"]` filtered to empty
   text. The other button matching those classes is the named model selector.
2. Menu item **Third party sources** → dialog **Third Party Data**.
3. **Add Data Sources** → heading **Amazon S3**.
4. Textbox **Bucket\***, combobox **Region\***, then regional option.
5. Expand **Optional settings Folder, source name, and KMS encryption**.
   Folder placeholder `analytics/q1/`; source-name placeholder `Q1 analytics`.
6. **Connect S3 source** verifies the pre-granted scoped bucket policy.
7. For this account the existing heading **assessment-orders-s3** is followed
   by **Connected**; **Browse files** shows `input/orders.csv`, 669 B, and
   `1 supported file loaded · ap-southeast-2`.

Do not count a connection dialog closing as success. Assert Connected and the
exact expected source object. Do not click Disconnect as test cleanup: this
source is reused by the assessment pipeline.

## Builder and output

The AI Builder contains a textarea with `data-rcb-element="chat-input-textarea"`
and an unnamed arrow-up submit button. Typing `/` exposes button **Pipeline
/pipeline Focus this turn on pipeline and canvas work**. Selecting it adds a
Pipeline chip and **Clear active command**. Enter submits the text.
The AI's generated node chips include **orders_raw**, **orders_cleaned**,
**Node icon orders_sorted**, and **orders_output**. Clicking a node chip selects
its Transform panel. Generated names are prompt-dependent.

**orders_output** → Data Output panel → **Add New Destination** → dialog
**Select Destination Provider** → heading **Amazon S3** → dialog
**Add New Destination**. Observed labelled inputs: **Access Key \***,
**Secret Key \***, **Region \*** (native select) and **Bucket Name \***.
Buttons **Create Destination**, **Cancel**, **Back**. This form has not been
submitted. Its success/result controls are therefore not yet calibrated.

The Data Output panel also offers **Download Locally**, format CSV, filename
placeholder `RhombusAI_output`, and **Apply**. This fallback was selected and
the canvas displayed **Data Output Export to Download Locally (csv)**. It
cannot be recorded as GCS output.

## Preview and logs

Select a node, then **Preview**. **Node Preview** contains an actual table.
**Download** opens a menu; choose **Download as CSV** or **Download as Excel
(XLSX)**. Wait for the download event after choosing the format, not after
opening the menu. Inbuilt-browser CSV capture timed out; cause unestablished.

Never assert success using the generic log line "Pipeline execution completed
successfully." It appeared alongside actual pipeline failures. Inspect the
structured pipeline summary's status/error and the produced data.

## Schedule

**Schedule** → **Add Schedule** → dialog **Create Schedule** → frequency
combobox → **Custom** → label **Custom Cron Expression** → toggle button
**Notify on failure** to `aria-pressed=false` → **Create**. The frequency
combobox has a hidden native counterpart; target the visible control.

The schedule card has an unnamed history button containing `svg.lucide-history`
and an edit button containing `svg.lucide-pencil`. Edit opens **Edit Schedule**
with **Custom Cron Expression** and **Update**. The switch is named
**Deactivate schedule** when active and **Activate schedule** when inactive.
Use a click followed by an awaited state assertion: the server update is
asynchronous and immediate `setChecked` verification can run too early.

History opens the **Executions** tab, with columns Execution, Started, Duration,
Status, Failed Node and Completed Nodes. Actual observed content was **No
results.**; successful row formatting remains unverified. The CLI parser
therefore fails closed if status/node count cannot be recognized. Both schedule
trials were deactivated; the final card is Inactive, notifications off.
