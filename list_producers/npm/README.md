---
type: Package Registry
besides: Yes
format: [sigstore bundle]
visibility: [Public]
---

# npm

npm stores attestations that can be accessed through the API as `https://registry.npmjs.org/-/npm/v1/attestations/{PACKAGE}@{VERSION}`. Note, some prior versions used [Sigstore Rekor](?tab=t.0#heading=h.cqvn1c2pmkyd) to store attestations.

**References:** 

- [https://docs.npmjs.com/generating-provenance-statements](https://docs.npmjs.com/generating-provenance-statements)  
- [https://github.blog/security/supply-chain-security/introducing-npm-package-provenance/](https://github.blog/security/supply-chain-security/introducing-npm-package-provenance/)