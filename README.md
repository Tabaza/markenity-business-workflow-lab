# Markenity Business Workflow Lab

Small, reproducible failure checks for teams commissioning a website, campaign workflow or document assistant. Run locally with Python's standard library. No signup, customer records, email service, CRM or tracking call is involved.

## Start in one minute

Requires Python3.10 or newer.

```sh
git clone https://github.com/Tabaza/markenity-business-workflow-lab.git
cd markenity-business-workflow-lab
python -m unittest discover -s tests -v
```

## What is inside?

| Exercise | Buyer question | Boundary tested |
|---|---|---|
| Intake/outbox | Can the system promise acceptance without losing the follow-up job? | Atomic insert, repeated requests, conflicting retries, provider failure and lost acknowledgement. |
| Campaign labels | Can we identify the campaign without exporting arbitrary query strings? | Exact approved values, duplicate rejection, unrelated contact fields and oversized inputs. |
| Approval binding | Does yesterday's approval still authorize today's edited draft? | Exact proposal, revision, content digest, action and expiry boundary. |

Each module and its tests are teaching fixtures. Passing these tests does not certify a production system. The outbox has one sequential worker, an in-memory SQLite database and a fake provider. Approval objects are plain data, not trusted/signed credentials; authentication, permission checks, durable storage and atomic compare-and-execute still belong to a real implementation. Campaign filtering covers only the returned dictionary, not other SDKs, cookies, IP addresses or network metadata.

## How to use the exercises in a project review

1. Ask the supplier to identify where each relevant boundary is enforced in the real workflow.
2. Reproduce failures in a safe test environment using synthetic information.
3. Assign an owner to each recovery path, including a queue item that needs manual review.
4. Save the evidence and record which parts were not tested.

A screenshot of a green success message is useful UI evidence. It is not evidence that an enquiry was delivered, assigned or answered. A model's confidence is not permission to perform an action. An analytics label is not permission to send a whole URL.

## Further reading

- [Markenity's practical guide to website lead routing](https://markenity.com/en/insights/website-lead-routing-hubspot-n8n/)
- [A form success message is a promise](https://markenity.wordpress.com/2026/11/24/form-success-enquiry-handoff-failure-tests/)
- [English/Arabic form parity](https://markenity.wordpress.com/2026/11/24/bilingual-form-parity/)
- [Document permission acceptance tests](https://markenity.wordpress.com/2026/11/24/ai-document-permission-tests/)
- [SQLite transactions](https://www.sqlite.org/lang_transaction.html)
- [Python unittest](https://docs.python.org/3/library/unittest.html)

Published by [Markenity](https://markenity.com/), a marketing and technology team serving B2B companies in Jordan, Saudi Arabia and the UAE. This repository is a public educational resource, not client work, a production deployment or independent validation of the company. No customer results or production performance figures are asserted.

Code: MIT. Examples use synthetic values only.
