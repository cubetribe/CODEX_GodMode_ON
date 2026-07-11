# OCR escalation

## Deterministic ladder

1. Run `doctor`; report missing tools without installing them.
2. Use `pdfinfo` and page-scoped `pdftotext -layout` for PDFs.
3. Accept native text only when the page contains at least 32 alphanumeric characters, no tool error, and at most a 0.02 replacement-character ratio.
4. Render only unresolved PDF pages with `pdftoppm` at 300 DPI.
5. Run Tesseract locally with OEM 1, PSM 3, and the case languages. Preserve TXT, TSV, and hOCR.
6. Accept OCR automatically only with at least eight alphanumeric characters, valid TSV, and a character-weighted confidence of at least 70.00.
7. Queue every remaining page for visual review. The CLI never calls a model or uploads a page.

Use final text only from the selected route while retaining native and OCR artifacts separately. Treat timeouts, malformed TSV, missing languages, encrypted input, corruption, and resource limits as explicit review or controlled failure outcomes.

For every executed extraction route, bind the executable's real path, version, SHA-256, normalized argument contract, and relevant Tesseract `.traineddata` paths and hashes into the page record and audit event. These facts make the run reproducible and reviewable; they do not attest that an externally installed binary is trustworthy.

## Capability tiers

The MVP supports local `pdfinfo`, `pdftotext`, `pdftoppm`, and Tesseract on Python 3.11+ in a validated Unix-like environment. OCRmyPDF is detected as an optional derivative capability but is not required. The following remain deliberately deferred: Docling, PaddleOCR, Apple Vision, automatic tool installation, Office/TIFF processing, required OCRmyPDF derivatives, password-protected PDFs, encrypted archives, a native Windows guarantee, and automatic vision or cloud escalation.

Ask the user before any future installation or external processing. Record the exact tool, version, affected pages, privacy boundary, and reason for escalation.
