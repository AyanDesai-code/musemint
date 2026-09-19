# MuseMint MVP feature specification and data model

**Status:** implementation proposal, not shipped functionality. **Format:** three page-sized sections. This spec defines a testnet MVP; stack, chain, contract, AI provider, storage vendor, and policy approval remain open. Defaults below make implementation and tests concrete without claiming those decisions are approved.

## Page 1 — Product scope and API contract

**Goal:** a creator uploads AI artwork, publishes immutable NFT metadata, mints one token, and offers it at a fixed price; a collector discovers, purchases, likes, and comments on it. Show creator, current owner, provenance, price, and pending/failed transaction states. Wallet signatures authenticate users; the service never holds private keys.

**Proposed defaults:** one EVM testnet, ERC-721 (one token per artwork), ERC-2981 royalty signaling, one native payment currency, no platform fee, non-custodial marketplace settlement. Upload is the required creation path; integrated AI generation is deferred pending provider/cost/moderation decisions. Auctions, editions, bids, fiat, multi-chain, messaging, and production deployment are out of scope. Users attest that they have rights to uploaded content; public release requires an approved moderation/reporting policy.

### REST endpoints

All paths start with `/api/v1`. `Public` reads exclude drafts; `Auth` requires a wallet session. IDs are UUIDs. Mutation responses return the affected resource; transaction preparation also returns `transaction_id` and unsigned `{chain_id,to,data,value}` wallet instructions. Clients sign and broadcast, then submit the hash. Any separate token approval is wallet-driven and checked before listing preparation.

| Method and path | Access | Input / result |
| --- | --- | --- |
| `POST /auth/challenge` | Public, rate-limited | `{wallet_address,chain_id}` → single-use nonce, domain-bound message, 5-minute expiry |
| `POST /auth/verify` | Public, rate-limited | `{message,signature}` → session and user; create user on first valid login |
| `DELETE /auth/session` | Auth | Invalidate session; `204` |
| `GET /users/me`; `PATCH /users/me` | Auth | Read profile; patch `display_name,bio,avatar_uri` only |
| `GET /users/{id}` | Public | Public profile only; no session/security data |
| `POST /uploads` | Auth | PNG/JPEG/WebP multipart file, maximum 10 MiB → server-validated, pinned `{image_uri,upload_receipt}` bound to uploader; reject SVG and MIME mismatches |
| `POST /artworks` | Auth | `{title,description,image_uri,upload_receipt,attributes?,royalty_bps?,royalty_recipient?,rights_attested:true}` (§3) → private draft; creator/owner set from session |
| `PATCH /artworks/{id}` | Creator | Patch §3 fields while unminted without a live mint intent; changed image requires upload receipt |
| `GET /artworks`; `GET /artworks/{id}` | Public / creator for own drafts | Browse/detail; filters `creator_id,owner_wallet,listed,q` (title search); `scope=mine` requires Auth |
| `POST /artworks/{id}/mint` | Creator | Empty body; freeze metadata, pin JSON, prepare mint transaction; minted or pending artwork → `409` |
| `GET /listings`; `GET /listings/{id}` | Public | Active-only feed; detail includes historical status, price/currency/seller for minted artwork; optional `artwork_id,seller_id` |
| `POST /listings` | Current owner | `{artwork_id,price_atomic}` → pending listing and listing-creation transaction |
| `POST /listings/{id}/purchase` | Auth, not seller | `{expected_price_atomic}` → purchase transaction after on-chain availability/price checks |
| `POST /listings/{id}/cancel` | Seller | Empty body; prepare cancellation transaction; listing remains purchasable until cancellation confirms |
| `POST /transactions/{id}/submit` | Initiator | `{tx_hash}` → submitted transaction; hash cannot be reassigned to a different intent |
| `GET /transactions`; `GET /transactions/{id}` | Initiator | Own intent/status history; optional `artwork_id,status` filters |
| `GET /artworks/{id}/comments`; `POST /artworks/{id}/comments` | Public / Auth | List comments; create `{body}` (1–2,000 trimmed characters) on minted artwork |
| `DELETE /comments/{id}` | Author | Soft delete; `204`, including repeat deletion |
| `PUT /artworks/{id}/like`; `DELETE /artworks/{id}/like` | Auth | Idempotent like/unlike on minted artwork; return `like_count,liked_by_me` |

Lists return `{items,next_cursor}` with opaque cursors, default `limit=20`, maximum 100, descending `(created_at,id)` ordering. Cursors bind to the selected filters; invalid/mismatched cursors return `400`. Details include counts and confirmed mint/sale provenance hashes, not other users' private transaction intents. Return `201` for resource creation, `202` for transaction preparation/submission, `200` otherwise unless specified. Errors: `{error:{code,message,fields?}}`; use `400` malformed, `401` unauthenticated, `403` forbidden, `404` absent/invisible, `409` state/price/idempotency conflict, `422` invalid fields, `429` rate limit. Reject unknown write fields. Rate-limit auth, uploads, and social writes; protect cookie-session writes against CSRF.

