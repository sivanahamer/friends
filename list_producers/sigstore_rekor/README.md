---
type: Database
besides: No
format: [dsse, intoto, hashrekord]
visibility: [Public, Private]
---


# Sigstore Rekor

Sigstore Rekor provides an immutable tamper-resistant ledger of software supply chain metadata. For older `in-toto` entries, Rekor stores the attestation payload and certificate, whereas newer entries (e.g., `dsse` and `hashrekord`) do not. A public instance of Sigstore Rekor is available, while organizations can also create private instances.

**References:** 

- [https://github.com/sigstore/rekor](https://github.com/sigstore/rekor)  
- [https://docs.sigstore.dev/logging/overview/](https://docs.sigstore.dev/logging/overview/)