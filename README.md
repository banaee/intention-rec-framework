# intention-rec-framework
Framework for intention recognition in human-robot collaboration



Follow these steps to set up your environment and run the application.

## 1. Create a Virtual Environment

First, navigate to your virtual environments directory and create a new virtual environment:

```bash
cd /path/to/your/my-venvs
python3 -m venv teamrob-sp4-basic-no-mesa
```

Replace `/path/to/your/my-venvs` with the actual path to your virtual environments directory.

## 2. Navigate to the Project Directory

Change to the directory where your project is located:

```bash
cd /path/to/your/project
```

Replace `/path/to/your/project` with the actual path to your project directory.

## 3. Activate the Virtual Environment

Activate the virtual environment with the following command:

```bash
source /path/to/your/my-venvs/teamrob-sp4-basic-no-mesa/bin/activate
```

Replace `/path/to/your/my-venvs` with the path to your virtual environments directory.

## 4. Install Required Packages

Install the necessary Python packages using `pip`:

```bash
pip install -r requirements.txt
```

Ensure that you have a `requirements.txt` file in your project directory listing all required dependencies.

## 5. Run the Application

Start the application with Solara by running:

```bash
solara run app.py
```

This command will launch your application using Solara.

## Notes

- Ensure that you have all necessary permissions to execute these commands.
- The paths in the commands should be adjusted to fit your local setup.

For any issues or additional setup details, please refer to the project's documentation or contact the project maintainers.
