# 🏛️ Digital Empire

Claude-powered Slack agent + YouTube automation pipeline for African history content creation.

## Features

- **AI Script Generation** - Claude generates viral YouTube Shorts scripts
- **Email Marketing** - Automated 3-email sales sequences
- **Social Media** - Twitter threads + Instagram captions
- **Metadata Generation** - Titles, descriptions, tags, thumbnails
- **Channel Routing** - Automatic message routing to relevant Slack channels
- **Pipeline Logging** - Execution tracking and monitoring

## Setup

### 1. Environment Variables

Create a `.env` file with:

```
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_SIGNING_SECRET=your-signing-secret
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 2. Deploy to Vercel

```bash
vercel deploy
```

The app will be deployed as a serverless function at your Vercel URL.

### 3. Configure Slack App

1. Go to your Slack app settings
2. Set Request URL to: `https://your-vercel-url.vercel.app/api/slack`
3. Subscribe to events: `message`, `app_mention`
4. Install the app to your workspace

## Commands

- `generate script about [topic]` - Create YouTube Shorts script
- `post to youtube` - Generate full YouTube video package
- `email sequence` - Create sales email sequence
- `social post about [topic]` - Generate Twitter + Instagram content
- `status` - Check system status
- `help` - Show available commands

## Episodes

The bot cycles through curated African history episodes:
- The African Queen Who Defeated Rome — Queen Amanirenas
- Mansa Musa — The Richest Human Who Ever Lived
- The Moors Who Built Medieval Europe
- The Great Zimbabwe Empire
- And 6 more...

## Tech Stack

- **Framework**: Flask + Slack Bolt
- **AI**: Anthropic Claude Opus 4.6
- **Deployment**: Vercel (Python Runtime)
- **Python**: 3.9+

## Architecture

```
Slack → Vercel (Flask) → Slack Bolt → Claude API → Slack Channels
```

Messages in monitored channels trigger the bot, which:
1. Routes the request to the appropriate handler
2. Calls Claude for content generation
3. Posts results to the target channel
4. Logs execution to pipeline-logs
