import csv
from pathlib import Path


BATCH_SIZE = 100


def load_requests(input_path):
    with input_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return reader.fieldnames, list(reader)


def save_batch(rows, fieldnames, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def split_requests(input_path, output_dir, batch_size=BATCH_SIZE):
    fieldnames, requests = load_requests(input_path)
    batch_paths = []

    for start in range(0, len(requests), batch_size):
        batch_number = len(batch_paths) + 1
        batch_rows = requests[start : start + batch_size]
        batch_path = output_dir / f"batch{batch_number:03d}.csv"
        save_batch(batch_rows, fieldnames, batch_path)
        batch_paths.append(batch_path)

    return batch_paths


def main():
    project_root = Path(__file__).resolve().parent.parent
    input_path = project_root / "data" / "manus_requests" / "manus_request_from_ebay.csv"
    output_dir = project_root / "data" / "manus_requests"

    batch_paths = split_requests(input_path, output_dir)

    print(f"Manus依頼CSVを{len(batch_paths)}個のバッチに分割しました。")
    for batch_path in batch_paths:
        print(batch_path)


if __name__ == "__main__":
    main()
