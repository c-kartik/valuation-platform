# Stage 1 — Apple FCFE financing execution

4 November 2026. **Source replay passes; full FCFE remains OPEN.** The approved action is executed as an evidence-bound classification and calculation review. An exact numerical fix is not possible from the retained disclosures: a complete statement sum establishes cash completeness at caption level, not the economic content of the unsplit Other caption or finance-lease cash principal containment.

No old source, approval, runtime amount, forecast or valuation is changed. The [classification CSV](financing-classifications.csv) lists every disclosed financing row once with source period, table, row, column, inline ID and receipt hash. [Results](results.json) retain primary/instance evidence for each row and independently rebound CFO and cash PP&E. The original FY2021-to-later-comparative stock presentation bridge is also replayed.

## Five-year result

USD millions. These are exact arithmetic on the identified funding perimeter, **not verified full FCFE**.

| FY | CFO less cash PP&E | Identified net borrowing | Provisional FCFE | Unallocated Other | Full FCFE |
|---|---:|---:|---:|---:|---|
| 2021 | 92,953 | 12,665 | 105,618 | −129 | Unresolved |
| 2022 | 111,443 | −123 | 111,320 | −160 | Unresolved |
| 2023 | 99,584 | −9,901 | 89,683 | −581 | Unresolved |
| 2024 | 108,807 | −5,998 | 102,809 | −361 | Unresolved |
| 2025 | 98,767 | −8,483 | 90,284 | −111 | Unresolved |

Identified net borrowing includes the separately disclosed term-debt issuance **net** line, term-debt repayments and net commercial-paper cash once. “Net” issuance must retain its disclosed net presentation; no gross proceeds/fees split is invented. Common-stock issuance, buybacks, common dividends/dividend equivalents and employee award withholding remain outside borrowing. Their exclusion from net borrowing does not assert that they have no separate equity-valuation significance.

Other remains an explicitly unallocated cash row. Its debt component, actual consolidated finance-lease principal, and containing parent caption remain `null`, never zero. Finance-lease principal must not be deducted again if already contained in an identified parent cash population. Small net Other is not a gross bound. Liability stock changes, prospective maturities, ROU additions and subsidiary IFRS payments cannot substitute for annual consolidated USGAAP principal.

## Executed steps and remaining dependency

1. Bound the selected five original annual primary/instance source pairs and verified source hashes, fiscal dates, units, primary inline observation and extracted-instance agreement.
2. Rebound every financing row, preserved its actual sign, rejected duplicate or omitted source cells, and reproduced all five zero-difference financing statement sums.
3. Rebound ten CFO/cash-PP&E inputs and reproduced all five provisional FCFE figures with no numerical change.
4. Replayed FY2021's known equity reclassification: original Other −129M plus common-stock proceeds 1,105M equals later Other 976M. This fixes presentation, not the original Other classification.
5. Preserved unsupported Other and finance-principal classifications as unknown. Existing bounded research already examined notes, quarterlies, later comparatives and annual calculation/presentation relationships; repeating those absence searches supplies no new figure.
6. Prepared a precise [issuer evidence request](issuer-evidence-request.txt). It has **not been sent**; no authority to contact Apple was inferred.

**Closure:** obtain source-supported transaction composition for Other and actual finance-principal cash plus parent-caption containment, or a complete liability roll-forward that isolates principal without residual assumptions. Then classify each economic cash flow once, recalculate, independently review and adopt. An issuer answer is an external dependency, not something implementation can manufacture.

## Replay

From the repository root:

```sh
.venv/bin/python docs/company-resolutions/AAPL/remaining-issues-2026-11-04/financing/replay.py
.venv/bin/python -m unittest discover -s docs/company-resolutions/AAPL/remaining-issues-2026-11-04/financing -p 'test_*.py' -v
```

Replay is offline and byte-compares only this stage's results/CSV. `--write` regenerates this folder's outputs. It never writes the historical source bank or accepted runtime inputs. Both stage and parent status distinguish successful evidence replay from unresolved financial classification.
