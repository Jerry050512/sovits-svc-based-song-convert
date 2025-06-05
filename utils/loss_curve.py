import re
import matplotlib.pyplot as plt
import numpy as np

def plot_loss_curve(log_file_path="train.log"):
    """
    Parses a log file, extracts loss values and reference loss,
    and plots them as loss curves.

    Args:
        log_file_path (str): The path to the train.log file.
    """
    losses = []
    reference_losses = [] # New list for reference loss
    steps = []
    
    # Updated regular expression to match the loss line and capture
    # the losses array, step, and reference_loss.
    # It looks for "Losses: [...]", "step: X", and "reference_loss: Y".
    loss_pattern = re.compile(r"Losses: \[(.*?)\], step: (\d+), lr: [\d\.e-]+, reference_loss: ([\d\.]+)")

    print(f"Attempting to read log file: {log_file_path}")

    try:
        with open(log_file_path, 'r') as f:
            for line in f:
                match = loss_pattern.search(line)
                if match:
                    # Extract the string representation of the losses list
                    losses_str = match.group(1)
                    # Extract the step number
                    step = int(match.group(2))
                    # Extract the reference loss
                    ref_loss = float(match.group(3))
                    
                    try:
                        # Convert the comma-separated string of numbers into a list of floats
                        current_losses = [float(x.strip()) for x in losses_str.split(',')]
                        
                        if current_losses:
                            losses.append(current_losses[0]) # Still taking the first loss value
                            steps.append(step)
                            reference_losses.append(ref_loss) # Add reference loss to its list
                        
                    except ValueError as ve:
                        print(f"Warning: Could not parse losses or reference_loss from line: {line.strip()} - {ve}")
                    except IndexError:
                        print(f"Warning: No loss values found in the list on line: {line.strip()}")

        if not losses:
            print("No loss data found in the log file matching the pattern.")
            print("Please ensure the log file contains lines like:")
            print("2025-06-05 09:15:40,622 44k INFO    Losses: [value1, value2, ...], step: XXX, lr: Y.Ye-Z, reference_loss: RRR")
            return

        # Plotting the loss curves
        plt.figure(figsize=(12, 6))
        plt.plot(steps, losses, marker='o', linestyle='-', color='skyblue', markersize=4, label='First Loss Value')
        plt.plot(steps, reference_losses, marker='x', linestyle='--', color='salmon', markersize=4, label='Reference Loss') # Plot reference loss
        
        # Add labels and title
        plt.title('Training Loss and Reference Loss Over Steps', fontsize=16)
        plt.xlabel('Training Step', fontsize=12)
        plt.ylabel('Loss Value', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend() # Show legend for both lines
        
        # Improve layout and save/show plot
        plt.tight_layout()
        plt.show()
        print(f"Successfully plotted {len(losses)} loss points.")

    except FileNotFoundError:
        print(f"Error: The file '{log_file_path}' was not found.")
        print("Please make sure the log file is in the same directory as the script, or provide its full path.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    plot_loss_curve("so-vits-svc/logs/44k/train.log")
