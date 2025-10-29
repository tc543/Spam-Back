import subprocess

def send_imessage(recipient, message): # TODO add a spec
    # TODO Write a check if this message exist in imessage or not
    # chat_identifiers = set(extract_chats())
    applescript_command = f"""
    osascript -e '
    on run {{targetBuddyPhone, targetMessage}}
        tell application "Messages"
            set targetService to 1st service whose service type = iMessage
            set targetBuddy to buddy targetBuddyPhone of targetService
            send targetMessage to targetBuddy
        end tell
    end run
    ' {recipient} "{message}"
    """
    try:
        subprocess.run(applescript_command, shell=True, check=True)
        print(f"Message sent to {recipient} successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error sending message: {e}")
        print(f"AppleScript error output: {e.stderr}")
