from datetime import datetime

def check_chronological_order(filename):
    with open(filename, "r") as file:
        lines = file.readlines()

    previous_start_time = None
    chronology_broken = False

    for line_number, line_content in enumerate(lines, start=1):
        line_content = line_content.strip()
        if not line_content:
            continue

        fields = line_content.split(", ")
        if len(fields) < 4:
            continue

        try:
            current_start_time = datetime.fromisoformat(fields[3])
        except ValueError:
            continue

        if previous_start_time and current_start_time < previous_start_time:
            print(f"{filename}: Нарушен порядок на строке {line_number}: {current_start_time} < {previous_start_time}")
            chronology_broken = True

        previous_start_time = current_start_time

    if not chronology_broken:
        print(f"{filename}: хронология не нарушена.")

def check_multiple_files(start_counter=1, end_counter=5):
    for file_counter in range(start_counter, end_counter + 1):
        filename = f"CDR{file_counter}.csv"
        try:
            check_chronological_order(filename)
        except FileNotFoundError:
            print(f"{filename}: файл не найден.")

check_multiple_files(1, 20)
