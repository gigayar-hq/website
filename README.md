# gigayar.com

The Gigayar company website. Nyongo is the first product page. Static HTML, English (`/`) and French (`/fr/`), served for free by GitHub Pages from the `docs/` folder.

```
build.py                    generates every page into docs/ (Python 3, standard library only)
content/legal/nyongo/       Nyongo privacy + terms texts, copied from the app
docs/                       the published site (generated, committed)
docs/assets/style.css       the only stylesheet (edited by hand)
```

| Page | URL |
|---|---|
| Home | https://gigayar.com/ |
| Nyongo | https://gigayar.com/nyongo/ |
| Nyongo privacy policy (Google Play field) | https://gigayar.com/nyongo/privacy/ |
| Nyongo terms | https://gigayar.com/nyongo/terms/ |
| Nyongo account deletion (Google Play field) | https://gigayar.com/nyongo/delete-account/ |

## Edit and preview

All page text is in `build.py` (the `T` dictionary, one block per language). Change it, then:

```
python build.py
python -m http.server 8765 -d docs     # open http://localhost:8765
```

Commit both `build.py` and the regenerated `docs/`.

**Legal texts:** the app (`nyongo_manager/assets/legal/`) is the source of truth. After changing them there:

```
python build.py --sync-legal ../nyongo_app/nyongo_manager/assets/legal
```

**Adding a product:** add a page function and its `PAGES` entry in `build.py`, its texts in both languages, and a card in `home()` (replacing the "More to come" card).

## Hosting (GitHub Pages)

Repo settings → Pages → Source: *Deploy from a branch*, branch `main`, folder `/docs`. Custom domain `gigayar.com` (also set by `docs/CNAME`), then tick *Enforce HTTPS* once the certificate is issued.

Organization settings → Pages → *Add a domain* → verify `gigayar.com` (a TXT record). This stops anyone else from claiming the domain on GitHub.

## DNS (Squarespace → Domains → gigayar.com → DNS)

Add:

| Type | Host | Value |
|---|---|---|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| AAAA | @ | 2606:50c0:8000::153 |
| AAAA | @ | 2606:50c0:8001::153 |
| AAAA | @ | 2606:50c0:8002::153 |
| AAAA | @ | 2606:50c0:8003::153 |
| CNAME | www | `<github-org>.github.io` |

Remove the **Squarespace Defaults** A/CNAME records for `@` and `www` if present (they point to a Squarespace page).

**Never touch** the records for email: MX (Google Workspace), TXT `v=spf1 ...`, `google._domainkey`, `google-site-verification`, and the Resend records (`resend._domainkey`, `send`). The website and the email are independent.
