# Solve *SSLCertVerificationError* with **siboif.gob.ni** web service

1. Download every chain of certificates from EDGE browser:

- Server Certificate (\*.siboif.gob.ni)
- Intermediate Certificate (e.g., Sectigo RSA Domain Validation Secure Server CA)
- Root Certificate (the highest certificate in the chain)

2. Concatenate them into one file in this order:
```bash
cat siboif.crt intermediate.crt root.crt > siboif_chain.crt
```

3. Verify the Certificate Chain:
```bash
openssl verify -CAfile siboif_chain.crt siboif.crt
```

> This command must return: `siboif.crt: OK`
