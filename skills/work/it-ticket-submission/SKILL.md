---
name: it-ticket-submission
description: Submit a Crown IT Self-Serve Portal (Cherwell) ticket requesting access to a specific software application or website, by asking the requester for the needed details and then operating the portal's browser UI to fill the request. Use when the user asks to submit, file, or fill out an IT/access-request ticket for software or website access. Do not use for other Cherwell ticket types (hardware, incident reports, other Software-page links) until they have been walked through and added to this Skill; do not enter or ask for the user's login password.
---

# IT Ticket Submission (Software/Website Access Request)

Operate the Crown IT Self-Serve Portal (Cherwell) to submit one "Submit an
Access Request" ticket per requestor. This Skill covers only the
software/website access-request flow; every other ticket type on the Software
page (hardware, incident reports, per-app "Report an Issue"/"Submit a
Request" links) is out of scope until a user walks through it and this file is
extended.

## Portal facts (verified by hands-on walkthrough)

- Portal home: `http://itselfserve/CherwellPortal/IT`. When not authenticated
  it redirects to a Cherwell login page with a session-specific `state` query
  string — never hardcode or reuse a previously seen login URL; always start
  from the portal home and follow whatever redirect appears.
- The browser tool cannot complete Windows/Kerberos SSO. Clicking
  "Use Windows Login" only loops back to the credential form. Check the page
  title/URL first: `Crown Home Page - IT` means already authenticated; a
  login form means you must stop and ask the user to log in manually (they
  may use Windows Login or type credentials themselves). Never type into the
  password field yourself.
- **Finding the correct link is confusing — read this carefully.** The
  Software page has **two different** "- Submit an Access Request" links in
  the page snapshot, and neither is visually inside a tile literally labeled
  for it in an obvious way:
  - The **wrong** one is a real DOM-and-visual child of the **Crown 360
    Retail** tile (it sits among that tile's other "Crown 360 Retail"-labeled
    links, both in the snapshot and on screen). Do not use this one.
  - The **correct** one is the snapshot node that comes immediately after
    (next sibling of) the heading node whose text is exactly **"FAS"** — but
    the page's CSS grid reorders tiles independently of DOM order, so this
    link is not visually shown inside a "FAS" tile. On screen it renders
    inside the **Other** tile (whose visible box also shows unrelated links
    like "Submit a Restore Request" and "Purchase/Install Software" that
    belong to completely different, unrelated DOM positions). The FAS tile
    visually shown on screen only ever contains a single, unrelated
    "- Submit a Request" link — ignore it.
  - Reliable procedure: get a fresh page snapshot (refs change every page
    load — never reuse refs from an earlier snapshot), find the heading node
    with text "FAS", and click the very next "Create Business Object" node
    after it in the snapshot list. Do not rely on the screenshot alone to
    find this link, since its visual position is misleading.
- Confirm you landed on the right form before filling anything: it must show
  **Account Type** (dropdown) and **Employee Details** (Name, Employee
  ID(Clock #), Email, Mirror Access) fields, plus **Request Type**
  (New/Delete/Modify radios). If instead you see **Request Options** with
  choices like Distribution Group/Shared Mailbox/Out of Office, you opened the
  wrong link (the generic "Other - Submit a Request" Exchange form) —
  abandon it (see below) and retry from the FAS-associated link.
- **Side effect risk**: merely navigating to or reading a ticket-creation link
  can auto-create a real, numbered Incident in "Assigned" status before you
  click anything else. Always check the ticket number shown after navigating,
  and abandon any ticket you did not intend to keep (see below). Before
  finishing a session, check the Home dashboard's "My Tickets" list for
  unexpected stray "Assigned" tickets and abandon those too.
- **Abandoning a draft reliably**: the right-hand "Withdraw Ticket" action is
  unreliable (clicks on it often do nothing visible). Instead use the top
  toolbar **Cancel** button, which raises an "Abandon changes to Incident
  #####?" dialog — click **Yes**. This is the only pattern confirmed to work.
- **Ticket Description** is a rich-text field inside an iframe, with no
  distinct accessible textbox in the page snapshot. Do not use the
  `iframe >> body` selector to focus it — it reliably times out and can
  leave focus on whatever field was previously focused, so the following
  type-text call silently lands in the wrong field (e.g. corrupting Mirror
  Access) instead of erroring. Instead, get the page snapshot, find the
  iframe's own element ref, and click that ref directly — this focuses the
  field without a timeout. Fill the Ticket Description **first**, before any
  other field, so there is nothing else on the page that a misdirected click
  could corrupt. After typing, re-check the page snapshot (or a screenshot)
  to confirm the description text actually landed in the iframe before
  moving on to the rest of the form.
- **Account Type** is a fixed dropdown (Ariba, Azure, Confluence, GitHub,
  Jira, Sharepoint, VPN, Windows(AD), etc., plus a generic **Other**). Match
  the requested software to the closest option; use "Other" if nothing fits,
  and say so in the Ticket Description.

## Required information

Ask for whatever is not already given; do not guess or invent any of these:

- **Software/website** the requestor needs access to.
- **Who needs access** — name(s) and email(s) of the beneficiary/beneficiaries.
  The form has only one Name/Employee ID/Email set, which represents the
  **person submitting the ticket**, not necessarily the beneficiary. If the
  requester is submitting on behalf of others, put the beneficiaries' names
  and emails in the Ticket Description instead of the Employee Details
  fields, and confirm with the user whether that should be one ticket or
  several (default: one ticket, all names listed in the description, unless
  the user asks for separate tickets per person).
- **Business reason** for the access.
- **Request Type**: New / Modify / Delete. Infer from context when clear
  (e.g. "get access" implies New); ask if ambiguous.
- **Requester's own Name, Employee ID (Clock #), and Email** for the Employee
  Details fields. Look for a repository-local "UserInfo" document first; if
  none exists or is configured, ask the user directly rather than guessing.
- **Mirror Access** (whose existing permissions the new access should match).
  Always ask the user explicitly — never infer or default this value.

## Procedure

1. **Scope check first.** Confirm the request is a software/website access
   request — the only ticket type this Skill knows how to fill. If it's a
   different Cherwell ticket type (hardware request, incident/issue report,
   any other Software-page "Submit a Request" link), stop before touching
   the portal: tell the user this ticket type isn't mapped out yet, and ask
   whether they want to walk through it together now (the same way the
   access-request flow was discovered) so it can be added to this Skill as a
   new section. Do not guess at an unfamiliar form's fields or improvise a
   procedure for it.
2. **State the plan before collecting anything.** Summarize, in plain
   language, what is about to happen: which ticket type/flow this is (the
   software/website access request), the ordered steps that will follow
   (open portal → confirm login → fill Ticket Description/Request
   Type/Account Type/Employee Details/Mirror Access → screenshot for review
   → confirm → submit or abandon), and the list of information still needed
   from the user (see "Required information" above, minus anything already
   given). Let the user correct the scope or add context before any portal
   action starts.
3. Open `http://itselfserve/CherwellPortal/IT`. If it lands on a login page,
   stop and ask the user to complete login themselves, then continue once
   they confirm.
4. Collect the required information above (ask only for what is missing).
5. Navigate Software menu → the FAS-associated "Submit an Access Request"
   link. Verify the form matches the "Account Type / Employee Details"
   shape described above; if not, abandon and retry.
6. Fill the Ticket Description (software, beneficiary name(s)/email(s),
   business reason, and the mirror-access note), select the Request Type
   radio, pick the closest Account Type, and fill Employee Details and
   Mirror Access for the requester.
7. Take a screenshot of the completed form and show it to the user for
   review.
8. Ask for explicit confirmation before submitting this specific ticket.
   Only click the **Submit** action after the user confirms "yes, submit
   this one for real." If the user does not confirm, abandon the draft via
   Cancel → Yes instead.
9. Report the resulting ticket number and status, or confirm the draft was
   abandoned. Check the Home dashboard for any other stray "Assigned"
   tickets created as a side effect and abandon those as well.

## Validation

- The filled form must show the exact Account Type, Request Type, and
  Employee Details the user confirmed, visible in a pre-submit screenshot.
- Submit is never clicked without an explicit per-ticket confirmation from
  the user.
- After the session, the dashboard ticket list shows no unintended stray
  "Assigned" tickets beyond the one the user chose to submit (if any).