## Page 2 — Relational data model and state rules

Proposed PostgreSQL logical schema. Every table has `id UUID PK` and `created_at TIMESTAMPTZ`; mutable tables also have `updated_at`. Fields are required unless marked `?`. Arrows below identify foreign keys; chain/token/on-chain identifiers are external values. Normalize EVM addresses to lowercase validated 20-byte hex; timestamps are UTC. Currency amounts and token IDs use exact `NUMERIC(78,0)` (uint256 range), serialized as decimal strings, never floats. `chain_id` is a positive integer. `json` denotes JSONB.

| Table | Fields beyond common columns | Constraints / indexes |
| --- | --- | --- |
| `users` | `wallet_address`, `display_name VARCHAR(80)`, `bio VARCHAR(500)?`, `avatar_uri?` | Unique wallet; wallet immutable in MVP; default display name is shortened wallet |
| `artworks` | `creator_id → users`, `owner_wallet`, `title VARCHAR(120)`, `description VARCHAR(2000)`, `image_uri`, `attributes json`, `royalty_recipient`, `royalty_bps SMALLINT`, `rights_attested_at`, `metadata_uri?`, `chain_id?`, `contract_address?`, `token_id?`, `mint_status` | Unique `(chain_id,contract_address,token_id)` when minted; index creator, owner, creation time; minted requires all token/metadata fields |
| `listings` | `artwork_id → artworks`, `seller_id → users`, `seller_wallet`, `chain_id`, `marketplace_address`, `onchain_listing_id?`, `price_atomic`, `currency_address`, `status` | Price > 0 within uint256; native currency uses zero address; unique non-null chain/marketplace/on-chain ID; at most one `pending` or `active` listing per artwork; index status/creation time |
| `transactions` | `artwork_id → artworks`, `listing_id? → listings`, `initiator_id → users`, `kind`, `status`, `chain_id`, `from_wallet`, `to_address`, `call_data`, `value_atomic`, `tx_hash?`, `block_number?`, `block_hash?`, `log_index?`, `failure_code?`, `expires_at`, `idempotency_key`, `request_hash`, `buyer_wallet?`, `seller_wallet?`, `sale_price_atomic?`, `royalty_amount_atomic?`, `confirmed_at?` | Unique `(initiator_id,idempotency_key)` and non-null `(chain_id,tx_hash)`; kind = mint/list/cancel/purchase; listing required except mint; purchase snapshots populated from settlement event; index status, initiator/creation time |
| `comments` | `artwork_id → artworks`, `user_id → users`, `body VARCHAR(2000)`, `deleted_at?` | Index artwork/creation time; exclude soft-deleted comments from lists/counts |
| `likes` | `artwork_id → artworks`, `user_id → users` | Unique `(artwork_id,user_id)`; index user; no `updated_at` needed |

**Integrity:** use DB checks for lengths, nonblank title/description/comment, lifecycle enums, uint256 bounds, and royalty range; unique live-listing constraint is a partial index. Use a composite foreign key to enforce that a transaction’s listing belongs to its artwork and chain; listing seller wallet must match the authenticated owner at listing creation. Addresses/URIs/hash/calldata use validated text; block/log numbers are nonnegative integers. Server controls identity, status, timestamps, ownership, and settlement fields; reject attempts to set them through metadata/profile writes. Draft `owner_wallet` is provisional until mint confirmation. Defaults: artwork `unminted`, listing `pending`, transaction `prepared`, attributes `[]`, royalty 0 bps; rights attestation time is server-generated.

**Relationships:** user 1:N created artworks, listings, initiated transactions, comments, and likes. Artwork 1:N historical listings, transactions, comments, and likes; listing 1:N transaction attempts. Users M:N artworks through likes. Current ownership is `owner_wallet`, not creator or last buyer: an external wallet need not have a user row. Restrict hard deletion of referenced records; likes can be deleted. Nonces, sessions, and rate limits use a TTL security store outside these six domain tables.

**Lifecycle and consistency:** artwork `unminted → pending → minted`; failed mint returns to unminted. Listing `pending → active → sold|cancelled|invalidated`; failed creation → `failed`. Transactions `prepared → submitted → confirmed|failed`; unused preparation expires to `expired` after safe reconciliation. Event discovery can move an unreported `prepared` intent directly to `confirmed|failed`. Expiry alone must not unlock mint/list state: an unsigned preparation can still be broadcast without hash submission. Proposed contracts must enforce intent deadlines/nonces; only after the deadline is finalized and canonical events reconciled may an unused mint/list intent release its pending state (artwork → unminted; listing → failed). A transaction included before deadline can confirm afterward. Cancel/purchase expiry leaves the active listing unchanged. A mempool delay alone is not failure. Require `Idempotency-Key` on all transaction-preparation routes: same key/body returns the existing intent, changed body returns `409`. Check key replay before lifecycle guards so retries return the same intent even after state changes. Persist key/result with the transaction; lock artwork/listing rows during preparation and enforce uniqueness in the DB.

