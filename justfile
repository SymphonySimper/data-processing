set quiet

init:
    uv sync

[default]
run:
    uv run src/main.py

clean:
    git reset --hard origin/main
    git clean -fdX ./input
    git clean -fdX ./output
