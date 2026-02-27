import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--dir", required=True, type=str)
parser.add_argument("--output", required=False, type=str, default=None)

if __name__ == "__main__":
    args = parser.parse_args()

    # List all files in directory
    files = os.listdir(args.dir)

    # Remove extensions safely
    filenames_without_ext = []
    for f in files:
        # Skip directories
        full_path = os.path.join(args.dir, f)
        if os.path.isfile(full_path):
            name, _ = os.path.splitext(f)
            filenames_without_ext.append(name)

    if args.output is not None:
        # Save to output file
        with open(args.output, "w", encoding="utf-8") as out:
            for name in filenames_without_ext:
                out.write(name + "\n")

        print(f"Saved {len(filenames_without_ext)} filenames to {args.output}")