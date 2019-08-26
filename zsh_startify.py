import libtmux
from pyfiglet import Figlet
#  from colorama import Fore, Style
from PyInquirer import prompt, style_from_dict, Token


############
# Prettify #
############

def splash(text, font):
    """Print splash screen text."""
    # TODO: Add splash screen config option in .zshrc
    # TODO: Add pretty colors
    fig = Figlet(font=font)
    text = fig.renderText(text)
    print(text.replace("\n", "\n\t"))


########
# tmux #
########

def get_tmux_session_names(server) -> list:
    return [session.name for session in server.list_sessions()]


def attach_to_session(server, name):
    session = server.find_where({"session_name": name})
    session.attach_session()


#############
# Prompting #
#############

prepend = {
    "tmux-session": "    ",
    "non-tmux-session": "- ",
}

actions = {
    "zsh": "Launch zsh",
    "new-tmux-session": "Create new tmux session",
    "attach-tmux-session": "Attach to existing tmux session",
}


def prompt_for_action(tmux_sessions) -> str:
    """
    Show a prompt with all available tmux sessions, letting the user choose a
    session to attach to, the option to create a new session, or create a
    non-tmux-session session.
    """
    choices = [
        prepend["non-tmux-session"] + actions["zsh"],
        prepend["non-tmux-session"] + actions["new-tmux-session"],
        {
             'name': actions["attach-tmux-session"],
             'disabled': 'Select from below'
        }
    ]

    choices += [prepend["tmux-session"] + session for session in tmux_sessions]

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
    answers = prompt(questions, style=style_from_dict({
        Token.QuestionMark: '#dcbf85 bold',
        Token.Question: '#1776A5 bold',
        Token.Instruction: '#1776A5 bold',
        Token.Pointer: '#FF9D00 bold',
        Token.Selected: '#cc5454',
        Token.Answer: '#f44336 bold',
    }))

    print(answers["action"])
    return answers["action"]


##################
# And here we go #
##################

def action_handler(server, action):
    # Attach to session
    if action.startswith(prepend["tmux-session"]):
        attach_to_session(server, action.strip())
    # TODO: Create new session
    elif action == actions["new-tmux-session"]:
        # TODO: Prompt for name of new session
        # TODO: create_new_session()
        pass
    # Launch zsh
    else:
        return


def main():
    splash("zsh", "univers")
    # TODO: What happens if no server is running?
    server = libtmux.Server()
    tmux_sessions = get_tmux_session_names(server)
    print("TMUX Sessions:", tmux_sessions)
    action = prompt_for_action(tmux_sessions)
    action_handler(server, action)


if __name__ == "__main__":
    main()