Only a verified receipt and expected contract event, after configured chain confirmation depth, change ownership, mint state, or sale status. Validate chain, sender, target, calldata, value, and event identity; client hashes are not proof. A worker reconciles receipts and external transfers; revoke active listings when ownership/approval becomes invalid. Replay events idempotently; on reorg, roll back affected projections and reprocess canonical events. Update transaction/listing/artwork atomically. Competing purchases may be submitted: the contract must allow exactly one settlement; losers fail without changing ownership. Royalties and price snapshots come from that settlement, not mutable client input.

## Page 3 — NFT metadata and acceptance contract

Metadata is UTF-8 JSON pinned to content-addressed storage before minting. Store essential fields on `artworks`; metadata URI is the token URI. Mint freezes the fields: later profile changes cannot alter NFT metadata. A failed mint may be edited and repinned under a new URI. Require canonical `ipfs://` URIs for image and metadata (no expiring upload URLs); serve through a configured gateway with safe content handling. Upload handling must decode images, enforce byte limits, and avoid arbitrary server-side URL fetching.

| Essential field | JSON mapping / validation |
| --- | --- |
| Title | `name` ← `title`: trimmed, 1–120 characters |
| Description | `description`: trimmed, 1–2,000 characters; plain text, not executable markup |
| Image URI | `image` ← `image_uri`: required pinned image; creator must reference their validated upload using a server-signed upload receipt |
| Attributes | `attributes`: array, defaults to `[]`, maximum 20 entries; each `{trait_type,value}` with unique nonempty trait type ≤64 characters; value string ≤256 characters or finite JSON number |
| Royalties | `seller_fee_basis_points` ← integer `royalty_bps`, defaults to 0, proposed range 0–1,000 (0–10%); `fee_recipient` ← valid nonzero `royalty_recipient`, defaults to creator wallet |

Example (CID/address placeholders must be replaced before minting):

```json
{
  "name": "Neon Orchard",
  "description": "An AI-assisted study of a luminous garden.",
  "image": "ipfs://<image-cid>/orchard.png",
  "attributes": [{"trait_type": "Style", "value": "Surrealism"}],
  "seller_fee_basis_points": 500,
  "fee_recipient": "<creator-wallet-address>"
}
```

Royalty JSON keys are marketplace conventions, not ERC-721 guarantees. Set the same recipient/rate in the token contract; require marketplace settlement to honor ERC-2981: royalty = floor(price × bps / 10,000), seller receives the remainder, buyer pays price plus gas. Other marketplaces may not enforce royalties. Do not publish private prompts or personal information in immutable metadata.

### Implementation acceptance tests

1. **Auth/access:** reject expired/replayed nonces, wrong domain/chain/signature, unauthenticated writes, non-owner listing, non-author deletion, and other users' draft reads. Session logout prevents reuse.
2. **Creation/metadata:** valid upload → draft → pinned JSON with the exact field mapping; reject oversized/spoofed files, missing title, invalid attributes/URI, out-of-range royalties, and another user’s upload receipt. Omitted attributes/royalties yield `[]`/0 bps. Freeze pending/minted metadata; failed mint permits editing.
3. **Mint/list:** unconfirmed receipts never publish ownership/listings; verified confirmation does. Duplicate preparation/submission/event replay creates no duplicate token or listing. Cross-artwork listing references and forged server-managed fields fail. Price is exact; zero/negative/overflow prices fail. Same idempotency key/body returns the same intent; changed body returns `409`. Concurrent duplicate live listings fail at the DB constraint.
4. **Purchase/cancel:** stale price and self-purchase fail; two racing buyers yield one sale; failed/cancelled-chain transactions do not transfer ownership. Confirmed purchase sets buyer ownership and exact royalty/seller amounts. Purchase versus cancellation follows canonical event order.
5. **Social/discovery:** stable cursor pagination, filters, and private-draft exclusion; repeated like creates one row, unlike and comment deletion are repeat-safe, escaped comments render without script execution, counts match visible rows.
6. **Recovery:** worker restart, delayed receipt, external transfer, approval revocation, and reorg converge to canonical ownership/status without duplicate settlement. Test expiry with an unreported broadcast, confirmation after deadline, and idempotent retry after confirmation. Test at the chosen confirmation threshold and with a mock chain.

These are required future application/contract tests, not existing test coverage. Before implementation, approve the proposed defaults, select contracts/storage and confirmation depth, and define retention/moderation policy; production additionally requires security and legal review.
