# Design: "The Shop at 57 Broadway" (Problem 10)

**Concept:** Campus Customs as a real college-town storefront. An 1880s brick building, a shop that moved in in 1975, and 50 years of layers since, including the 1984 back-room amp that goes to 11. Yale blue stays the anchor color, so it still reads as Bulldog Blue. Styles live in `frontend/src/theme.css`, loaded after the base styles.

| Area | What we changed | Why it helps shoppers stay and buy |
|---|---|---|
| **Fonts** | Three typefaces for three eras: **Rye** (1880s gold-leaf sign) for the wordmark and labels, **Fraunces** with its soft, rounded 1970s settings for headings and prices, and **Karla** for body text. | Distinct type gives the store a personality you remember. Body text stays plain and readable, so descriptions and prices are easy to scan. |
| **Color** | Yale blue and navy kept as the anchor, layered with cream paper (with a subtle grain), brick, wood, brass and 70s mustard and orange. | It feels warm and established instead of a generic template, and still clearly Yale. Prices and buttons stay high-contrast blue or brass on cream. |
| **Storefront shell** | The header is a wood sign board with a gold-leaf "Campus Customs," a CC "Est. 1975" seal and a brick-red banner. A striped **scalloped awning** sways gently. | The first second says "real shop, been here forever," which builds trust that the merch is legit and officially licensed. |
| **Hero** | A **wood-framed arched shop window** on a brick wall, with gold-leaf lettering, a slow glass glare, a flickering **neon OPEN sign** and 70s sunset stripes rising behind it. A brass "Lay some threads on me" button. | One obvious place to look and one obvious button (Shop). Motion is slow and decorative, so it catches the eye without getting in the way. |
| **Hierarchy** | Home tiles became **pinned notes** on a corkboard (slight tilts, colored pins). "Fresh off the rack, *hand-picked by the clerk*." | Short, scannable sections in a clear order: window, then categories, then products. |
| **Product presentation** | Cards hang from a **hanger hook** that appears on hover, tilt slightly and zoom the photo. Prices sit on a paper **hang tag** with a punched hole. Stock badges look like tilted stickers. On product pages, the photo sits in a **brass-trimmed frame**, and sizes are round buttons. | Browsing feels like flipping through a rack. The price is the most noticeable thing on each card, and the hover feedback invites clicks into the product page. |
| **Chat feel** | The chat button is a **brass counter bell** 🛎️ that rings on hover. The panel is **"Ask the Clerk"**: a wood header, replies on **ruled notepad paper** with a red margin line, typewriter-style serif text. Chat results arrive as "the clerk pulled these from the back room," over a 70s-stripe banner. | Asking the clerk feels natural and friendly, so more shoppers use the chat, which leads them straight to in-stock products. |
| **Footer** | A wood counter with a **brass plaque** timeline (1880s building, 1975 opening, 1984 amps to 11, today), plus contact info. | The story builds trust, and the store's address, phone and email are always one glance away. |
| **Delight: up to 11** | A working **amp knob** in the footer (click, or use the arrow keys; it's a real slider for keyboards and screen readers). At **11**, the whole site flips to **1984 metal mode**: black and chrome, Metal Mania headlines, flames in the sunset, a glowing knob. Click again to go back to 7. The setting is remembered. | A memorable, shareable easter egg that rewards exploring, and it ties straight to the Spinal Tap theme of our copy. Turning it on is optional, so normal shopping is never affected. |

**Accessibility and responsiveness:**
- All animation stops for users who turn on the reduced-motion setting.
- Contrast is kept on cream, wood and navy.
- The knob is keyboard-operable, and focus outlines are gold.
- On phones, the header shrinks to one line (logo and Menu) and scrolls away instead of covering the screen. The footer stacks into one column.

**Checked in the running app (2026-10-21):**
- Home, product page, chat, footer and metal mode all render on desktop and at 375 px mobile width.
- Rye, Fraunces and Karla load, and Metal Mania loads when 11 is turned on.
- The chat still answers correctly in the new panel: "Morse 1/4 Zip… in stock in M, with 8 available at $72.00."
