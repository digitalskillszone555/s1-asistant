# Midnight Obsidian Design System

### 1. Overview & Creative North Star
**Creative North Star: "The Obsidian Lens"**
Midnight Obsidian is a high-end editorial system designed for technical sophistication and cinematic depth. It eschews the "flatness" of typical SaaS dashboards in favor of a layered, immersive experience that feels like peering through a high-precision glass instrument. The system is built on the tension between the deep, infinite voids of the background and the sharp, glowing precision of interactive elements.

Asymmetry is used intentionally to guide the eye; large typographic headers are offset by compact, high-density data visualizations, creating a rhythmic "ebb and flow" of information.

### 2. Colors
The palette is rooted in deep space blacks (`#0a0c10`) and slate grays, punctuated by high-vibrancy accent "neon" signals.

- **The "No-Line" Rule:** Structural borders are strictly prohibited for layout sectioning. Visual separation is achieved through background color shifts (e.g., transitioning from `surface` to `surface_container_low`) or by utilizing the "Glass" effect.
- **Surface Hierarchy & Nesting:** Use `surface_container_low` for the base canvas and `surface_container` for interactive cards. The hierarchy must feel natural—darker elements appear further away, while lighter, glass-filtered elements float "closer" to the user.
- **The "Glass & Gradient" Rule:** All floating menus and sticky headers must use Glassmorphism (Background: `rgba(15, 23, 42, 0.6)` with a `12px` backdrop blur). 
- **Signature Textures:** Hero headings should employ a subtle vertical or horizontal text gradient (e.g., `from-white to-slate-500`) to create a sense of metallic sheen.

### 3. Typography
The system utilizes **Inter** across all roles to maintain a unified, technical aesthetic, relying on extreme weight variance and tracking to create hierarchy.

- **Display & Headline:** Uses the high end of the scale (`3rem` or `2.25rem`). Tracking should be set to `-0.025em` (tight) for headlines to create a sophisticated editorial look.
- **Body & Labels:** Employs `1rem` and `0.875rem` for readability. 
- **The "Technical Subtext":** Labels and status indicators use a micro-scale (`10px`) with high letter spacing (`0.1em`) and uppercase styling to denote system-level information.

**Real-world scale used in this system:**
- Display: `3rem` (48px) / `2.25rem` (36px)
- Title: `1.25rem` (20px) / `1.125rem` (18px)
- Body: `1rem` (16px) / `0.875rem` (14px)
- Label: `0.75rem` (12px) / `10px`

### 4. Elevation & Depth
Elevation is expressed through light and transparency, not just shadow.

- **Ambient Shadows:** Shadows must be soft and expansive. The standard elevation shadow is `0 8px 32px 0 rgba(0, 0, 0, 0.37)`.
- **Glow states:** Interactive elements use "Glow" instead of traditional shadows. The "Primary Glow" is `0 0 20px rgba(56, 189, 248, 0.15)`.
- **Glassmorphism:** Components like the header utilize a `1px` border with `white/10` opacity to define the edge of the glass pane without creating a heavy visual line.
- **The Layering Principle:** Stack `surface_container` on top of `surface` with a 1px `white/5` border-top to simulate thin glass sheets.

### 5. Components
- **Buttons:** Primary buttons are not solid blocks; they are transparent glass panes with a vibrant `accent` border and text.
- **Cards:** Use a "Glow-Hover" pattern. Upon hover, cards should lift (`-2px` Y-axis) and the shadow should intensify to `0 0 25px rgba(56, 189, 248, 0.3)`.
- **Chips & Indicators:** Status chips are pill-shaped with a `10%` opacity background of their semantic color (e.g., Emerald for success) and a `20%` opacity border.
- **Input Fields:** High-density, `xl` (0.75rem) rounded corners, utilizing a subtle `slate-800/50` fill.

### 6. Do's and Don'ts
**Do:**
- Use gradients in text for primary headlines to add depth.
- Use backdrop-blur for all overlapping UI elements.
- Maintain wide gutters (spacing: 3) to allow the "Obsidian" background to breathe.

**Don't:**
- Never use a solid `#000000` background; use the curated obsidian dark `#0a0c10`.
- Do not use standard 1px solid gray borders.
- Avoid using icons without purpose; every icon should either be an action or a semantic signal.