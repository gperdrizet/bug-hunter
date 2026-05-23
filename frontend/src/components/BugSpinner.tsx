// Two-frame pixel-art walking animation using a tripod gait.
// Frame A: Tripod A (L-front, R-mid, L-back) supporting; Tripod B raised 1px.
// Frame B: Tripod B (R-front, L-mid, R-back) supporting; Tripod A raised 1px.
// CSS alternates the two <g> groups with steps(1, end) for crisp pixel jumps.

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

      {/* ── Frame A: Tripod A normal · Tripod B raised ── */}
      <g className="bug-walk-a">
        {/* L-front — normal: (4,6) (3,5) (1-2,4) */}
        <rect x="4" y="6" width="1" height="1" fill={G} />
        <rect x="3" y="5" width="1" height="1" fill={G} />
        <rect x="1" y="4" width="2" height="1" fill={G} />

        {/* R-mid — normal: (11-14,8) */}
        <rect x="11" y="8" width="4" height="1" fill={G} />

        {/* L-back — normal: (4,10) (3,11) (1-2,12) */}
        <rect x="4" y="10" width="1" height="1" fill={G} />
        <rect x="3" y="11" width="1" height="1" fill={G} />
        <rect x="1" y="12" width="2" height="1" fill={G} />

        {/* R-front — raised (y−1): (11,5) (12,4) (13-14,3) */}
        <rect x="11" y="5" width="1" height="1" fill={G} />
        <rect x="12" y="4" width="1" height="1" fill={G} />
        <rect x="13" y="3" width="2" height="1" fill={G} />

        {/* L-mid — raised (y−1): (1-4,7) */}
        <rect x="1" y="7" width="4" height="1" fill={G} />

        {/* R-back — raised (y−1): (11,9) (12,10) (13-14,11) */}
        <rect x="11" y="9"  width="1" height="1" fill={G} />
        <rect x="12" y="10" width="1" height="1" fill={G} />
        <rect x="13" y="11" width="2" height="1" fill={G} />
      </g>

      {/* ── Frame B: Tripod A raised · Tripod B normal ── */}
      <g className="bug-walk-b">
        {/* L-front — raised (y−1): (4,5) (3,4) (1-2,3) */}
        <rect x="4" y="5" width="1" height="1" fill={G} />
        <rect x="3" y="4" width="1" height="1" fill={G} />
        <rect x="1" y="3" width="2" height="1" fill={G} />

        {/* R-mid — raised (y−1): (11-14,7) */}
        <rect x="11" y="7" width="4" height="1" fill={G} />

        {/* L-back — raised (y−1): (4,9) (3,10) (1-2,11) */}
        <rect x="4" y="9"  width="1" height="1" fill={G} />
        <rect x="3" y="10" width="1" height="1" fill={G} />
        <rect x="1" y="11" width="2" height="1" fill={G} />

        {/* R-front — normal: (11,6) (12,5) (13-14,4) */}
        <rect x="11" y="6" width="1" height="1" fill={G} />
        <rect x="12" y="5" width="1" height="1" fill={G} />
        <rect x="13" y="4" width="2" height="1" fill={G} />

        {/* L-mid — normal: (1-4,8) */}
        <rect x="1" y="8" width="4" height="1" fill={G} />

        {/* R-back — normal: (11,10) (12,11) (13-14,12) */}
        <rect x="11" y="10" width="1" height="1" fill={G} />
        <rect x="12" y="11" width="1" height="1" fill={G} />
        <rect x="13" y="12" width="2" height="1" fill={G} />
      </g>
    </svg>
  );
}
