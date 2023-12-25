import re
import matplotlib.pyplot as plt

def plot_benchmark_results(results):
    workers = [result['Number of Workers'] for result in results]
    total_times = [result['Time taken for tests'] for result in results]

    plt.plot(workers, total_times, marker='o')
    plt.title('Number of Workers vs Total Time\nRequests: 1000, Concurrency: 5, Worker Sleep Time: 0.1s')
    plt.xlabel('Number of Workers')
    plt.ylabel('Total Time (seconds)')

    # Set y-axis limits to include 0
    plt.ylim(0, max(total_times) + 20)

    plt.grid(True)
    plt.show()

def parse_document(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Define the regular expressions to extract relevant information
    pattern_workers = re.compile(r'Number of Workers:\s*(\d+)')
    pattern_time = re.compile(r'Time taken for tests:\s*([\d.]+)\s*seconds')

    # Extract data from the document using regular expressions
    matches_workers = pattern_workers.findall(content)
    matches_time = pattern_time.findall(content)

    # Print the matches for debugging
    print(matches_workers, matches_time)

    # Create a list of dictionaries containing the extracted information
    results = [{'Number of Workers': int(w), 'Time taken for tests': float(t)} for w, t in zip(matches_workers, matches_time)]

    return results

if __name__ == "__main__":
    # Replace 'your_document.txt' with the path to your actual document
    document_path = 'visualisation/results.txt'
    
    # Parse the document to get benchmark results
    benchmark_results = parse_document(document_path)

    # Plot the benchmark results
    plot_benchmark_results(benchmark_results)
