# Setup (macOS)
Setup procedure I followed for installing manim here. In case I need to reinstall later...  

## Python + Manim
```bash
brew install pkg-config cairo        # system libs for manim
uv init --python 3.12
uv add manim                         # creates .venv
printf ".venv/\nmedia/\n__pycache__/\n.DS_Store\n" >> .gitignore
```

## LaTeX (TinyTeX, user-local)
```bash
curl -sL "https://yihui.org/tinytex/install-bin-unix.sh" | sh   # installs to ~/Library/TinyTeX
ls ~/Library/TinyTeX/bin/                                       # note arch folder, e.g. universal-darwin

# keep it out of /usr/local/bin; use PATH instead
sudo ~/Library/TinyTeX/bin/universal-darwin/tlmgr path remove
echo 'export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"' >> ~/.zshrc
exec zsh

tlmgr install standalone preview dvisvgm babel-english
```

## Verify
```bash
uv run manim checkhealth
```

## Uninstall TinyTeX
`rm -rf ~/Library/TinyTeX` and remove the PATH line from `~/.zshrc`.
