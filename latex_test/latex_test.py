import matplotlib.pyplot as plt

def latex_to_png(latex_string, output_path="output.png", dpi=300):
    """
    Convert LaTeX string to PNG.

    Args:
        latex_string (str): The LaTeX code as a string (e.g., r"$E = mc^2$").
        output_path (str): Filepath to save the PNG.
        dpi (int): Dots per inch for the output image.
    """
    # Create a figure for rendering
    plt.figure(figsize=(2, 2), dpi=dpi)
    plt.text(0.5, 0.5, latex_string, fontsize=20, ha='center', va='center', usetex=True)
    plt.axis('off')  # Remove axes

    # Save as PNG
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight', pad_inches=0)
    plt.close()
    print(f"Saved LaTeX to {output_path}")

# Example usage
latex_code = r"$X_{k} = \displaystyle\sum_{n=0}^{N-1}x_{n}\cdot e^{-\frac{i2\pi}{N}kn}$"
latex_to_png(latex_code, "equation.png")
