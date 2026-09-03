from pathlib import Path

from app.core.race_control import RaceControl


PROJECT_ROOT = Path(__file__).resolve().parent


def main():

    print()
    print("=" * 70)
    print("       BANKAI RACE CONTROL")
    print("       Agentic Local AI Coding Command Center")
    print("=" * 70)
    print()

    controller = RaceControl(
        PROJECT_ROOT
    )

    while True:

        try:

            command = input("BANKAI > ").strip()

            if not command:
                continue

            if command.lower() in {
                "exit",
                "quit",
                "shutdown"
            }:

                print("BANKAI RACE CONTROL OFFLINE.")
                break

            if command.lower() == "inspect project":

                files = controller.agent.inspect()

                print()
                print(f"Files detected: {len(files)}")

                for file in files[:30]:
                    print("  ", file)

                if len(files) > 30:
                    print(
                        f"  ... {len(files) - 30} more"
                    )

                print()

                continue

            mission = controller.dispatch(
                command
            )

            print()
            print("MISSION CREATED")
            print("-" * 70)
            print(
                f"ID       : {mission['mission_id']}"
            )
            print(
                f"OBJECTIVE: {mission['objective']}"
            )
            print(
                f"PHASE    : {mission['phase']}"
            )
            print()

        except KeyboardInterrupt:

            print()
            print("BANKAI RACE CONTROL INTERRUPTED.")
            break

        except Exception as exc:

            print(
                f"BANKAI ERROR: {exc}"
            )


if __name__ == "__main__":
    main()
