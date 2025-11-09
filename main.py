import argparse
from src import spam_back

parser = argparse.ArgumentParser(description="My Spam Back tool")

help_text = """
    Must input a phone number with country code or group chat ID.\n\n
    Phone number must in this form +18880001111.\n
    Make sure to include + symbol
"""

parser.add_argument(
    "--chat",        # command-line flag
    type=str,        # type of the argument
    help=help_text,  # TODO need to implement group chat ID
    required=True
)

args = parser.parse_args()

spam_back(args.chat)
