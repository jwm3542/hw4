# HW 4 — Scenario

Campus Customs needs a real customer-facing website with a helpful chatbot.

## Stack
- **Front end:** React + Vite + TypeScript
- **Back end:** Python FastAPI, with a PydanticAI Agent as the brain
- **Analog:** Lecture 7

## What shoppers should be able to do
- Browse products
- Create an account
- Chat about merch
- See matching items appear on the page from the chat
- Get honest answers about price and stock, pulled from a local database

## Data
`data.zip` unzips to `data/`, which git ignores and we never commit.
- `data/campus_customs.db` is a SQLite database with these tables:
  - `catalogue` (102 rows): `product_id`, `name`, `garment_type`, `description`, `colors` (JSON list), `search_tags` (JSON list), `image_file_path` (relative to `data/`, e.g. `products/x.jpg`) and `price` ($32 to $98)
  - `inventory` (612 rows): `product_id`, `size` (XS, S, M, L, XL or XXL) and `quantity`. 145 of these rows have a quantity of 0, so the agent must check stock honestly.
  - `users` (3 rows): `name`, `first_name`, `last_name`, `email`, `password_hash` (`pbkdf2_sha256`) and `created_at`. The given test user is `test@campuscustoms.yale.edu`.
  - `chat_messages` (22 rows): `user_id`, `role`, `content`, `products_json` and `created_at`. It holds saved chat history, including which products were shown.
- `data/products/` has 102 product images. Every `image_file_path` value points to a file that exists.
- `garment_type` values aren't consistent (for example "short-sleeve T-shirt" and "t-shirt"), so search should match on more than exact type.

## Style and agent knowledge
Research yalebulldogblue.com for the look of the Campus Customs page and for store information the agent should know. Findings are in `STYLE_RESEARCH.md`.

## AI calls
- All AI calls go through Portkey (OpenAI-compatible). They use `PORTKEY_API_KEY`, which is kept in `../.env`, the course folder one level above HW 4.
- We can use any model in the 5.6 or 6 series.
- The professor suggests using smarter models for the harder agent steps. See the model tiers in `.env.example`.

## Working rules
- We work one problem at a time. I describe each problem in my own words, with no screenshots or pasted URLs.

## Submission
- Push the project to a **public GitHub repo** and submit the repo URL on Canvas.
- **Do not commit the database or product images.** `.gitignore` excludes `*.db`, `data/` and image files.
