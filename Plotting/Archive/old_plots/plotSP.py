import matplotlib.pyplot as plt

def plot(fig, ax):
    # Initialize lists to store the coordinates
    x_coords = []
    y_coords = []
    z_coords = []

    # Read data from sp.csv
    with open("C:\\Users\\alasd\\Documents\\MPhys\\Plotting\\sp.csv", "r") as file:
        for line in file:
            values = line.strip().split(',')
            print(values)
            x_coords.append(float(values[0]))
            y_coords.append(float(values[1]))
            z_coords.append(float(values[2]))



    ax.scatter(x_coords, y_coords, z_coords, c='b', marker='o')

    # Add labels and title
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.set_zlabel("Z Coordinate")
    ax.set_title("3D Scatter Plot of Spacepoints")

    print(x_coords)


