import pandas as pd

# Change path to your dataset folder
logon = pd.read_csv("data/logon.csv")
file = pd.read_csv("data/file.csv")
email = pd.read_csv("data/email.csv")
device = pd.read_csv("data/device.csv")
users = pd.read_csv("data/users.csv")

print("Logon Data:")
print(logon.head())
print("\nColumns:", logon.columns)

print("\nFile Data:")
print(file.head())
print("\nColumns:", file.columns)

print("\nEmail Data:")
print(email.head())
print("\nColumns:", email.columns)

print("\nDevice Data:")
print(device.head())
print("\nColumns:", device.columns)

print("\nUsers Data:")
print(users.head())
print("\nColumns:", users.columns)
