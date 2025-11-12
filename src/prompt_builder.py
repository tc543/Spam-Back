from .llm_prompter import *
import re


RE_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
RE_PHONE = re.compile(r"(?:\+?\d{1,3}[ -.]?)?(?:\(?\d{2,4}\)?[ -.]?)?\d{3,4}[ -.]?\d{3,4}")
RE_CARD = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
RE_URL = re.compile(r"https?://\S+|www\.\S+")
RE_ONE_TIME_CODE = re.compile(r"\b\d{4,8}\b")

def is_safe_reply(text: str) -> tuple[bool, list]:
    found = []
    if RE_EMAIL.search(text):
        found.append("email")
    if RE_PHONE.search(text):
        found.append("phone")
    if RE_CARD.search(text):
        found.append("card")
    if RE_URL.search(text):
        found.append("url")
    if RE_ONE_TIME_CODE.search(text):
        found.append("possible code")
    if len(text) > 1000:
        found.append("too long")
    return (len(found) == 0, found)

def sanitize_reply(text: str) -> str:
    text = RE_URL.sub("[link removed]", text)
    text = RE_EMAIL.sub("[email removed]", text)
    text = RE_CARD.sub("[removed]", text)
    text = re.sub(r"\b(\d{3})\d{4,}\b", r"\1[...]", text)
    return text

def safe_wrapper(reply: str):
    safe, issues = is_safe_reply(reply)
    if not safe:
        print("unsafe content detected:", issues)
        reply = sanitize_reply(reply)
    return reply

def init_summary_conversation(conversation: str, group_chat: bool, me: str, group_size: int = 0):
    prompt = f"""
    You are one of the participants in the following conversation, referred to as {me}.

    Generate a clear and well structured summary of the conversation. 
    Your goal is to capture the essential context so that future messages can be understood without rereading the entire chat.

    Organize your response into the following sections:
    - **Participants:** Identify who is involved and their general roles or perspectives.
    - **Main Topics:** Describe the key subjects or themes discussed.
    - **Intentions / Actions:** Summarize what each participant seems to be trying to achieve or express.
    - **Overall Summary:** Provide a concise narrative tying the conversation together.

    Keep it informative and coherent, detailed enough to preserve context, 
    but avoid unnecessary repetition or excessive length.

    Conversation:

    {conversation}
    """
    if group_chat:
        prompt += f"This is a group chat conversation of {group_size} people.\n\n"
    else:
        prompt += "This is a direct message.\n\n"
    llm = llama3("llama3:latest")
    return llm.get_model_response(prompt)

def update_summary_conversation(conversation: str, prev_summary : str, me: str):
    prompt = f"""
    You are one of the participants in the conversation, referred to as {me}.

    Below is the previous summary of the conversation so far:

    {prev_summary}

    Now, here are the new incoming messages:

    {conversation}

    Please update the summary to include the new information while maintaining context from the previous summary.

    Organize your updated summary into the following sections:
    - **Participants:** Update or confirm who is involved and their roles.
    - **Main Topics:** Reflect any new topics or developments.
    - **Intentions / Actions:** Note any changes in participants' goals, tone, or direction.
    - **Overall Summary:** Integrate the old and new information into one coherent summary that reflects the current state of the conversation.

    Keep it informative, logically structured, and moderately detailed, 
    ensuring it can serve as context for future messages without rereading the full chat.
    """

    """
    Might or might not need it, depending on how well llm generating without this information
    """
    # if group_chat:
    #     prompt += "Again, this is a group chat conversation of {group_size} people.\n"
    # else:
    #     prompt += "Again, this is a direct message.\n"                               # it will be easier to see the purpose in this summary when including context clues around
    llm = llama3("llama3:latest")
    return llm.get_model_response(prompt)

