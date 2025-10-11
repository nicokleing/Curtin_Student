"""Runs the AdventureWorld simulation from the CLI."""

from adventure.interface.cli import CLIManager
from adventure.config.loader import ConfigLoader
from adventure.core.engine import SimulationEngine


def main():
    # Handle command-line arguments
    cli = CLIManager()
    args = cli.parse_arguments()

    config_loader = ConfigLoader()
    config = config_loader.load_from_args(args, cli)
    engine = SimulationEngine(config)
    engine.run(interactive=config.interactive)


if __name__ == "__main__":
    main()
