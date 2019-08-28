# zsh-startify

**TODO: Insert demo.**

This is a start screen for zsh. After starting a terminal session, it will load `tmux` and show you sessions you can attach to. It will also give you the option to create a new named sesion, as well as launch a regular `zsh` session.

## Configuration

This tool comes with sensible defaults. No configuration is necessary, however, the following settings may be changed in your `~/.zshrc` file:

- **ZSH_STARTIFY_HEADER_FONT**
	+ This is the Figlet font that the header text will be printed in.
	+ Default: `univers`. Accepts any [Figlet font](http://www.figlet.org/examples.html).
- **ZSH_STARTIFY_HEADER_TEXT**
	+ This string will be printed as the header.
	+ Default: `zsh`. Accepts any string.

A simple example of this is:

```bash
export ZSH_STARTIFY_HEADER_TEXT="custom-header"
export ZSH_STARTIFY_HEADER_FONT="slant"
```

## Inspiration

I've used [vim-startify](https://github.com/mhinz/vim-startify) pretty much every day for the past year. I figured it was time for `zsh` and `tmux` to have a similar tool.
