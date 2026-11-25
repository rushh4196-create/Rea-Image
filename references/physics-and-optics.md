# Optical, Lighting & Physical Realism Audit Checklist

Apply this checklist during Stage 2 (reverse engineering) and Stage 5 (final verification) so recreated images maintain convincing real-world physics rather than flat or warped approximations.

## 1. Camera Optics & Depth of Field

- **Focal Length & Compression**: Wide lenses (24-35mm) exaggerate foreground-to-background scale and perspective convergence; portrait/telephoto lenses (85-135mm) compress background distance and isolate subjects.
- **Focal Plane Consistency**: Identify the exact sharp focus plane and enforce continuous optical bokeh falloff in front of and behind that plane. Foreground objects closer than the focus plane must blur softly and organically.
- **Orientation & Horizon**: Respect exact camera tilt, Dutch angle, or 90-degree sideways rotation without accidentally straightening the horizon.

## 2. Lighting & Atmospheric Physics

- **Single Coherent Light Logic**: Lock key light direction, elevation, and hardness (hard direct sun creates crisp shadow edges; overcast/mist creates soft diffused falloff).
- **Backlighting & Rim Wrap**: When strong light sits behind a subject (sun, bright cloud, window), add realistic warm/cool rim highlights along hair, fingers, clothing edges, and translucent grass/leaves, with subtle atmospheric bloom rather than hard artificial halos.
- **Shadow Color & Bounce Light**: Shadows in outdoor daylight pick up cool sky bounce light (blue/teal); never render flat neutral-black shadows unless the scene is pitch-dark.

## 3. Anatomy, Gravity & Material Behavior

- **Hands, Limbs & Posture**: Check finger counts, natural knuckle bends, wrist taper, grip pressure around held objects (stems, cups, tools), and believable joint angles.
- **Gravity & Fabric Drape**: Clothing folds, sleeves, hair strands, and plant stems must obey gravity and wind direction consistently across the entire frame.
- **Contact & Weight**: Resting objects (on tables, posts, grass) must make solid contact with grounded contact shadows and natural occlusion—never floating or clipped.
- **Material Specularity & Translucency**: Distinguish matte fabric, glossy glass/metal reflections, subsurface scattering on skin/petals, and translucent backlit cloth or foliage.
