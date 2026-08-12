# Critical-Service Assessment Wizard Guide

> Synthetic demonstration only. Do not enter secrets, credentials, regulated customer data, or real sensitive architecture.

Open the Streamlit **Critical-Service Assessment Wizard** tab. The 16-step progress control supports previous/next navigation, direct review, explicit atomic draft saves, JSON import/export, version comparison, and read-only approved assessments. Unknown, Evidence unavailable, and Requires review are valid responses. The reusable record editor covers services, impacts, tolerances, processes, applications, data, infrastructure, control planes, security, roles, providers, workarounds, recovery, evidence, relationships, and approvals. Each editor supports validated create/edit, view, duplicate, archive, and confirmation-delete operations. Record fields are shown in an editable JSON form so nested lists and relationship identifiers remain explicit rather than hidden by a flattened table.

Drafts are stored in the Git-ignored `data/private_assessments/`; only the Harbor Ridge demonstration is tracked. Submitting a record and navigating between completed steps durably saves the assessment using same-directory temporary files, validation, filesystem synchronization, and atomic replacement. Saving an existing draft creates version history. Archive is non-destructive; deletion requires explicit confirmation.

Completeness is reported separately for data entry, ownership, evidence, approvals, and testing. No universal risk score is produced. Automated analysis recommends review items and never replaces accountable business, technology, risk, legal, compliance, audit, or board judgment.
