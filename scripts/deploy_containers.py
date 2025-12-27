import sys
import os
import subprocess

def git_diff():
  args = sys.argv
  res = subprocess.run(f"git diff --name-only {args[1]} {args[2]}", capture_output=True, shell=True, text=True)
  return [x for x in res.stdout.strip().split("\n") if "tasks/" in x or "roles/" in x]

def construct_command(tag = None, host = None):
  command = f"ANSIBLE_CONFIG=ansible.cfg /usr/bin/ansible-playbook main.yml --vault-password-file ~/.vault_pass.txt"

  if host:
    command += f" -l {host}"
  if tag:
    command += f" --tags {tag}_deploy"

  return command

def deploy(tag = None, host = None):
  command = construct_command(tag, host)
  
  if tag:
    print(f"[MAIN] Deploying {tag}...")
  else:
    print(f"[MAIN] Deploying host {host}...")
  res = subprocess.run(command, shell=True)

  return res.returncode == 0

def main():
  dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')
  diff = git_diff()

  # containers that need special treatment
  removed_containers = []
  vpn_containers = [
    "tasks/qbittorrent.yml",
    "tasks/jackett.yml"
  ]
  managed_roles = [
    "roles/fivem",
    "roles/gitea-runner",
    "roles/traefik"
  ]

  # special actions
  if "tasks/gluetun.yml" in diff:
    print("[MAIN] Detected Gluetun in diff, recreating dependent containers..")
    for container in vpn_containers:
      if container not in diff:
        diff.append(container)

  # clean up the diff
  new_diff = []
  for file in diff:
    task_name = f"{file.split("/")[0]}/{file.split("/")[1]}"

    # i'm not proud of this either
    if not os.path.exists(os.path.join(dir_path, file)):
      if "roles" in file and not os.path.exists(os.path.join(dir_path, task_name)) and task_name in managed_roles:
        print(f"[MAIN] '{task_name}' role removed, marking for cleanup..")
        removed_containers.append(task_name)
      elif "tasks" in task_name:
        print(f"[MAIN] '{task_name}' non-existent, marking for cleanup..")
        removed_containers.append(task_name) 
    elif "roles" in file:      
      if task_name in managed_roles:
        if task_name not in new_diff:
          new_diff.append(task_name)
    elif "tasks" in file:
      new_diff.append(file.split(".")[0])
    else:
      new_diff.append(file)

  deployed = []
  failed = []

  for task in new_diff:
    deployment = deploy(tag=task.split("/")[1])

    if not deployment:
      failed.append(task)
    else:
      deployed.append(task)

  for task in removed_containers:
    print(f"[MAIN] Attempting to remove containers related to '{task}'...")
    if len(task.split("/")) > 1:
      task_name = task.split("/")[1].split(".")[0]
    else:
      task_name = task
 
    containers = subprocess.Popen(f'docker ps --filter "name={task_name}" -q', shell=True, stdout=subprocess.PIPE)
    for line in containers.stdout:
      print(f"[MAIN] Found Docker container {line} related to {task_name}, removing..")
      subprocess.run(f"/usr/bin/docker container stop {line}", shell=True)
      subprocess.run(f"/usr/bin/docker container rm {line}", shell=True)
      subprocess.run("/usr/bin/docker image prune -f", shell=True)
      subprocess.run("/usr/bin/docker container prune -f", shell=True)

  if len(failed) <= 0 and len(deployed) > 0:
    print("\n---------------------")
    print(" Deployment succeeded!")
    print(f" All tasks: {", ".join(deployed)}")
    print("---------------------\n")
    sys.exit(0)
  elif len(failed) > 0:
    print("\n---------------------")
    print(" Deployment failed!")
    print(f" Failed tasks: {", ".join(failed)}")
    print(f" All tasks: {", ".join(deployed)}")
    print("---------------------\n")
    sys.exit(1)
  elif len(deployed) <= 0:
    print("[MAIN] Successfully executed, no tasks required execution")
    sys.exit(0)

if __name__ == "__main__":
  main()