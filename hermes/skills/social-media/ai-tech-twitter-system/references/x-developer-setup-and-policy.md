# X Developer Setup + Data-Use Notes

Use this reference when setting up or troubleshooting Shivang's X/Twitter posting workflow for the AI/tech content system.

## OAuth app setup

Tool: `xurl`.

User-facing setup steps:
1. Open X Developer Portal: https://developer.x.com/en/portal/dashboard
2. Create/open Project + App.
3. User authentication settings:
   - Enable OAuth 2.0.
   - App type: `Web App, Automated App or Bot`.
   - Callback/redirect URI: `http://localhost:8080/callback`.
   - Website URL: portfolio/GitHub/LinkedIn/project page if no dedicated site.
4. Keys and tokens:
   - Use OAuth 2.0 Client ID and Client Secret.
   - Do not paste secrets into chat.
5. User runs locally:
   ```bash
   xurl auth apps add my-app --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
   xurl auth oauth2 --app my-app
   xurl auth default my-app
   xurl auth status
   xurl whoami
   ```
6. If username lookup fails after OAuth:
   ```bash
   xurl auth oauth2 --app my-app YOUR_X_USERNAME
   xurl auth default my-app YOUR_X_USERNAME
   ```

## Important xurl auth pitfall

`xurl auth status` can show a valid named app while the built-in `default` app has no credentials. The correct state is:
- named app, e.g. `my-app`, marked with `▸`
- OAuth2 user under that app also marked with `▸`

If `default` has no credentials and the named app is not selected, fix with:
```bash
xurl auth default my-app USERNAME
```

Then verify with:
```bash
xurl auth status
xurl whoami
```

## CreditsDepleted behavior

A successful `xurl whoami` proves auth can work even when search/read endpoints fail with:
`CreditsDepleted` / no API credits.

Do not conclude auth is broken just because `xurl search ...` fails with credits depleted. Treat it as an X billing/credits issue. Posting may still need to be tested with an approved real post; do not waste a post on a throwaway test unless the user explicitly asks.

## Data-use description for X Developer Portal

Use/adapt this for X's "Describe all of your use cases of X's data and API" field:

```text
I will use the X API to manage and publish content from my own X account.

Primary use cases:
1. Create posts from my own account about AI, technology, software engineering, product building, and startup/operator insights.
2. Draft and publish approved posts through an internal approval workflow. Posts are generated or edited by me before publishing.
3. Read my own account information to verify authentication and confirm which account is connected.
4. Retrieve my own published posts or post IDs when needed for confirmation, review, or deletion.
5. Optionally search public X content related to AI, technology, software engineering, startups, and product trends to understand what topics are currently relevant and to avoid duplicating existing discussions.

Data usage:
- I will not sell X data.
- I will not use X data for surveillance, profiling, credit decisions, employment decisions, or sensitive personal-data analysis.
- I will not store large-scale X datasets.
- I will not share X data with third parties.
- I will only store minimal operational data such as post text, post IDs, timestamps, and approval status for content management.
- Any public content viewed through the API will be used only for trend awareness and content inspiration, not for copying, scraping, or redistributing.

Automation:
- The system may draft suggested posts on a schedule, but publishing requires my explicit approval.
- The API will only post content from my authorized account.
- The system will comply with X's Developer Agreement, automation rules, and rate limits.
```

## Safety reminders

- Never read or print `~/.xurl`.
- Never ask the user to paste tokens/secrets.
- Never use `--verbose` with xurl in agent sessions.
- For Shivang's workflow, post only after explicit approval tied to visible final text.
