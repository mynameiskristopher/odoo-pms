---
trigger: always_on
---

# Property Management System (PMS) Agent Rules

You are an expert Odoo developer building a custom PMS. 
You have access to a local knowledge base folder located at `~/odoo-pms-brain`.

## 🧠 Knowledge Recall via QMD
Before making architectural decisions, refactoring, or asking the user for context about past work, you must query the local knowledge base to understand the existing state of the project.

1. **Tool Usage:** You are connected to a QMD MCP server. Use it to search for relevant documentation, past decisions, and framework quirks.
2. **Target Collection:** Always restrict your queries to the `opb` collection (Odoo PMS Brain). 
3. **Execution:** If a user asks you to modify a model (e.g., `pms.unit`), first query the MCP server for "pms.unit" in the `opb` collection to read the architecture notes before you begin coding.

## Documentation Mandate (Definition of Done)
Every time you create a new module, refactor logic, introduce a new database model, or solve a complex bug, you MUST update the knowledge base.

1. **Changelog Tracking:** Maintain a changelog for the current day `.docs/odoo-pms-brain/changelog/YYYY-MM-DD.md` file. Append a brief, dated entry for every significant architectural change you make. (where YYYY is the four digit year, MM is the two digit month, and DD is the two digit day)
2. **Architecture Notes:** When creating new Odoo models (e.g., `pms.property`), create or update a corresponding markdown file in `.docs/odoo-pms-brain/models/` explaining the schema, relationships, and business logic.
3. **Execution Order:** Always write the tracking documentation *before* or *simultaneously* with completing the code task. Do not wait for the user to ask you to document it.

## 💻 Coding Standards & Odoo Nuances
You must prioritize the official Odoo Coding Guidelines above standard PEP-8 or standard Pythonic patterns when they conflict.

1. **The ORM is King:** NEVER use standard Python loops or list comprehensions to filter or extract data from recordsets. You must exclusively use Odoo's `mapped()`, `filtered()`, and `sorted()` methods to prevent N+1 query performance issues.
2. **Context and Environment:** Always propagate the context. Never bypass the ORM to write raw SQL unless absolutely necessary for a massive performance gain, and if you do, absolutely no SQL injections.
3. **Strict Naming Conventions:**
   - **Models:** Singular form (e.g., `pms.property`, not `pms.properties`).
   - **Fields:** `Many2one` fields must end in `_id`. `One2many` and `Many2many` fields must end in `_ids`.
   - **Methods:** Use `_compute_` for compute methods, `_inverse_` for inverse methods, `_search_` for search methods, and `_onchange_` for onchange methods. 
4. **No Hardcoding:** Never hardcode database IDs. Always use XML External IDs (`ref="module.xml_id"`) when linking records or checking environments.