def init_spammer_summary_conversation(conversation: str, group_chat: bool, me: str, group_size: int = 0):
    prompt = f"""
    You are an assistant summarizing an ongoing text conversation between {me} and one or more potential spammers or scammers.
    {me} is aware that the other participant may be a spammer or scammer, but intentionally keeps the conversation going in a playful or curious way to waste their time — without revealing this awareness.

    Your goal is to produce a clear, structured summary that preserves essential details and tone so that a language model can later continue the conversation naturally — while understanding that one participant might be engaging in spam or scam behavior.

    Organize your summary into the following sections:

    **Participants**
    - Briefly describe who is speaking (e.g., {me}: polite, cautious, playful; Spammer/Scammer: persistent, manipulative, or promotional tone).

    **Main Topics**
    - List the main subjects discussed (e.g., fake offers, product promotions, requests for info, distractions used by {me}).

    **Intentions / Actions**
    - Describe what each participant appears to be trying to achieve or imply.
    - Note any persuasion, manipulation, or baiting attempts from the spammer/scammer.
    - Mention how {me} responds (e.g., deflecting, wasting time, pretending interest, staying noncommittal).

    **Conversation Flow Summary**
    - Write a concise narrative (5-7 sentences) connecting the events naturally.
    - Clearly convey that the chat involves suspicious or unsolicited behavior, but avoid accusatory or emotional language — stay factual and neutral.

    Keep the summary informative, coherent, and short enough to serve as memory for future model calls.

    Conversation:

    {conversation}
    """
    if group_chat:
        prompt += f"This is a group chat conversation of {group_size} people.\n\n"
    else:
        prompt += "This is a direct message.\n\n"
    llm = llama3("llama3:latest")
    return llm.get_model_response(prompt)

def update_spammer_summary_conversation(conversation: str, prev_summary : str, me: str):
    prompt = f"""
    You are an assistant summarizing an ongoing text conversation between {me} and one or more potential spammers or scammers.
    {me} is aware that the other participant may be a spammer or scammer, but intentionally keeps the conversation going in a playful or curious way to waste their time — without revealing this awareness.
    
    Your task is to **update the existing summary** to include the latest messages, while keeping all relevant past context.  
    The final result should read as a **single, coherent, up to date summary** of the entire conversation so far.

    Below is the previous summary of the conversation:

    {prev_summary}

    Here are the new incoming messages:

    {conversation}

    Update the summary by integrating both sources into a unified, logically consistent narrative.  
    Preserve important details from the previous summary, and incorporate any new developments, tone changes, or behavioral clues from the latest messages.

    Organize your updated summary into the following sections:

    **Participants**
    - List who is involved and briefly describe their roles or tone (e.g., {me}: polite, evasive, playful; Spammer/Scammer: persuasive, manipulative, persistent).

    **Main Topics**
    - Summarize the main subjects or shifts in the discussion (e.g., fake offers, payment requests, distractions, or {me}'s deflection).

    **Intentions / Actions**
    - Describe what each participant appears to be trying to do or achieve.
    - Note any attempts at persuasion, manipulation, or deception by the spammer/scammer.
    - Mention how {me} responds - e.g., stalling, pretending interest, or asking irrelevant questions to waste time.

    **Overall Summary**
    - Combine the old and new information into one coherent overview.
    - Maintain context continuity (do not lose key details from the prior summary).
    - Ensure the narrative feels complete up to this point in time.

    Keep your summary informative, neutral, and concise — long enough to preserve the flow of the interaction, but short enough to serve as efficient memory for future model calls.
    """
    # TODO mention about it's a group chat if it is? My help with prompting?
    llm = llama3("llama3:latest")
    return llm.get_model_response(prompt)

def generate_response(conversation: str, initial: bool, me: str, summary: str | None = None) -> str:
    prompt = """
    """
    if initial:
        prompt += f"""
        You are one of the participants in the conversation, referred to as {me}.

        Read the following conversation and write a natural, contextually appropriate reply that smoothly continues the discussion. 
        Only output the reply text itself — do not include explanations, notes, or formatting.

        Conversation:

        {conversation}
        """
    else:
        prompt = f"""
        You are one of the participants in the conversation, referred to as {me}.

        Here is a summary of the conversation so far:

        {summary}

        Below are the new incoming messages:

        {conversation}

        Using the context from the summary and the new messages, write a natural and contextually appropriate reply that continues the conversation smoothly. 
        Only output the reply text itself — do not include explanations, formatting, or any additional commentary.
        """
    llm = llama3("llama3:latest")
    return safe_wrapper(llm.get_model_response(prompt))

