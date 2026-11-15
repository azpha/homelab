import sys
import os
import subprocess

# c08dc6b088e90512fb8a2dafe9f1ae5de3f486d1
# 894be8a440ba41aa228e53d7d523bcb1ae34da41

ignore_deploys_for = [ # don't auto-deploy these
  "tasks/infra/runner",
  "templates/runner",
  "roles/docker"
]

def git_diff():
  args = sys.argv
  res = subprocess.run(f"git diff --name-only {args[1]} {args[2]}", capture_output=True, shell=True, text=True)
  return [x for x in res.stdout.strip().split("\n") if "tasks/" in x or "roles/" in x or "templates/" in x]

def construct_command(tags):
  command = f"ANSIBLE_CONFIG=ansible.cfg ansible-playbook main.yml --tags={",".join(tags)} --vault-password-file ~/.vault_pass.txt"
  return command

def deploy(tags):
  print(f"[MAIN] Deploying...")
  command = construct_command(tags)
  res = subprocess.run(command, shell=True)
  return res.returncode == 0

def get_normalized_task_name(container):
  if "tasks/" in container:
    split_path = container.split("/")
    if len(split_path) > 2:
      task_name = split_path[2].split(".")[0]
    else:
      task_name = split_path[1].split(".")[0]
  elif "roles/" or "templates/" in container:
    task_name = container.split("/")[1]

  return task_name

def main():
  dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')

  print("Task environment variable: " + os.environ.get("TASK"))
  if os.environ.get("TASK"):
    diff = [os.environ.get("TASK")]
    deployable_containers = [os.environ.get("TASK")]
  else:
    diff = git_diff()
    deployable_containers = []

  if not os.environ.get("TASK"):
    for file in diff:
      if os.path.exists(os.path.join(dir_path, file)):
        deployable_containers.append(file)

  print(f"[MAIN] Deployable: {len(deployable_containers)}")

  if len(deployable_containers) > 0:
    to_deploy = []
    if not os.environ.get("TASK"):
      for container in deployable_containers:
        task_name = get_normalized_task_name(container)
        if task_name:
          to_deploy.append(task_name + "_deploy")
    else:
      to_deploy.append(os.environ.get("TASK"))
      
    if len(to_deploy) > 0:
      result = deploy(to_deploy)
      print("deploy result: ", result)
      
if __name__ == "__main__":
  main()