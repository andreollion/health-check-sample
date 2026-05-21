# Extracting from SharePoint Documents

## What this source provides

SharePoint exports are typically architecture diagrams, design documents, and supplementary artefacts that don't fit naturally into Confluence or ARB. Often a mix of PDFs (architecture diagrams in PDF form), Visio exports, and additional reference material.

In most pipelines, SharePoint is the **secondary architecture source** — the primary being the ARB output. SharePoint fills in details ARB omits.

## What to extract per schema area

SharePoint extraction overlaps heavily with ARB extraction. Use the ARB extraction guide first; fall back to SharePoint for fields ARB doesn't cover.

Typical SharePoint-only contributions:
- More detailed network diagrams (firewall rules, proxy paths)
- Detailed component interaction diagrams
- Legacy design documents that predate the current ARB
- Operational handover artefacts that didn't make it into Confluence
- Vendor architectural attestations

### data_protection
- `data_protection.data_stores[]` — supplementary detail on databases / storage
- `data_protection.tls_version_min` — from network design docs

### resilience
- Cross-check with ARB outputs

### operations
- `operations.network_diagram_current` — confirm against SharePoint if ARB is silent
- `operations.firewall_rules_documented` — confirm against SharePoint exports
- `operations.proxy_rules_documented` — confirm against SharePoint exports

## Extraction approach

Run the ARB extraction guide first. Then for each SharePoint document, ask:

1. Does this duplicate ARB content? If yes, ignore.
2. Does this contradict ARB? If yes, prefer the more recent document and flag the conflict.
3. Does this add new information ARB didn't cover? If yes, extract.

## Provenance examples

```json
{
  "property_path": "operations.firewall_rules_documented",
  "source": "sharepoint",
  "ref": "sharepoint/Apollo-Network-Design-v3.pdf — p.4 Firewall Section",
  "excerpt": "Inbound rules: HTTPS/443 from ALB; HTTP/80 redirect. Outbound: 443 to vendor APIs via Zscaler.",
  "extracted_at": "2026-05-05T14:23:00Z"
}
```

## Caveats

- SharePoint exports are often the most heterogeneous in format. PDFs may be scanned (need OCR), images-only (need vision-capable AI), or text-heavy. Filter for usable formats before extraction.
- SharePoint documents are sometimes the oldest — flag any document >12 months as stale.
- If SharePoint duplicates ARB content perfectly, treat ARB as authoritative and skip SharePoint to avoid noise.
