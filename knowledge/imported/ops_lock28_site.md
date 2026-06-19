# ops.lock28.com Public Site Notes

Source: public frontend bundle from `https://ops.lock28.com` on June 19, 2026.

## Public routes observed

- `/`
- `/login`
- `/reset-password`
- `/pricing`
- `/privacy`
- `/privacy-policy`
- `/terms`
- `/quote`
- `/quote/success`
- `/form/:slug`
- `/form/:slug/submitted`
- `/start`
- `/sign/:token`
- `/approve/:token`
- `/portal/login`
- `/portal`
- `/derack`
- `/derack/request`
- `/app`
- `/app/derack`
- `/app/derack/:id`

## Site identity

- The site title is `Eko Solar Ops`.
- The application uses Supabase auth and a client portal.
- The public site includes a detach-and-reattach landing page for roofing-related solar work.

## Detach and Reattach public marketing copy

The public derack flow describes a four-step process:

1. Request a quote
2. Site survey
3. Scheduled removal
4. Reinstall and commission

The site says:

- customers can fill out the form or call
- Eko Solar will review system size and roof type
- the company will visit to confirm panel count, inverter location, and access challenges
- panels are disconnected, photographed, labeled, and safely removed before roof work begins
- after roofing is done, the system is reinstalled, inspected, and brought back online

The call to action says:

- `Ready to Protect Your Solar Investment?`
- `Get a flat-rate quote for your detach & reattach project. Most quotes returned within 24 hours.`
- phone number shown: `(404) 551-6532`
- service area shown: `Serving metro Atlanta and North Georgia`

## Detach and Reattach quote request form

The public quote request form asks for:

- full name
- company or roofing contractor
- email
- phone
- property address
- panel count
- panel wattage
- inverter type
- number of stories
- roof material
- roof pitch
- roofing contractor name
- roofing contractor phone
- preferred removal date
- additional notes
- optional roof and array photos

The visible inverter type options include:

- string
- microinverter
- power optimizer
- hybrid
- not sure

The visible roof material options include:

- asphalt shingle
- clay tile
- concrete tile
- metal standing seam
- metal corrugated
- flat TPO
- flat EPDM
- wood shake
- slate

The visible roof pitch options include:

- flat / low slope
- 4/12 gentle
- 6/12 moderate
- 8/12 steep
- 10/12+ very steep
- not sure

## Submission behavior observed in the frontend

The detach-and-reattach request is stored with:

- type: `Detach & Reinstall`
- status: `PENDING`
- source: `derack-landing`

The success screen says:

- `Quote Request Sent`
- most quotes are returned within 24 hours
- users should check email for confirmation

## Portal and auth behavior observed

- There is a separate client portal login route at `/portal/login`.
- There is a portal route at `/portal`.
- There is also an authenticated app route at `/app`.
- Google sign-in is present in the app auth flow.
- Password reset flow exists at `/reset-password`.

## Limits of this snapshot

- These notes come from the public frontend bundle and route configuration.
- They do not include private portal data.
- They do not prove every route is enabled for every user role.
