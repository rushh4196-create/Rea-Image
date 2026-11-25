# Image Taxonomy & Pipeline Selection Guide

Combine deterministic forensics (`forensics/report.json`) with visual inspection (`grid_overlay.png`, `tiles_3x3.png`) to assign the primary class and select the highest-fidelity recreation route.

## The 10 Image Classes

| Class | Forensic Signals | Visual Clues | Primary Route |
|---|---|---|---|
| **1. Real Photo** | Camera EXIF, low `flat_region_ratio` (< 0.35), natural Laplacian grain | Optical bokeh, authentic skin/fabric micro-texture, consistent reflections | Route A (or D for local edits) |
| **2. AI-Generated** | AIGC/C2PA/prompt tags, or missing EXIF with smooth shadow transitions | Hyper-clean lighting, stylized atmosphere, fine painterly smoothness | Route A |
| **3. 3D Render** | Software metadata (`Blender`, `Octane`, `C4D`), clean anti-aliased edges | Studio HDRI reflections, precise bevels, uniform subsurface scattering | Route A (or Three.js) |
| **4. 2D Illustration / Painting** | Distinct palette clusters, medium-high `edge_density` | Ink linework, cel shading, watercolor/oil brushwork, paper grain | Route A |
| **5. Vector / Flat Graphic / Logo** | Very high `flat_region_ratio` (> 0.65), small palette, crisp edges | Solid fills, Bezier geometry, zero sensor noise | Route B (SVG / HTML+CSS) |
| **6. UI / App / Web Screenshot** | Screen dimensions, high `flat_region_ratio`, PNG format | System fonts, 1px borders, aligned cards/navbars, crisp icons | Route B (HTML+CSS) |
| **7. Data Chart / Infographic** | High `flat_region_ratio`, structured grid, crisp data labels | Axes, bars/lines/pies, arrows, flow nodes, exact numbers | Route B (HTML / SVG / Matplotlib) |
| **8. Typographic Poster / Social Card** | High contrast, structured margins, large text coverage | Text hierarchy is the main visual on solid/gradient/geometric backdrop | Route B (HTML+CSS) |
| **9. Collage / Cutout Composite** | Mixed textures and lighting across layers | Torn edges, pasted photos, drop shadows separating elements | Route A, C, or D |
| **10. Hybrid (Base + Overlays)** | Photo/AI/3D base + razor-sharp flat text/badges on top | YouTube thumbnails, ad creatives, magazine covers, product banners, memes | Route C (AI Base + Code) |

## Quick Routing Checks

- **Real Photo vs. AI-Generated**: Platforms often strip EXIF on upload. Inspect `tiles_3x3.png` for micro-text legibility, hand/finger joints, jewelry symmetry, and reflection geometry.
- **Typographic Poster vs. Hybrid**: If the backdrop is solid, gradient, or geometric, choose **Route B** (pure code). Choose **Route C** when the backdrop is a complex photo, portrait, or painting with crisp text/graphics overlaid.
