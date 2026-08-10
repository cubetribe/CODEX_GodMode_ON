# AGENTS.md — Prototype Only

- This workspace is disposable and local-only. Do not deploy, push to `main`,
  share externally, or use production data, credentials, or live services.
- Use `$godmode-prototype` as the sole primary mode and keep the parent as the
  only writer.
- Keep output under `prototype/` or `spike/`, or prefix names with `proto_`.
- Put a `PROTOTYPE ONLY — NOT FOR PRODUCTION` header in every generated source
  file.
- Prove the promised local behavior end to end; file creation or process startup
  alone is not completion.
- Report unverified edges and the production migration checklist.
- Promotion starts a separate `$godmode-workflow` run in the real project. Remove
  all watermarks and temporary boundaries before production validation.
