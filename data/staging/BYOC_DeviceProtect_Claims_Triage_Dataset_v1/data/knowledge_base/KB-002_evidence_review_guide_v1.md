# Evidence Review Guide

**Document ID:** KB-002  
**Version:** 1.0  
**Effective date:** 2026-06-23  
**Purpose:** Guide evidence handling for DeviceProtect smartphone claims. Evidence requirements are authoritative only when retrieved from the Evidence Profile Requirements dataset and the Policy Rule Catalog.

## 1. Evidence-review principles

- Evidence validates a potentially eligible claim; it does not create coverage.
- A required document can be **present**, **missing**, **unreadable**, **invalid**, or **contradictory**.
- Missing or unreadable mandatory evidence normally requires a targeted follow-up.
- Contradictory or materially invalid evidence requires analyst review; do not infer fraud or issue an automated decline.
- Optional evidence can support repair feasibility or cost context but should not block progression unless a separate rule makes it required.

## 2. Evidence profiles

Use the evidence profile linked to the applicable claim category:

| Claim category | Evidence profile | Primary required evidence |
|---|---|---|
| SCREEN_DAMAGE | EVD-SCREEN-01 | Damage photo |
| ACCIDENTAL_DAMAGE | EVD-ACCIDENTAL-01 | Damage photo |
| LIQUID_DAMAGE | EVD-LIQUID-01 | Damage photo |
| MECHANICAL_BREAKDOWN | EVD-MECHANICAL-01 | Diagnostic report |
| THEFT | EVD-THEFT-01 | Police report reference |

Repair quotes are supporting evidence where available and may be useful for repair feasibility or high-cost review. They are not automatically a reason to proceed or decline.

## 3. Evidence status handling

| Evidence status | Operational handling |
|---|---|
| VALID | Use the documented fact only within its stated scope. |
| MISSING | Ask for the specific required document or detail. |
| UNREADABLE | Ask for a clearer or complete re-upload. |
| INVALID | Route to manual review when validation controls identify a material issue. |
| CONTRADICTORY | Route to manual review and identify the specific conflict. |
| NOT_REQUIRED | Do not request it solely because it is commonly submitted. |

## 4. Examples of targeted requests

- **Damage photo missing:** “Please upload one or more clear photos showing the reported device damage.”
- **Diagnostic report missing:** “Please provide a diagnostic report or repair-provider assessment describing the device malfunction.”
- **Police report reference missing:** “Please provide the police report reference for the reported theft incident.”
- **Unreadable document:** “The submitted document could not be read clearly. Please upload a complete, legible copy.”

## 5. Consistency checks

Flag for review when evidence materially conflicts with structured facts or the reported incident. Typical examples include a document date inconsistent with the stated incident date, a repair report for a different device identifier, or a document describing a materially different event category. The agent must describe the inconsistency neutrally and avoid conclusions about intent.

## 6. References

- Evidence Profile Requirements v1: Item #7
- EVD-001 and EVD-002: Policy Rule Catalog v1 (Item #3)
- Follow-up Communication Guide: KB-003
- Manual Review and Escalation SOP: KB-004
