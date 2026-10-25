# Website rules (read before changing anything)

For any person or bot working on aussiehomeschoolinghub.com.au.

## 1. Start from GitHub, never from the live site
- Always edit the files in this repo (`Aussie-Home-Schooling-Hub/ahh-website`, branch `main`). Pull the latest first.
- Never use a page saved from a browser or downloaded from the live site. Netlify changes pages when it serves them (adds a tracking script, rewrites links), so a saved copy is not the real file.

## 2. Change only what the job needs
- Edit the exact lines asked for. Leave everything else as it is.
- If a small fix changes lots of lines, stop and check what went wrong.

## 3. Check before handing over
Search every changed file for these. If any appear, the file came from the live site: throw it away and start again from GitHub.
- `netlify-rum`
- `.netlify/scripts`
- `data-netlify-cwv-token`

Also check:
- Links use the repo's own style (for example `shop.html`, not a rewritten `/shop` version from the live page).
- Waitlist and contact forms keep their exact `name` and hidden `form-name` (`pdf-curriculum-waitlist`, `workshop-waitlist`, `contact`). Renaming one splits its sign-ups in Netlify.
- Every page still has the same menu, including Coming soon.
- The page works on a phone-sized screen with no sideways scrolling.

## 4. Say exactly what changed
With every hand-over, list each file and the change in it (one line each). New pages: say so.

## 5. Standing AHH rules
- Plain, friendly Australian English.
- Every fact must be checked against a real source. If it can't be confirmed, leave it out.
- No prices or claims that haven't been agreed (for example, Wattlewood Workshop is "Price to be announced").
- Registration content is general information only, not legal advice. Safety messages stay generic and Australia-wide.
- Never show fix notes, version numbers or test text on the site.
- Don't touch `google6fbe169d25c43d1c.html` (it verifies Google Search Console).

## 6. Netlify deploys cost credits: batch them
Every merge or upload to `main` is a production deploy, and each one uses **15 Netlify credits**. The Personal plan has **1,000 credits a month**, shared by every AHH site (this website and Wattlewood Workshop). If they run out, **every site goes offline** until the next month. (Netlify pricing and credits pages, checked 25 Oct 2026.)

- **Never push or upload straight to `main`.** Make a branch and open a pull request, or hand the files to Pete.
- **Deploy Previews are free.** Check your work on the pull request's preview link, not on the live site.
- **One release a week.** Pete merges the week's pull requests together on release day. Don't ask for a merge for each small change.
- **Only urgent fixes skip the queue:** the site is broken, a link or form doesn't work, a price is wrong, or something is untrue. Say "urgent" and why.
- **Group related changes** into one pull request where you can, instead of one PR per line.
- **Uploading in GitHub:** drag all the files in at once, so it's one commit and one deploy.
- Don't change the build settings in Netlify.
