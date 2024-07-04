import os
import time


def compress(data):
    """
    Compress time-series data with continuous constant values.
    :param data: A string containing the time-series data in (timestamp,value) format.
    :return: A compressed string representation of the data.
    """

    points = data.strip().split('\n')
    if not points:
        return ""

    compressed_data = []

    # Extract and parse the first data point
    previous_time, previous_value = points[0].split(',')
    previous_time = int(previous_time)
    previous_value = float(previous_value)

    # Append the first data point to the compressed data
    compressed_data.append(f"{previous_time},{previous_value}")

    current_interval = None
    count = 0

    # Iterate over the remaining data points
    for point in points[1:]:
        # Extract and parse the current data point
        current_time, current_value = point.split(',')
        current_time = int(current_time)
        current_value = float(current_value)

        # Check if current data point continues the previous segment
        if current_value == previous_value and current_time - previous_time == current_interval:
            # Update the previous time and increment the count
            previous_time = current_time
            count += 1
        else:
            if count > 0:
                # Append the last point of the previous segment
                compressed_data.append(f"{previous_time},{previous_value}")
            # Append the current data point and reset the interval
            compressed_data.append(f"{current_time},{current_value}")
            current_interval = current_time - previous_time
            count = 0
            previous_time = current_time
            previous_value = current_value

    # Append the last data point
    compressed_data.append(f"{previous_time},{previous_value}")

    return '\n'.join(compressed_data)


def decompress(data):
    """
    Decompress compressed time-series data with continuous constant values.
    :param data: A string containing the compressed time-series data in (timestamp,value) format.
    :return: A decompressed string representation of the data.
    """

    points = data.strip().split('\n')
    if len(points) <= 2:
        return data

    decompressed_data = []

    # Handle the first and second points
    front = points[0].split(',')
    curr = points[1].split(',')
    front_time, front_value = int(front[0]), float(front[1])
    curr_time, curr_value = int(curr[0]), float(curr[1])
    interval = curr_time - front_time

    decompressed_data.append(f"{front_time},{front_value}")
    decompressed_data.append(f"{curr_time},{curr_value}")

    # Handle the remaining points
    for i in range(1, len(points) - 1):
        front = points[i].split(',')
        curr = points[i + 1].split(',')

        front_time, front_value = int(front[0]), float(front[1])
        curr_time, curr_value = int(curr[0]), float(curr[1])

        # Check if values are the same and interval matches
        if front_value == curr_value and (curr_time - front_time) % interval == 0:
            pointer = front_time
            while pointer + interval <= curr_time:
                pointer += interval
                decompressed_data.append(f"{pointer},{front_value}")
        else:
            decompressed_data.append(f"{curr_time},{curr_value}")

        # Update interval
        interval = curr_time - front_time

    return '\n'.join(decompressed_data)




def validate_data(file_path):
    """
    Check if the data is in the format (timestamp,value) and verify if the timestamps are at consistent intervals.
    :param file_path: The path to the file to check.
    :return: True if data meets requirements, otherwise False.
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if len(lines) < 2:
                print("Not enough data lines, at least two lines are required.")
                return False

            previous_time = None
            interval = None

            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue

                tokens = line.split(',')
                if len(tokens) != 2:
                    print(f"Format error on line {i + 1}, should be timestamp,value")
                    return False

                try:
                    current_time = int(tokens[0])
                    value = float(tokens[1])
                except ValueError:
                    print(f"Format error on line {i + 1}, timestamp or value format error")
                    return False

                if previous_time is not None:
                    current_interval = current_time - previous_time
                    if interval is None:
                        interval = current_interval
                    elif current_interval != interval:
                        print(f"Inconsistent timestamp interval on line {i + 1}")
                        return False

                previous_time = current_time

            return True
    except Exception as e:
        print(f"Error checking the file: {e}")
        return False




def main(input_file_path, compressed_file_path, decompressed_file_path):
    """
    Main function to call the compression and decompression functions and output related statistics.
    :param input_file_path: Path to the input file to be compressed.
    :param compressed_file_path: Path to save the compressed data.
    :param decompressed_file_path: Path to save the decompressed data.
    """
    # Validate input file
    if not validate_data(input_file_path):
        print("Input data does not meet requirements. Operation terminated.")
        return

    # Read input data
    with open(input_file_path, 'r') as file:
        input_data = file.read()

    # Record the size of the original file
    input_file_size = os.path.getsize(input_file_path)

    # Compress data
    start_time = time.time()
    compressed_data = compress(input_data)
    compress_time = time.time() - start_time

    # Save compressed data
    with open(compressed_file_path, 'w') as file:
        file.write(compressed_data)

    # Record the size of the compressed file
    compressed_file_size = os.path.getsize(compressed_file_path)

    # Decompress data
    start_time = time.time()
    decompressed_data = decompress(compressed_data)
    decompress_time = time.time() - start_time

    # Save decompressed data
    with open(decompressed_file_path, 'w') as file:
        file.write(decompressed_data)

    # Record the size of the decompressed file
    decompressed_file_size = os.path.getsize(decompressed_file_path)

    # Calculate compression ratio
    compression_ratio = compressed_file_size / input_file_size if input_file_size > 0 else 0

    # Output statistics
    print(f"Original file size: {input_file_size} bytes")
    print(f"Compression time: {compress_time/1000:.6f} milliseconds")
    print(f"Compressed file size: {compressed_file_size} bytes")
    print(f"Decompression time: {decompress_time/1000:.6f} milliseconds")
    print(f"Decompressed file size: {decompressed_file_size} bytes")
    print(f"Compression ratio: {compression_ratio:.6f}")



# Example usage
if __name__ == "__main__":
    input_file = "data/input_data.txt"
    compressed_file = "data/compressed_data.txt"
    decompressed_file = "data/decompressed_data.txt"
    main(input_file, compressed_file, decompressed_file)
