# Keeping secrets out of Claude Code's transcripts — setup guide

## The real risk (in one paragraph)

Claude Code persists every session as **plaintext JSONL transcripts on disk**
(typically under `~/.claude/projects/.../*.jsonl`). Whatever you type or paste
into the chat — API keys, database URLs, OAuth tokens, passwords — is written to
those files verbatim. They are not encrypted. They may be picked up by backups,
sync clients, or anything that can read your home directory. So the moment you
paste `sk-proj-…` into the chat window, treat that secret as **compromised** and
plan to rotate it.

The fix is not "be careful what you paste." The fix is a workflow where **raw
values never enter the chat or the context window at all**:

1. Store secrets in a vault (or, more lightly, your shell environment).
2. Reference them in prompts by **NAME** only — e.g. "use `${OPENAI_API_KEY}`",
   never the value.
3. Let an **allowlisted CLI** fetch the value at runtime, so the tool process
   sees it but Claude (and the transcript) never does.

This guide gives you a vault-light path and a vault-full path. Pick one.

---

## Option A (lighter): environment variables + direnv

Good enough for many local workflows and zero new services.

1. Put real values in a file Claude can't read into the chat, **git-ignored**:

   ```bash
   # .envrc  (add ".envrc" and ".env*" to .gitignore!)
   export OPENAI_API_KEY="sk-proj-…"
   export DATABASE_URL="postgres://…"
   ```

2. Install [direnv](https://direnv.net/) and `direnv allow` the directory.
   Now the variables are present in your shell whenever you `cd` in — and in any
   process Claude Code launches from that shell.

3. In prompts, reference names only: *"run the migration using `$DATABASE_URL`
   from the environment."* Claude tells the tool to read the env var; it never
   needs the value.

4. Confirm what's wired up without exposing values:

   ```bash
   python scripts/secret_env.py        # redacted status table
   ```

Trade-off: values still sit in `.envrc`/`.env` in plaintext on disk (just not in
the transcript, and not in git). That's a real improvement, but a vault is
stronger because values are encrypted at rest and access is auditable.

---

## Option B (stronger): an open-source vault — Infisical as the primary example

[Infisical](https://github.com/Infisical/infisical) is an open-source secrets
manager. Values live encrypted in a vault; a CLI fetches them on demand. Any
similar tool works the same way (Vault, Doppler, 1Password CLI, `pass`,
`aws secretsmanager`, `gcloud secrets`) — only the fetch command changes.

### 1. Install the CLI and log in

```bash
# macOS
brew install infisical/get-cli/infisical
# or see https://infisical.com/docs/cli/overview for Linux/Windows
infisical login
```

### 2. Create a project and add secrets in the vault (never in chat)

Create a project at `app.infisical.com`, then add each secret **outside** the
chat window — via the web UI or:

```bash
infisical secrets set OPENAI_API_KEY="sk-proj-…" --env=dev
infisical secrets set DATABASE_URL="postgres://…" --env=dev
```

### 3. Fetch by NAME at runtime

```bash
# Inject the whole set into a command's environment (values never printed):
infisical run --env=dev -- python my_app.py

# Or fetch a single value to stdout for a tool to consume:
infisical secrets get OPENAI_API_KEY --plain --env=dev
```

### 4. Wire the vault into this helper

`scripts/secret_env.py` will use a vault CLI as a fallback when a name isn't in
the environment. Point it at your CLI with a `{name}` placeholder:

```bash
export SECRET_ENV_VAULT_CMD="infisical secrets get {name} --plain --env=dev"
python scripts/secret_env.py        # now resolves from the vault, redacted
```

---

## Allowlist the vault CLI so Claude can fetch without seeing values

The point is that Claude can **invoke** the fetch command but never has to read
the value into its context. Add the read-only fetch command to Claude Code's
allowlist so it runs without a prompt — and **do not** allowlist anything that
prints all secrets to the chat.

In your project `.claude/settings.json` (or `settings.local.json`):

```json
{
  "permissions": {
    "allow": [
      "Bash(infisical run:*)",
      "Bash(infisical secrets get:*)",
      "Bash(direnv exec:*)",
      "Bash(python scripts/secret_env.py*)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./.envrc)",
      "Bash(infisical secrets get * --plain)"
    ]
  }
}
```

Notes:
- Allow `infisical run -- <cmd>` so secrets are injected into the *child
  process* environment — Claude orchestrates, the value flows tool→tool, not
  through chat.
- The `deny` on reading `.env*`/`.envrc` stops Claude from slurping raw values
  into the transcript "to be helpful."
- Keep `secret_env.py`'s default (redacted) mode allowlisted; treat `--export`
  (which prints real values) as something *you* run in your own terminal, not
  something Claude pipes into chat.

---

## Rotate anything already pasted — checklist

If you (or a teammate) have ever pasted a real secret into a Claude Code chat,
assume it is on disk in plaintext. Work through this:

- [ ] **Find the evidence.** Search transcripts for tell-tale prefixes:
  ```bash
  grep -RInE 'sk-[A-Za-z0-9]|ghp_|xox[baprs]-|AKIA[0-9A-Z]{16}|-----BEGIN' ~/.claude/projects/ 2>/dev/null
  ```
- [ ] **Rotate each exposed secret at the source** (provider dashboard / `infisical secrets set ...` with a new value). Old value must be revoked, not just replaced locally.
- [ ] **Revoke OAuth / session tokens** and passwords that were pasted; re-issue.
- [ ] **Update the vault / `.envrc`** with the new values — outside the chat window.
- [ ] **Scrub or delete the offending transcripts** once rotation is done (they still hold the old, now-dead secret; delete to avoid confusion and to clean backups).
- [ ] **Purge from backups / cloud sync** if your home dir is backed up (Time Machine, OneDrive, Dropbox, etc.) — the plaintext may persist there too.
- [ ] **Run a repo secret-scan** (`gitleaks detect`, `trufflehog`) to catch anything committed.
- [ ] **Add guards going forward:** `.gitignore` for `.env*`/`.envrc`, the `deny` rules above, and reference secrets by `${NAME}` from now on.
- [ ] **Verify wiring** without exposing values: `python scripts/secret_env.py` should show `present` for the names you rotated.
