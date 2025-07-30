import re
import subprocess

# Define scripts and their descriptions
scripts = [
    {
        "name": "Substrate Polish",
        "version": "1.0.0",
        "description": "Substrate Polish, it polishes your model and centers it to (0,0)",
        "features": ["aaaaaa", "bbbbbb", "cccccc"],
        "program": "/home/doc/substrate_polish.py",
        "args": ["model path", "model name"],      
    },
    {
        "name": "Substrate CTE (with IPD)",
        "version": "1.0.0",
        "description": "Substrate CTE (with IPD)",
        "features": ["aaaaaa", "bbbbbb", "cccccc"],
        "program": "/home/doc/meshmodel2_ipd.py",
        "args": ["model path", "model name"],      
    },
    {
        "name": "WMCM",
        "version": "1.0.0",
        "description": "WMCM",
        "features": ["aaaaaa", "bbbbbb", "cccccc"],
        "program": "/home/doc/meshmodel2_ipd.py",
        "args": ["model path", "model name"],      
    },
]

# Display menu
print("Available Toolkit Service")
for index, info in enumerate(scripts):
    print(f"{index+1}. \033[92m{info['name']}\033[0m")
print('others, Add * in front of index to show details of corresponding service')
print('others, Type "EXIT" to exit')

# User interaction loop
choice = None
while True:
    user_input = input("\033[93mEnter the number of the program to run: \033[0m").strip()
    
    if user_input.lower() == "exit":
        print("\033[31mExiting program.\033[0m")
        exit()

    match = re.fullmatch(r"\*?(\d+)", user_input)
    if not match:
        print("\033[31mExiting program, Invalid input format.\033[0m")
        #continue
        exit()

    if_description = user_input.startswith("*")
    choice = int(match.group(1))

    if not (1 <= choice <= len(scripts)):
        print("\033[31mExiting program, Choice out of range.\033[0m")
        #continue
        exit()

    info = scripts[choice - 1]

    if if_description:
        print(f"  [Name]: {info['name']}")
        print(f"  [Version]: {info['version']}")
        print(f"  [Description]: {info["description"]}")
        print(f"  [Features]:")
        for f in info["features"]:
            print(f"    * {f}")
        continue
    else:
        break  # valid choice without *

# Ask for arguments
args = []
for arg_name in info["args"]:
    arg = input(f"\033[94m  Input {arg_name}: \033[0m").strip()
    args.append(arg)

# Run the script with arguments
print(f"\nRunning: python3 {info['program']} {' '.join(args)}\n")
subprocess.run(["python3", info["program"]] + args)