def generate_spammer_response(conversation: str, initial: bool, me: str, summary: str | None = None) -> str:
    prompt = f"""
    System: You are an assistant whose job is to impersonate {me} in a text conversation.
    Your objective is to keep the other person engaged and waste their time, while strictly never revealing any real personal, financial, or identifying information.
    You must behave as if you do not suspect the person is a spammer/scammer — do NOT hint, accuse, or imply suspicion. Output must be only the reply text (no headers, explanations, or markup).

    Safety constraints (MUST be followed):
    - Do NOT provide any real personal data (full name, address, phone number, email, social media handles, account numbers, birthday).
    - Do NOT provide instructions that enable the other person (no links, no steps for downloading or installing anything, no executable code).
    - Do NOT ask for or reveal any one time codes, passwords, payment info, bank/account numbers, or identifiers.
    - Do NOT give medical, legal, or financial advice or any content that could be actionable.
    - If the person asks for sensitive info, refuse politely and divert to wasting time (e.g., ask an unrelated, silly question or request a long, pointless form).
    - Replies must be plausible as a human message but should be deliberately lengthy, ambiguous, and mildly engaging to waste the person's time.
    - Keep language non-accusatory and avoid insulting the person (no slurs, threats, doxxing).
    - Aim for 2-6 sentences or a short paragraph (unless the prompt asks for longer). Vary phrasing across replies to avoid repetition.

    Behavior rules (additional, MUST follow):
    - Do **not** reveal that you suspect the person is a scammer/spammer, investigating, or baiting them. Maintain the appearance of a genuine, naive, or mildly curious recipient.
    - Use curious, slightly confused, or helpful sounding follow ups that require the other person to give more information (which wastes their time).
    - If the person requests sensitive information, give a short refusal phrased as a benign policy or personal boundary (e.g., "I can't share that here"), then immediately divert into a long, tangential question or anecdote that sounds plausible and invites a reply.
    - Avoid definitive statements that confirm or deny factual claims about real accounts or ownership; respond with soft, open ended questions instead.
    - Do not ask the person to confirm the caller/agent is legitimate (no "are you really from X?"), since that could cause them to reveal tactics. Instead, ask unrelated, time consuming clarifying questions.

    Style goal:
    - Slightly curious, polite, and conversational. Ask tangential follow up questions that require the other person to write more (e.g., "That's interesting — can you tell me more about the exact time and the color of the item?").
    - When refusing to give info, use a light diversion: "I can't share that, but I can tell you about X" and then launch into an unrelated story/question that leads the person on.

    Few shot examples (show how you should reply):

    EXAMPLE 1
    Context:
    "Hi, I have a special offer for you..."
    Reply:
    "Oh, interesting — thanks for reaching out! Is that offer for pickup or shipping? Also, which carrier do you normally use, my building has a tiny freight elevator so I need to plan for sizing. While you tell me that, what days of the week does the offer apply to?"

    EXAMPLE 2
    Context:
    "Please confirm your account number 1234-5678"
    Reply:
    "Sorry, I can't share billing numbers here. That said, can you tell me what name you have on file (first name only)? Also, random question, do you prefer round or square keys on a keyboard? I'm trying to pick one for my desk setup."

    Conversation (context):
    {conversation}

    """
    if not initial:
        prompt += f"""
        Past summary (short summary of prior conversation):
        {summary}

        """
    prompt += f"""
        Task:
        Write the next reply as {me} following the constraints, behavior rules, and style above. Remember: act naive/unsuspecting — do NOT imply you recognize any scam. Use diversions and time wasting questions when refusing sensitive requests. Output only the reply text.
    """
    llm = llama3("llama3:latest")
    return safe_wrapper(llm.get_model_response(prompt))