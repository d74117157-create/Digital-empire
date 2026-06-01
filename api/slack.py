import os, re, json, logging
from flask import Flask, request, make_response
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
import anthropic

log = logging.getLogger("empire-agent")
bolt = App(token=os.environ["SLACK_BOT_TOKEN"], signing_secret=os.environ["SLACK_SIGNING_SECRET"])
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
flask_app = Flask(__name__)
handler = SlackRequestHandler(bolt)

CHANNELS = {
    "all-lulu":"C0AR83WJ0P5","content-engine":"C0B6UCSMX3R",
    "affiliate-revenue":"C0B6UCSH3K9","digital-products":"C0B73FDDS1H",
    "marketing-engine":"C0B7DF286Q4","pipeline-logs":"C0B76F1LS2H",
    "youtube-queue":"C0B79TDFNSE","youtube-live":"C0B7BNAK4NM","empire-results":"C0B79TDQUD8",
}
MONITORED = set(CHANNELS.values())
EPISODES = [
    "The African Queen Who Defeated Rome — Queen Amanirenas",
    "Mansa Musa — The Richest Human Who Ever Lived",
    "The Moors Who Built Medieval Europe",
    "The Great Zimbabwe Empire",
    "Cleopatra Was Black — The Historical Evidence",
    "The Ethiopian Victory Over Italy 1896",
    "Sundiata Keita — The Real Lion King",
    "The University of Timbuktu — 700,000 Manuscripts",
    "The Benin Bronzes — Africa's Stolen Masterpieces",
    "Queen Nzinga — Who Outsmarted Portugal",
]
_idx = 0

def ask(system, user, tokens=1000):
    r = claude.messages.create(model="claude-opus-4-6", max_tokens=tokens, system=system, messages=[{"role":"user","content":user}])
    return r.content[0].text.strip()

def gen_script(topic):
    return ask("Viral African history YouTube Shorts scriptwriter. Return script only.",
        f"Write 60-second script (≤175 words) for: '{topic}'\n[HOOK 0:00-0:03]\n[BODY 0:03-0:50]\n[CTA 0:50-1:00] include [ELEVENLABS_LINK] [GUMROAD_LINK]")

def gen_email():
    return ask("Email copywriter for African history creator.",
        "Write 3-email sequence selling 'AI First $500 Blueprint' ($37) at luluheart33.gumroad.com\nEmail 1: history hook\nEmail 2: AI tools value\nEmail 3: product pitch. Include subject lines.")

def gen_social(topic):
    return ask("Viral social media strategist for Black history.",
        f"For: '{topic}'\nWrite: 1 Twitter thread (7 tweets) + 1 Instagram caption (150 words + 12 hashtags)")

def gen_metadata(topic):
    raw = ask("Return ONLY valid JSON, no markdown.",
        f'{{"title":"...viral title...","description":"...200 words with [ELEVENLABS_LINK] [TUBEBUDDY_LINK] [GUMROAD_LINK] [BEEHIIV_LINK]...","tags":["...30 tags..."],"thumbnail_text":"4 WORDS ALL CAPS"}} for topic: "{topic}"')
    try: return json.loads(raw)
    except: return json.loads(re.sub(r"```json|```","",raw).strip())

def route(text):
    global _idx
    t = text.lower()
    if any(w in t for w in ["status","check"]): return "pipeline-logs","🟢 *EMPIRE STATUS* — All systems online ✅"
    if "email" in t: return "marketing-engine",f"📧 *EMAIL SEQUENCE*\n\n{gen_email()}"
    if any(w in t for w in ["social","twitter","instagram"]):
        m=re.search(r"(?:about|on)\s+(.+)",t); topic=m.group(1).strip() if m else EPISODES[0]
        return "marketing-engine",f"📱 *SOCIAL — {topic}*\n\n{gen_social(topic)}"
    if any(w in t for w in ["youtube","upload","post video","next video"]):
        topic=EPISODES[_idx%len(EPISODES)]; _idx+=1; meta=gen_metadata(topic); script=gen_script(topic)
        return "youtube-live",f"🎬 *YOUTUBE — {topic}*\n*Title:* {meta.get('title','')}\n*Thumbnail:* `{meta.get('thumbnail_text','')}`\n\n```{script[:700]}```"
    if any(w in t for w in ["script","generate","episode","write","next"]):
        m=re.search(r"(?:about|on|for)\s+(.+)",t); topic=m.group(1).strip() if m else EPISODES[_idx%len(EPISODES)]; _idx+=1
        meta=gen_metadata(topic); script=gen_script(topic)
        return "content-engine",f"🎬 *SCRIPT — {topic}*\n\n```{script[:800]}```\n\n📌 *Title:* {meta.get('title','')}\n🖼️ `{meta.get('thumbnail_text','')}`"
    if any(w in t for w in ["help","commands"]): return "pipeline-logs","🤖 *COMMANDS*\n`generate script about [topic]`\n`post to youtube`\n`email sequence`\n`social post about [topic]`\n`status`"
    topic=text[:100] if len(text)>8 else EPISODES[_idx%len(EPISODES)]; _idx+=1
    return "content-engine",f"🎬 *SCRIPT*\n\n```{gen_script(topic)[:800]}```"

@bolt.event("message")
def on_message(event, client, say):
    if event.get("bot_id") or event.get("subtype"): return
    channel=event.get("channel"); text=re.sub(r"<@[A-Z0-9]+>","",event.get("text","")).strip(); ts=event.get("ts")
    if channel not in MONITORED or len(text)<3: return
    try: client.reactions_add(channel=channel,timestamp=ts,name="zap")
    except: pass
    try:
        target_name,result=route(text); target_id=CHANNELS.get(target_name,channel)
        client.chat_postMessage(channel=target_id,text=result)
        if target_id!=channel: say(text=f"✅ → #{target_name}",thread_ts=ts)
        client.chat_postMessage(channel=CHANNELS["pipeline-logs"],text=f"```[EXEC] {text[:60]} → #{target_name}```")
    except Exception as e: say(text=f"❌ `{e}`",thread_ts=ts)

@bolt.event("app_mention")
def on_mention(event,client,say): on_message(event,client,say)

@flask_app.route("/api/slack",methods=["POST"])
def slack_events(): return handler.handle(request)

@flask_app.route("/",methods=["GET"])
def health(): return make_response("🏛️ Digital Empire — Live",200)

app=flask_app
