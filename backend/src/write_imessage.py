import subprocess

def send_imessage(recipient, message, group : bool = False): # TODO add a spec
    # TODO Write a check if this message exist in imessage or not
    if (not group and recipient[0] == 'c') or (group and recipient != 'c'):
        raise ValueError("chat id and group variable parameter does not match")
    target = 'iMessage;'
    if group:
        target += '+;'
    else:
        target += '-;'
    target += recipient
    applescript_command = f"""
    on run {{targetBuddyPhone, targetMessage}}
        tell application "Messages"
            set targetChat to chat id targetBuddyPhone
            send targetMessage to targetChat
        end tell
    end run
    """
    try:
        subprocess.run(["osascript", "-e", applescript_command, target, message], check=True)
        print(f"Message sent to {recipient} successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error sending message: {e}")
        print(f"AppleScript error output: {e.stderr}")
