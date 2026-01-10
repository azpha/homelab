import sys
import os
import subprocess

def git_diff():
  args = sys.argv
  res = subprocess.run(f"git diff --name-only {args[1]} {args[2]}", capture_output=True, shell=True, text=True)
  return [x for x in res.stdout.strip().split("\n") if "tasks/" in x or "roles/" in x]

def construct_command(tags):
  command = f"ANSIBLE_CONFIG=ansible.cfg /usr/bin/ansible-playbook main.yml --vault-password-file ~/.vault_pass.txt"
  command += f" --tags {",".join(tags)}"

  print(command)
  return command

def deploy(tags):
  print(f"[MAIN] Deploying...")
  command = construct_command(tags)
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
  ignore_deploys_for = [
    "tasks/runner",
    "templates/runner",
    "roles/docker"
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
    split_string = file.split("/")
    service_name = split_string[1].split(".")[0] + "_deploy" if "." in split_string[1] else split_string[1] + "_deploy"

    # i'm not proud of this either
    if not os.path.exists(os.path.join(dir_path, file)):
      if "roles" in file and not os.path.exists(os.path.join(dir_path, service_name)):
        print(f"[MAIN] '{task_name}' role removed, marking for cleanup..")
        removed_containers.append(service_name)
      elif "tasks" in task_name:
        print(f"[MAIN] '{task_name}' non-existent, marking for cleanup..")
        removed_containers.append(service_name) 
    else:
      if service_name not in ignore_deploys_for and service_name not in new_diff:
        new_diff.append(service_name)

  if len(new_diff) > 0:
    print(new_diff, ",".join(new_diff))
    deployed = deploy(",".join(new_diff))
  else:
    # success, nothing deployed
    deployed = True

  for task in removed_containers:
    print(f"[MAIN] Attempting to remove containers related to '{task}'...")
    if len(task.split("/")) > 1:
      task_name = task.split("/")[1].split(".")[0]
    else:
      task_name = task
 
    containers = subprocess.Popen(f'docker ps --filter "name={task_name}" -q', shell=True, stdout=subprocess.PIPE)
    for line in containers.stdout:
      container_id = line.strip().decode("utf8")
      print(f"[MAIN] Found Docker container {container_id} related to {task_name}, removing..")
      subprocess.run(f"/usr/bin/docker container stop {container_id}", shell=True)
      subprocess.run(f"/usr/bin/docker container rm {container_id}", shell=True)
      subprocess.run("/usr/bin/docker image prune -f", shell=True)
      subprocess.run("/usr/bin/docker container prune -f", shell=True)

  if deployed and len(new_diff) > 0: 
    print("\n---------------------")
    print(" Deployment succeeded!")
    print(f" All tasks: {', '.join(new_diff)}")
    print("---------------------\n")
    sys.exit(0)
  elif not deployed and len(new_diff) > 0:
    print("\n---------------------")
    print(" Deployment failed!")
    print(f" All tasks: {', '.join(new_diff)}")
    print("---------------------\n")
    sys.exit(1)
  elif len(new_diff) <= 0:
    print("[MAIN] Successfully executed, no tasks required execution")
    sys.exit(0)

if __name__ == "__main__":
  main()