# Verification: ecosystem guidance synchronization

Date: 2026-11-12
Result: PARTIAL
Baseline: eceef44f732fb9e2f4387f177c57f922b692a000

## Scope and review

Current general tutorials use the unified source CLI. Versioned practical articles retain their original CLI/template versions, commands, results and attachments, with an explicit version boundary and current template-guide link at the beginning. Preserve template quick links, dates and draft state.

Command spellings and options were compared with the current parser and built help. Replacing historical result text, adding aliases, modifying runtime algorithms, upgrading template dependencies and recreating cloud resources were excluded after examining whether they were necessary for this task.

## Results

Local checks are recorded below. No cloud resources were created. Existing runtime receipts were preserved; modified source identity does not inherit a new qualification.

## Delivery limitations

The root dotenv's configured GitHub credential returned HTTP401, no alternate process credential or configured Git credential helper/gh session was available, and private Registry/Website fetches could not authenticate. Public producer main revisions were fetched and checked. Private consumers are based on the latest locally recovered task branches, not claimed current remote main. Finish local commits and reproducible bundles; push, PR, remote CI, review and merge remain blocked until authentication is restored. No new package, image or live website release is claimed.

## Local verification

- scripts/validate.py: 59 post directories checked, zero problems.
- Current general CLI examples were compared with actual built help. Versioned cases keep their pinned commands and prior execution claims; notices direct current-source users to the current owner guide.
- Direct Lychee on article source cannot resolve existing website-root /start/ and /blog/ links. Site-root routes and fragments are checked after normal Website blog synchronization/build; this limitation does not justify editing historical outputs.
- Article Python attachments and historical business results are unchanged. No article business program or model task was rerun, and no new business result is claimed.

A global-selector-aware pass added the same explicit historical version boundary to the Base, Desktop and OpenSandbox interpreter cases. There are 54 version-note article files; current general tutorials retain supported source-CLI examples. All 59 post directories still pass validation.

## Authentication and delivery follow-up

The initial API Bearer request returned HTTP401, but the credential was not
invalid. Git push/fetch and the API's Basic authentication succeeded with the
same existing credential; no credential was changed or created. Public
producer source branches can now be pushed. Private Registry/Website main was
fetched successfully, and the prior coordinating PRs were confirmed merged.
This supersedes the initial delivery-authentication limitation above.
