# Network Watchlist

This file contains the list of endpoints that the `network-sentry` skill checks during a full diagnostic run.

## Target Endpoints
Add your important servers or services here.

- **Google DNS**: 8.8.8.8 (Baseline for external connectivity)
- **Local Gateway**: localhost (Port 18789)
- **Public Entry**: bot1.twming1.dpdns.org (Port 443)

## How to use
Tell the agent to "Update my network watchlist with [Target]" to modify this list.
