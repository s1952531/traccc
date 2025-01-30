import matplotlib.pyplot as plt

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

# Create a 3D scatter plot
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

ax.scatter(x_coords, y_coords, z_coords, c='b', marker='o')

# Add labels and title
ax.set_xlabel("X Coordinate")
ax.set_ylabel("Y Coordinate")
ax.set_zlabel("Z Coordinate")
ax.set_title("3D Scatter Plot of Spacepoints")

print(x_coords)

# Show plot
plt.show()
