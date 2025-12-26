import argparse
from src import spam_back

parser = argparse.ArgumentParser(description="My Spam Back tool")

help_chat = """
    Must input a phone number with country code or group chat ID.\n\n
    Phone number must in this form +12223334444.\n
    Make sure to include + symbol
"""

help_spammer = """
    Must input 1 for spammer and 0 for not a spammer
    Any other input would be invalid
"""

parser.add_argument(
    "--chat",        # command-line flag
    type=str,        # type of the argument
    help=help_chat,  # TODO need to implement group chat ID
    required=True
)

parser.add_argument(
    "--is_spam",
    type=int,
    help=help_spammer,
    required=True
)

args = parser.parse_args()

if args.is_spam not in [0, 1]:
    raise ValueError("is_spam must be either 0 or 1")

spam_back(args.chat, args.is_spam)
