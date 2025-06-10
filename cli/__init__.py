import typer

app = typer.Typer(help="SquirrelFocus command line interface")


@app.command()
def hello(name: str = "world"):
    """Say hello to NAME."""
    typer.echo(f"Hello {name}!")


if __name__ == "__main__":
    app()
