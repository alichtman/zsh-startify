import libtmux
from pyfiglet import Figlet
from colorama import Fore, Style
from PyInquirer import prompt, style_from_dict, Token, \
                        Validator, ValidationError


############
# Prettify #
############

def print_green(text):
    print(Fore.GREEN + text + Style.RESET_ALL)


def splash(text, font):
    """Print splash screen text."""
    # TODO: Add splash screen config option in .zshrc
    # TODO: Add pretty colors
    fig = Figlet(font=font)
    text = fig.renderText(text)
    print_green(text.replace("\n", "\n\t"))


########
# tmux #
########

def get_tmux_session_names(server) -> list:
    return [session.name for session in server.list_sessions()]


def attach_to_session(server, name):
    session = server.find_where({"session_name": name})
    session.attach_session()


def create_new_named_session(server, name):
    session = server.new_session(name)
    session.attach_session()


#############
# Prompting #
#############

MARK = {
    "tmux-session": "    ",
    "non-tmux-session": "- ",
}

ACTIONS = {
    "zsh": "Launch zsh",
    "new-tmux-session": "Create new tmux session",
    "attach-tmux-session": "Attach to existing tmux session",
}

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
    choices = [
        MARK["non-tmux-session"] + ACTIONS["zsh"],
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

    # TODO: Finalize default colors
    # TODO: Make colors configurable. Maybe add color themes?
    answers = prompt(questions, style=SELECTOR_STYLE)

    print(answers["action"])
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
    print("ACTION:", action)
    if action.startswith(MARK["tmux-session"]):
        attach_to_session(server, action.strip())
    # Create new session
    elif ACTIONS["new-tmux-session"] in action:
        session_name = prompt_for_session_name()
        print("Session name:", session_name)
        create_new_named_session(server, session_name)
    # Launch zsh
    else:
        return


def main():
    splash("zsh", "univers")
    # TODO: What happens if no server is running?
    server = libtmux.Server()
    tmux_sessions = get_tmux_session_names(server)
    #  print("TMUX Sessions:", tmux_sessions)
    action = prompt_for_action(tmux_sessions)
    action_handler(server, action)


if __name__ == "__main__":
    main()
