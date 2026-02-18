# Bliss

A simple app that shows **100 top song recommendations** (title, artist, year). 

## Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://127.0.0.1:8000

# FastAPI Deployment to Azure App Service (Linux)

## Overview

This project is a FastAPI application deployed to Azure App Service (Linux) using an Azure DevOps pipeline.

The application runs in production using Gunicorn with Uvicorn workers:

gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT


---

## Issues Faced During Deployment

### 1. Archive Error: `zip error: Nothing to do!`

**Problem**

Pipeline failed with:

zip error: Nothing to do!


**Cause**

The archive task was pointing to the wrong directory.

Azure agent uses different folders:

- `/s` → Source directory (`$(System.DefaultWorkingDirectory)`)
- `/a` → Artifact staging directory (`$(Build.ArtifactStagingDirectory)`)

Files were copied to `/a/app`, but the archive step was trying to zip `/s/app`.

**Fix**

Updated the archive step to:

rootFolderOrFile: '$(Build.ArtifactStagingDirectory)/app'


---

### 2. Unnecessary Files Included in Deployment

**Problem**

The ZIP package included unwanted files such as:

- `.git/`
- `__pycache__/`
- `azure-pipelines.yml`

**Fix**

Used `CopyFiles@2` to stage only required files:

- `main.py`
- `requirements.txt`

Then archived only that clean staging folder.

---

### 3. Runtime Error: `ModuleNotFoundError: No module named 'uvicorn'`

**Problem**

After deployment, the application crashed with:

ModuleNotFoundError: No module named 'uvicorn'

Even though `uvicorn` was present in `requirements.txt`.

**Root Cause**

Azure App Service did not run the build process.

Logs showed:

Could not find virtual environment directory  
Could not find package directory  

This meant:
- No virtual environment was created
- `pip install -r requirements.txt` was not executed
- Dependencies were not installed

Additionally, the runtime stack was set to:

PYTHON|3.13

Python 3.13 support was not fully stable in Azure App Service at the time of deployment.

**Fix**

Changed the runtime stack to:

PYTHON|3.11

After switching to Python 3.11:
- Oryx build executed properly
- Virtual environment was created
- Dependencies were installed
- Application started successfully

---

## Final Working Configuration

### requirements.txt

fastapi>=0.115.0  
uvicorn[standard]  
gunicorn  
httpx>=0.27.0  


---

### AzureWebApp Pipeline Task

- task: AzureWebApp@1
  inputs:
    azureSubscription: 'azsvc'
    appType: 'webAppLinux'
    appName: 'musicappindia'
    package: '$(Build.ArtifactStagingDirectory)/app.zip'
    runtimeStack: 'PYTHON|3.11'
    startUpCommand: 'gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT'


---

## Lessons Learned

- Azure pipeline agent uses different directories for source and artifacts
- ZIP deployment does not guarantee dependency installation
- If build is not triggered, dependencies will not be installed
- Bleeding-edge Python versions may not be fully supported in managed cloud environments
- Stable runtime versions are safer for production deployments


---

## Adding Screenshots to README

### Step 1: Create a folder in your repository

Example:

docs/images/


### Step 2: Add screenshot files

Example:

docs/images/pipeline-error.png  
docs/images/success-deploy.png  


### Step 3: Reference images in README

Standard Markdown:

![Pipeline Error](docs/images/pipeline-error.png)

With custom width (GitHub supports HTML):

<img src="docs/images/pipeline-error.png" width="700">


---

## Conclusion

The deployment issues were primarily caused by:

- Incorrect directory usage in the pipeline
- Packaging unnecessary files
- Using an unstable runtime version (Python 3.13)

Switching to a stable runtime (Python 3.11) and correcting the pipeline configuration resolved the issues completely.
