// Two-frame pixel-art walking animation using a tripod gait.
// Each leg pivots between two angles — swept forward (raised/swinging) and swept back (planted/pushing).
// Frame A: Tripod A (L-front, R-mid, L-back) planted/swept-back · Tripod B raised/swept-forward.
// Frame B: Tripod B (R-front, L-mid, R-back) planted/swept-back · Tripod A raised/swept-forward.
// Leg tips sweep 4 pixels vertically between frames for a visible angle change.

const G = "#00FF41"; // main green
const D = "#00CC33"; // darker wing stripe
const E = "#003300"; // eyes

export default function BugSpinner({ size = 96 }: { size?: number }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 16 16"
      width={size}
      height={size}
      shapeRendering="crispEdges"
      style={{ imageRendering: "pixelated" }}
    >
      {/* ── Static: antennas, head, body, tail ── */}

      {/* Antennas */}
      <rect x="5"  y="1" width="1" height="1" fill={G} />
      <rect x="10" y="1" width="1" height="1" fill={G} />
      <rect x="6"  y="2" width="1" height="1" fill={G} />
      <rect x="9"  y="2" width="1" height="1" fill={G} />
      <rect x="6"  y="3" width="4" height="1" fill={G} />

      {/* Head */}
      <rect x="5" y="4" width="6" height="2" fill={G} />
      <rect x="6" y="5" width="1" height="1" fill={E} />
      <rect x="9" y="5" width="1" height="1" fill={E} />

      {/* Body */}
      <rect x="5" y="6" width="6" height="6" fill={G} />
      <rect x="7" y="6" width="2" height="6" fill={D} />

      {/* Tail */}
      <rect x="6" y="12" width="4" height="1" fill={G} />

      {/* ── Frame A: Tripod A planted (swept back) · Tripod B raised (swept forward) ── */}
      <g className="bug-walk-a">
        {/* L-front — planted/back:    root(4,6) → (3,7) → tip(1-2,8) */}
        <rect x="4" y="6"  width="1" height="1" fill={G} />
        <rect x="3" y="7"  width="1" height="1" fill={G} />
        <rect x="1" y="8"  width="2" height="1" fill={G} />

        {/* R-mid — planted/back:      root(11,8) → (12,9) → tip(13-14,10) */}
        <rect x="11" y="8"  width="1" height="1" fill={G} />
        <rect x="12" y="9"  width="1" height="1" fill={G} />
        <rect x="13" y="10" width="2" height="1" fill={G} />

        {/* L-back — planted/back:     root(4,10) → (3,11) → tip(1-2,12) */}
        <rect x="4" y="10" width="1" height="1" fill={G} />
        <rect x="3" y="11" width="1" height="1" fill={G} />
        <rect x="1" y="12" width="2" height="1" fill={G} />

        {/* R-front — raised/forward:  root(11,6) → (12,5) → tip(13-14,4) */}
        <rect x="11" y="6" width="1" height="1" fill={G} />
        <rect x="12" y="5" width="1" height="1" fill={G} />
        <rect x="13" y="4" width="2" height="1" fill={G} />

        {/* L-mid — raised/forward:    root(4,8) → (3,7) → tip(1-2,6) */}
        <rect x="4" y="8" width="1" height="1" fill={G} />
        <rect x="3" y="7" width="1" height="1" fill={G} />
        <rect x="1" y="6" width="2" height="1" fill={G} />

        {/* R-back — raised/forward:   root(11,10) → (12,9) → tip(13-14,8) */}
        <rect x="11" y="10" width="1" height="1" fill={G} />
        <rect x="12" y="9"  width="1" height="1" fill={G} />
        <rect x="13" y="8"  width="2" height="1" fill={G} />
      </g>

      {/* ── Frame B: Tripod B planted (swept back) · Tripod A raised (swept forward) ── */}
      <g className="bug-walk-b">
        {/* R-front — planted/back:    root(11,6) → (12,7) → tip(13-14,8) */}
        <rect x="11" y="6" width="1" height="1" fill={G} />
        <rect x="12" y="7" width="1" height="1" fill={G} />
        <rect x="13" y="8" width="2" height="1" fill={G} />

        {/* L-mid — planted/back:      root(4,8) → (3,9) → tip(1-2,10) */}
        <rect x="4" y="8"  width="1" height="1" fill={G} />
        <rect x="3" y="9"  width="1" height="1" fill={G} />
        <rect x="1" y="10" width="2" height="1" fill={G} />

        {/* R-back — planted/back:     root(11,10) → (12,11) → tip(13-14,12) */}
        <rect x="11" y="10" width="1" height="1" fill={G} />
        <rect x="12" y="11" width="1" height="1" fill={G} />
        <rect x="13" y="12" width="2" height="1" fill={G} />

        {/* L-front — raised/forward:  root(4,6) → (3,5) → tip(1-2,4) */}
        <rect x="4" y="6" width="1" height="1" fill={G} />
        <rect x="3" y="5" width="1" height="1" fill={G} />
        <rect x="1" y="4" width="2" height="1" fill={G} />

        {/* R-mid — raised/forward:    root(11,8) → (12,7) → tip(13-14,6) */}
        <rect x="11" y="8" width="1" height="1" fill={G} />
        <rect x="12" y="7" width="1" height="1" fill={G} />
        <rect x="13" y="6" width="2" height="1" fill={G} />

        {/* L-back — raised/forward:   root(4,10) → (3,9) → tip(1-2,8) */}
        <rect x="4"  y="10" width="1" height="1" fill={G} />
        <rect x="3"  y="9"  width="1" height="1" fill={G} />
        <rect x="1"  y="8"  width="2" height="1" fill={G} />
      </g>
    </svg>
  );
}
