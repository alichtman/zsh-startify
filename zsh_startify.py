#!/usr/bin/env python3
# zsh-startify <https://github.com/alichtman/zsh-startify>

# Standard Library Imports
from os import system, getenv
from time import sleep

# 3rd Party Library Imports
import libtmux
from halo import Halo
from pyfiglet import Figlet
from colorama import Fore, Style
from PyInquirer import prompt, style_from_dict, Token, \
                        Validator, ValidationError


############
# Prettify #
############

def print_blue(text):
    print(Fore.BLUE + Style.BRIGHT + text + Style.RESET_ALL)


def print_red(text):
    print(Fore.RED + Style.BRIGHT + text + Style.RESET_ALL)


def print_yellow(text):
    print(Fore.YELLOW + Style.BRIGHT + text + Style.RESET_ALL)


def print_green(text):
    print(Fore.GREEN + Style.BRIGHT + text + Style.RESET_ALL)


def splash():
    """Print splash screen text. Uses env vars for font and header if they
    exist."""
    # TODO: Add pretty colors. lolcat?
    font = getenv("ZSH_STARTIFY_HEADER_FONT", "univers")
    text = getenv("ZSH_STARTIFY_HEADER_TEXT", "zsh")
    fig = Figlet(font=font)
    formatted = "\t" + fig.renderText(text).replace("\n", "\n\t")
    print_green(formatted)


def sleep_with_spinner(secs):
    """Sleep with a nice spinner and then print a success messsage."""
    spinner = Halo(text='Loading', spinner='dots')
    spinner.start()
    sleep(secs)
    spinner.succeed("Success.")


########
# tmux #
########

def get_tmux_session_names(server) -> list:
    """Returns all current tmux session names"""
    return [session.name for session in server.list_sessions()]


def get_tmux_session(server, name) -> libtmux.Session:
    """Looks up a tmux session by name and returns it if it exists. Returns
    None if the session doesn't exist.
    """
    session = server.find_where({"session_name": name})
    if session is None:
        raise ValueError(f"Error: No session of name \'{name}\' exists.")
    return session


def attach_to_session(server, name):
    session = get_tmux_session(server, name)
    session.attach_session()


def create_new_named_session(server, name):
    session = server.new_session(name)
    session.attach_session()


def get_tmux_server() -> libtmux.Server:
    """
    Returns tmux server if it's running, and starts one if it's not.
    """
    server = libtmux.Server()
    try:
        server.list_sessions()
    except libtmux.exc.LibTmuxException:
        print_blue("Starting tmux server...")
        # Apparently, there is no way to start a server without any sessions
        # (https://github.com/tmux/tmux/issues/182). So, we're going to spawn a
        # new server, create a dummy session and then kill it later. I'm sorry.
        hack_session = "zsh-startify-tmux-server-hack"
        start_server_hack = f"tmux has-session -t {hack_session} || \
                              tmux new-session -d -s {hack_session}"
        system(start_server_hack)
        # Sleep to give tmux some time to restore sessions if tmux-resurrect or
        # tmux-continuum is used
        # TODO: Make this sleep value configurable in .zshrc
        sleep_with_spinner(5)
        server = libtmux.Server()
        # Kill the hacky tmux session we just started.
        get_tmux_session(server, hack_session).kill_session()

    return server


#############
# Prompting #
#############

# These get prepended to the actions in the list for selection.
MARK = {
    "tmux-session": "    ",
    "non-tmux-session": "- ",
}

ACTIONS = {
    "zsh": "Launch zsh",
    "new-tmux-session": "Create new tmux session",
    "attach-tmux-session": "Attach to existing tmux session",
}

# TODO: Finalize default colors
# TODO: Make colors configurable. Maybe add color themes?
SELECTOR_STYLE = style_from_dict({
        Token.QuestionMARK: '#dcbf85 bold',
        Token.Question: '#1776A5 bold',
        Token.Instruction: '#1776A5 bold',
        Token.Pointer: '#FF9D00 bold',
        Token.Selected: '#cc5454',
        Token.Answer: '#f44336 bold',
})


def prompt_for_action(tmux_sessions) -> str:
    """
    Show a prompt with all available tmux sessions, letting the user choose a
    session to attach to, the option to create a new session, or create a
    non-tmux-session session.
    """
    launch_zsh = MARK["non-tmux-session"] + ACTIONS["zsh"]
    choices = [
        launch_zsh,
        MARK["non-tmux-session"] + ACTIONS["new-tmux-session"],
        {
            'name': ACTIONS["attach-tmux-session"],
            'disabled': 'Select from below'
        }
    ]

    choices += [MARK["tmux-session"] + session for session in tmux_sessions]

    questions = [
        {
            'type': 'list',
            'name': 'action',
            'message': 'What do you want to do?',
            'choices': choices
        },
    ]

    try:
        answers = prompt(questions, style=SELECTOR_STYLE)
    # Handle CTRL+D
    except EOFError:
        return launch_zsh

    if answers == {}:
        return launch_zsh
    else:
        return answers["action"]


class TmuxSessionValidator(Validator):
    """
    Tmux sesion names must not contain periods and must not be the empty
    string.
    """
    def validate(self, document):
        name = document.text
        if len(name) == 0:
            raise ValidationError(
                message="tmux session name must not be an empty string",
                cursor_position=0)
        elif "." in name:
            raise ValidationError(
                message="tmux session names may not contain '.'",
                cursor_position=len(name))  # Move cursor to end


def prompt_for_session_name() -> str:
    questions = [
        {
            'type': 'input',
            'name': 'session_name',
            'message': 'Enter a session name',
            'default': "",
            'validate': TmuxSessionValidator
        },
    ]

    answers = prompt(questions, style=SELECTOR_STYLE)
    return answers["session_name"]


##################
# And here we go #
##################

def action_handler(server, action):
    # Attach to session
    if action.startswith(MARK["tmux-session"]):
        attach_to_session(server, action.strip())
    # Create new session
    elif ACTIONS["new-tmux-session"] in action:
        session_name = prompt_for_session_name()
        create_new_named_session(server, session_name)
    # Launch zsh
    else:
        return


def main():
    splash()
    server = get_tmux_server()
    tmux_sessions = get_tmux_session_names(server)
    action = prompt_for_action(tmux_sessions)
    action_handler(server, action)


if __name__ == "__main__":
    main()
