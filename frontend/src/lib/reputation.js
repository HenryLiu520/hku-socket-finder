/**
 * What an account has earned, from one number: settled reports that turned out right.
 *
 * The incentive is deliberately counted in confirmed reports rather than in reports, so
 * filing more earns nothing and being right earns everything. The tiers are the only place
 * a threshold lives, which keeps the reward rule readable next to the score rule.
 */
export const BADGES = [
  { key: 'starter', at: 1 },
  { key: 'reliable', at: 5 },
  { key: 'trusted', at: 10 },
  { key: 'steward', at: 25 }
]

export function badgeFor(confirmed = 0) {
  const earned = BADGES.filter((b) => confirmed >= b.at)
  const next = BADGES.find((b) => confirmed < b.at) || null
  const floor = earned.length ? earned[earned.length - 1].at : 0
  const ceiling = next ? next.at : floor
  const span = Math.max(1, ceiling - floor)
  return {
    earned: earned.length ? earned[earned.length - 1].key : null,
    earnedCount: earned.length,
    next: next ? next.key : null,
    need: next ? next.at - confirmed : 0,
    progress: next ? Math.min(1, Math.max(0, (confirmed - floor) / span)) : 1
  }
}
